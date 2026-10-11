import random
from .space_statistics_vectors import hx
from .space_precession_reference import OUTPUT_FRAME


def make(times=(0,),vectors=((1,0,0),)):
    return dict(encoding='binary32-hex',time_scale='TT',input_frame='GCRS',output_frame=OUTPUT_FRAME,tt_centuries=hx(list(times)),vectors=[hx(list(v)) for v in vectors])
# Frozen exact graph result; scientific anchors are checked independently in float64.
GOLDEN={74:(make(),[int(v,16) for v in ['b489c323','330dfd3e','b4597746','3ed17496','3f800000','b39801c0','33ad0182','339801c0','3f800000','330dfd3c','b3ad0182','b30dfd3a','3f800000','3f800000','339801c0','b3ad0182']])}


def fixture(op=74,seed=271828,scale=1):
    if op!=74:raise ValueError(op)
    rng=random.Random(seed);N=17*scale
    return make([rng.randrange(-128,129)/128 for _ in range(N)],[[rng.randrange(-16,17)/8 for _ in range(3)] for _ in range(N)])


def edges(op=74):
    if op!=74:raise ValueError(op)
    out=[('j2000_bias_axes',make([0]*3,[(1,0,0),(0,1,0),(0,0,1)])),('past_limit',make([-1],[(1,-1,1)])),('future_limit',make([1],[(-1,1,-1)])),
         ('zero_vector',make([.5],[(0,0,0)])),('large_vector',make([1],[(2**60,-2**60,2**59)])),('small_vector',make([-.5],[(2**-60,-2**-60,2**-61)])),
         ('polar_vectors',make([-.75,.75],[(0,0,1),(0,0,-1)]))]
    signed=make();signed['tt_centuries'][0]='80000000';signed['vectors'][0][1]='80000000';out.append(('signed_zero',signed))
    sub=make();sub['tt_centuries'][0]='00000001';out.append(('subnormal_epoch',sub))
    sub=make();sub['vectors'][0]=['00000001','80000001','00000000'];out.append(('subnormal_vector',sub))
    limits=make([1,-1],[(1,0,0),(0,1,0)]);limits['tt_centuries']=['3f7fffff','bf7fffff'];out.append(('inside_boundaries',limits))
    base=fixture();out.append(('maximum_records',dict(base,tt_centuries=(base['tt_centuries']*241)[:4096],vectors=(base['vectors']*241)[:4096])))
    return out
