"""Analytic free motion, exact two-body energy and boundary scenarios."""
import copy,random
from .space_statistics_vectors import hx,payload


def model(**kwargs):
    p=payload(gravitational_constant=hx(1),softening_squared=hx(0),states=hx([[[-.5,0,0,0,-.5,0],[.5,0,0,0,.5,0]]]),masses=hx([[1,1]]));p.update(kwargs);return p


def orbit(**kwargs):
    p=model(duration=hx(.25),dt_initial=hx(.125),dt_min=hx(2**-12),dt_max=hx(.25),rtol=hx(2**-14),atol=hx([2**-18]*6),max_attempts=32);p.update(kwargs);return p

GOLDEN={
 69:(orbit(gravitational_constant=hx(0),states=hx([[[1,2,3,1,0,-1],[-1,0,2,0,1,0]]]),masses=hx([[1,2]]),duration=hx(1),dt_initial=hx(1),dt_max=hx(2)),[0,1,1,0]+[int(x,16) for x in hx([1,0,2,2,2,2,1,0,-1,-1,1,2,0,1,0])]),
 70:(model(states=hx([[[-.5,0,0,0,-.5,0],[.5,0,0,0,.5,0]],[[0,0,0,0,0,0],[1,0,0,0,0,0]]]),masses=hx([[1,1],[1,2]])),
     [0]+[int(x,16) for x in hx([2,.25,-1,-.75,0,0,0,0,0,.5,0,0,0,1])]+[0]+[int(x,16) for x in hx([3,0,-2,-2,0,0,0,0,0,0])]+[0x3f2aaaab,0,0,int(hx(1),16)])}


def fixture(op,seed=271828,scale=1):
    rng=random.Random(seed);b=(3 if op==69 else 7)*scale;n=3
    states=[[[2*j-2+rng.randrange(-1,2)/8,rng.randrange(-2,3)/8,rng.randrange(-2,3)/8,rng.randrange(-2,3)/16,rng.randrange(-2,3)/16,rng.randrange(-2,3)/16] for j in range(n)] for _ in range(b)]
    p=model(states=hx(states),masses=hx([[rng.randrange(1,5)/4 for _ in range(n)] for _ in range(b)]),gravitational_constant=hx(1/16),softening_squared=hx(1/16))
    if op==69:
        params=orbit();params.update(p);params.update(duration=hx(.125),dt_initial=hx(.125),dt_max=hx(.25));return params
    if op==70:return p
    raise ValueError(op)


def edges(op):
    if op==69:
        return [
          ('zero_duration',orbit(duration=hx(0),states=hx([[[0]*6]*2]))),
          ('one_body_free_motion',orbit(states=hx([[[1,2,3,1,0,-1]]]),masses=hx([[2]]))),
          ('all_massless',orbit(masses=hx([[0,0]]))),
          ('massless_test_particle',orbit(masses=hx([[1,0]]),softening_squared=hx(.25))),
          ('coincident_softened',orbit(states=hx([[[0]*6]*2]),softening_squared=hx(1))),
          ('singular_initial',orbit(states=hx([[[0]*6]*2]))),
          ('singular_intermediate',orbit(states=hx([[[-1,0,0,2,0,0],[1,0,0,-2,0,0]]]),duration=hx(1),dt_initial=hx(1),dt_max=hx(1))),
          ('attempt_limit',orbit(duration=hx(1),dt_initial=hx(.03125),dt_max=hx(.03125),max_attempts=1)),
          ('rejected_then_accepted',orbit(duration=hx(.5),dt_initial=hx(.5),dt_max=hx(.5),rtol=hx(2**-16),atol=hx([2**-20]*6))),
          ('minimum_step_failure',orbit(duration=hx(1),dt_initial=hx(1),dt_min=hx(1),dt_max=hx(1),rtol=hx(0),atol=hx([2**-24]*6))),
          ('terminal_clip',orbit(gravitational_constant=hx(0),duration=hx(.1875),dt_initial=hx(.125),dt_min=hx(.125),dt_max=hx(.125))),
          ('half_step_underflow',orbit(gravitational_constant=hx(0),duration='00000001',dt_initial='00000001',dt_min='00000001',dt_max='00000001')),
          ('signed_zero_states',orbit(states=[[['80000000']*6]*2],duration=hx(0))),
          ('maximum_systems',orbit(states=hx([[[0]*6]]*16),masses=hx([[1]]*16),gravitational_constant=hx(0))),
          ('maximum_bodies_interacting',orbit(states=hx([[[j,0,0,0,0,0] for j in range(8)]]),masses=hx([[1]*8]),gravitational_constant=hx(1/64),softening_squared=hx(1),max_attempts=16)),
          ('maximum_work_attempts',orbit(states=hx([[[0]*6]*8]*4),masses=hx([[1]*8]*4),gravitational_constant=hx(0),duration=hx(8),dt_initial=hx(.125),dt_max=hx(.125),max_attempts=64))]
    if op==70:
        out=[]
        for name,key,v in [('no_gravity','gravitational_constant',hx(0)),('softened','softening_squared',hx(.25)),('all_massless','masses',hx([[0,0]])),('massless_member','masses',hx([[1,0]])),('singular_pair','states',hx([[[0]*6]*2])),('stationary_system','states',hx([[[-.5,0,0,0,0,0],[.5,0,0,0,0,0]]]))]:
            p=model();p[key]=v;out.append((name,p))
        out.extend([
          ('single_body',model(states=hx([[[1,2,3,1,0,-1]]]),masses=hx([[2]]))),
          ('signed_zero_parameters',model(gravitational_constant='80000000',softening_squared='80000000')),
          ('subnormal_mass',model(states=hx([[[0,0,0,0,0,0]]]),masses=[['00000001']])),
          ('maximum_batch',model(states=hx([[[0]*6]]*64),masses=hx([[1]]*64))),
          ('maximum_bodies_work',model(states=hx([[[j,0,0,0,0,0] for j in range(64)]]*16),masses=hx([[1]*64]*16),gravitational_constant=hx(0)))])
        return out
    raise ValueError(op)
