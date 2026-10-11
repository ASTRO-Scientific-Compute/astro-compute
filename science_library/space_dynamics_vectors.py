"""Analytic axis/equator/circular/free-motion vectors before GPU implementation."""
import copy
import random
from .space_statistics_vectors import hx,payload
from .f32 import hex32


def model(**kwargs):return payload(mu=hex32(1),reference_radius=hex32(1),j2=hex32(1/16),**kwargs)

def orbit(**kwargs):
    p=model(states=hx([[1,0,0,0,1,0]]));p.update(duration=hex32(.25),dt_initial=hex32(.125),dt_min=hex32(2**-12),dt_max=hex32(.25),rtol=hex32(2**-14),atol=hx([2**-18]*6),max_attempts=32);p.update(kwargs);return p

GOLDEN={
 54:(model(positions=hx([[1,0,0],[0,0,1],[0,0,0]])),[0]+[int(x,16) for x in hx([-1.09375,0,0])]+[0]+[int(x,16) for x in hx([0,0,-.8125])]+[1,0,0,0]),
 55:(orbit(mu=hex32(0),j2=hex32(0),states=hx([[1,2,3,1,0,-1]]),duration=hex32(1),dt_initial=hex32(1),dt_max=hex32(2)),[0,1,1,0]+[int(x,16) for x in hx([1,0,2,2,2,2,1,0,-1])]),
 56:(model(states=hx([[1,0,0,0,1,0],[0,0,1,1,0,0],[0,0,0,0,0,0]])),[0]+[int(x,16) for x in hx([1,1,-.53125,0,0,1])]+[0]+[int(x,16) for x in hx([1,1,-.4375,0,1,0])]+[1,0,0,0,0,0,0]),
}


def fixture(op,seed=271828,scale=1):
    r=random.Random(seed);n=(5 if op==55 else 29)*scale
    states=[[1+r.randrange(0,9)/16,r.randrange(-4,5)/16,r.randrange(-4,5)/16,r.randrange(-2,3)/16,1+r.randrange(-2,3)/16,r.randrange(-2,3)/16] for _ in range(n)]
    if op==54:return model(positions=hx([s[:3] for s in states]))
    if op==55:return orbit(states=hx(states))
    if op==56:return model(states=hx(states))
    raise ValueError(op)


def edges(op):
    g=copy.deepcopy(GOLDEN[op][0]);cases=[]
    if op in (54,56):
        for name,key,v in [('central_only','j2',0),('free_motion','mu',0),('zero_radius','reference_radius',0),('negative_j2','j2',-1/16)]:
            p=copy.deepcopy(g);p[key]=hex32(v);cases.append((name,p))
        p=copy.deepcopy(g);p['positions' if op==54 else 'states']=hx([[-2,0,0],[0,2,0],[0,0,-2]]) if op==54 else hx([[-2,0,0,0,-1,0],[0,2,0,1,0,0],[0,0,-2,1,0,0]]);cases.append(('axis_symmetry',p))
        p=copy.deepcopy(g);p['positions' if op==54 else 'states']=[['00000001','80000000','00000000']+([] if op==54 else ['00000000']*3)];cases.append(('radius_underflow_status',p))
        p=copy.deepcopy(g);p['mu']='80000000';p['reference_radius']='80000000';p['j2']='80000000';cases.append(('signed_zero_parameters',p))
    elif op==55:
        cases.append(('singular_intermediate',orbit(states=hx([[1,0,0,-2,0,0]]),duration=hex32(1),dt_initial=hex32(1),dt_max=hex32(1))))
        cases.append(('maximum_attempts',orbit(mu=hex32(0),duration=hex32(16),dt_initial=hex32(.125),dt_max=hex32(.125),max_attempts=128)))
        cases.append(('zero_duration',orbit(duration=hex32(0),states=hx([[0]*6]))))
        cases.append(('attempt_limit',orbit(duration=hex32(1),dt_initial=hex32(.03125),dt_max=hex32(.03125),max_attempts=1)))
        cases.append(('rejected_then_accepted',orbit(duration=hex32(1),dt_initial=hex32(1),dt_max=hex32(1),rtol=hex32(2**-16),atol=hx([2**-20]*6))))
        cases.append(('minimum_step_failure',orbit(duration=hex32(1),dt_initial=hex32(1),dt_min=hex32(1),dt_max=hex32(1),rtol=hex32(0),atol=hx([2**-24]*6))))
        cases.append(('singular_initial',orbit(states=hx([[0]*6]))))
        cases.append(('terminal_clip',orbit(duration=hex32(.1875),dt_initial=hex32(.125),dt_min=hex32(.125),dt_max=hex32(.125),rtol=hex32(2**-8))))
        cases.append(('half_step_underflow',orbit(mu=hex32(0),duration='00000001',dt_initial='00000001',dt_min='00000001',dt_max='00000001')))
        cases.append(('central_circular',orbit(j2=hex32(0),duration=hex32(1),dt_initial=hex32(.25),dt_max=hex32(.5))))
    return cases
