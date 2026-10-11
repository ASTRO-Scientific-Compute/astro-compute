"""Analytic examples plus repeatable data; not live researcher jobs."""
import random
from . import f32 as f
from .float_vectors import bits


def strain(xs):return dict(encoding='binary32-hex',strain=[f.hex32(x) for x in xs])

def pair(x,y):return dict(encoding='binary32-hex',h1=[f.hex32(v) for v in x],l1=[f.hex32(v) for v in y])

IMPULSE=[0]*256;IMPULSE[128]=1
PSD=[f.hex32(1)]*129
GOLDEN={
30:(strain([1]+[0]*255),bits([1,0]*256)),
31:(strain([25,0]),bits([15,10])),
32:(pair([1]+[0]*64,[0,1]+[0]*63),bits([0]*65+[1]+[0]*63)),
33:(pair([1]+[0]*64,[0,1]+[0]*63),bits([0]*65+[1]+[0]*63)),
34:(dict(packed_rows=[0,1,1800,1801,0xabcd0001,1,0xffffffff]),[4,1,1800,0xabcd0001,1,0,0,0]),
35:(strain(IMPULSE),[f.div(f.rounded(1 if k in (0,128) else 2),f.rounded(393216)) for k in range(129)]),
36:({**strain(IMPULSE),'psd':PSD},[x for k in range(129) for x in (f.mul(f.rounded(1 if k%2==0 else -1),f.sqrt(f.div(f.rounded(1 if k in (0,128) else 2),f.rounded(393216)))),0)]),
}


def fixture(op,seed=271828,scale=1):
    r=random.Random(seed)
    if op==34:return dict(packed_rows=[(r.randrange(256)<<16)|r.choice([0,1,1800,1801,r.randrange(65536)]) for _ in range(777*scale)])
    if op in (32,33):return pair([r.randrange(-32,33)/8 for _ in range(513*scale)],[r.randrange(-32,33)/8 for _ in range(513*scale)])
    d=strain([r.randrange(-32,33)/8 for _ in range(1024*scale)])
    if op==36:d['psd']=[f.hex32(r.randrange(1,16)/8) for _ in range(129)]
    return d


def edges(op):
    if op==30:return [('signed_subnormal_fft',dict(encoding='binary32-hex',strain=['80000000','00000001','80000001','00800000']*64))]
    if op==31:return [('single_sample',strain([25])),('tiny_clamped_stream',dict(encoding='binary32-hex',strain=['00000003','80000001']))]
    if op in (32,33):return [('zero_energy',pair([0]*65,[0]*65)),('opposite_lag',pair([0,1]+[0]*63,[1]+[0]*64))]
    if op==34:return [('empty',dict(packed_rows=[])),('none',dict(packed_rows=[0,65535]*200)),('all',dict(packed_rows=[1,1800,1]*400))]
    if op==35:return [('zero_psd',strain([0]*384)),('two_segments',strain([1]*384))]
    if op==36:return [('zero_signal',{**strain([0]*384),'psd':PSD})]
    return []
