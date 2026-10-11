"""Zero-bit amendments retain original scientific parameters and input bits."""
import numpy as np
from .reference import Job,MAGIC,encode,array
from .float_reference import values
from . import f32 as f
from . import vector_f32 as v
from .twiddles import TWIDDLES
from .hann import HANN
from .spectral_constants import HANN_LOW,TWIDDLE_LOW
from .spectral_precision import fft_windowed

WEIGHTS=[f.rounded(__import__('fractions').Fraction(x,25)) for x in (1,2,3,4,5,4,3,2,1)]


def spectral(strain):
    return fft_windowed(strain)


def prepare_legacy(wid,op,payload):
    a=[];b=[];c=[];out=[];n=0;m=0;ow=1
    if op==34:
        a=array(payload['packed_rows'],0,0xffffffff,'packed_rows',131072);n=len(a);m=(n+255)//256
        selected=[x for x in a if 1<=(x&65535)<=1800]
        out=[len(selected)]+selected+[0]*(n-len(selected));records=n+1
    else:
        if payload.get('encoding')!='binary32-hex':raise ValueError('explicit binary32-hex encoding required')
        v.check_host()
        if op in (32,33):
            a=values(payload['h1'],131072,65);b=values(payload['l1'],131072,65)
            if len(a)!=len(b):raise ValueError('time-aligned equal-length detector streams required')
            n=len(a);records=129;x=v.array(a);y=v.array(b)
            for lag in range(-64,65):
                start=max(0,-lag);stop=min(n,n-lag);xx=x[start:stop];yy=y[start+lag:stop+lag]
                xy=v.total(v.mul(xx,yy))
                if op==32:out.extend(v.words(xy))
                else:
                    energy=v.mul(v.total(v.mul(xx,xx)),v.total(v.mul(yy,yy)))
                    denominator=v.sqrt(energy)
                    out.extend(v.words(v.div(xy,denominator)) if float(denominator)>0 else [0])
        else:
            a=values(payload['strain'],131072);n=len(a);x=v.array(a)
            if op==31:
                b=WEIGHTS;total=np.zeros(n,dtype=np.float32)
                for j,weight in enumerate(v.array(WEIGHTS)):
                    indices=np.clip(np.arange(n)+j-4,0,n-1)
                    total=v.add(total,v.mul(x[indices],weight))
                out=v.words(total);records=n
            elif op==30:
                if n%256:raise ValueError('FFT input length multiple256 required')
                records=n//256;ow=512;n=256;b=[z for pair in TWIDDLES for z in pair]
                re,im=v.fft256(x.reshape(-1,256));out=v.words(np.stack((re,im),axis=-1))
            elif op in (35,36):
                if n<256 or (n-256)%128:raise ValueError('Hann256/hop128 stream length required')
                m=(n-256)//128+1;n=256;b=[z for high,low in zip(TWIDDLES,TWIDDLE_LOW) for z in (high[0],low[0],high[1],low[1])];c=HANN+HANN_LOW
                re,im=spectral(a);re=re[:,:129];im=im[:,:129]
                q=np.array([1]+[2]*127+[1],dtype=np.float32)
                if op==35:
                    power=v.div(v.mul(q,v.add(v.mul(re,re),v.mul(im,im))),np.float32(393216))
                    out=v.words(v.div(v.total(power,axis=0),np.float32(m)));records=129
                else:
                    psd=values(payload['psd'],129)
                    if len(psd)!=129 or any(f.rational(word)<=0 for word in psd):raise ValueError('129 positive PSD bins required')
                    c+=psd
                    scales=v.sqrt(v.div(q,v.mul(np.float32(393216),v.array(psd))))
                    out=v.words(np.stack((v.mul(re,scales),v.mul(im,scales)),axis=-1));records=m;ow=258
            else:raise ValueError('legacy opcode')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,m,0,0,0,0,0,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
