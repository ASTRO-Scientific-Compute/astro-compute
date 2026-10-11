"""Exact rational RN32 force/RK4 oracle, independent of GPU integer arithmetic."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import rows,values


class SingularForce(ValueError):
    pass


def acceleration(position,mu,radius,j2):
    if not mu:return [0,0,0]
    r2=f.dot(position,position)
    if not r2:raise SingularForce('rounded radius squared is zero')
    r=f.sqrt(r2);base=f.neg(f.div(mu,f.mul(r2,r)))
    out=[f.mul(base,x) for x in position]
    if j2 and radius:
        q=f.div(f.mul(position[2],position[2]),r2)
        scale=f.div(f.mul(f.mul(f.mul(0x3fc00000,j2),mu),f.mul(radius,radius)),f.mul(f.mul(r2,r2),r))
        t=f.mul(0x40a00000,q)
        out=[f.add(a,f.mul(f.mul(scale,x),f.sub(t,0x40400000 if k==2 else f.ONE))) for k,(a,x) in enumerate(zip(out,position))]
    return out


def diagnostics(state,mu,radius,j2):
    r2=f.dot(state[:3],state[:3]);v2=f.dot(state[3:],state[3:])
    if not r2 and mu:return [1,0,0,0,0,0,0]
    r=f.sqrt(r2);potential=0
    if mu:
        potential=f.neg(f.div(mu,r))
        if j2 and radius:
            q=f.div(f.mul(state[2],state[2]),r2)
            shape=f.sub(f.mul(0x40400000,q),f.ONE)
            correction=f.mul(f.mul(j2,f.div(f.mul(radius,radius),r2)),f.mul(f.HALF,shape))
            potential=f.mul(potential,f.sub(f.ONE,correction))
    energy=f.add(f.mul(f.HALF,v2),potential)
    angular=[f.sub(f.mul(state[a],state[b+3]),f.mul(state[b],state[a+3])) for a,b in ((1,2),(2,0),(0,1))]
    return [0,r,v2,energy]+angular


def rk4(state,step,mu,radius,j2):
    def derivative(s):return s[3:]+acceleration(s[:3],mu,radius,j2)
    def advance(k,h):return [f.add(s,f.mul(h,v)) for s,v in zip(state,k)]
    half=f.mul(step,f.HALF);sixth=f.div(step,0x40c00000)
    k1=derivative(state);k2=derivative(advance(k1,half));k3=derivative(advance(k2,half));k4=derivative(advance(k3,step))
    return [f.add(s,f.mul(sixth,f.add(f.add(f.add(a,f.mul(f.TWO,b)),f.mul(f.TWO,c)),d))) for s,a,b,c,d in zip(state,k1,k2,k3,k4)]


def adaptive(state,params,mu,radius,j2,max_attempts,trace=None):
    duration,h,hmin,hmax,rtol,*atol=params
    state=[f.add(x,0) for x in state];elapsed=error=attempts=accepted=rejected=0;status=1
    while f.rational(elapsed)<f.rational(duration) and attempts<max_attempts:
        remaining=f.sub(duration,elapsed);step=min(h,remaining,key=f.rational)
        if not step or f.rational(f.add(elapsed,step))<=f.rational(elapsed):status=2;break
        attempts+=1;half=f.mul(step,f.HALF)
        if not half:status=2;break
        try:
            coarse=rk4(state,step,mu,radius,j2)
            mid=rk4(state,half,mu,radius,j2)
            fine=rk4(mid,half,mu,radius,j2)
        except SingularForce:status=3;break
        errors=[]
        for a,b,c,tol in zip(state,fine,coarse,atol):
            scale=f.add(tol,f.mul(rtol,max(a&0x7fffffff,b&0x7fffffff)))
            errors.append(f.div(f.div(f.sub(b,c)&0x7fffffff,0x41700000),scale))
        error=max(errors)
        if trace is not None:trace.append(dict(step=step,error=error,accepted=error<=f.ONE))
        if error<=f.ONE:
            state=fine;accepted+=1
            elapsed=duration if step==remaining else f.add(elapsed,step)
            h=step
            if error<=0x3d000000:
                h=f.mul(step,f.TWO) if step<=f.mul(hmax,f.HALF) else hmax
            h=max(h,hmin)
        else:
            rejected+=1
            if half<hmin:status=2;break
            h=half
    if elapsed==duration:status=0
    return [status,attempts,accepted,rejected,elapsed,error,h]+state


def prepare_space_dynamics(wid,op,payload):
    if payload.get('encoding')!='binary32-hex':raise ValueError('encoding=binary32-hex required')
    mu,radius,j2=[f.add(f.parse(payload[k]),0) for k in ('mu','reference_radius','j2')]
    if f.rational(mu)<0 or f.rational(radius)<0:raise ValueError('nonnegative mu and reference radius required')
    a,b,out=[],[],[];n=0
    if op==54:
        positions=rows(payload['positions'],3,4096);records=len(positions);ow=4
        for position in positions:
            a.extend(position)
            try:out.extend([0]+acceleration(position,mu,radius,j2))
            except SingularForce:out.extend([1,0,0,0])
    elif op in (55,56):
        states=rows(payload['states'],6,64 if op==55 else 4096);records=len(states)
        if op==55:
            b=[f.add(f.parse(payload[k]),0) for k in ('duration','dt_initial','dt_min','dt_max','rtol')]+[f.add(v,0) for v in values(payload['atol'],6)]
            if len(b)!=11:raise ValueError('six component absolute tolerances required')
            duration,h,hmin,hmax,rtol,*atol=b
            if f.rational(duration)<0 or f.rational(rtol)<0 or any(f.rational(x)<=0 for x in atol) or not 0<f.rational(hmin)<=f.rational(h)<=f.rational(hmax):raise ValueError('invalid integration interval, steps or tolerances')
            n=integer(payload['max_attempts'],1,128,'max_attempts')
            if n*records>2048:raise ValueError('bounded trajectory attempt budget exceeded')
            ow=13
        else:ow=7
        for state in states:
            a.extend(state);out.extend(adaptive(state,b,mu,radius,j2,n) if op==55 else diagnostics(state,mu,radius,j2))
    else:raise ValueError('unknown dynamics opcode')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,0,0,0,mu,radius,j2,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b,records,ow,encode(out))
