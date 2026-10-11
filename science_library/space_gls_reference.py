"""Independent Fraction-based Cholesky/augmented-quadratic GLS reference."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import values
from .space_statistics_reference import rectangular_float


def correlated_fit(y,t,diagonal,u):
    n=len(y);k=len(u);inv=[f.div(f.ONE,d) for d in diagonal]
    g=[[0]*k for _ in range(k)];lower=[[0]*k for _ in range(k)]
    for a in range(k):
        for b in range(a+1):
            v=f.summation(f.mul(f.mul(u[a][i],inv[i]),u[b][i]) for i in range(n))
            g[a][b]=g[b][a]=f.add(f.ONE if a==b else 0,v)
    bt=[f.summation(f.mul(f.mul(row[i],inv[i]),t[i]) for i in range(n)) for row in u]
    by=[f.summation(f.mul(f.mul(row[i],inv[i]),y[i]) for i in range(n)) for row in u]
    for a in range(k):
        for b in range(a+1):
            value=g[a][b]
            for j in range(b):value=f.sub(value,f.mul(lower[a][j],lower[b][j]))
            if a==b:
                if f.rational(value)<=f.rational(f.mul(g[a][a],0x37800000)):return [2]+[0]*5
                lower[a][a]=f.sqrt(value)
            else:lower[a][b]=f.div(value,lower[b][b])
    def solve(rhs):
        v=[0]*k;z=[0]*k
        for a in range(k):
            value=rhs[a]
            for j in range(a):value=f.sub(value,f.mul(lower[a][j],v[j]))
            v[a]=f.div(value,lower[a][a])
        for a in range(k-1,-1,-1):
            value=v[a]
            for j in range(a+1,k):value=f.sub(value,f.mul(lower[j][a],z[j]))
            z[a]=f.div(value,lower[a][a])
        return z
    zt=solve(bt);zy=solve(by)
    qt=[f.sub(t[i],f.summation(f.mul(u[a][i],zt[a]) for a in range(k))) for i in range(n)]
    qy=[f.sub(y[i],f.summation(f.mul(u[a][i],zy[a]) for a in range(k))) for i in range(n)]
    information=f.summation(f.mul(f.mul(qt[i],inv[i]),qt[i]) for i in range(n))
    numerator=f.summation(f.mul(f.mul(qt[i],inv[i]),qy[i]) for i in range(n))
    for a in range(k):information=f.add(information,f.mul(zt[a],zt[a]));numerator=f.add(numerator,f.mul(zt[a],zy[a]))
    if not information:return [1]+[0]*5
    amplitude=f.div(numerator,information);variance=f.div(f.ONE,information)
    zr=[f.sub(zy[a],f.mul(amplitude,zt[a])) for a in range(k)]
    residual=[f.sub(y[i],f.mul(amplitude,t[i])) for i in range(n)]
    qr=[f.sub(residual[i],f.summation(f.mul(u[a][i],zr[a]) for a in range(k))) for i in range(n)]
    chi=f.summation(f.mul(f.mul(qr[i],inv[i]),qr[i]) for i in range(n))
    for v in zr:chi=f.add(chi,f.mul(v,v))
    return [0,amplitude,variance,chi,information,k]


def prepare_space_gls(wid,op,payload):
    if op!=67 or payload.get('encoding')!='binary32-hex':raise ValueError('binary32 GLS contract required')
    y,n=rectangular_float(payload['flux'],64,128);t,tn=rectangular_float(payload['template'],64,128);d,dn=rectangular_float(payload['diagonal_variance'],64,128);records=len(y)
    if tn!=n or dn!=n or len(t)!=records or len(d)!=records:raise ValueError('matching GLS planes required')
    if any(f.rational(v)<=0 for row in d for v in row):raise ValueError('strictly positive diagonal variance required')
    raw=payload['factors']
    if not isinstance(raw,list) or len(raw)!=records or not all(isinstance(rows,list) for rows in raw):raise ValueError('GLS factor batch shape')
    k=integer(len(raw[0]),0,8,'GLS factor count')
    if records*n*(k+1)**2>131072:raise ValueError('GLS work limit')
    u=[]
    for rows in raw:
        if len(rows)!=k:raise ValueError('uniform GLS factor count required')
        block=[]
        for row in rows:
            v=values(row,128)
            if len(v)!=n:raise ValueError('GLS factor width')
            block.append(v)
        u.append(block)
    a=[v for row in y for v in row];b=[v for row in t for v in row];c=[v for row in d for v in row];factors=[v for block in u for row in block for v in row];out=[]
    for row in zip(y,t,d,u):out.extend(correlated_fit(*row))
    header=[MAGIC,1,op,records,n,k,0,0,16+3*records*n,0,0,16+records*n,16+2*records*n,6,0,0]
    return Job(wid,payload,header+a+b+c+factors,records,6,encode(out))
