"""Independent vectorized CPU binary32 oracle, for full public strain streams.

GPU uses software integer significands; CPU uses separate NumPy float32 ufuncs.
No BLAS, fused multiply-add, pairwise sum or float64 intermediate arithmetic.
The host's rounding/underflow mode is probed against the Fraction oracle.
"""
import numpy as np
from . import f32
from .twiddles import TWIDDLES


def array(words):
    return np.array(words,dtype=np.uint32).view(np.float32)


def words(values):
    return np.asarray(values,dtype=np.float32).reshape(-1).view(np.uint32).tolist()


def canonical(x):
    x=np.asarray(x,dtype=np.float32)
    if not np.isfinite(x).all():raise ValueError('nonfinite binary32 intermediate')
    return np.where(x==0,np.float32(0),x).astype(np.float32)


def operation(fn,*args):
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise',under='ignore'):
            return canonical(fn(*args,dtype=np.float32))
    except FloatingPointError as e:raise ValueError('invalid binary32 intermediate: '+str(e)) from e


def add(a,b):return operation(np.add,a,b)
def sub(a,b):return operation(np.subtract,a,b)
def mul(a,b):return operation(np.multiply,a,b)
def div(a,b):return operation(np.divide,a,b)
def sqrt(a):return operation(np.sqrt,a)


def total(x,axis=0):
    x=np.asarray(x,dtype=np.float32)
    if not x.shape[axis]:return np.zeros(x.shape[:axis]+x.shape[axis+1:],dtype=np.float32)
    with np.errstate(over='ignore',invalid='ignore',under='ignore'):
        cumulative=np.cumsum(x,axis=axis,dtype=np.float32)
    # Check all prefix sums so an overflowing prefix cannot later be hidden.
    canonical(cumulative)
    return canonical(np.take(cumulative,-1,axis=axis))


def check_host():
    a=[1,3,0x007fffff,0x00800000,0x3f800000,0x3f800001,0xbf800000,0x80000000]
    b=[0x3f000000,0x3f000000,1,0x3f000000,0x33800000,0x33800000,0x3f800000,0x3f800000]
    for fn,oracle in ((add,f32.add),(mul,f32.mul),(div,f32.div)):
        if words(fn(array(a),array(b)))!=[oracle(x,y) for x,y in zip(a,b)]:
            raise ValueError('CPU binary32 rounding/underflow mode differs from RN32 contract')
    positive=[1,0x7fffff,0x00800000,0x40000000,0x7f7fffff]
    if words(sqrt(array(positive)))!=[f32.sqrt(x) for x in positive]:raise ValueError('CPU root rounding unsupported')
    order=[0x4b800000,0x3f800000,0xcb800000]
    if words(total(array(order)))!=[f32.summation(order)]:raise ValueError('CPU reduction reassociates')


def fft256(real):
    """Batch-first, fixed butterfly graph; each ufunc is one RN32 operation."""
    x=np.asarray(real,dtype=np.float32)
    if x.ndim!=2 or x.shape[1]!=256:raise ValueError('FFT batch shape')
    reverse=[int(f'{i:08b}'[::-1],2) for i in range(256)]
    re=x[:,reverse].copy();im=np.zeros_like(re)
    tw=array([v for pair in TWIDDLES for v in pair]).reshape(128,2)
    for size in (2,4,8,16,32,64,128,256):
        left=np.array([base+j for base in range(0,256,size) for j in range(size//2)])
        right=left+size//2;indices=np.tile(np.arange(size//2)*256//size,256//size)
        wr=tw[indices,0];wi=tw[indices,1]
        ar=re[:,left].copy();ai=im[:,left].copy();br=re[:,right].copy();bi=im[:,right].copy()
        tr=sub(mul(wr,br),mul(wi,bi));ti=add(mul(wr,bi),mul(wi,br))
        re[:,left]=add(ar,tr);im[:,left]=add(ai,ti);re[:,right]=sub(ar,tr);im[:,right]=sub(ai,ti)
    return re,im
