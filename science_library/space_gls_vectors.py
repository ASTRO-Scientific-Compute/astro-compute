"""Analytic G4/L2 common-mode examples and numerical rejection probes."""
import copy,random
from .space_statistics_vectors import hx,payload
GOLDEN={67:(payload(flux=hx([[2,3,4],[4,6,8]]),template=hx([[1,1,1]]*2),diagonal_variance=hx([[1,1,1]]*2),factors=hx([[[1,1,1]]]*2)),
 [0,int(hx(3),16),0x3faaaaab,int(hx(2),16),int(hx(.75),16),1,
  0,int(hx(6),16),0x3faaaaab,int(hx(8),16),int(hx(.75),16),1])}


def fixture(op,seed=271828,scale=1):
    if op!=67:raise ValueError(op)
    rng=random.Random(seed);b,n,k=5*scale,13,3
    return payload(flux=hx([[rng.randrange(-16,65)/8 for _ in range(n)] for _ in range(b)]),template=hx([[rng.randrange(1,9)/8 for _ in range(n)] for _ in range(b)]),diagonal_variance=hx([[rng.randrange(4,17)/4 for _ in range(n)] for _ in range(b)]),factors=hx([[[rng.randrange(-4,5)/8 for _ in range(n)] for _ in range(k)] for _ in range(b)]))


def edges(op):
    if op!=67:raise ValueError(op)
    out=[]
    for name,key,value in [('diagonal_only','factors',[[],[]]),('zero_template','template',hx([[0,0,0]]*2)),('negative_amplitude','flux',hx([[-2,-3,-4],[-4,-6,-8]])),('redundant_factors','factors',hx([[[1,1,1]]*2]*2)),('rejected_pivot','factors',hx([[[65536,65536,65536]]*2]*2))]:
        p=copy.deepcopy(GOLDEN[67][0]);p[key]=value;out.append((name,p))
    out.append(('subnormal_flux',payload(flux=[['00000001','80000001']],template=hx([[1,1]]),diagonal_variance=hx([[1,1]]),factors=[[]])))
    out.append(('underflow_information',payload(flux=hx([[0]]),template=[['00000001']],diagonal_variance=hx([[1]]),factors=[[]])))
    out.append(('signed_zero_template',payload(flux=hx([[2,3]]),template=[['80000000','00000000']],diagonal_variance=hx([[1,1]]),factors=[[]])))
    out.append(('one_pixel_correlated',payload(flux=hx([[6]]),template=hx([[2]]),diagonal_variance=hx([[1]]),factors=hx([[[1],[1],[1]]]))))
    out.append(('perfect_fit',payload(flux=hx([[3,6,3]]),template=hx([[1,2,1]]),diagonal_variance=hx([[1,2,4]]),factors=hx([[[.25,.5,.25]]]))))
    out.append(('maximum_rows_width',payload(flux=hx([[1]*128]*64),template=hx([[1]*128]*64),diagonal_variance=hx([[1]*128]*64),factors=[[] for _ in range(64)])))
    out.append(('maximum_factors',payload(flux=hx([[1,2]]),template=hx([[1,1]]),diagonal_variance=hx([[1,1]]),factors=hx([[[0,0]]*8]))))
    out.append(('maximum_work',payload(flux=hx([[1]*128]*64),template=hx([[1]*128]*64),diagonal_variance=hx([[1]*128]*64),factors=hx([[[0]*128]*3]*64))))
    return out
