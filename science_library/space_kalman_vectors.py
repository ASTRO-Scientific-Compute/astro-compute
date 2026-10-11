import random
from copy import deepcopy
from .space_statistics_vectors import hx,payload


def make(F=((1,),),Q=((0,),),H=((1,),),R=(3,),x=((0,),),P=(((1,),),),u=((0,),),y=((4,),)):
    return payload(transition=[hx(list(row)) for row in F],process_covariance=[hx(list(row)) for row in Q],observation=[hx(list(row)) for row in H],measurement_variance=hx(list(R)),states=[hx(list(row)) for row in x],covariances=[[hx(list(row)) for row in a] for a in P],controls=[hx(list(row)) for row in u],measurements=[hx(list(row)) for row in y])
GOLDEN={72:(make(),[0]+[int(v,16) for v in hx([0,1,1,.75,4,4])])}


def fixture(op=72,seed=271828,scale=1):
    if op!=72:raise ValueError(op)
    rng=random.Random(seed);B=5*scale
    return make(F=((1,.25,0),(0,1,.25),(0,0,1)),Q=((.125,0,0),(0,.25,0),(0,0,.5)),H=((1,0,0),(0,1,.5)),R=(.5,1),
        x=[[rng.randrange(-8,9)/4 for _ in range(3)] for _ in range(B)],P=[[[2,.25,0],[.25,1,.125],[0,.125,.5]] for _ in range(B)],
        u=[[rng.randrange(-2,3)/8 for _ in range(3)] for _ in range(B)],y=[[rng.randrange(-8,9)/4 for _ in range(2)] for _ in range(B)])


def edges(op=72):
    if op!=72:raise ValueError(op)
    out=[('analytic_scalar',make()),('zero_prior_process',make(P=(((0,),),))),('zero_observation',make(H=((0,),))),
         ('singular_transition',make(F=((0,),),Q=((1,),))),('nonzero_control',make(u=((2,),))),
         ('rank_deficient_observation',make(H=((1,),(1,)),R=(1,2),y=((1,2),))),
         ('tiny_noise_guard',make(H=((1,),(1,)),R=(2**-30,2**-30),y=((1,1),))),
         ('ill_scaled_guard',make(F=((1,0),(0,1)),Q=((0,0),(0,0)),H=((1,0),(0,1)),R=(1,2**-20),x=((0,0),),P=(((1,0),(0,0)),),u=((0,0),),y=((1,1),))),
         ('rank_one_covariance',make(F=((1,0),(0,1)),Q=((1,1),(1,1)),H=((1,0),),R=(1,),x=((0,0),),P=(((1,1),(1,1)),),u=((0,0),),y=((1,),)))]
    signed=make();signed['states'][0][0]='80000000';out.append(('signed_zero',signed))
    sub=make();sub['states'][0][0]='00000001';sub['controls'][0][0]='00000001';out.append(('subnormal_state',sub))
    tiny=make(P=(((0,),),),R=(2**-126,),y=((2**-70,),));out.append(('tiny_positive_variance',tiny))
    I=[[int(a==b) for b in range(6)] for a in range(6)];Q=[[int(a==b)/8 for b in range(6)] for a in range(6)]
    out.append(('maximum_dimensions_batch',make(F=I,Q=Q,H=I[:3],R=(.5,1,2),x=[[a/8 for a in range(6)] for _ in range(64)],P=[I for _ in range(64)],u=[[0]*6 for _ in range(64)],y=[[1,2,3] for _ in range(64)])))
    out.append(('correlated_prior_process',make(F=((1,.5),(0,1)),Q=((.5,.125),(.125,.25)),H=((1,0),),R=(.25,),x=((0,1),),P=(((2,.5),(.5,1)),),u=((0,0),),y=((1,),))))
    return out
