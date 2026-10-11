import random
from .space_statistics_vectors import hx


def make(elements=((1,1.25,0),),mu=1):
    return dict(encoding='binary32-hex',anomaly_unit='hyperbolic-radian',a_semantics='POSITIVE_HYPERBOLIC_MAGNITUDE',frame='PERIFOCAL',distance_unit='length',time_unit='time',elements=[hx(list(v)) for v in elements],mu=hx(mu))


GOLDEN={76:(make(),[0,0x3e800000,0x3e800000,0,0,0,0x40400000,0])}


def fixture(op=76,seed=271828,scale=1):
    if op!=76:raise ValueError(op)
    rng=random.Random(seed)
    return make([[2**rng.randrange(-8,9),rng.randrange(20,65)/16,rng.randrange(-256,257)/16] for _ in range(17*scale)],mu=2)


def edges(op=76):
    if op!=76:raise ValueError(op)
    out=[('periapsis',make([[1,e,0] for e in (1.25,1.5,2,4)])),
         ('minimum_eccentricity',make([[1,1.25,k/2] for k in range(-32,33)])),
         ('maximum_eccentricity',make([[1,4,k/2] for k in range(-32,33)])),
         ('anomaly_limits',make([[1,e,m] for e in (1.25,2,4) for m in (-16,16)])),
         ('small_anomaly',make([[1,1.25,m] for m in (-2**-24,2**-24)])),
         ('minimum_scales',make([[2**-32,1.25,-16],[2**-32,4,16]],mu=2**-32)),
         ('maximum_scales',make([[2**32,1.25,-16],[2**32,4,16]],mu=2**32)),
         ('maximum_velocity',make([[2**-32,1.25,0],[2**-32,4,16]],mu=2**32)),
         ('minimum_velocity',make([[2**32,1.25,0],[2**32,4,-16]],mu=2**-32))]
    p=make();p['elements'][0][2]='80000000';out.append(('signed_zero',p))
    p=make([[1,1.25,0],[1,1.25,0]]);p['elements'][0][2]='00000001';p['elements'][1][2]='80000001';out.append(('subnormal_anomaly',p))
    p=fixture();p['elements']=(p['elements']*61)[:1024];out.append(('maximum_records',p))
    return out
