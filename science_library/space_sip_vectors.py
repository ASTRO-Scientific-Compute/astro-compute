"""Bounded isolated terms, asymmetric polynomials and supplied distortion models."""
import random
from fractions import Fraction
from . import f32 as f
from .space_statistics_vectors import hx
from .space_sip_reference import TAGS,terms,coefficient_limit


def make(offsets=None,ao=2,bo=2,a=None,b=None):
    if offsets is None:offsets=[[16,8]]
    if a is None:a=[0]*len(terms(ao));a[-1]=2**-12
    if b is None:b=[0]*len(terms(bo));b[1]=-2**-13
    return dict(**TAGS,model_id='supplied-bounded-sip-model',a_order=ao,b_order=bo,a_coefficients=hx(a),b_coefficients=hx(b),offsets=hx(offsets))


GOLDEN={81:(make(),[f.parse(x) for x in hx([16.0625,7.984375,.0625,-.015625])])}


def fixture(op=81,seed=271828,scale=1):
    if op!=81:raise ValueError(op)
    rng=random.Random(seed)
    coefficients=[[float(coefficient_limit(d))*rng.randrange(-16,17)/16 for d,_,_ in terms(order)] for order in (5,4)]
    return make([[rng.randrange(-8192,8193)/8,rng.randrange(-8192,8193)/8] for _ in range(min(17*scale,4096))],5,4,*coefficients)


def spitzer_example():
    # Supplied published numerical model, not an observational calibration reproduction.
    aa={(0,2):'9.0886e-6',(0,3):'4.8066e-9',(1,1):'4.8146e-5',(1,2):'-1.7096e-7',(2,0):'2.82e-5',(2,1):'3.3336e-8',(3,0):'-1.8684e-7'}
    bb={(0,2):'4.1248e-5',(0,3):'-1.9016e-7',(1,1):'1.4761e-5',(1,2):'2.1973e-8',(2,0):'-6.4708e-6',(2,1):'-1.8188e-7',(3,0):'1.0084e-10'}
    job=make([[u,v] for u in (-128,-64,0,64,128) for v in (-128,-64,0,64,128)],3,3,a=[0]*7,b=[0]*7)
    for key,table in (('a_coefficients',aa),('b_coefficients',bb)):
        job[key]=[f'{f.rounded(Fraction(table[(p,q)])):08x}' for _,p,q in terms(3)]
    job['model_id']='published-Spitzer-IRAC4-numerical-example';return job


def edges(op=81):
    if op!=81:raise ValueError(op)
    square=[[u,v] for u in (-1024,-1,0,1,1024) for v in (-1024,-1,0,1,1024)]
    data=[('zero_distortion',make(square,5,3,a=[0]*18,b=[0]*7)),('axes_center',make([[0,0],[0,16],[16,0],[-16,0],[0,-16]])),
          ('pure_quadratic',make(square,a=[0,0,2**-16],b=[-2**-17,0,0])),('cross_term',make(square,a=[0,2**-16,0],b=[0,-2**-16,0]))]
    for name,ao,bo in [('odd_cubic',3,3),('quintic_mix',5,5),('asymmetric2_5',2,5),('asymmetric5_2',5,2)]:
        a=[float(coefficient_limit(d))*(-1 if i%2 else 1)/4 for i,(d,_,_) in enumerate(terms(ao))]
        b=[float(coefficient_limit(d))*(1 if i%2 else -1)/8 for i,(d,_,_) in enumerate(terms(bo))]
        data.append((name,make(square,ao,bo,a,b)))
    a=[float(coefficient_limit(d)) for d,_,_ in terms(5)]
    data.append(('coefficient_boundaries',make(square,5,5,a,[-v for v in a])))
    a=[v*(-1 if i%2 else 1) for i,v in enumerate(a)]
    data.append(('cancellation',make([[1024,1024],[-1024,-1024],[16,16]],5,5,a,[-v for v in a])))
    p=make([[0,0],[1,1],[0,0]],a=[0,0,0],b=[0,0,0]);p['offsets'][0]=['00000001','80000001'];p['a_coefficients'][0]='00000001';p['b_coefficients'][2]='80000001';data.append(('subnormal_values',p))
    p=make([[0,0]],a=[0,0,0],b=[0,0,0]);p['offsets'][0]=['80000000','80000000'];p['a_coefficients'][0]='80000000';data.append(('signed_zero',p))
    data.append(('spitzer_numerical_example',spitzer_example()))
    p=fixture();p['offsets']=(p['offsets']*241)[:4096];data.append(('maximum_records',p))
    return data
