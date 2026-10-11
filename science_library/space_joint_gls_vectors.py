"""Overlapping-column analytic fit with exactly representable Cholesky factors."""
import copy,random
from .space_statistics_vectors import hx,payload
GOLDEN={68:(payload(flux=hx([[6,4,0,2],[-6,-4,0,-2]]),templates=hx([[[1,1,0,0],[1,1,0,1]]]*2),diagonal_variance=hx([[1]*4]*2),factors=hx([[[1,1,1,0]]]*2)),
 [0,*[int(hx(v),16) for v in [3,2,2,-1,-1,1,2]],0,*[int(hx(v),16) for v in [-3,-2,2,-1,-1,1,2]]])}


def fixture(op,seed=271828,scale=1):
    if op!=68:raise ValueError(op)
    rng=random.Random(seed);b,n,m,k=5*scale,13,3,2
    return payload(flux=hx([[rng.randrange(-16,65)/8 for _ in range(n)] for _ in range(b)]),templates=hx([[[rng.randrange(-4,9)/8+(2 if i==a else 0) for i in range(n)] for a in range(m)] for _ in range(b)]),diagonal_variance=hx([[rng.randrange(4,17)/4 for _ in range(n)] for _ in range(b)]),factors=hx([[[rng.randrange(-4,5)/8 for _ in range(n)] for _ in range(k)] for _ in range(b)]))


def edges(op):
    if op!=68:raise ValueError(op)
    out=[]
    for name,key,value in [('diagonal_only','factors',[[],[]]),('zero_templates','templates',hx([[[0]*4]*2]*2)),('duplicate_templates','templates',hx([[[1,1,0,0]]*2]*2)),('redundant_factors','factors',hx([[[1,1,1,0]]*2]*2)),('rejected_factor_pivot','factors',hx([[[65536]*4]*2]*2)),('zero_flux','flux',hx([[0]*4]*2))]:
        p=copy.deepcopy(GOLDEN[68][0]);p[key]=value;out.append((name,p))
    identity=payload(flux=[['00000001','80000001']],templates=hx([[[1,0],[0,1]]]),diagonal_variance=hx([[1,1]]),factors=[[]])
    out.append(('subnormal_signed_flux',identity))
    p=copy.deepcopy(identity);p['flux']=[['80000000','00000000']];out.append(('signed_zero_flux',p))
    p=copy.deepcopy(identity);p['templates']=[[['00000001','00000000'],['00000000','00000001']]];out.append(('underflow_information',p))
    p=copy.deepcopy(identity);p['templates']=hx([[[1,0],[1,1/1024]]]);out.append(('near_degenerate_templates',p))
    p=copy.deepcopy(GOLDEN[68][0]);p['flux']=hx([[5,5,0,2],[-5,-5,0,-2]]);out.append(('perfect_fit',p))
    out.append(('maximum_rows_width',payload(flux=hx([[1]*64]*32),templates=hx([[[int(i==j) for i in range(64)] for j in range(2)]]*32),diagonal_variance=hx([[1]*64]*32),factors=[[] for _ in range(32)])))
    out.append(('maximum_templates_factors',payload(flux=hx([[1]*5]),templates=hx([[[int(i==j) for i in range(5)] for j in range(5)]]),diagonal_variance=hx([[1]*5]),factors=hx([[[0]*5]*4]))))
    out.append(('maximum_work',payload(flux=hx([[1]*64]*32),templates=hx([[[int(i==j) for i in range(64)] for j in range(4)]]*32),diagonal_variance=hx([[1]*64]*32),factors=hx([[[0]*64]*3]*32))))
    return out
