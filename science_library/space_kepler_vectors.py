import random
from .space_statistics_vectors import hx


def make(elements=((1,0,.25),), mu=1):
    return dict(encoding='binary32-hex', angle_unit='turn', frame='PERIFOCAL', distance_unit='length', time_unit='time',
                elements=[hx(list(v)) for v in elements], mu=hx(mu))


GOLDEN = {75: (make(), [0x3e800000,0x3f800000,0,0x3f800000,0,0xbf800000,0,0])}


def fixture(op=75, seed=271828, scale=1):
    if op != 75:raise ValueError(op)
    rng = random.Random(seed)
    return make([[2**rng.randrange(-8,9), rng.randrange(31)/32, rng.randrange(1024)/1024] for _ in range(17*scale)], mu=2)


def edges(op=75):
    if op != 75:raise ValueError(op)
    out = [('circular_axes', make([[1,0,m] for m in (0,.25,.5,.75)])),
           ('apsides', make([[1,e,m] for e in (.5,.9375) for m in (0,.5)])),
           ('high_eccentricity', make([[1,.9375,i/64] for i in range(64)])),
           ('small_anomaly', make([[1,.9375,2**-24],[1,.9375,1-2**-24]])),
           ('minimum_scales', make([[2**-32,.9375,.125]], mu=2**-32)),
           ('maximum_scales', make([[2**32,.9375,.875]], mu=2**32)),
           ('maximum_velocity', make([[2**-32,.9375,0],[2**-32,.9375,.125]],mu=2**32)),
           ('minimum_velocity', make([[2**32,.9375,.5],[2**32,.9375,.875]],mu=2**-32))]
    p=make();p['elements'][0][1:]=['80000000','80000000'];out.append(('signed_zero',p))
    p=make([[1,.9375,0]]);p['elements'][0][2]='00000001';out.append(('subnormal_anomaly',p))
    p=make();p['elements'][0][1]='00000001';out.append(('subnormal_eccentricity',p))
    p=fixture();p['elements']=(p['elements']*61)[:1024];out.append(('maximum_records',p))
    return out
