"""Analytic axes, plane corners, pole crossings and bounded deterministic samples."""
import random
from .space_statistics_vectors import hx


def make(plane=None,point=(0,0)):
    if plane is None:plane=[[0,0]]
    return dict(encoding='binary32-hex',angle_unit='turn',projection='GNOMONIC_TAN',axes='EAST_NORTH',frame='declared-common-celestial-frame',tangent_point=hx(list(point)),plane_coordinates=hx(plane))


GOLDEN={80:(make(),[0x3f800000,0,0,0x3f800000])}


def fixture(op=80,seed=271828,scale=1):
    if op!=80:raise ValueError(op)
    rng=random.Random(seed)
    return make([[rng.randrange(-256,257)/16,rng.randrange(-256,257)/16] for _ in range(min(17*scale,4096))],point=(.375,-.125))


def edges(op=80):
    if op!=80:raise ValueError(op)
    out=[('east_north_axes',make([[1,0],[-1,0],[0,1],[0,-1]])),
         ('plane_corners',make([[x,y] for x in (-16,16) for y in (-16,16)])),
         ('plane_edges',make([[16,0],[-16,0],[0,16],[0,-16]])),
         ('north_pole',make([[0,0],[1,0],[0,1],[16,-16]],point=(.25,.25))),
         ('south_pole',make([[0,0],[1,0],[0,1],[-16,16]],point=(.75,-.25))),
         ('pole_crossing',make([[0,1],[0,2],[0,-1],[2,2]],point=(.125,.125))),
         ('dense_plane',make([[x/2,y/2] for x in range(-32,33,2) for y in range(-32,33,2)],point=(.625,.0625))),
         ('tiny_offsets',make([[2**-24,0],[0,-2**-24],[2**-24,-2**-24]],point=(.125,-.125))),
         ('opposite_tangent',make([[0,0],[1,2],[-1,-2]],point=(.5,0)))]
    p=make([[0,0],[1,2]]);p['tangent_point'][0]='3f7fffff';out.append(('ra_endpoint',p))
    p=make([[0,0],[0,0]]);p['plane_coordinates']=[['00000001','80000001'],['80000001','00000001']];out.append(('subnormal_plane',p))
    p=make();p['plane_coordinates']=[['80000000','80000000']];p['tangent_point']=['80000000','80000000'];out.append(('signed_zero',p))
    p=fixture();p['plane_coordinates']=(p['plane_coordinates']*241)[:4096];out.append(('maximum_records',p))
    return out
