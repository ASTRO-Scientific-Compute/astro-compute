import random
from .space_statistics_vectors import hx,payload


def pair(a0=(-2,0,0),a1=(2,0,0),b0=(0,0,0),b1=(0,0,0),ra=.5,rb=.5):return hx(list(a0)+list(a1)+list(b0)+list(b1)+[ra,rb])
GOLDEN={71:(payload(pairs=[pair(),pair(a0=(-2,2,0),a1=(2,2,0)),pair(a0=(1,0,0),a1=(2,0,0))]),
    [1]+[int(x,16) for x in hx([.5,0,4,4,1])]+[0]+[0]+[int(x,16) for x in hx([.5,4,8,8,1])]+[0]+[1]+[int(x,16) for x in hx([0,1,1,4,1])]+[0])}


def fixture(op=71,seed=271828,scale=1):
    if op!=71:raise ValueError(op)
    rng=random.Random(seed);pairs=[]
    for k in range(17*scale):
        origin=[rng.randrange(-8,9)/4 for _ in range(3)];end=[rng.randrange(-8,9)/4 for _ in range(3)]
        offset=[rng.randrange(-6,7)/4 for _ in range(3)];motion=[rng.randrange(-6,7)/4 for _ in range(3)]
        pairs.append(pair(origin,end,offset,motion,ra=rng.randrange(1,5)/8,rb=rng.randrange(1,5)/8))
    return payload(pairs=pairs)


def edges(op=71):
    if op!=71:raise ValueError(op)
    cases=[('initial_overlap',pair(a0=(.25,0,0))),('start_touch',pair(a0=(1,0,0))),('end_touch',pair(a0=(-3,0,0),a1=(-1,0,0))),
      ('interior_tangent',pair(a0=(-2,1,0),a1=(2,1,0))),('pass_through',pair()),('receding',pair(a0=(2,0,0),a1=(3,0,0))),
      ('static_disjoint',pair(a0=(2,0,0),a1=(2,0,0))),('static_overlap',pair(a0=(.5,0,0),a1=(.5,0,0))),
      ('common_translation',pair(a0=(1,0,0),a1=(3,0,0),b0=(0,0,0),b1=(2,0,0))),('zero_radius_crossing',pair(ra=0,rb=0)),
      ('tiny_separation',pair(a0=(2**-20,0,0),a1=(-2**-20,0,0),ra=0,rb=0))]
    out=[(name,payload(pairs=[p])) for name,p in cases]
    signed=pair();signed[1]=signed[2]=signed[12]='80000000';out.append(('signed_zero',payload(pairs=[signed])))
    sub=pair(a0=(0,0,0),a1=(0,0,0),ra=0,rb=0);sub[0]='00000001';out.append(('rounded_stationary_underflow',payload(pairs=[sub])))
    out.append(('maximum_records',payload(pairs=fixture()['pairs']*240+fixture()['pairs'][:16])))
    return out
