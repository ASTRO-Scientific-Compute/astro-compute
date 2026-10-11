"""Independent Python integer oracle and strict job contracts (no NumPy casts)."""
from dataclasses import dataclass
import struct
from .catalog import SPECS

MASK = 0xffffffff
MAGIC = 0x41535452
MAX_RECORDS = 1_000_000


def integer(value, lo, hi, name='integer'):
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError(f'{name}: expected integer in [{lo},{hi}], got {value!r}')
    return value


def array(value, lo, hi, name='array', maximum=MAX_RECORDS):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f'{name}: expected list with <= {maximum} entries')
    return [integer(v, lo, hi, name) for v in value]


def matrix(value, width, lo, hi, name='matrix', maximum=MAX_RECORDS):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(name+': invalid rows')
    rows = [array(v,lo,hi,name,width) for v in value]
    if any(len(v)!=width for v in rows):
        raise ValueError(name+': invalid row width')
    return rows


def words64(x):
    if not -(1<<63) <= x < (1<<64):
        raise ValueError('64-bit accumulator overflow')
    return [x & MASK, (x >> 32) & MASK]


def encode(words):
    return struct.pack('<'+'I'*len(words), *(x & MASK for x in words))


def distance2(q,p):
    return sum((a-b)**2 for a,b in zip(q,p))


@dataclass
class Job:
    workload_id: str
    payload: dict
    words: list
    records: int
    output_width: int
    reference: bytes
    geometry_reference: bytes | None = None

    @property
    def input_bytes(self):
        return encode(self.words)


def prepare(workload_id, payload):
    spec = SPECS[workload_id]
    op = spec['opcode']
    if not isinstance(payload, dict):
        raise ValueError('payload must be an object')
    if op==81:
        from .space_sip_reference import prepare_space_sip
        return prepare_space_sip(workload_id,payload)
    if op==80:
        from .space_tangent_vector_reference import prepare_space_tangent_vector
        return prepare_space_tangent_vector(workload_id,payload)
    if op==79:
        from .space_gnomonic_reference import prepare_space_gnomonic
        return prepare_space_gnomonic(workload_id,payload)
    if op==78:
        from .space_coherence_reference import prepare_space_coherence
        return prepare_space_coherence(workload_id,payload)
    if op==77:
        from .space_parabolic_reference import prepare_space_parabolic
        return prepare_space_parabolic(workload_id,payload)
    if op==76:
        from .space_hyperbolic_reference import prepare_space_hyperbolic
        return prepare_space_hyperbolic(workload_id,payload)
    if op==75:
        from .space_kepler_reference import prepare_space_kepler
        return prepare_space_kepler(workload_id,payload)
    if op==74:
        from .space_precession_reference import prepare_space_precession
        return prepare_space_precession(workload_id,payload)
    if op==73:
        from .space_rts_reference import prepare_space_rts
        return prepare_space_rts(workload_id,payload)
    if op==72:
        from .space_kalman_reference import prepare_space_kalman
        return prepare_space_kalman(workload_id,payload)
    if op==71:
        from .space_encounter_reference import prepare_space_encounter
        return prepare_space_encounter(workload_id,payload)
    if op in (69,70):
        from .space_nbody_reference import prepare_space_nbody
        return prepare_space_nbody(workload_id,op,payload)
    if op==68:
        from .space_joint_gls_reference import prepare_space_joint_gls
        return prepare_space_joint_gls(workload_id,op,payload)
    if op==67:
        from .space_gls_reference import prepare_space_gls
        return prepare_space_gls(workload_id,op,payload)
    if 65<=op<=66:
        from .space_uncertainty_reference import prepare_space_uncertainty
        return prepare_space_uncertainty(workload_id,op,payload)
    if op==64:
        from .space_mode_reference import prepare_space_mode
        return prepare_space_mode(workload_id,op,payload)
    if op==63:
        from .space_biweight_reference import prepare_space_biweight
        return prepare_space_biweight(workload_id,op,payload)
    if op>=61:
        from .space_background_reference import prepare_space_background
        return prepare_space_background(workload_id,op,payload)
    if op>=59:
        from .space_psf_reference import prepare_space_psf
        return prepare_space_psf(workload_id,op,payload)
    if op>=57:
        from .space_period_reference import prepare_space_period
        return prepare_space_period(workload_id,op,payload)
    if op>=54:
        from .space_dynamics_reference import prepare_space_dynamics
        return prepare_space_dynamics(workload_id,op,payload)
    if op>=51:
        from .space_imaging_reference import prepare_space_imaging
        return prepare_space_imaging(workload_id,op,payload)
    if op>=48:
        from .space_inference_reference import prepare_space_inference
        return prepare_space_inference(workload_id,op,payload)
    if op>=45:
        from .space_statistics_reference import prepare_space_statistics
        return prepare_space_statistics(workload_id,op,payload)
    if op>=39:
        from .space_search_reference import prepare_space_search
        return prepare_space_search(workload_id,op,payload)
    if op>=37:
        from .triangle_reference import prepare_triangle
        return prepare_triangle(workload_id,op,payload)
    if op>=30:
        from .legacy_reference import prepare_legacy
        return prepare_legacy(workload_id,op,payload)
    if op>=25:
        from .domain_reference import prepare_domain
        return prepare_domain(workload_id,op,payload)
    if op>=14:
        from .float_reference import prepare_float
        return prepare_float(workload_id,op,payload)
    a=[];b=[];c=[];out=[];records=0;ow=1;n=0;m=0;w=0;h=0;p0=0;p1=0;p2=0
    if op==1:
        images=payload['images']
        if not isinstance(images,list) or not 1<=len(images)<=4096: raise ValueError('images count')
        h=len(images[0]); integer(h,1,64,'height')
        w=len(images[0][0]);integer(w,1,64,'width')
        for image in images:
            rows=matrix(image,w,0,65535,'image',64)
            if len(rows)!=h: raise ValueError('image height')
            moments=[0]*6
            for y,row in enumerate(rows):
                for x,v in enumerate(row):
                    for k,factor in enumerate((1,x,y,x*x,x*y,y*y)): moments[k]+=v*factor
                a.extend(row)
            for value in moments: out.extend(words64(value))
        records=len(images);ow=12
    elif op==2:
        image=payload['image'];h=len(image);integer(h,1,64,'height')
        w=len(image[0]);integer(w,1,64,'width')
        image=matrix(image,w,-65535,65535,'image',64)
        a=[v for row in image for v in row]
        apertures=matrix(payload['apertures'],4,-65535,65535,'apertures')
        for cx,cy,r,bg in apertures:
            integer(cx,0,w-1,'cx');integer(cy,0,h-1,'cy');integer(r,0,64,'radius')
            vals=[image[y][x]-bg for y in range(h) for x in range(w) if (x-cx)**2+(y-cy)**2<=r*r]
            out.extend((sum(vals),len(vals)));b.extend((cx,cy,r,bg))
        records=len(apertures);ow=2
    elif op==3:
        times=array(payload['times'],0,10_000_000,'times',8192)
        flux=array(payload['flux'],-1000,1000,'flux',8192)
        if len(times)!=len(flux):raise ValueError('time/flux length')
        periods=array(payload['periods'],1,1_000_000,'periods',4096)
        p0=integer(payload['bins'],1,256,'bins');n=len(times);m=len(periods)
        a=times;b=flux;c=periods
        for period in periods:
            accum=[[0,0,0] for _ in range(p0)]
            for t,y in zip(times,flux):
                row=accum[(t%period)*p0//period];row[0]+=1;row[1]+=y;row[2]+=y*y
            for count,total,square in accum: out.extend([count]+words64(total)+words64(square))
        records=m*p0;ow=5
    elif op==4:
        batches=payload['samples']
        if not isinstance(batches,list) or not 1<=len(batches)<=4096:raise ValueError('fits count')
        n=len(batches[0]);integer(n,0,1024,'samples per fit')
        for samples in batches:
            samples=matrix(samples,3,-1000,1000,'samples',1024)
            if len(samples)!=n:raise ValueError('fit length')
            sums=[0]*6
            for x,y,weight in samples:
                integer(weight,0,100,'weight');a.extend((x,y,weight))
                for j,z in enumerate((1,x,y,x*x,x*y,y*y)):sums[j]+=weight*z
            for total in sums:out.extend(words64(total))
        records=len(batches);ow=12
    elif op in (5,7,8,9):
        queries=matrix(payload['queries'],3,-1_000_000_000,1_000_000_000,'queries',65536)
        points=matrix(payload['catalog'],3,-1_000_000_000,1_000_000_000,'catalog',65536)
        unit=payload.get('coordinate_unit')
        if not isinstance(unit,str) or not unit.strip() or len(unit)>256:raise ValueError('explicit coordinate_unit required')
        n=len(queries);m=len(points)
        if n*m>16_000_000:raise ValueError('spatial job exceeds16M pairs; submit smaller query/catalog tiles')
        a=[v for q in queries for v in q];b=[v for q in points for v in q]
        if op in (5,7):
            r2=integer(payload['squared_radius'],0,12_000_000_000_000_000_000,'squared_radius')
            p0,p1=words64(r2)
            for q in queries:
                matches=[(distance2(q,p),j) for j,p in enumerate(points) if distance2(q,p)<=r2]
                if op==7:out.append(len(matches))
                else:
                    dist,idx=min(matches) if matches else ((1<<64)-1,MASK)
                    out.extend([len(matches),idx]+words64(dist))
            records=n;ow=4 if op==5 else 1
        elif op==8:
            if n*m>MAX_RECORDS:raise ValueError('pair tile too large')
            for q in queries:
                for p in points:out.extend(words64(distance2(q,p)))
            records=n*m;ow=2
        else:
            edges=array(payload['squared_edges'],0,12_000_000_000_000_000_000,'squared_edges',65)
            if len(edges)<2 or any(x>=y for x,y in zip(edges,edges[1:])):raise ValueError('strictly increasing edges required')
            p0=len(edges)-1
            if n*p0>MAX_RECORDS or n*m*p0>16_000_000:raise ValueError('RDF tile too large')
            c=[v for edge in edges for v in words64(edge)]
            for q in queries:
                ds=[distance2(q,p) for p in points]
                out.extend(sum(lo<=d<hi for d in ds) for lo,hi in zip(edges,edges[1:]))
            records=n*p0
    elif op==6:
        pairs=payload['pairs']
        if not isinstance(pairs,list) or len(pairs)>65536:raise ValueError('pairs')
        # Full 2D dynamic-programming oracle; GPU uses rolling rows independently.
        for pair in pairs:
            if not isinstance(pair,list) or len(pair)!=2:raise ValueError('pair')
            s,t=pair
            if any(not isinstance(x,str) or len(x)>128 or set(x)-set('ACGT') for x in pair):raise ValueError('DNA ACGT length0..128')
            rows=[[0]*(len(t)+1) for _ in range(len(s)+1)]
            for i,x in enumerate(s,1):
                for j,y in enumerate(t,1):
                    rows[i][j]=max(0,rows[i-1][j-1]+(2 if x==y else -1),rows[i-1][j]-2,rows[i][j-1]-2)
            out.append(max(max(row) for row in rows))
            a.extend([len(s),len(t)]+['ACGT'.index(x) for x in s]+[0]*(128-len(s))+['ACGT'.index(x) for x in t]+[0]*(128-len(t)))
        records=len(pairs)
    elif op==10:
        spins=payload['spins'];h=len(spins);integer(h,3,1024,'height');w=len(spins[0]);integer(w,3,1024,'width')
        spins=matrix(spins,w,-1,1,'spins',1024)
        if any(v==0 for row in spins for v in row):raise ValueError('spin must be -1 or +1')
        for y,row in enumerate(spins):
            for x,s in enumerate(row):out.extend((-s*(row[(x+1)%w]+spins[(y+1)%h][x]),s))
            a.extend(row)
        records=w*h;ow=2
    elif op==11:
        a=array(payload['samples'],-32768,32767,'samples')
        b=array(payload['coefficients'],-32768,32767,'coefficients',1024)
        if not b:raise ValueError('at least one coefficient required')
        n=len(a);m=len(b)
        for i in range(n):out.extend(words64(sum(coef*a[i-k] for k,coef in enumerate(b) if k<=i)))
        records=n;ow=2
    elif op==12:
        ptr=array(payload['rowptr'],0,MAX_RECORDS,'rowptr')
        col=array(payload['col'],0,MAX_RECORDS,'col')
        val=array(payload['values'],-32768,32767,'values')
        vector=array(payload['vector'],-32768,32767,'vector')
        if not ptr or ptr[0]!=0 or ptr[-1]!=len(col) or len(col)!=len(val):raise ValueError('CSR lengths')
        if any(x>y or y-x>65536 for x,y in zip(ptr,ptr[1:])) or any(i>=len(vector) for i in col):raise ValueError('CSR bounds')
        a=ptr;b=[v for pair in zip(col,val) for v in pair];c=vector
        for start,end in zip(ptr,ptr[1:]):out.extend(words64(sum(val[j]*vector[col[j]] for j in range(start,end))))
        records=len(ptr)-1;ow=2
    elif op==13:
        triangles=payload['triangles']
        if not isinstance(triangles,list) or len(triangles)>MAX_RECORDS:raise ValueError('triangles')
        for tri in triangles:
            tri=matrix(tri,2,-10000,10000,'triangle',3)
            if len(tri)!=3:raise ValueError('triangle needs3 points')
            (ax,ay),(bx,by),(cx,cy)=tri
            det=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
            out.extend((det,(det>0)-(det<0)));a.extend(v for p in tri for v in p)
        records=len(triangles);ow=2
    else:raise ValueError('unknown opcode')
    integer(records,0,MAX_RECORDS,'record count')
    if len(out)!=records*ow:raise AssertionError('CPU result shape')
    header=[MAGIC,1,op,records,n,m,w,h,p0,p1,p2,16+len(a),16+len(a)+len(b),ow,0,0]
    words=header+a+b+c
    if len(words)>32_000_000:raise ValueError('job exceeds128MB')
    return Job(workload_id,payload,words,records,ow,encode(out))


def compare_bytes(expected, actual):
    if len(actual)!=len(expected):
        return dict(pass_exact=False,compared_bytes=min(len(expected),len(actual)),expected_bytes=len(expected),actual_bytes=len(actual),differing_bits=None,reason='LENGTH_MISMATCH')
    count=sum((a^b).bit_count() for a,b in zip(expected,actual))
    return dict(pass_exact=count==0,compared_bytes=len(expected),expected_bytes=len(expected),actual_bytes=len(actual),differing_bits=count,allowed_differing_bits=0)
