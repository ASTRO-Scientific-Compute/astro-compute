"""Independent rational CPU oracle; equations defined before GPU implementation."""
from fractions import Fraction
from math import factorial
from . import f32 as f
from .reference import Job,MAGIC,encode,integer,array
from .float_reference import values,rows

TAU=0x40c90fdb
SIN_COEFF=tuple(f.rounded(Fraction((-1)**k,factorial(2*k+1))) for k in range(7))
COS_COEFF=tuple(f.rounded(Fraction((-1)**k,factorial(2*k))) for k in range(8))


def sincos(turns):
    """Exact fractional-turn reduction, then declared RN32 Taylor-Horner graph."""
    v=f.rational(turns);phase=abs(v)%1
    quadrant=int(phase*4)
    residual=f.rounded(phase-Fraction(quadrant,4))
    x=f.mul(residual,TAU);z=f.mul(x,x)
    def poly(coeff):
        acc=coeff[-1]
        for c in reversed(coeff[:-1]):acc=f.add(c,f.mul(z,acc))
        return acc
    sn=f.mul(x,poly(SIN_COEFF));cs=poly(COS_COEFF)
    sn,cs=((sn,cs),(cs,f.neg(sn)),(f.neg(sn),f.neg(cs)),(f.neg(cs),sn))[quadrant]
    return (f.neg(sn) if v<0 else sn),cs


def gls(samples,frequency):
    trig=[sincos(f.mul(t,frequency)) for t,y,w in samples]
    weights=[r[2] for r in samples];s=f.summation(weights)
    if not s:return [1,0,0,0,0,0]
    ymean=f.div(f.dot(weights,[r[1] for r in samples]),s)
    cmean=f.div(f.dot(weights,[r[1] for r in trig]),s)
    smean=f.div(f.dot(weights,[r[0] for r in trig]),s)
    cc=ss=cs=yc=ys=yy=0
    for (t,y,w),(sn,cn) in zip(samples,trig):
        c=f.sub(cn,cmean);sn=f.sub(sn,smean);y=f.sub(y,ymean)
        wc=f.mul(w,c);ws=f.mul(w,sn);wy=f.mul(w,y)
        cc=f.add(cc,f.mul(wc,c));ss=f.add(ss,f.mul(ws,sn));cs=f.add(cs,f.mul(wc,sn))
        yc=f.add(yc,f.mul(wy,c));ys=f.add(ys,f.mul(wy,sn));yy=f.add(yy,f.mul(wy,y))
    if not yy:return [1,0,0,0,0,0]
    product=f.mul(cc,ss);d=f.sub(product,f.mul(cs,cs))
    if f.rational(d)<=f.rational(f.mul(product,0x36800000)):return [2,0,0,0,0,0] # 2^-18 relative conditioning floor
    ac=f.div(f.sub(f.mul(yc,ss),f.mul(ys,cs)),d)
    bs=f.div(f.sub(f.mul(ys,cc),f.mul(yc,cs)),d)
    offset=f.sub(f.sub(ymean,f.mul(ac,cmean)),f.mul(bs,smean))
    chi=0
    for (_,y,w),(sn,cn) in zip(samples,trig):
        residual=f.sub(y,f.add(f.add(offset,f.mul(ac,cn)),f.mul(bs,sn)))
        chi=f.add(chi,f.mul(w,f.mul(residual,residual)))
    return [0,f.div(f.sub(yy,chi),yy),offset,ac,bs,chi]


def bls(times,flux,period,bins,lo,hi):
    counts=[0]*bins;sums=[0]*bins
    for t,y in zip(times,flux):
        k=(t%period)*bins//period;counts[k]+=1;sums[k]=f.add(sums[k],y)
    total=f.summation(sums);best=[1,0,0,0,0,0]
    for start in range(bins):
        ni=0;yi=0
        for width in range(1,hi+1):
            k=(start+width-1)%bins;ni+=counts[k];yi=f.add(yi,sums[k])
            no=len(times)-ni
            if width<lo or not ni or not no:continue
            outer=f.div(f.sub(total,yi),f.rounded(no))
            depth=f.sub(outer,f.div(yi,f.rounded(ni)))
            if f.rational(depth)<=0:continue
            score=f.div(f.mul(f.mul(f.mul(depth,depth),f.rounded(ni)),f.rounded(no)),f.rounded(len(times)))
            if f.rational(score)>f.rational(best[5]):best=[0,start,width,depth,outer,score]
    return best


def derivative(state,mu):
    if not mu:return state[3:]+[0,0,0]
    r2=f.dot(state[:3],state[:3]);factor=f.neg(f.div(mu,f.mul(r2,f.sqrt(r2))))
    return state[3:]+[f.mul(factor,x) for x in state[:3]]


def trajectory(state,mu,dt,steps):
    state=[f.add(x,0) for x in state];result=state[:]
    half=f.mul(dt,f.HALF);sixth=f.div(dt,f.rounded(6))
    for _ in range(steps):
        k1=derivative(state,mu)
        k2=derivative([f.add(y,f.mul(half,k)) for y,k in zip(state,k1)],mu)
        k3=derivative([f.add(y,f.mul(half,k)) for y,k in zip(state,k2)],mu)
        k4=derivative([f.add(y,f.mul(dt,k)) for y,k in zip(state,k3)],mu)
        state=[f.add(y,f.mul(sixth,f.add(f.add(f.add(a,f.mul(f.TWO,b)),f.mul(f.TWO,c)),d))) for y,a,b,c,d in zip(state,k1,k2,k3,k4)]
        result.extend(state)
    return result


def prepare_space_search(wid,op,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('encoding=binary32-hex required')
    a=[];b=[];c=[];out=[];n=m=w=h=p0=p1=p2=0;ow=1
    if op==39:
        samples=rows(payload['samples'],3,512);n=len(samples);integer(n,3,512)
        b=values(payload['frequencies'],256);records=len(b);ow=6
        if n*records>65536:raise ValueError('Lomb-Scargle tile exceeds limit')
        if any(f.rational(x[2])<0 for x in samples) or any(f.rational(x)<=0 for x in b):raise ValueError('nonnegative weights and positive frequencies required')
        for frequency in b:
            if any(abs(f.rational(f.mul(t,frequency)))>256 for t,y,wt in samples):raise ValueError('center times / split frequency tile: |time*frequency|<=256 required')
            out.extend(gls(samples,frequency))
        a=[x for row in samples for x in row]
    elif op==40:
        a=array(payload['times'],0,10000000,maximum=4096);n=len(a);integer(n,2,4096)
        b=values(payload['flux'],4096);c=array(payload['periods'],1,1000000,maximum=128);records=len(c);integer(records,1,128);ow=6
        if len(b)!=n:raise ValueError('time/flux length mismatch')
        p0=integer(payload['bins'],2,64);p1=integer(payload['min_width'],1,p0-1);p2=integer(payload['max_width'],p1,p0-1)
        if records*(n+p0**3)>2000000:raise ValueError('BLS tile exceeds limit')
        out=[x for period in c for x in bls(a,b,period,p0,p1,p2)]
    elif op==41:
        raw=payload['image']
        if not isinstance(raw,list) or not raw or not isinstance(raw[0],list):raise ValueError('image matrix required')
        w=integer(len(raw[0]),1,256);image=rows(raw,w,256);h=len(image);records=w*h
        valid=payload['valid']
        if not isinstance(valid,list) or len(valid)!=h:raise ValueError('valid mask height')
        mask=[array(row,0,1,maximum=w) for row in valid]
        if any(len(row)!=w for row in mask):raise ValueError('valid mask width')
        p0=f.parse(payload['threshold']);p1=integer(payload['radius'],1,4)
        a=[x for row in image for x in row];b=[x for row in mask for x in row]
        for y in range(h):
            for x in range(w):
                value=f.rational(image[y][x]);peak=mask[y][x]==1 and value>f.rational(p0)
                for dy in range(-p1,p1+1):
                    for dx in range(-p1,p1+1):
                        yy=y+dy;xx=x+dx
                        if 0<=yy<h and 0<=xx<w:
                            if not mask[yy][xx]:continue
                            other=f.rational(image[yy][xx])
                        else:other=0
                        if other>value:peak=False
                out.append(int(peak))
    elif op==42:
        raw=payload['flux']
        if not isinstance(raw,list) or not raw or not isinstance(raw[0],list):raise ValueError('flux matrix required')
        n=integer(len(raw[0]),1,64);obs=rows(raw,n,128);weight=rows(payload['weights'],n,128);templates=rows(payload['templates'],n,128);m=len(templates);records=len(obs)*m;ow=3
        if len(obs)!=len(weight) or records*n>1048576:raise ValueError('template tile or weights shape')
        if any(f.rational(x)<0 for row in weight for x in row):raise ValueError('negative inverse variance')
        a=[x for y,wt in zip(obs,weight) for pair in zip(y,wt) for x in pair];b=[x for row in templates for x in row]
        for y,wt in zip(obs,weight):
            for t in templates:
                wt_t=[f.mul(wi,ti) for wi,ti in zip(wt,t)];den=f.dot(wt_t,t)
                if not den:out.extend([1,0,0]);continue
                amp=f.div(f.dot(wt_t,y),den)
                if f.rational(amp)<0:amp=0
                residual=[f.sub(yi,f.mul(amp,ti)) for yi,ti in zip(y,t)]
                chi=f.dot(wt,[f.mul(x,x) for x in residual]);out.extend([0,amp,chi])
    elif op==43:
        coordinates=rows(payload['coordinates'],3,4096);records=len(coordinates);ow=3
        for r,lat,lon in coordinates:
            if f.rational(r)<0 or abs(f.rational(lat))>Fraction(1,4) or abs(f.rational(lon))>65536:raise ValueError('spherical radius/turn bounds')
            sl,cl=sincos(lat);sn,cn=sincos(lon);rc=f.mul(r,cl)
            out.extend([f.mul(rc,cn),f.mul(rc,sn),f.mul(r,sl)])
        a=[x for row in coordinates for x in row]
    elif op==44:
        states=rows(payload['states'],6,64);records=len(states);n=integer(payload['steps'],1,64);ow=6*(n+1)
        p0=f.add(f.parse(payload['mu']),0);p1=f.parse(payload['dt'])
        if f.rational(p0)<0 or f.rational(p1)<=0:raise ValueError('mu>=0 and dt>0 required')
        for state in states:out.extend(trajectory(state,p0,p1,n))
        a=[x for row in states for x in row]
    else:raise ValueError('unknown SPACE search operation')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,m,w,h,p0,p1,p2,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
