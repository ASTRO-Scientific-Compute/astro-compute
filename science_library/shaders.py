from .space_sip_shaders import BODIES as SPACE_SIP_BODIES
from .space_tangent_vector_shaders import BODIES as SPACE_TANGENT_VECTOR_BODIES, HELPERS as TANGENT_VECTOR_HELPERS
from .space_gnomonic_shaders import BODIES as SPACE_GNOMONIC_BODIES, HELPERS as GNOMONIC_HELPERS
from .space_coherence_shaders import BODIES as SPACE_COHERENCE_BODIES
from .space_parabolic_shaders import BODIES as SPACE_PARABOLIC_BODIES
from .space_hyperbolic_shaders import BODIES as SPACE_HYPERBOLIC_BODIES, HELPERS as HYPERBOLIC_HELPERS
from .space_kepler_shaders import BODIES as SPACE_KEPLER_BODIES, HELPERS as KEPLER_HELPERS
from .space_precession_shaders import BODIES as SPACE_PRECESSION_BODIES, HELPERS as PRECESSION_HELPERS
from .space_rts_shaders import BODIES as SPACE_RTS_BODIES
from .space_kalman_shaders import BODIES as SPACE_KALMAN_BODIES
from .space_encounter_shaders import BODIES as SPACE_ENCOUNTER_BODIES
from .space_nbody_shaders import BODIES as SPACE_NBODY_BODIES, helpers as nbody_helpers
from .space_joint_gls_shaders import BODIES as SPACE_JOINT_GLS_BODIES
from .space_gls_shaders import BODIES as SPACE_GLS_BODIES
from .space_uncertainty_shaders import BODIES as SPACE_UNCERTAINTY_BODIES
from .space_mode_shaders import BODIES as SPACE_MODE_BODIES
from .space_biweight_shaders import BODIES as SPACE_BIWEIGHT_BODIES
from .space_background_shaders import BODIES as SPACE_BACKGROUND_BODIES
from .space_psf_shaders import BODIES as SPACE_PSF_BODIES
from .space_period_shaders import BODIES as SPACE_PERIOD_BODIES, helpers as period_helpers
from .space_dynamics_shaders import BODIES as SPACE_DYNAMICS_BODIES, helpers as dynamics_helpers
from .space_imaging_shaders import BODIES as SPACE_IMAGING_BODIES, helpers as imaging_helpers
from .space_search_shaders import BODIES as SPACE_SEARCH_BODIES, helpers as space_search_helpers
from .space_statistics_shaders import BODIES as SPACE_STATISTICS_BODIES
from .space_inference_shaders import BODIES as SPACE_INFERENCE_BODIES, helpers as inference_helpers
"""GPU implementations; contracts, CPU oracle and analytic vectors precede these."""
from .triangle_shader import ARITHMETIC as TRIANGLE_ARITHMETIC, body as triangle_body
from .catalog import SPECS
from .float_shaders import BODIES as FLOAT_BODIES, helpers
from .legacy_shaders import BODIES as LEGACY_BODIES, helpers as legacy_helpers

HEADER = r'''
#version 460
#ifdef USE_RT
#extension GL_EXT_ray_query : require
layout(set=0,binding=3) uniform accelerationStructureEXT scene;
#endif
#if defined(USE_RT) || defined(USE_WORKSPACE)
layout(set=0,binding=2,std430) buffer Seen { uint seen[]; };
#endif
layout(local_size_x=LOCAL) in;
layout(set=0,binding=0,std430) readonly buffer Input { uint data[]; };
layout(set=0,binding=1,std430) writeonly buffer Output { uint result[]; };
layout(push_constant) uniform PC { uint first; uint count; } pc;
uint A(uint i){return data[16u+i];}
uint B(uint i){return data[data[11]+i];}
uint C(uint i){return data[data[12]+i];}
uvec2 add64(uvec2 a,uvec2 b){uint lo=a.x+b.x;return uvec2(lo,a.y+b.y+uint(lo<a.x));}
uvec2 mul64(uint a,uint b){uint hi,lo;umulExtended(a,b,hi,lo);return uvec2(lo,hi);}
uvec2 signed64(int x){return uvec2(uint(x),x<0?0xffffffffu:0u);}
bool less64(uvec2 a,uvec2 b){return a.y<b.y||(a.y==b.y&&a.x<b.x);}
bool equal64(uvec2 a,uvec2 b){return all(equal(a,b));}
void put64(uint o,uvec2 x){result[o]=x.x;result[o+1]=x.y;}
uvec2 d2(uint q,uint p){uvec2 sum=uvec2(0);for(uint k=0;k<3;k++){int d=int(A(q*3+k))-int(B(p*3+k));uint v=uint(abs(d));sum=add64(sum,mul64(v,v));}return sum;}
'''

BODIES={
1:r'''
    uvec2 sums[6];for(uint k=0;k<6;k++)sums[k]=uvec2(0);
    uint w=data[6],h=data[7];
    for(uint y=0;y<h;y++)for(uint x=0;x<w;x++){
        uint v=A(i*w*h+y*w+x);uint f[6]=uint[6](1,x,y,x*x,x*y,y*y);
        for(uint k=0;k<6;k++)sums[k]=add64(sums[k],mul64(v,f[k]));
    }
    for(uint k=0;k<6;k++)put64(i*12+k*2,sums[k]);
''',
2:r'''
    int cx=int(B(i*4)),cy=int(B(i*4+1)),r=int(B(i*4+2)),bg=int(B(i*4+3));int flux=0;uint count=0;
    for(uint y=0;y<data[7];y++)for(uint x=0;x<data[6];x++){
        int dx=int(x)-cx,dy=int(y)-cy;if(dx*dx+dy*dy<=r*r){flux+=int(A(y*data[6]+x))-bg;count++;}
    }
    result[i*2]=uint(flux);result[i*2+1]=count;
''',
3:r'''
    uint bin=i%data[8],period=C(i/data[8]),count=0;uvec2 sum=uvec2(0),square=uvec2(0);
    for(uint j=0;j<data[4];j++)if((A(j)%period)*data[8]/period==bin){int v=int(B(j));count++;sum=add64(sum,signed64(v));square=add64(square,mul64(uint(abs(v)),uint(abs(v))));}
    result[i*5]=count;put64(i*5+1,sum);put64(i*5+3,square);
''',
4:r'''
    uvec2 sums[6];for(uint k=0;k<6;k++)sums[k]=uvec2(0);
    for(uint j=0;j<data[4];j++){uint base=(i*data[4]+j)*3;int x=int(A(base)),y=int(A(base+1)),w=int(A(base+2));int v[6]=int[6](w,w*x,w*y,w*x*x,w*x*y,w*y*y);for(uint k=0;k<6;k++)sums[k]=add64(sums[k],signed64(v[k]));}
    for(uint k=0;k<6;k++)put64(i*12+k*2,sums[k]);
''',
6:r'''
    uint base=i*258,na=A(base),nb=A(base+1);int prev[129],cur[129];for(uint j=0;j<=nb;j++)prev[j]=0;int best=0;
    for(uint x=1;x<=na;x++){cur[0]=0;for(uint y=1;y<=nb;y++){int score=A(base+2+x-1)==A(base+130+y-1)?2:-1;cur[y]=max(0,max(prev[y-1]+score,max(prev[y]-2,cur[y-1]-2)));best=max(best,cur[y]);}for(uint y=0;y<=nb;y++)prev[y]=cur[y];}
    result[i]=uint(best);
''',
8:r'''
    put64(i*2,d2(i/data[5],i%data[5]));
''',
10:r'''
    uint w=data[6],h=data[7],x=i%w,y=i/w;int s=int(A(i));int e=-s*(int(A(y*w+(x+1)%w))+int(A(((y+1)%h)*w+x)));result[i*2]=uint(e);result[i*2+1]=uint(s);
''',
11:r'''
    uvec2 total=uvec2(0);for(uint k=0;k<data[5]&&k<=i;k++)total=add64(total,signed64(int(B(k))*int(A(i-k))));put64(i*2,total);
''',
12:r'''
    uvec2 total=uvec2(0);for(uint j=A(i);j<A(i+1);j++)total=add64(total,signed64(int(B(j*2+1))*int(C(B(j*2)))));put64(i*2,total);
''',
13:r'''
    uint b=i*6;int ax=int(A(b)),ay=int(A(b+1)),bx=int(A(b+2)),by=int(A(b+3)),cx=int(A(b+4)),cy=int(A(b+5));int det=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax);result[i*2]=uint(det);result[i*2+1]=uint(det>0?1:(det<0?-1:0));
''',
}


BODIES.update(SPACE_SEARCH_BODIES)
BODIES.update(SPACE_STATISTICS_BODIES)
BODIES.update(SPACE_INFERENCE_BODIES)
BODIES.update(SPACE_IMAGING_BODIES)
BODIES.update(SPACE_DYNAMICS_BODIES)
BODIES.update(SPACE_PERIOD_BODIES)
BODIES.update(SPACE_PSF_BODIES)
BODIES.update(SPACE_BACKGROUND_BODIES)
BODIES.update(SPACE_BIWEIGHT_BODIES)
BODIES.update(SPACE_MODE_BODIES)
BODIES.update(SPACE_UNCERTAINTY_BODIES)
BODIES.update(SPACE_GLS_BODIES)
BODIES.update(SPACE_JOINT_GLS_BODIES)
BODIES.update(SPACE_NBODY_BODIES)
BODIES.update(SPACE_ENCOUNTER_BODIES)
BODIES.update(SPACE_KALMAN_BODIES)
BODIES.update(SPACE_RTS_BODIES)
BODIES.update(SPACE_KEPLER_BODIES)
BODIES.update(SPACE_HYPERBOLIC_BODIES)
BODIES.update(SPACE_PARABOLIC_BODIES)
BODIES.update(SPACE_COHERENCE_BODIES)
BODIES.update(SPACE_GNOMONIC_BODIES)
BODIES.update(SPACE_TANGENT_VECTOR_BODIES)
BODIES.update(SPACE_SIP_BODIES)
BODIES.update(SPACE_PRECESSION_BODIES)
BODIES.update(FLOAT_BODIES)
BODIES.update(LEGACY_BODIES)

def spatial(op, rt):
    setup = 'uint q=i,bin=0;uvec2 lower=uvec2(0),upper=uvec2(data[8],data[9]);' if op!=9 else 'uint q=i/data[8],bin=i%data[8];uvec2 lower=uvec2(C(bin*2),C(bin*2+1)),upper=uvec2(C((bin+1)*2),C((bin+1)*2+1));'
    setup += 'uint count=0,nearest=0xffffffffu;uvec2 best=uvec2(0xffffffffu);'
    accept = 'bool inside=!less64(upper,dist);' if op!=9 else 'bool inside=!less64(dist,lower)&&less64(dist,upper);'
    process = 'uvec2 dist=d2(q,j);'+accept+'if(inside){count++;if(less64(dist,best)||(equal64(dist,best)&&j<nearest)){best=dist;nearest=j;}}'
    if rt:
        loop = r'''
        uint seen_words=(data[5]+31u)/32u,seen_base=i*seen_words;
        for(uint k=0;k<seen_words;k++)seen[seen_base+k]=0u;
        rayQueryEXT rq;
        vec3 origin=vec3(int(A(q*3)),int(A(q*3+1)),int(A(q*3+2)));
        rayQueryInitializeEXT(rq,scene,0u,0xffu,origin,0.0,vec3(0,0,1),1.0);
        while(rayQueryProceedEXT(rq)){
            if(rayQueryGetIntersectionTypeEXT(rq,false)==gl_RayQueryCandidateIntersectionAABBEXT){
                uint j=rayQueryGetIntersectionPrimitiveIndexEXT(rq,false);
                if(j<data[5]){uint slot=seen_base+j/32u,mask=1u<<(j%32u);if((seen[slot]&mask)==0u){seen[slot]|=mask;PROCESS}}
            }
        }
        '''.replace('PROCESS',process)
    else:loop='for(uint j=0;j<data[5];j++){'+process+'}'
    end = 'result[i*4]=count;result[i*4+1]=nearest;put64(i*4+2,best);' if op==5 else 'result[i]=count;'
    return setup+loop+end


def shader(workload_id, local=64, pack=1, backend='GENERIC_COMPUTE'):
    from astro_demo.limits import require_workload
    require_workload(workload_id)
    if backend != 'GENERIC_COMPUTE':
        raise ValueError('GPU demo supports compute only')
    if local not in (32,64,128,256) or pack not in (1,2,4):raise ValueError('illegal genome')
    op=SPECS[workload_id]['opcode'];rt=backend in ('RT_COMPUTE','RT_REBUILD')
    if backend not in ('GENERIC_COMPUTE','RT_COMPUTE','RT_REBUILD') or rt and op not in (5,7,9,37,38) or backend=='RT_REBUILD' and op!=38:raise ValueError('unsupported backend')
    body=triangle_body(rt) if op in (37,38) else spatial(op,rt) if op in (5,7,9) else BODIES[op]
    text=HEADER.replace('#version 460',f'#version 460\n#define LOCAL {local}\n'+('#define USE_RT\n' if rt else ''))
    if op in (34,35,38):text=text.replace('#version 460','#version 460\n#define USE_WORKSPACE')
    if op>=14:text+=helpers(op)
    if op==80:text+=TANGENT_VECTOR_HELPERS
    if op==79:text+=GNOMONIC_HELPERS
    if op==76:text+=HYPERBOLIC_HELPERS
    if op==75:text+=KEPLER_HELPERS
    if op==74:text+=PRECESSION_HELPERS
    if 30<=op<=36:text+=legacy_helpers(op)
    if op==38:text=text.replace("#version 460","#version 460\n#define DYNAMIC_TRIANGLES")
    if op in (37,38):text+=TRIANGLE_ARITHMETIC
    if op>=39:text+=space_search_helpers(op)
    if op>=48:text+=inference_helpers(op)
    if op>=51:text+=imaging_helpers(op)
    if op>=54:text+=dynamics_helpers(op)
    if op>=57:text+=period_helpers(op)
    if op>=69:text+=nbody_helpers(op)
    if op in (34,35,38):
        main='void main(){uint base=gl_GlobalInvocationID.x*'+str(pack)+'u;for(uint lane=0u;lane<'+str(pack)+'u;lane++){uint index=base+lane;if(index<pc.count){if((pc.first&0x80000000u)!=0u)run_prepass(index);else run_record(pc.first+index);}}}'
        return text+'\nvoid run_record(uint i){\n'+body+'\n}\n'+main+'\n'
    return text+'\nvoid run_record(uint i){\n'+body+'\n}\nvoid main(){uint base=gl_GlobalInvocationID.x*'+str(pack)+'u;for(uint lane=0;lane<'+str(pack)+'u;lane++){uint index=base+lane;if(index<pc.count)run_record(pc.first+index);}}\n'
