"""Independent exact-rational robust-statistics oracle."""
from . import f32 as f
from .reference import Job, MAGIC, encode
from .space_statistics_reference import rectangular_float, masks


def median(values):
    ordered=sorted(values,key=f.rational);n=len(ordered)
    return f.add(ordered[n//2],0) if n%2 else f.add(f.mul(ordered[n//2-1],f.HALF),f.mul(ordered[n//2],f.HALF))


def biweight(row, valid, c_location, c_variance):
    data=[v for v,k in zip(row,valid) if k];n=len(data)
    if not n:return [1,0]+[0]*7
    center=median(data);residuals=[f.sub(v,center) for v in data]
    mad=median([v&0x7fffffff for v in residuals])
    if not mad:return [2,n]+[0]*7
    location_scale=f.mul(c_location,mad);variance_scale=f.mul(c_variance,mad)
    a=b=c=d=nl=nv=0
    for residual in residuals:
        u=f.div(residual,location_scale)
        if abs(f.rational(u))<1:
            t=f.sub(f.ONE,f.mul(u,u));weight=f.mul(t,t)
            a=f.add(a,f.mul(residual,weight));b=f.add(b,weight);nl+=1
        u=f.div(residual,variance_scale)
        if abs(f.rational(u))<1:
            u2=f.mul(u,u);t=f.sub(f.ONE,u2);t2=f.mul(t,t);t4=f.mul(t2,t2)
            c=f.add(c,f.mul(f.mul(residual,residual),t4))
            d=f.add(d,f.mul(t,f.sub(f.ONE,f.mul(0x40a00000,u2))));nv+=1
    if not b or abs(f.rational(d))<=f.rational(f.mul(f.rounded(n),0x37800000)):
        return [3,n]+[0]*7
    location=f.add(center,f.div(a,b));variance=f.div(f.mul(f.rounded(n),c),f.mul(d,d));scale=f.sqrt(variance)
    return [0,n,center,mad,location,variance,scale,nl,nv]


def prepare_space_biweight(wid,op,payload):
    if op!=63 or payload.get('encoding')!='binary32-hex':raise ValueError('binary32 biweight contract required')
    samples,n=rectangular_float(payload['samples'],128,256);valid=masks(payload['valid'],len(samples),n)
    cl=f.parse(payload['c_location']);cv=f.parse(payload['c_variance'])
    if not 1<=f.rational(cl)<=16 or not 1<=f.rational(cv)<=16:raise ValueError('tuning constants must be in[1,16]')
    records=len(samples)
    if records*n*n>2097152:raise ValueError('biweight sorting work limit')
    a=[v for row in samples for v in row];b=[v for row in valid for v in row];out=[]
    for row,keep in zip(samples,valid):out.extend(biweight(row,keep,cl,cv))
    header=[MAGIC,1,op,records,n,0,0,0,cl,cv,0,16+len(a),16+len(a)+len(b),9,0,0]
    return Job(wid,payload,header+a+b,records,9,encode(out))
