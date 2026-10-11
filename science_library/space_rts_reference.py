"""Independent Fraction/RN32 stabilized RTS oracle."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .space_kalman_reference import matrix,require_psd,mm,transpose
from .space_joint_gls_reference import solve
WID='SPACE_RTS_SMOOTHER_STEP_F32_V1'


def step(F,Q,x,P,u,next_x,next_P):
    n=len(x);width=1+2*n+3*n*n;xp=[f.add(f.dot(row,x),v) for row,v in zip(F,u)];T=mm(F,P);Pp=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):Pp[a][b]=Pp[b][a]=f.add(f.dot(T[a],F[b]),Q[a][b])
    threshold=f.mul(max([0]+[Pp[a][a] for a in range(n)],key=f.rational),0x37800000);L=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):
            residual=Pp[a][b]
            for j in range(b):residual=f.sub(residual,f.mul(L[a][j],L[b][j]))
            if a==b:
                if f.rational(residual)<=f.rational(threshold):return [1]+[0]*(width-1)
                L[a][b]=f.sqrt(residual)
            else:L[a][b]=f.div(residual,L[b][b])
    C=mm(P,transpose(F));G=[solve(L,row) for row in C];delta=[f.sub(v,pred) for v,pred in zip(next_x,xp)];xs=[f.add(v,f.dot(row,delta)) for v,row in zip(x,G)]
    GF=mm(G,F);A=[[f.sub(f.ONE if a==b else 0,GF[a][b]) for b in range(n)] for a in range(n)]
    B=[[f.add(next_P[a][b],Q[a][b]) for b in range(n)] for a in range(n)];U=mm(G,B);V=mm(A,P);Ps=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):Ps[a][b]=Ps[b][a]=f.add(f.dot(U[a],G[b]),f.dot(V[a],A[b]))
    return [0]+xp+sum(Pp,[])+xs+sum(Ps,[])+sum(G,[])


def prepare_space_rts(wid,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('binary32 RTS contract required')
    if not isinstance(payload['transition'],list) or not isinstance(payload['states'],list):raise ValueError('matrix lists required')
    n=integer(len(payload['transition']),1,6,'state dimension');B=integer(len(payload['states']),1,64,'batch')
    F=matrix(payload['transition'],n,n);Q=matrix(payload['process_covariance'],n,n);require_psd(Q)
    x=matrix(payload['states'],B,n);u=matrix(payload['controls'],B,n);nx=matrix(payload['next_states'],B,n)
    cov=[]
    for key in ('covariances','next_covariances'):
        raw=payload[key]
        if not isinstance(raw,list) or len(raw)!=B:raise ValueError('covariance batch')
        rows=[matrix(v,n,n) for v in raw]
        for a in rows:require_psd(a)
        cov.append(rows)
    P,NP=cov;flat=sum(F,[])+sum(Q,[]);offset=16+len(flat);out=[]
    for args in zip(x,P,u,nx,NP):
        out+=step(F,Q,*args);xx,pp,uu,nn,cc=args;flat+=xx+sum(pp,[])+uu+nn+sum(cc,[])
    width=1+2*n+3*n*n;header=[MAGIC,1,73,B,n,0,0,0,0,0,0,offset,offset,width,0,0]
    return Job(wid,payload,header+flat,B,width,encode(out))
