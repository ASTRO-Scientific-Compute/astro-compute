"""Independent Fraction/RN32 coupled-system RK4 and invariant oracle."""
from . import f32 as f
from .reference import Job,MAGIC,encode,integer
from .float_reference import rows,values
from .space_statistics_reference import rectangular_float


class SingularInteraction(ValueError):
    pass


def derivative(state,masses,g,eps2):
    n=len(masses);out=[]
    for i in range(n):
        acceleration=[0,0,0]
        if g:
            for j in range(n):
                if i==j:continue
                gm=f.mul(g,masses[j])
                if not gm:continue
                delta=[f.sub(state[j*6+a],state[i*6+a]) for a in range(3)]
                distance=f.add(f.dot(delta,delta),eps2)
                if not distance:raise SingularInteraction('rounded softened distance squared is zero')
                scale=f.div(gm,f.mul(distance,f.sqrt(distance)))
                for a in range(3):acceleration[a]=f.add(acceleration[a],f.mul(scale,delta[a]))
        out.extend(state[i*6+3:i*6+6]+acceleration)
    return out


def rk4(state,step,masses,g,eps2):
    half=f.mul(step,f.HALF);sixth=f.div(step,0x40c00000)
    def advance(k,h):return [f.add(s,f.mul(h,v)) for s,v in zip(state,k)]
    k1=derivative(state,masses,g,eps2);k2=derivative(advance(k1,half),masses,g,eps2)
    k3=derivative(advance(k2,half),masses,g,eps2);k4=derivative(advance(k3,step),masses,g,eps2)
    return [f.add(s,f.mul(sixth,f.add(f.add(f.add(a,f.mul(f.TWO,b)),f.mul(f.TWO,c)),d))) for s,a,b,c,d in zip(state,k1,k2,k3,k4)]


def adaptive(state,masses,params,g,eps2,max_attempts,trace=None):
    duration,h,hmin,hmax,rtol,*atol=params
    state=[f.add(x,0) for x in state];elapsed=error=attempts=accepted=rejected=0;status=1
    while f.rational(elapsed)<f.rational(duration) and attempts<max_attempts:
        remaining=f.sub(duration,elapsed);step=min(h,remaining)
        if not step or f.rational(f.add(elapsed,step))<=f.rational(elapsed):status=2;break
        attempts+=1;half=f.mul(step,f.HALF)
        if not half:status=2;break
        try:
            coarse=rk4(state,step,masses,g,eps2)
            mid=rk4(state,half,masses,g,eps2)
            fine=rk4(mid,half,masses,g,eps2)
        except SingularInteraction:status=3;break
        error=0
        for index,(a,b,c) in enumerate(zip(state,fine,coarse)):
            scale=f.add(atol[index%6],f.mul(rtol,max(a&0x7fffffff,b&0x7fffffff)))
            error=max(error,f.div(f.div(f.sub(b,c)&0x7fffffff,0x41700000),scale))
        if trace is not None:trace.append(dict(step=step,error=error,accepted=error<=f.ONE))
        if error<=f.ONE:
            state=fine;accepted+=1;elapsed=duration if step==remaining else f.add(elapsed,step);h=step
            if error<=0x3d000000:h=f.mul(step,f.TWO) if step<=f.mul(hmax,f.HALF) else hmax
            h=max(h,hmin)
        else:
            rejected+=1
            if half<hmin:status=2;break
            h=half
    if elapsed==duration:status=0
    return [status,attempts,accepted,rejected,elapsed,error,h]+state


def invariants(states,masses,g,eps2):
    total=f.summation(masses)
    if not total:return [2]+[0]*14
    kinetic=potential=0;momentum=[0]*3;angular=[0]*3;center=[0]*3;minimum=None
    for state,mass in zip(states,masses):
        if not mass:continue
        position,velocity=state[:3],state[3:]
        kinetic=f.add(kinetic,f.mul(f.mul(f.HALF,mass),f.dot(velocity,velocity)))
        for a in range(3):
            momentum[a]=f.add(momentum[a],f.mul(mass,velocity[a]));center[a]=f.add(center[a],f.mul(mass,position[a]))
            b,c=(a+1)%3,(a+2)%3
            cross=f.sub(f.mul(position[b],velocity[c]),f.mul(position[c],velocity[b]))
            angular[a]=f.add(angular[a],f.mul(mass,cross))
    for i in range(len(states)):
        for j in range(i+1,len(states)):
            delta=[f.sub(states[j][a],states[i][a]) for a in range(3)];distance=f.dot(delta,delta)
            minimum=distance if minimum is None else min(minimum,distance)
            coupling=f.mul(f.mul(g,masses[i]),masses[j])
            if not coupling:continue
            softened=f.add(distance,eps2)
            if not softened:return [1]+[0]*14
            potential=f.sub(potential,f.div(coupling,f.sqrt(softened)))
    return [0,total,kinetic,potential,f.add(kinetic,potential)]+momentum+angular+[f.div(x,total) for x in center]+[minimum or 0]


def prepare_space_nbody(wid,op,payload):
    if payload.get('encoding')!='binary32-hex' or op not in (69,70):raise ValueError('binary32 N-body contract required')
    g,eps2=[f.add(f.parse(payload[k]),0) for k in ('gravitational_constant','softening_squared')]
    if f.rational(g)<0 or f.rational(eps2)<0:raise ValueError('nonnegative G and softening squared required')
    max_b,max_n=(16,8) if op==69 else (64,64)
    raw=payload['states']
    if not isinstance(raw,list) or not 1<=len(raw)<=max_b:raise ValueError('N-body batch size')
    systems=[rows(s,6,max_n) for s in raw];n=len(systems[0]);records=len(systems)
    if any(len(s)!=n for s in systems):raise ValueError('uniform body count required')
    masses,mn=rectangular_float(payload['masses'],max_b,max_n)
    if len(masses)!=records or mn!=n:raise ValueError('matching system masses required')
    if any(f.rational(m)<0 for row in masses for m in row):raise ValueError('nonnegative masses required')
    masses=[[f.add(m,0) for m in row] for row in masses];params=[];attempts=0;out=[]
    if op==69:
        params=[f.add(f.parse(payload[k]),0) for k in ('duration','dt_initial','dt_min','dt_max','rtol')]+[f.add(x,0) for x in values(payload['atol'],6)]
        if len(params)!=11:raise ValueError('six absolute component tolerances required')
        duration,h,hmin,hmax,rtol,*atol=params
        if f.rational(duration)<0 or f.rational(rtol)<0 or any(f.rational(x)<=0 for x in atol) or not 0<f.rational(hmin)<=f.rational(h)<=f.rational(hmax):raise ValueError('invalid duration, step bounds or tolerances')
        attempts=integer(payload['max_attempts'],1,64,'max_attempts')
        if records*n*n*attempts>16384:raise ValueError('N-body integration work limit')
        width=7+6*n
    else:
        if records*n*n>65536:raise ValueError('N-body diagnostic work limit')
        width=15
    for system,mass in zip(systems,masses):
        out.extend(adaptive([v for body in system for v in body],mass,params,g,eps2,attempts) if op==69 else invariants(system,mass,g,eps2))
    a=[v for system in systems for body in system for v in body];b=[v for row in masses for v in row]
    header=[MAGIC,1,op,records,n,attempts,0,0,g,eps2,0,16+len(a),16+len(a)+len(b),width,0,0]
    return Job(wid,payload,header+a+b+params,records,width,encode(out))
