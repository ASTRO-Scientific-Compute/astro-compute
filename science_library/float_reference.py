"""Canonical science algorithms on the independent rational binary32 oracle."""
from . import f32 as f
from .reference import Job, MAGIC, encode, integer
from .twiddles import TWIDDLES


def values(xs, maximum=4096, minimum=1):
    if not isinstance(xs, list) or not minimum <= len(xs) <= maximum:
        raise ValueError('binary32 vector length')
    return [f.parse(x) for x in xs]


def rows(xs, width, maximum=4096):
    if not isinstance(xs, list) or not 1 <= len(xs) <= maximum:
        raise ValueError('binary32 row count')
    result = [values(x, width) for x in xs]
    if any(len(x) != width for x in result):
        raise ValueError('binary32 row width')
    return result


def batches(xs, width, maximum=1024):
    if not isinstance(xs, list) or not 1 <= len(xs) <= 64:
        raise ValueError('binary32 batch count')
    result = [rows(x, width, maximum) for x in xs]
    if any(len(x) != len(result[0]) for x in result):
        raise ValueError('uniform batch length required')
    return result


def fft(signal):
    n = len(signal)
    levels = n.bit_length() - 1
    data = [list(signal[int(f'{j:0{levels}b}'[::-1], 2)]) for j in range(n)]
    for stage in range(1, levels + 1):
        size = 1 << stage
        for base in range(0, n, size):
            for j in range(size // 2):
                wr, wi = TWIDDLES[j * 256 // size]
                ar, ai = data[base + j]
                br, bi = data[base + j + size // 2]
                tr = f.sub(f.mul(wr, br), f.mul(wi, bi))
                ti = f.add(f.mul(wr, bi), f.mul(wi, br))
                data[base+j] = [f.add(ar, tr), f.add(ai, ti)]
                data[base+j+size//2] = [f.sub(ar, tr), f.sub(ai, ti)]
    return data


def prepare_float(wid, op, payload):
    if payload.get('encoding') != 'binary32-hex':
        raise ValueError('explicit encoding=binary32-hex required')
    a=[];b=[];c=[];out=[];n=0;m=0;w=0;h=0;p0=0;p1=0;p2=0;ow=1
    if op in (14,15,16):
        a=values(payload['x']);b=values(payload['kernel' if op==14 else 'y'],1024 if op==14 else 4096)
        n=len(a);m=len(b)
        if n*m>1048576:raise ValueError('correlation/convolution tile too large')
        records=n+m-1;ow=2 if op==16 else 1
        for index in range(records):
            pairs=[(x,b[k]) for j,x in enumerate(a) if 0 <= (k := (index-j if op==14 else j-(index-(m-1)))) < m]
            total=f.dot([x for x,y in pairs],[y for x,y in pairs])
            if op==16:
                sx=f.summation(f.mul(x,x) for x,y in pairs)
                sy=f.summation(f.mul(y,y) for x,y in pairs)
                denominator=f.sqrt(f.mul(sx,sy))
                out.extend([0,f.div(total,denominator)] if denominator else [1,0])
            else:out.append(total)
    elif op in (17,24):
        raw=payload['signals']
        if op==24:
            if not isinstance(raw,list) or not 1<=len(raw)<=64:raise ValueError('signals count')
            signals=[[[x,'00000000'] for x in row] for row in raw]
        else:signals=raw
        signals=batches(signals,2,256);n=len(signals[0])
        if n<2 or n&(n-1):raise ValueError('FFT size must be power of two2..256')
        b=[v for pair in TWIDDLES for v in pair]
        records=len(signals);ow=2*n if op==17 else n
        if op==24:
            p0=f.parse(payload['fs'])
            if f.rational(p0)<=0:raise ValueError('positive fs required')
            denominator=f.mul(p0,f.rounded(n))
        for signal in signals:
            a.extend(v for pair in signal for v in pair)
            transformed=fft(signal)
            if op==17:out.extend(v for pair in transformed for v in pair)
            else:out.extend(f.div(f.add(f.mul(re,re),f.mul(im,im)),denominator) for re,im in transformed)
    elif op==18:
        fits=batches(payload['samples'],3);n=len(fits[0]);records=len(fits);ow=3
        for fit in fits:
            if any(f.rational(weight)<0 for x,y,weight in fit):raise ValueError('negative weight')
            sums=[0]*5
            for x,y,weight in fit:
                a.extend((x,y,weight))
                terms=[weight,f.mul(weight,x),f.mul(weight,y),f.mul(f.mul(weight,x),x),f.mul(f.mul(weight,x),y)]
                sums=[f.add(s,t) for s,t in zip(sums,terms)]
            s,sx,sy,sxx,sxy=sums;d=f.sub(f.mul(s,sxx),f.mul(sx,sx))
            if not s or f.rational(d)<=0:out.extend((1,0,0))
            else:
                slope=f.div(f.sub(f.mul(s,sxy),f.mul(sx,sy)),d)
                intercept=f.div(f.sub(sy,f.mul(slope,sx)),s)
                out.extend((0,intercept,slope))
    elif op==19:
        vectors=rows(payload['vectors'],3);mat=rows(payload['matrix'],3,3)
        if len(mat)!=3:raise ValueError('3x3 matrix required')
        a=[v for row in vectors for v in row];b=[v for row in mat for v in row]
        records=len(vectors);ow=3
        out=[f.dot(row,vec) for vec in vectors for row in mat]
    elif op==20:
        curves=batches(payload['curves'],2,4096);n=len(curves[0]);records=len(curves)
        for curve in curves:
            a.extend(v for pair in curve for v in pair)
            out.append(f.summation(f.mul(f.mul(f.sub(x2,x1),f.add(y1,y2)),f.HALF) for (x1,y1),(x2,y2) in zip(curve,curve[1:])))
    elif op==21:
        bodies=rows(payload['bodies'],4,256);n=len(bodies);records=n;ow=3;p0=f.parse(payload['epsilon_squared'])
        if f.rational(p0)<=0 or any(f.rational(row[3])<0 for row in bodies):raise ValueError('positive softening, nonnegative mu required')
        a=[v for row in bodies for v in row]
        for i,body in enumerate(bodies):
            acc=[0]*3
            for j,other in enumerate(bodies):
                if i==j:continue
                d=[f.sub(other[k],body[k]) for k in range(3)]
                s=f.add(f.dot(d,d),p0)
                factor=f.div(other[3],f.mul(s,f.sqrt(s)))
                acc=[f.add(x,f.mul(factor,y)) for x,y in zip(acc,d)]
            out.extend(acc)
    elif op==22:
        states=rows(payload['states'],9);records=len(states);ow=6;p0=f.parse(payload['dt'])
        if f.rational(p0)<=0:raise ValueError('positive dt required')
        for row in states:
            a.extend(row)
            vel=[f.add(row[3+k],f.mul(p0,row[6+k])) for k in range(3)]
            pos=[f.add(row[k],f.mul(p0,vel[k])) for k in range(3)]
            out.extend(pos+vel)
    elif op==23:
        images=payload['images']
        if not isinstance(images,list) or not 1<=len(images)<=64:raise ValueError('image count')
        h=len(images[0]);integer(h,1,64);w=len(images[0][0]);integer(w,1,64)
        records=len(images);ow=3
        for image in images:
            image=rows(image,w,64)
            if len(image)!=h or any(f.rational(v)<0 for row in image for v in row):raise ValueError('nonnegative uniform images required')
            sums=[0]*3
            for y,row in enumerate(image):
                for x,v in enumerate(row):
                    a.append(v)
                    sums=[f.add(s,t) for s,t in zip(sums,(v,f.mul(f.rounded(x),v),f.mul(f.rounded(y),v)))]
            s,x,y=sums;out.extend((0,f.div(x,s),f.div(y,s)) if s else (1,0,0))
    else:raise ValueError('unknown binary32 opcode')
    if len(out)!=records*ow:raise AssertionError('float output shape')
    if len(a)+len(b)+len(c)>2000000:raise ValueError('binary32 tile exceeds2M input words')
    header=[MAGIC,1,op,records,n,m,w,h,p0,p1,p2,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
