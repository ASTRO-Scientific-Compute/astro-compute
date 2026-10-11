"""Independent Fraction/RN32 Barker equation and zero-energy conic state."""
from fractions import Fraction
from . import f32 as f
from .reference import Job, MAGIC, encode
from .float_reference import rows
WID='SPACE_PARABOLIC_BARKER_STATE_F32_V1'


def state(q,mean,mu):
    mean=f.add(mean,0);anomaly=0
    if mean:
        negative=f.rational(mean)<0;target=f.neg(mean) if negative else mean
        lo,hi=0,0x40800000
        for _ in range(32):
            mid=f.mul(f.add(lo,hi),f.HALF)
            cube=f.mul(f.mul(mid,mid),mid)
            residual=f.sub(f.add(mid,f.div(cube,0x40400000)),target)
            if f.rational(residual)<0:lo=mid
            else:hi=mid
        anomaly=f.mul(f.add(lo,hi),f.HALF)
        if negative:anomaly=f.neg(anomaly)
    square=f.mul(anomaly,anomaly);den=f.add(f.ONE,square)
    radius=f.mul(q,den);x=f.mul(q,f.sub(f.ONE,square));y=f.mul(f.mul(f.TWO,q),anomaly)
    scale=f.div(f.sqrt(f.div(f.mul(f.TWO,mu),q)),den)
    return [anomaly,radius,x,y,0,f.neg(f.mul(scale,anomaly)),scale,0]


def prepare_space_parabolic(wid,payload):
    tags=dict(encoding='binary32-hex',model='PARABOLIC_E1',anomaly_unit='barker-dimensionless',frame='PERIFOCAL')
    if set(payload)!=set(tags)|{'distance_unit','time_unit','mu','elements'} or any(payload.get(k)!=v for k,v in tags.items()):
        raise ValueError('exact parabolic e1 fields and explicit Barker/PERIFOCAL contract required')
    for key in ('distance_unit','time_unit'):
        text=payload[key]
        if not isinstance(text,str) or not text.strip() or len(text)>64:raise ValueError('explicit bounded distance/time units required')
    elements=rows(payload['elements'],2,1024);mu=f.parse(payload['mu']);lo,hi=Fraction(1,1<<32),Fraction(1<<32)
    if not lo<=f.rational(mu)<=hi:raise ValueError('mu outside bounded parabolic scale')
    output=[]
    for q,mean in elements:
        if not lo<=f.rational(q)<=hi or not -16<=f.rational(mean)<=16:raise ValueError('q/M outside bounded parabolic contract')
        output.extend(state(q,mean,mu))
    n=len(elements);header=[MAGIC,1,77,n,2,0,0,0,mu,0,0,16+2*n,16+2*n,8,0,0]
    return Job(wid,payload,header+sum(elements,[]),n,8,encode(output))
