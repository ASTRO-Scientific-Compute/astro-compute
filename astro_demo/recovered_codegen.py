"""Contract-preserving generated variants; no change to canonical mathematics."""
import re
import subprocess
from pathlib import Path

from science_library.catalog import SPECS
from science_library.shaders import shader
from .support import sha
from .limits import require_workload

FAMILIES = ('DIRECT', 'COMPILER_VARIANT', 'TILED')


def legal(job, config, caps):
    require_workload(job.workload_id)
    family, local, pack = config['family'], config['local_size'], config['pack']
    if family not in FAMILIES or local not in (32, 64, 128, 256) or pack not in (1, 2, 4):
        return False
    if local > caps['limits']['max_compute_workgroup_invocations']:
        return False
    if family == 'TILED':
        op = SPECS[job.workload_id]['opcode']
        if op in (30, 32):
            return pack == 1 and (2048 if op == 30 else local*4) <= caps['limits']['max_compute_shared_memory_size']
        if op not in (11, 31):
            return False
        taps = job.words[5] if op == 11 else 9
        needed = 4 * (local * pack + taps - 1 + taps)
        return needed <= caps['limits']['max_compute_shared_memory_size']
    return True


def source(job, config):
    require_workload(job.workload_id)
    family, local, pack = config['family'], config['local_size'], config['pack']
    op = SPECS[job.workload_id]['opcode']
    if family not in FAMILIES:
        raise ValueError('unknown experimental family')
    text = shader(job.workload_id, local, pack, 'GENERIC_COMPUTE')
    if family == 'DIRECT':
        return text
    if family == 'TILED':
        if op in (30, 32):
            if pack != 1:
                raise ValueError('cooperative record requires pack1')
            return cooperative_source(job, local)
        if op not in (11, 31):
            raise ValueError('no contract-preserving tiled adapter for opcode')
        taps = job.words[5] if op == 11 else 9
        tile_size = local * pack + taps - 1
        prefix = text.split('\nvoid run_record(uint i){')[0]
        prefix += f'\nshared uint tile[{tile_size}];\nshared uint weights[{taps}];\n'
        # All lanes, including inactive output lanes, participate in both loads
        # and the barrier. Partial partitions keep their original global indices.
        load_index = f'int(block+t)-{taps-1}' if op == 11 else 'int(block+t)-4'
        load = ('tile[t]=(idx>=0 && idx<int(data[4]))?A(uint(idx)):0u;' if op == 11
                else 'tile[t]=A(uint(clamp(idx,0,int(data[4])-1)));')
        if op == 11:
            compute = f'''uvec2 total=uvec2(0);for(uint k=0u;k<{taps}u && k<=i;k++)
                total=add64(total,signed64(int(weights[k])*int(tile[offset+{taps-1}u-k])));
                put64(i*2u,total);'''
        else:
            compute = '''uint total=0u;for(uint j=0u;j<9u;j++)
                total=sfadd(total,sfmul(tile[offset+j],weights[j]));result[i]=total;'''
        text = prefix + f'''
void main(){{
    uint lid=gl_LocalInvocationID.x,block=pc.first+gl_WorkGroupID.x*{local*pack}u;
    for(uint t=lid;t<{tile_size}u;t+={local}u){{int idx={load_index};{load}}}
    for(uint t=lid;t<{taps}u;t+={local}u)weights[t]=B(t);
    barrier();
    for(uint lane=0u;lane<{pack}u;lane++){{
        uint offset=lid*{pack}u+lane,index=gl_WorkGroupID.x*{local*pack}u+offset;
        if(index<pc.count){{uint i=pc.first+index;{compute}}}
    }}
}}
'''
    # Only the ABI header is specialized, never any scientific input/output.
    # The dispatcher checks all 16 words before it can use this artifact.
    return re.sub(r'\bdata\[(\d+)\]', lambda m: str(job.words[int(m[1])])+'u'
                  if int(m[1]) < 16 else m[0], text)


def cooperative_source(job, local):
    require_workload(job.workload_id)
    """Restore LDS/cooperative families without borrowing old tolerance math.

    FFT parallelizes independent radix-2 butterflies of the *canonical* graph.
    XCORR parallelizes products but performs every addition in canonical order.
    """
    op = SPECS[job.workload_id]['opcode']
    prefix = shader(job.workload_id, local, 1, 'GENERIC_COMPUTE').split('\nvoid run_record(uint i){')[0]
    if op == 30:
        body = f'''
shared uvec2 z[256];
void main(){{
    uint record=pc.first+gl_WorkGroupID.x,lid=gl_LocalInvocationID.x;
    for(uint j=lid;j<256u;j+={local}u){{uint reverse=bitfieldReverse(j)>>24u;z[j]=uvec2(A(record*256u+reverse),0u);}}
    barrier();
    for(uint size=2u;size<=256u;size*=2u){{
        for(uint butterfly=lid;butterfly<128u;butterfly+={local}u){{
            uint halfsize=size/2u,j=butterfly%halfsize,base=(butterfly/halfsize)*size,t=j*256u/size;
            uvec2 tw=uvec2(B(t*2u),B(t*2u+1u)),a=z[base+j],b=z[base+j+halfsize];
            uvec2 v=uvec2(sfsub(sfmul(tw.x,b.x),sfmul(tw.y,b.y)),sfadd(sfmul(tw.x,b.y),sfmul(tw.y,b.x)));
            z[base+j]=uvec2(sfadd(a.x,v.x),sfadd(a.y,v.y));z[base+j+halfsize]=uvec2(sfsub(a.x,v.x),sfsub(a.y,v.y));
        }}
        barrier();
    }}
    for(uint j=lid;j<256u;j+={local}u){{result[record*512u+j*2u]=z[j].x;result[record*512u+j*2u+1u]=z[j].y;}}
}}
'''
    elif op == 32:
        body = f'''
shared uint products[{local}];
void main(){{
    uint record=pc.first+gl_WorkGroupID.x,lid=gl_LocalInvocationID.x;
    int lag=int(record)-64;uint begin=uint(max(0,-lag)),end=min(data[4],uint(int(data[4])-max(0,lag))),sum=0u;
    for(uint block=begin;block<end;block+={local}u){{
        uint j=block+lid;products[lid]=j<end?sfmul(A(j),B(uint(int(j)+lag))):0u;
        barrier();
        if(lid==0u)for(uint k=0u;k<min({local}u,end-block);k++)sum=sfadd(sum,products[k]);
        barrier();
    }}
    if(lid==0u)result[record]=sum;
}}
'''
    else:
        raise ValueError('unsupported cooperative record')
    return prefix + body


def compile_candidate(job, config, directory, caps):
    require_workload(job.workload_id)
    if not legal(job, config, caps):
        raise ValueError('unsupported config or runtime hardware limit')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    path = directory / 'kernel.comp'
    path.write_text(source(job, config))
    binary = directory / 'kernel.spv'
    for args in [['glslangValidator', '-V', '--target-env', 'vulkan1.1', '-S', 'comp', str(path), '-o', str(binary)],
                 ['spirv-val', '--target-env', 'vulkan1.1', str(binary)]]:
        cp = subprocess.run(args, capture_output=True, text=True, timeout=90)
        if cp.returncode:
            raise RuntimeError(cp.stdout + cp.stderr)
    artifact = dict(source=str(path.resolve()), spirv=str(binary.resolve()), source_sha256=sha(path),
                    spirv_sha256=sha(binary), local=config['local_size'], pack=config['pack'],
                    backend='GENERIC_COMPUTE', experimental_family=config['family'], config=config,
                    header_binding=list(job.words[:16]) if config['family'] != 'DIRECT' else None,
                    workload_id=job.workload_id, production_ready=False)
    artifact['dispatch_mode'] = ('WORKGROUP_PER_RECORD' if config['family']=='TILED' and
                                 SPECS[job.workload_id]['opcode'] in (30,32) else 'INVOCATION_PER_RECORD')
    return artifact


def check_job_binding(job, artifact):
    require_workload(job.workload_id)
    if artifact['workload_id'] != job.workload_id:
        raise ValueError('workload mismatch')
    if artifact.get('header_binding') is not None and list(job.words[:16]) != artifact['header_binding']:
        raise ValueError('specialized ABI header mismatch: compile this shape separately')
    if sha(artifact['source']) != artifact['source_sha256'] or sha(artifact['spirv']) != artifact['spirv_sha256']:
        raise ValueError('candidate artifact changed')
