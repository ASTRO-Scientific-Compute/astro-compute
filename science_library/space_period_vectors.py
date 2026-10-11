"""Analytic golden vectors and bounded adversarial period-search fixtures."""
import copy
import random
from .space_statistics_vectors import hx,payload
from .f32 import hex32

GOLDEN={
 57:(payload(samples=hx([[j,[2,1,0,1][j%4],1] for j in range(8)]),frequencies=hx([.125,.25]),harmonics=2),
     [0]+[int(x,16) for x in hx([1,0,1,0,0,1,0])]+[2,0,0,0,0,0,0,0]),
 58:(payload(times=[0,1,2,3,4],flux=hx([0,2,0,2,0]),periods=[2],bins=2),
     [0,0,0x3f99999a,0,2,3]),
}
# PDM analytic variance: sum((y-.8)^2)/(5-1)=1.2. Its declared RN32
# two-pass graph is checked explicitly before any GPU implementation.


def fixture(op,seed=271828,scale=1):
    r=random.Random(seed)
    if op==57:return payload(samples=hx([[j/8+r.randrange(4)/32,r.randrange(-64,65)/16,r.randrange(1,9)/4] for j in range(31)]),frequencies=hx([(j+2)/8 for j in range(7*scale)]),harmonics=3)
    if op==58:
        times=[r.randrange(256) for _ in range(97)];flux=[1-(.5 if t%32<8 else 0)+r.randrange(-4,5)/128 for t in times]
        return payload(times=times,flux=hx(flux),periods=list(range(27,27+9*scale)),bins=8)
    raise ValueError(op)


def edges(op):
    g=copy.deepcopy(GOLDEN[op][0]);cases=[]
    if op==57:
        p=copy.deepcopy(g);p['samples']=hx([[j,2,1] for j in range(8)]);cases.append(('constant_signal',p))
        p=copy.deepcopy(g);p['samples']=hx([[j,j,0] for j in range(8)]);cases.append(('zero_weights',p))
        p=copy.deepcopy(g);p['samples']=hx([[0,j,1] for j in range(8)]);cases.append(('coincident_times_rank_failure',p))
        p=fixture(op);p['samples']=hx([[-j/8,float(j%5),1] for j in range(31)]);cases.append(('negative_times',p))
        p=fixture(op);p['harmonics']=4;cases.append(('four_harmonics',p))
        p=copy.deepcopy(g);p['frequencies']=hx([.125,.125]);cases.append(('duplicate_frequencies',p))
        p=copy.deepcopy(g);p['samples']=[['80000000',row[1],row[2]] for row in p['samples']];cases.append(('signed_zero_time',p))
        p=copy.deepcopy(g);p['samples']=[[row[0],'00000001',row[2]] for row in p['samples']];cases.append(('subnormal_constant',p))
        p=payload(samples=hx([[j/16,j%7,1] for j in range(256)]),frequencies=hx([.5]),harmonics=4);cases.append(('maximum_samples',p))
    elif op==58:
        for name,times,flux,periods,bins in [('constant_flux',list(range(5)),[1]*5,[2],2),('single_occupied',[0]*5,[0,1,2,3,4],[4],4),('no_degrees',list(range(4)),[0,1,2,3],[4],4),('singleton_bins',[0,1,2,2],[0,2,1,3],[4],4),('large_ticks',[10000000,9999999,0,1,2],[1,0,1,0,1],[1,2,1000000,2],64),('maximum_samples',list(range(4096)),[j%4 for j in range(4096)],[32],64)]:
            cases.append((name,payload(times=times,flux=hx(flux),periods=periods,bins=bins)))
        p=copy.deepcopy(g);p['flux']=['80000000','00000001','80000001','00000001','00000000'];cases.append(('variance_underflow',p))
    return cases
