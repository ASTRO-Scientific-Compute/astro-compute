"""Independent exact-rational RN32 oracle for jointly fitted GLS amplitudes."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import values
from .space_statistics_reference import rectangular_float


def cholesky(matrix):
    n=len(matrix);lower=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):
            v=matrix[a][b]
            for j in range(b):v=f.sub(v,f.mul(lower[a][j],lower[b][j]))
            if a==b:
                if f.rational(v)<=f.rational(f.mul(matrix[a][a],0x37800000)):return None
                lower[a][a]=f.sqrt(v)
            else:lower[a][b]=f.div(v,lower[b][b])
    return lower


def forward(lower,rhs):
    v=[]
    for a in range(len(rhs)):
        value=rhs[a]
        for j in range(a):value=f.sub(value,f.mul(lower[a][j],v[j]))
        v.append(f.div(value,lower[a][a]))
    return v


def solve(lower,rhs):
    v=forward(lower,rhs);n=len(v);z=[0]*n
    for a in range(n-1,-1,-1):
        value=v[a]
        for j in range(a+1,n):value=f.sub(value,f.mul(lower[j][a],z[j]))
        z[a]=f.div(value,lower[a][a])
    return z


def joint_fit(y,templates,diagonal,u):
    n=len(y);m=len(templates);k=len(u);width=2+m+m*m
    inv=[f.div(f.ONE,d) for d in diagonal];g=[[0]*k for _ in range(k)]
    for a in range(k):
        for b in range(a+1):
            s=f.summation(f.mul(f.mul(u[a][i],inv[i]),u[b][i]) for i in range(n))
            g[a][b]=g[b][a]=f.add(f.ONE if a==b else 0,s)
    lower=cholesky(g)
    if lower is None:return [2]+[0]*(width-1)
    z=[];q=[]
    for v in templates+[y]:
        rhs=[f.summation(f.mul(f.mul(row[i],inv[i]),v[i]) for i in range(n)) for row in u]
        solution=solve(lower,rhs);z.append(solution)
        q.append([f.sub(v[i],f.summation(f.mul(u[a][i],solution[a]) for a in range(k))) for i in range(n)])
    def inner(a,b):
        value=f.summation(f.mul(f.mul(q[a][i],inv[i]),q[b][i]) for i in range(n))
        for j in range(k):value=f.add(value,f.mul(z[a][j],z[b][j]))
        return value
    h=[[0]*m for _ in range(m)]
    for a in range(m):
        for b in range(a+1):h[a][b]=h[b][a]=inner(a,b)
    rhs=[inner(a,m) for a in range(m)];model_lower=cholesky(h)
    if model_lower is None:return [1]+[0]*(width-1)
    amplitude=solve(model_lower,rhs)
    # Columns of L^-1; covariance=(L^-1)^T L^-1, mirrored explicitly.
    inverse_columns=[forward(model_lower,[f.ONE if j==a else 0 for j in range(m)]) for a in range(m)]
    covariance=[[0]*m for _ in range(m)]
    for a in range(m):
        for b in range(a+1):
            covariance[a][b]=covariance[b][a]=f.summation(f.mul(inverse_columns[a][j],inverse_columns[b][j]) for j in range(m))
    zr=[f.sub(z[m][j],f.summation(f.mul(amplitude[a],z[a][j]) for a in range(m))) for j in range(k)]
    chi=0
    for i in range(n):
        residual=f.sub(y[i],f.summation(f.mul(amplitude[a],templates[a][i]) for a in range(m)))
        qr=f.sub(residual,f.summation(f.mul(u[j][i],zr[j]) for j in range(k)))
        chi=f.add(chi,f.mul(f.mul(qr,inv[i]),qr))
    for v in zr:chi=f.add(chi,f.mul(v,v))
    return [0]+amplitude+[v for row in covariance for v in row]+[chi]


def prepare_space_joint_gls(wid,op,payload):
    if op!=68 or payload.get('encoding')!='binary32-hex':raise ValueError('binary32 joint GLS contract required')
    y,n=rectangular_float(payload['flux'],32,64);d,dn=rectangular_float(payload['diagonal_variance'],32,64);records=len(y)
    if dn!=n or len(d)!=records:raise ValueError('matching joint GLS planes required')
    if any(f.rational(v)<=0 for row in d for v in row):raise ValueError('strictly positive diagonal variance required')
    rawt=payload['templates'];rawu=payload['factors']
    if not all(isinstance(raw,list) and len(raw)==records and all(isinstance(block,list) for block in raw) for raw in (rawt,rawu)):raise ValueError('joint GLS batch shape')
    m=integer(len(rawt[0]),2,5,'template count');k=integer(len(rawu[0]),0,4,'factor count')
    if n<m:raise ValueError('at least as many samples as templates required')
    if records*n*(k+m+1)**2>131072:raise ValueError('joint GLS work limit')
    def blocks(raw,count):
        result=[]
        for block in raw:
            if len(block)!=count:raise ValueError('uniform joint GLS dimensions required')
            rows=[values(row,64) for row in block]
            if any(len(row)!=n for row in rows):raise ValueError('joint GLS width')
            result.append(rows)
        return result
    t=blocks(rawt,m);u=blocks(rawu,k);out=[];width=2+m+m*m
    for args in zip(y,t,d,u):out.extend(joint_fit(*args))
    flat=lambda blocks:[v for row in blocks for v in row]
    a=flat(y);b=flat([row for block in t for row in block]);c=flat(d);factors=flat([row for block in u for row in block])
    header=[MAGIC,1,op,records,n,k,m,0,16+records*n*(m+2),0,0,16+records*n,16+records*n*(m+1),width,0,0]
    return Job(wid,payload,header+a+b+c+factors,records,width,encode(out))
