"""Exact-rational oracle; independent of GPU integer arithmetic implementation."""
from fractions import Fraction
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import values
from .space_joint_gls_reference import forward,solve
WID='SPACE_LINEAR_KALMAN_STEP_F32_V1'


def matrix(raw,rows,cols):
    if not isinstance(raw,list) or len(raw)!=rows:raise ValueError('matrix rows')
    result=[values(row,cols) for row in raw]
    if any(len(row)!=cols for row in result):raise ValueError('matrix columns')
    return result


def require_psd(a):
    """Exact LDL residual elimination, accepting zero pivots only with zero column."""
    r=[[f.rational(v) for v in row] for row in a];n=len(r)
    if any(r[i][j]!=r[j][i] for i in range(n) for j in range(n)):raise ValueError('symmetric covariance required')
    for k in range(n):
        pivot=r[k][k]
        if pivot<0:raise ValueError('positive semidefinite covariance required')
        if not pivot:
            if any(r[i][k] for i in range(k+1,n)):raise ValueError('zero PSD pivot with nonzero residual')
            continue
        for i in range(k+1,n):
            for j in range(k+1,n):r[i][j]-=r[i][k]*r[k][j]/pivot


def mm(a,b):return [[f.dot(row,col) for col in zip(*b)] for row in a]
def transpose(a):return [list(row) for row in zip(*a)]


def step(F,Q,H,R,x,P,u,y):
    n=len(x);m=len(y);width=2+2*n+2*n*n+m
    xp=[f.add(f.dot(row,x),v) for row,v in zip(F,u)];T=mm(F,P);Pp=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):Pp[a][b]=Pp[b][a]=f.add(f.dot(T[a],F[b]),Q[a][b])
    C=mm(Pp,transpose(H));S=[[0]*m for _ in range(m)];e=[f.sub(v,f.dot(row,xp)) for v,row in zip(y,H)]
    for a in range(m):
        for b in range(a+1):S[a][b]=S[b][a]=f.add(f.dot(H[a],[C[j][b] for j in range(n)]),R[a] if a==b else 0)
    threshold=f.mul(max([0]+[S[a][a] for a in range(m)],key=f.rational),0x37800000);L=[[0]*m for _ in range(m)]
    for a in range(m):
        for b in range(a+1):
            residual=S[a][b]
            for j in range(b):residual=f.sub(residual,f.mul(L[a][j],L[b][j]))
            if a==b:
                if f.rational(residual)<=f.rational(threshold):return [1]+[0]*(width-1)
                L[a][b]=f.sqrt(residual)
            else:L[a][b]=f.div(residual,L[b][b])
    K=[solve(L,row) for row in C];post=[f.add(v,f.dot(row,e)) for v,row in zip(xp,K)]
    KH=mm(K,H);A=[[f.sub(f.ONE if a==b else 0,KH[a][b]) for b in range(n)] for a in range(n)]
    V=mm(A,Pp);Ppost=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):
            noise=f.summation(f.mul(f.mul(K[a][j],R[j]),K[b][j]) for j in range(m))
            Ppost[a][b]=Ppost[b][a]=f.add(f.dot(V[a],A[b]),noise)
    z=forward(L,e)
    return [0]+xp+sum(Pp,[])+post+sum(Ppost,[])+e+[f.dot(z,z)]


def prepare_space_kalman(wid,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('binary32 Kalman contract required')
    if not isinstance(payload['transition'],list) or not isinstance(payload['observation'],list) or not isinstance(payload['states'],list):raise ValueError('matrix lists required')
    n=integer(len(payload['transition']),1,6,'state dimension');m=integer(len(payload['observation']),1,3,'measurement dimension');B=integer(len(payload['states']),1,64,'batch')
    F=matrix(payload['transition'],n,n);Q=matrix(payload['process_covariance'],n,n);H=matrix(payload['observation'],m,n);R=values(payload['measurement_variance'],3)
    if len(R)!=m or any(f.rational(v)<=0 for v in R):raise ValueError('positive measurement variances required')
    x=matrix(payload['states'],B,n);u=matrix(payload['controls'],B,n);y=matrix(payload['measurements'],B,m)
    raw=payload['covariances']
    if not isinstance(raw,list) or len(raw)!=B:raise ValueError('covariance batch')
    P=[matrix(v,n,n) for v in raw];require_psd(Q)
    for cov in P:require_psd(cov)
    out=[];flat=sum(F,[])+sum(Q,[])+sum(H,[])+R;offset=16+len(flat)
    for args in zip(x,P,u,y):
        out+=step(F,Q,H,R,*args);xx,pp,uu,yy=args;flat+=xx+sum(pp,[])+uu+yy
    width=2+2*n+2*n*n+m;header=[MAGIC,1,72,B,n,m,0,0,0,0,0,offset,offset,width,0,0]
    return Job(wid,payload,header+flat,B,width,encode(out))
