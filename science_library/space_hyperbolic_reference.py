"""Independent unbounded Fraction/RN32 hyperbolic solve and escape state."""
from fractions import Fraction
from math import factorial
from . import f32 as f
from .reference import Job, MAGIC, encode
from .float_reference import rows
WID = 'SPACE_HYPERBOLIC_KEPLER_STATE_F32_V1'
SINH_COEFFICIENTS = tuple(f.rounded(Fraction(1, factorial(2*k+1))) for k in range(11))
COSH_COEFFICIENTS = tuple(f.rounded(Fraction(1, factorial(2*k))) for k in range(12))


def polynomial(q, coefficients):
    value = coefficients[-1]
    for coefficient in reversed(coefficients[:-1]):
        value = f.add(coefficient, f.mul(q, value))
    return value


def sinh(x):
    return f.mul(x, polynomial(f.mul(x,x), SINH_COEFFICIENTS))


def cosh(x):
    return polynomial(f.mul(x,x), COSH_COEFFICIENTS)


def state(a,e,mean,mu):
    mean=f.add(mean,0)
    anomaly=0
    if mean:
        negative=f.rational(mean)<0
        target=f.neg(mean) if negative else mean
        lo,hi=0,0x40800000
        for _ in range(32):
            mid=f.mul(f.add(lo,hi),f.HALF)
            residual=f.sub(f.sub(f.mul(e,sinh(mid)),mid),target)
            if f.rational(residual)<0:lo=mid
            else:hi=mid
        anomaly=f.mul(f.add(lo,hi),f.HALF)
        if negative:anomaly=f.neg(anomaly)
    s,c=sinh(anomaly),cosh(anomaly)
    beta=f.sqrt(f.sub(f.mul(e,e),f.ONE));d=f.sub(f.mul(e,c),f.ONE)
    radius=f.mul(a,d);scale=f.div(f.sqrt(f.div(mu,a)),d)
    return [anomaly,radius,f.mul(a,f.sub(e,c)),f.mul(f.mul(a,beta),s),0,f.neg(f.mul(scale,s)),f.mul(f.mul(scale,beta),c),0]


def prepare_space_hyperbolic(wid,payload):
    tags=dict(encoding='binary32-hex',anomaly_unit='hyperbolic-radian',a_semantics='POSITIVE_HYPERBOLIC_MAGNITUDE',frame='PERIFOCAL')
    if any(payload.get(k)!=v for k,v in tags.items()):raise ValueError('explicit hyperbolic units/a semantics/PERIFOCAL required')
    for key in ('distance_unit','time_unit'):
        text=payload.get(key)
        if not isinstance(text,str) or not text.strip() or len(text)>64:raise ValueError('explicit bounded distance/time unit labels required')
    elements=rows(payload['elements'],3,1024);mu=f.parse(payload['mu'])
    lo,hi=Fraction(1,1<<32),Fraction(1<<32)
    if not lo<=f.rational(mu)<=hi:raise ValueError('mu scale outside bounded hyperbolic contract')
    output=[]
    for a,e,mean in elements:
        if not lo<=f.rational(a)<=hi or not Fraction(5,4)<=f.rational(e)<=4 or not -16<=f.rational(mean)<=16:
            raise ValueError('a/e/M outside bounded hyperbolic contract')
        output.extend(state(a,e,mean,mu))
    n=len(elements);header=[MAGIC,1,76,n,3,0,0,0,mu,0,0,16+3*n,16+3*n,8,0,0]
    return Job(wid,payload,header+sum(elements,[]),n,8,encode(output))
