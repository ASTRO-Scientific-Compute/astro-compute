import random
from .space_statistics_vectors import hx


def make(elements=((2,0),),mu=1):
    return dict(encoding='binary32-hex',model='PARABOLIC_E1',anomaly_unit='barker-dimensionless',frame='PERIFOCAL',distance_unit='length',time_unit='time',elements=[hx(list(v)) for v in elements],mu=hx(mu))


GOLDEN={77:(make(),[0,0x40000000,0x40000000,0,0,0,0x3f800000,0])}


def fixture(op=77,seed=271828,scale=1):
    if op!=77:raise ValueError(op)
    rng=random.Random(seed)
    return make([[2**rng.randrange(-8,9),rng.randrange(-256,257)/16] for _ in range(17*scale)],mu=2)


def edges(op=77):
    if op!=77:raise ValueError(op)
    out=[('periapsis_scales',make([[q,0] for q in (2**-16,1,2,2**16)])),
         ('anomaly_grid',make([[1,k/2] for k in range(-32,33)])),
         ('anomaly_limits',make([[q,m] for q in (.25,1,16) for m in (-16,16)])),
         ('nonlinear_interior',make([[1,m] for m in (-2,-1,-.5,-.25,.25,.5,1,2)])),
         ('small_anomaly',make([[1,-2**-24],[1,2**-24]])),
         ('minimum_scales',make([[2**-32,-16],[2**-32,16]],mu=2**-32)),
         ('maximum_scales',make([[2**32,-16],[2**32,16]],mu=2**32)),
         ('maximum_velocity',make([[2**-32,0],[2**-32,16]],mu=2**32)),
         ('minimum_velocity',make([[2**32,0],[2**32,-16]],mu=2**-32))]
    p=make();p['elements'][0][1]='80000000';out.append(('signed_zero',p))
    p=make([[1,0],[1,0]]);p['elements'][0][1]='00000001';p['elements'][1][1]='80000001';out.append(('subnormal_anomaly',p))
    p=fixture();p['elements']=(p['elements']*61)[:1024];out.append(('maximum_records',p))
    return out
