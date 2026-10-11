import random
from .space_statistics_vectors import hx,payload


def make(F=((1,),),Q=((0,),),x=((0,),),P=(((1,),),),u=((0,),),nx=((1,),),NP=(((.5,),),)):
    return payload(transition=[hx(list(r)) for r in F],process_covariance=[hx(list(r)) for r in Q],states=[hx(list(r)) for r in x],covariances=[[hx(list(r)) for r in a] for a in P],controls=[hx(list(r)) for r in u],next_states=[hx(list(r)) for r in nx],next_covariances=[[hx(list(r)) for r in a] for a in NP])
GOLDEN={73:(make(),[0]+[int(v,16) for v in hx([0,1,1,.5,1])])}


def fixture(op=73,seed=271828,scale=1):
    if op!=73:raise ValueError(op)
    rng=random.Random(seed);B=5*scale
    return make(F=((1,.25,0),(0,1,.25),(0,0,1)),Q=((.25,.0625,0),(.0625,.25,0),(0,0,.5)),x=[[rng.randrange(-8,9)/4 for _ in range(3)] for _ in range(B)],
        P=[[[2,.25,0],[.25,1,.125],[0,.125,.5]] for _ in range(B)],u=[[rng.randrange(-2,3)/8 for _ in range(3)] for _ in range(B)],nx=[[rng.randrange(-8,9)/4 for _ in range(3)] for _ in range(B)],NP=[[[.5,.125,0],[.125,.5,0],[0,0,.25]] for _ in range(B)])


def edges(op=73):
    if op!=73:raise ValueError(op)
    out=[('analytic_scalar',make()),('zero_prior',make(P=(((0,),),),Q=((1,),))),('zero_transition',make(F=((0,),),Q=((1,),))),('zero_next_covariance',make(NP=(((0,),),))),
         ('nonzero_control',make(u=((2,),))),('no_future_information',make(Q=((0,),),nx=((0,),),NP=(((1,),),))),('singular_prediction_guard',make(P=(((0,),),))),
         ('rank_one_guard',make(F=((1,0),(0,1)),Q=((0,0),(0,0)),x=((0,0),),P=(((1,1),(1,1)),),u=((0,0),),nx=((1,1),),NP=(((1,1),(1,1)),))),
         ('ill_scaled_guard',make(F=((1,0),(0,1)),Q=((0,0),(0,0)),x=((0,0),),P=(((1,0),(0,2**-20)),),u=((0,0),),nx=((1,1),),NP=(((1,0),(0,1)),)))]
    signed=make();signed['states'][0][0]='80000000';out.append(('signed_zero',signed))
    sub=make();sub['states'][0][0]='00000001';sub['controls'][0][0]='00000001';out.append(('subnormal_state',sub))
    I=[[int(a==b) for b in range(6)] for a in range(6)];Q=[[int(a==b)/4 for b in range(6)] for a in range(6)]
    out.append(('maximum_dimensions_batch',make(F=I,Q=Q,x=[[a/8 for a in range(6)] for _ in range(64)],P=[I for _ in range(64)],u=[[0]*6 for _ in range(64)],nx=[[1]*6 for _ in range(64)],NP=[Q for _ in range(64)])))
    return out
