"""Independent Fraction/RN32 closest approach on supplied pair chords."""
from . import f32 as f
from .float_reference import rows
from .reference import Job,MAGIC,encode
WID='SPACE_SWEPT_SPHERE_ENCOUNTER_F32_V1'


def encounter(pair):
    a0,a1,b0,b1=pair[:3],pair[3:6],pair[6:9],pair[9:12]
    p=[f.sub(y,x) for x,y in zip(a0,b0)];q=[f.sub(y,x) for x,y in zip(a1,b1)]
    d=[f.sub(y,x) for x,y in zip(p,q)];aa=f.dot(d,d);bb=f.dot(p,d)
    t=0
    if aa and f.rational(bb)<0:t=f.ONE if f.rational(f.neg(bb))>=f.rational(aa) else f.div(f.neg(bb),aa)
    nearest=p if t==0 else q if t==f.ONE else [f.add(x,f.mul(t,v)) for x,v in zip(p,d)]
    dmin=f.dot(nearest,nearest);start=f.dot(p,p);end=f.dot(q,q);r=f.add(pair[12],pair[13]);r2=f.mul(r,r)
    return [int(dmin<=r2),t,dmin,start,end,r2,int(aa==0)]


def prepare_space_encounter(wid,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('binary32 encounter contract required')
    pairs=rows(payload['pairs'],14,4096)
    if any(f.rational(v)<0 for pair in pairs for v in pair[12:]):raise ValueError('nonnegative radii required')
    flat=[v for pair in pairs for v in pair];out=[v for pair in pairs for v in encounter(pair)]
    header=[MAGIC,1,71,len(pairs),14,0,0,0,0,0,0,16+len(flat),16+len(flat),7,0,0]
    return Job(wid,payload,header+flat,len(pairs),7,encode(out))
