"""Analytic Poisson/gain and common-mode addition/cancellation vectors."""
import copy
import random
from .space_statistics_vectors import hx,payload
GOLDEN={
 65:(payload(signal=hx([12,-1,16,99,0]),background_variance=hx([1,4,9,4,0]),gain=hx([4,2,0,1,1]),valid=[1,1,1,0,1]),
     [0,int(hx(3),16),int(hx(4),16),int(hx(2),16),int(hx(.25),16),
      0,0,int(hx(4),16),int(hx(2),16),int(hx(.25),16),
      0,0,int(hx(9),16),int(hx(3),16),0x3de38e39,1,0,0,0,0,2,0,0,0,0]),
 66:(payload(flux=hx([[4,8],[4,8]]),weights=hx([[1,1],[1,-1]]),diagonal_variance=hx([[2,2]]*2),factors=hx([[[1,1]]*3]*2)),
     [0,2,int(hx(12),16),int(hx(4),16),int(hx(12),16),int(hx(16),16),int(hx(4),16),int(hx(3),16),
      0,2,int(hx(-4),16),int(hx(4),16),0,int(hx(4),16),int(hx(2),16),int(hx(-2),16)])}


def fixture(op,seed=271828,scale=1):
    rng=random.Random(seed)
    if op==65:
        n=131*scale
        return payload(signal=hx([rng.randrange(-16,128)/8 for _ in range(n)]),background_variance=hx([rng.randrange(1,65)/8 for _ in range(n)]),gain=hx([rng.randrange(0,17)/4 for _ in range(n)]),valid=[int(rng.random()>.1) for _ in range(n)])
    if op==66:
        b,n,k=7*scale,19,3
        return payload(flux=hx([[rng.randrange(-32,65)/8 for _ in range(n)] for _ in range(b)]),weights=hx([[rng.randrange(-8,9)/8 for _ in range(n)] for _ in range(b)]),diagonal_variance=hx([[rng.randrange(1,17)/4 for _ in range(n)] for _ in range(b)]),factors=hx([[[rng.randrange(-8,9)/8 for _ in range(n)] for _ in range(k)] for _ in range(b)]))
    raise ValueError(op)


def edges(op):
    if op==65:
        out=[]
        for name,key,value in [('all_masked','valid',[0]*5),('zero_gain','gain',hx([0]*5)),('all_negative','signal',hx([-1]*5)),('no_background','background_variance',hx([0]*5))]:
            p=copy.deepcopy(GOLDEN[65][0]);p[key]=value;out.append((name,p))
        out.append(('source_underflow_to_zero',payload(signal=['00000001'],background_variance=['00000000'],gain=hx([2]),valid=[1])))
        out.append(('small_invertible_variance',payload(signal=hx([0]),background_variance=['00200001'],gain=hx([0]),valid=[1])))
        out.append(('largest_variance',payload(signal=hx([0]),background_variance=['7f7fffff'],gain=hx([0]),valid=[1])))
        out.append(('signed_zeros',payload(signal=['80000000'],background_variance=['80000000'],gain=['80000000'],valid=[1])))
        out.append(('masked_overflow_not_evaluated',payload(signal=['7f7fffff'],background_variance=['7f7fffff'],gain=['00000001'],valid=[0])))
        out.append(('maximum_pixels',payload(signal=hx([0]*65536),background_variance=hx([4]*65536),gain=hx([1]*65536),valid=[1]*65536)))
        return out
    if op!=66:raise ValueError(op)
    out=[]
    for name,key,value in [('no_active_weights','weights',hx([[0,0]]*2)),('diagonal_only','factors',[[],[]]),('correlated_only','diagonal_variance',hx([[0,0]]*2)),('fractional_weights','weights',hx([[.5,.5],[.5,-.5]]))]:
        p=copy.deepcopy(GOLDEN[66][0]);p[key]=value;out.append((name,p))
    out.append(('zero_covariance',payload(flux=hx([[4,8]]),weights=hx([[1,-1]]),diagonal_variance=hx([[0,0]]),factors=[[]])))
    out.append(('negative_covariance',payload(flux=hx([[4,8]]),weights=hx([[1,1]]),diagonal_variance=hx([[2,2]]),factors=hx([[[1,-1]]]))))
    out.append(('variance_underflow',payload(flux=hx([[0]]),weights=[['00000001']],diagonal_variance=hx([[1]]),factors=[[]])))
    out.append(('tiny_positive_variance',payload(flux=hx([[0]]),weights=hx([[1]]),diagonal_variance=[['00000001']],factors=[[]])))
    out.append(('signed_zero_weights',payload(flux=hx([[4,8]]),weights=[['80000000','00000000']],diagonal_variance=hx([[1,1]]),factors=[[]])))
    out.append(('maximum_rows_width',payload(flux=hx([[1]*256]*128),weights=hx([[1]*256]*128),diagonal_variance=hx([[1]*256]*128),factors=[[] for _ in range(128)])))
    out.append(('maximum_factors',payload(flux=hx([[2,4]]),weights=hx([[1,1]]),diagonal_variance=hx([[0,0]]),factors=hx([[[1,-1]]*15+[[1,1]]]))))
    out.append(('maximum_work',payload(flux=hx([[1]*256]*64),weights=hx([[1]*256]*64),diagonal_variance=hx([[1]*256]*64),factors=hx([[[0]*256]*15]*64))))
    return out
