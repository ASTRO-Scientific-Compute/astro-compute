"""Analytic shortest-half examples fixed before GPU measurements."""
import random
from .space_statistics_vectors import hx,payload

GOLDEN={64:(payload(samples=hx([[100,3,2,1,0,101],[-10,8,9,10,11,12]]),valid=[[1]*6]*2),
           [0,6,int(hx(1),16),0,int(hx(2),16),int(hx(2),16),3,1,0,
            0,6,int(hx(9),16),int(hx(8),16),int(hx(10),16),int(hx(2),16),3,1,1])}


def fixture(op,seed=271828,scale=1):
    if op!=64:raise ValueError(op)
    rng=random.Random(seed);rows=[[rng.randrange(-64,65)/8 for _ in range(43)]+[100,120,150,200] for _ in range(9*scale)]
    return payload(samples=hx(rows),valid=[[int(rng.random()>.1) for _ in row] for row in rows])


def edges(op):
    if op!=64:raise ValueError(op)
    out=[]
    for name,values in [('one',[3]),('two',[-2,4]),('three_left',[0,2,8]),('three_right',[0,6,8]),('three_tie',[0,4,8]),
                        ('constant',[7]*17),('odd_recursion',[0,2,5,9,20,50,100]),('even_recursion',list(range(32))),
                        ('positive_contamination',[9,10,10,10,10,11,100,200,300]),('negative_contamination',[-300,-200,-100,9,10,10,10,10,11]),
                        ('maximum_width',list(range(256)))]:
        out.append((name,payload(samples=hx([values]),valid=[[1]*len(values)])))
    out.append(('empty_mask',payload(samples=hx([[9,10,20]]),valid=[[0]*3])))
    out.append(('masked_contamination',payload(samples=hx([[100,2,4,1000]]),valid=[[0,1,1,0]])))
    out.append(('signed_zeros',payload(samples=[['80000000','00000000']]*2,valid=[[1,1]]*2)))
    out.append(('subnormal_half_rounding',payload(samples=[['00000001','00000003']],valid=[[1,1]])))
    out.append(('rounded_width_tie',payload(samples=[['80000001','3f800000','40000000','40800000']],valid=[[1]*4])))
    out.append(('maximum_rows',payload(samples=hx([[0,2,8]]*128),valid=[[1]*3]*128)))
    out.append(('constant_subnormal',payload(samples=[['00000001']*4,['80000001']*4],valid=[[1]*4]*2)))
    out.append(('maximum_finite_constant',payload(samples=[['7f7fffff']*2,['ff7fffff']*2],valid=[[1,1]]*2)))
    rng=random.Random(240064);pairs=[]
    for _ in range(128):
        exponent=rng.randrange(0,255);a=(exponent<<23)|rng.randrange(1<<23);b=(exponent<<23)|rng.randrange(1<<23)
        sign=rng.randrange(2)<<31;pairs.append([f'{a|sign:08x}',f'{b|sign:08x}'])
    out.append(('mean_rounding_pairs',payload(samples=pairs,valid=[[1,1]]*128)))
    return out
