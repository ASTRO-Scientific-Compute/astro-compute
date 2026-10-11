"""Deterministic double-single FFT for near-cancellation GWOSC whitening bins.

hi/lo components are binary32. This is a defined extended-precision algorithm,
not native FP64 output. CPU product residual uses exact float64 product of two
binary32 operands; GPU computes the residual from integer significands.
"""
import numpy as np
from . import vector_f32 as v
from .hann import HANN
from .twiddles import TWIDDLES
from .spectral_constants import HANN_LOW,TWIDDLE_LOW


def two_sum(a,b):
    s=v.add(a,b);z=v.sub(s,a)
    error=v.add(v.sub(a,v.sub(s,z)),v.sub(b,z))
    return s,error


def add(a,b):
    s,error=two_sum(a[0],b[0])
    return two_sum(s,v.add(v.add(error,a[1]),b[1]))


def neg(a):return v.canonical(-a[0]),v.canonical(-a[1])
def sub(a,b):return add(a,neg(b))


def product_error(a,b,product):
    # A binary32 product has <=48 significant bits, so binary64 holds it exactly.
    # Cancellation with its correctly rounded high part leaves an exact residual.
    with np.errstate(under='ignore'):
        return v.canonical(np.asarray(a,dtype=np.float64)*np.asarray(b,dtype=np.float64)-np.asarray(product,dtype=np.float64))


def mul(a,b):
    p=v.mul(a[0],b[0]);error=product_error(a[0],b[0],p)
    cross=v.add(v.mul(a[0],b[1]),v.mul(a[1],b[0]))
    return two_sum(p,v.add(error,cross))


def fft_windowed(strain):
    samples=v.array(strain)
    segments=np.lib.stride_tricks.sliding_window_view(samples,256)[::128]
    window=(v.array(HANN),v.array(HANN_LOW))
    hi,lo=mul((segments,np.zeros_like(segments)),window)
    reverse=[int(f'{i:08b}'[::-1],2) for i in range(256)]
    re=[hi[:,reverse].copy(),lo[:,reverse].copy()];im=[np.zeros_like(re[0]),np.zeros_like(re[0])]
    tw=v.array([z for p in TWIDDLES for z in p]).reshape(128,2)
    tl=v.array([z for p in TWIDDLE_LOW for z in p]).reshape(128,2)
    for size in (2,4,8,16,32,64,128,256):
        left=np.array([base+j for base in range(0,256,size) for j in range(size//2)])
        right=left+size//2;indices=np.tile(np.arange(size//2)*256//size,256//size)
        wr=(tw[indices,0],tl[indices,0]);wi=(tw[indices,1],tl[indices,1])
        ar=[x[:,left].copy() for x in re];ai=[x[:,left].copy() for x in im]
        br=[x[:,right].copy() for x in re];bi=[x[:,right].copy() for x in im]
        tr=sub(mul(wr,br),mul(wi,bi));ti=add(mul(wr,bi),mul(wi,br))
        for arrays,l,r in ((re,add(ar,tr),sub(ar,tr)),(im,add(ai,ti),sub(ai,ti))):
            for k in range(2):arrays[k][:,left]=l[k];arrays[k][:,right]=r[k]
    return v.add(*re),v.add(*im)
