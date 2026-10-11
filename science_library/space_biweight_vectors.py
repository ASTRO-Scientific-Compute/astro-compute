"""Analytic c=2 symmetric result: location=0, midvariance=9, scale=3."""
import copy
import random
from .space_statistics_vectors import hx,payload

GOLDEN={63:(payload(samples=hx([[-1,-1,1,1],[9,9,11,11]]),valid=[[1]*4]*2,c_location=hx(2),c_variance=hx(2)),
            [0,4,0,int(hx(1),16),0,int(hx(9),16),int(hx(3),16),4,4,
             0,4,int(hx(10),16),int(hx(1),16),int(hx(10),16),int(hx(9),16),int(hx(3),16),4,4])}


def fixture(op,seed=271828,scale=1):
    if op!=63:raise ValueError(op)
    rng=random.Random(seed)
    rows=[[rng.randrange(-32,33)/8 for _ in range(45)]+[-40,40] for _ in range(7*scale)]
    return payload(samples=hx(rows),valid=[[int(rng.random()>.1) for _ in row] for row in rows],c_location=hx(6),c_variance=hx(9))


def edges(op):
    if op!=63:raise ValueError(op)
    g=copy.deepcopy(GOLDEN[63][0]);out=[]
    for name,key,value in [('empty_mask','valid',[[0]*4]*2),('zero_mad','samples',hx([[7]*4]*2)),
                           ('strict_cutoff_all_excluded','c_location',hx(1)),('variance_denominator_zero','c_variance',hx(1))]:
        p=copy.deepcopy(g);p[key]=value;out.append((name,p))
    out.append(('single_valid',payload(samples=hx([[3,9]]),valid=[[1,0]],c_location=hx(6),c_variance=hx(9))))
    out.append(('symmetric_outliers',payload(samples=hx([[-1,1]*7+[-100,100]]),valid=[[1]*16],c_location=hx(6),c_variance=hx(9))))
    out.append(('cutoff_equality',payload(samples=hx([[-2,-1,-1,1,1,2]]),valid=[[1]*6],c_location=hx(2),c_variance=hx(2))))
    out.append(('maximum_width',payload(samples=hx([[j%17-8 for j in range(256)]]),valid=[[1]*256],c_location=hx(6),c_variance=hx(9))))
    out.append(('maximum_rows',payload(samples=hx([[-1,1]]*128),valid=[[1,1]]*128,c_location=hx(2),c_variance=hx(2))))
    out.append(('subnormal_mad_underflow',payload(samples=[['80000001','00000001']],valid=[[1,1]],c_location=hx(2),c_variance=hx(2))))
    out.append(('signed_zeros',payload(samples=[['80000000','00000000']],valid=[[1,1]],c_location=hx(6),c_variance=hx(9))))
    return out
