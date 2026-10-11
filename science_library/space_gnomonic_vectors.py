"""Exact axes, bounded all-sky samples and threshold-neighbor cases."""
import math
import random
from fractions import Fraction
from . import f32 as f
from .space_statistics_vectors import hx


def make(directions=None,point=(0,0)):
    if directions is None:directions=[[0,0]]
    return dict(encoding='binary32-hex',angle_unit='turn',projection='GNOMONIC_TAN',axes='EAST_NORTH',frame='declared-common-celestial-frame',tangent_point=hx(list(point)),directions=hx(directions))


GOLDEN={79:(make(),[0,0,0,0x3f800000])}


def fixture(op=79,seed=271828,scale=1):
    if op!=79:raise ValueError(op)
    rng=random.Random(seed)
    return make([[rng.randrange(1024)/1024,rng.randrange(-256,257)/1024] for _ in range(min(17*scale,4096))],point=(.125,-.125))


def edges(op=79):
    if op!=79:raise ValueError(op)
    out=[('east_north_axes',make([[.125,0],[.875,0],[0,.125],[0,-.125]])),
         ('horizon_and_back',make([[.25,0],[.75,0],[.5,0],[0,.25],[0,-.25]])),
         ('north_pole',make([[0,.25],[.25,.25],[.5,.25],[.75,.125]],point=(0,.25))),
         ('south_pole',make([[0,-.25],[.25,-.25],[.5,-.25],[.75,-.125]],point=(0,-.25))),
         ('dense_sky',make([[a/32,d/32] for a in range(32) for d in range(-8,9)],point=(.375,.125))),
         ('offset_center',make([[.75,-.125],[.875,-.25],[.625,0],[.25,.125]],point=(.75,-.125)))]
    boundary=f.rounded(Fraction.from_float(math.acos(1/16)/(2*math.pi)))
    for field in (0,1):
        p=make([[0,0]]*9)
        for row,delta in zip(p['directions'],range(-4,5)):row[field]=f'{boundary+delta:08x}'
        out.append(('threshold_ra' if field==0 else 'threshold_dec',p))
    p=make([[0,0],[2**-20,0]]);p['tangent_point'][0]='3f7fffff';out.append(('ra_wrap',p))
    p=make([[0,0],[0,0],[0,0]]);p['directions']=[['00000001','00000001'],['80000000','80000001'],['00000000','00000000']];out.append(('subnormal_angles',p))
    p=make();p['tangent_point']=['80000000','80000000'];p['directions']=[['80000000','80000000']];out.append(('signed_zero',p))
    p=make([[0,.25],[.5,0]],point=(0,.25));p['tangent_point'][0]='3f7fffff';out.append(('endpoint_center',p))
    p=fixture();p['directions']=(p['directions']*241)[:4096];out.append(('maximum_records',p))
    return out
