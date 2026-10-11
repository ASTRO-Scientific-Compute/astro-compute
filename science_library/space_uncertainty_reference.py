"""Independent exact-rational per-operation uncertainty reference."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import values
from .space_statistics_reference import rectangular_float,masks


def noise_pixel(signal,background,gain,valid):
    if not valid:return [1,0,0,0,0]
    source=f.div(signal,gain) if f.rational(signal)>0 and f.rational(gain)>0 else 0
    total=f.add(background,source)
    if not total:return [2,0,0,0,0]
    return [0,source,total,f.sqrt(total),f.div(f.ONE,total)]


def linear_flux(flux,weights,diagonal,factors):
    active=[i for i,w in enumerate(weights) if f.rational(w)!=0]
    if not active:return [1]+[0]*7
    total_flux=f.summation(f.mul(weights[i],flux[i]) for i in active)
    independent=f.summation(f.mul(f.mul(weights[i],weights[i]),diagonal[i]) for i in active)
    projections=[f.summation(f.mul(weights[i],row[i]) for i in active) for row in factors]
    correlated=f.summation(f.mul(p,p) for p in projections)
    variance=f.add(independent,correlated)
    if not variance:return [2,len(active),total_flux,0,0,0,0,0]
    error=f.sqrt(variance)
    return [0,len(active),total_flux,independent,correlated,variance,error,f.div(total_flux,error)]


def prepare_space_uncertainty(wid,op,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('binary32 uncertainty contract required')
    if op==65:
        a=values(payload['signal'],65536);records=len(a)
        b=values(payload['background_variance'],65536);c=values(payload['gain'],65536)
        if len(b)!=records or len(c)!=records:raise ValueError('equal-length noise arrays required')
        valid=masks([payload['valid']],1,records)[0]
        if any(f.rational(v)<0 for v in b+c):raise ValueError('nonnegative variance and gain required')
        out=[]
        for row in zip(a,b,c,valid):out.extend(noise_pixel(*row))
        header=[MAGIC,1,op,records,records,0,0,0,16+3*records,0,0,16+records,16+2*records,5,0,0]
        return Job(wid,payload,header+a+b+c+valid,records,5,encode(out))
    if op!=66:raise ValueError(op)
    flux,n=rectangular_float(payload['flux'],128,256);weights,wn=rectangular_float(payload['weights'],128,256);diagonal,dn=rectangular_float(payload['diagonal_variance'],128,256)
    records=len(flux)
    if wn!=n or dn!=n or len(weights)!=records or len(diagonal)!=records:raise ValueError('matching flux/weight/variance dimensions required')
    if any(f.rational(v)<0 for row in diagonal for v in row):raise ValueError('nonnegative diagonal variance required')
    factors=payload['factors']
    if not isinstance(factors,list) or len(factors)!=records or not all(isinstance(rows,list) for rows in factors):raise ValueError('factor batch shape mismatch')
    k=integer(len(factors[0]),0,16,'factor count');parsed=[]
    for rows in factors:
        if len(rows)!=k:raise ValueError('same factor count in every record required')
        block=[]
        for row in rows:
            r=values(row,256)
            if len(r)!=n:raise ValueError('factor row width mismatch')
            block.append(r)
        parsed.append(block)
    if records*n*(k+1)>262144:raise ValueError('covariance work limit')
    a=[v for row in flux for v in row];b=[v for row in weights for v in row];c=[v for row in diagonal for v in row];u=[v for block in parsed for row in block for v in row];out=[]
    for row in zip(flux,weights,diagonal,parsed):out.extend(linear_flux(*row))
    header=[MAGIC,1,op,records,n,k,0,0,16+3*records*n,0,0,16+records*n,16+2*records*n,8,0,0]
    return Job(wid,payload,header+a+b+c+u,records,8,encode(out))
