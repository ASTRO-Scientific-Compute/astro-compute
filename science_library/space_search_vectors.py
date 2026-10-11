"""Analytic expectations and deterministic algorithm tests, never winner seeds."""
import copy
import random
from .f32 import hex32


def hx(obj):
    return [hx(x) for x in obj] if isinstance(obj,list) else hex32(obj)


def payload(**kw):return dict(encoding='binary32-hex',**kw)

GOLDEN={
 39:(payload(samples=hx([[0,2,1],[1,1,1],[2,0,1],[3,1,1]]),frequencies=hx([0.25])),[0,0x3f800000,0x3f800000,0x3f800000,0,0]),
 40:(payload(times=[0,1,2,3],flux=hx([0,0,1,1]),periods=[4],bins=4,min_width=1,max_width=2),[0,0,2,0x3f800000,0x3f800000,0x3f800000]),
 41:(payload(image=hx([[1,3,2]]),valid=[[1,1,1]],threshold=hex32(1),radius=1),[0,1,0]),
 42:(payload(flux=hx([[2,4]]),weights=hx([[1,1]]),templates=hx([[1,2],[0,0],[-1,-2]])),[0,0x40000000,0,1,0,0,0,0,0x41a00000]),
 43:(payload(coordinates=hx([[2,0,0],[2,0.25,0],[2,0,0.25],[2,-0.25,0]])),[0x40000000,0,0,0,0,0x40000000,0,0x40000000,0,0,0,0xc0000000]),
 44:(payload(states=hx([[1,0,0,0,1,0]]),mu=hex32(0),dt=hex32(1),steps=2),[0x3f800000,0,0,0,0x3f800000,0,0x3f800000,0x3f800000,0,0,0x3f800000,0,0x3f800000,0x40000000,0,0,0x3f800000,0]),
}


def fixture(op,seed=271828,scale=1):
    r=random.Random(seed)
    if op==39:
        return payload(samples=hx([[j/8+r.randrange(4)/32,r.randrange(-64,65)/16,r.randrange(1,9)/4] for j in range(31)]),frequencies=hx([(j+1)/16 for j in range(7*scale)]))
    if op==40:
        t=[r.randrange(256) for _ in range(63)];y=[1-(0.25 if x%32<8 else 0)+r.randrange(-4,5)/256 for x in t]
        return payload(times=t,flux=hx(y),periods=list(range(24,24+7*scale)),bins=8,min_width=1,max_width=3)
    if op==41:
        return payload(image=hx([[r.randrange(-16,65)/8 for _ in range(19)] for _ in range(13*scale)]),valid=[[int(r.random()>0.12) for _ in range(19)] for _ in range(13*scale)],threshold=hex32(2),radius=2)
    if op==42:
        return payload(flux=hx([[r.randrange(-16,65)/8 for _ in range(7)] for _ in range(5*scale)]),weights=hx([[r.randrange(9)/4 for _ in range(7)] for _ in range(5*scale)]),templates=hx([[r.randrange(33)/8 for _ in range(7)] for _ in range(9)]))
    if op==43:
        return payload(coordinates=hx([[r.randrange(65)/4,r.randrange(-128,129)/512,r.randrange(-4096,4097)/1024] for _ in range(23*scale)]))
    if op==44:
        return payload(states=hx([[1+r.randrange(17)/16,r.randrange(-8,9)/64,r.randrange(-8,9)/64,r.randrange(-8,9)/64,0.75+r.randrange(9)/32,0] for _ in range(3*scale)]),mu=hex32(1),dt=hex32(1/64),steps=4)
    raise ValueError(op)


def edges(op):
    g=copy.deepcopy(GOLDEN[op][0]);cases=[]
    if op==39:
        d=copy.deepcopy(g);d['samples']=hx([[j,2,1] for j in range(4)]);cases.append(('constant_signal',d))
        d=copy.deepcopy(g);d['samples']=hx([[j,j,0] for j in range(4)]);cases.append(('zero_weights',d))
        d=copy.deepcopy(g);d['frequencies']=hx([1,0.5,0.25,0.25]);cases.append(('singular_duplicate_frequencies',d))
        d=fixture(op);d['samples']=[['80000000',row[1],row[2]] for row in d['samples']];cases.append(('coincident_signedzero_times',d))
        d=fixture(op);d['samples']=[hx([-j/8,float(j%3),1]) for j in range(31)];cases.append(('negative_times',d))
    elif op==40:
        d=copy.deepcopy(g);d['flux']=hx([1,1,1,1]);cases.append(('constant_flux',d))
        d=copy.deepcopy(g);d['times']=[0,0,0,0];cases.append(('empty_outside_windows',d))
        d=copy.deepcopy(g);d['flux']=hx([0,1,1,0]);cases.append(('wrapped_transit',d))
        d=copy.deepcopy(g);d['times']=[10000000,9999999,1,0];d['periods']=[1,1000000,4,4];cases.append(('large_ticks_duplicate_periods',d))
        d=copy.deepcopy(g);d['flux']=['80000000','00000000','00000001','00000001'];cases.append(('subnormal_score_underflow',d))
    elif op==41:
        for name,img,mask,threshold in [('tied_plateau',[[3,3,3]],[[1,1,1]],2),('masked_bright',[[1,9,2]],[[1,0,1]],0),('negative_border',[[-1]],[[1]],-2),('threshold_equality',[[1]],[[1]],1),('all_masked',[[10]],[[0]],1)]:
            cases.append((name,payload(image=hx(img),valid=mask,threshold=hex32(threshold),radius=4)))
    elif op==42:
        for name,wt in [('zero_weight',[[0,0]]),('masked_band',[[1,0]])]:
            d=copy.deepcopy(g);d['weights']=hx(wt);cases.append((name,d))
        d=copy.deepcopy(g);d['flux']=hx([[-2,-4]]);cases.append(('negative_flux',d))
        d=copy.deepcopy(g);d['templates']=hx([[1,2],[1,2]]);cases.append(('duplicate_templates',d))
    elif op==43:
        cases.append(('axes_wrap_and_zero',payload(coordinates=hx([[0,0.125,-0.125],[1,0,-65536],[1,0,65536],[1,0,-0.75],[1,0,0.5],[1,0,-0.5]]))))
        cases.append(('subnormal_radius',payload(coordinates=[['00000001','00000000','00000000'],['80000000','80000000','80000000']])) )
        cases.append(('adjacent_quadrant',payload(coordinates=[['3f800000','00000000',x] for x in ['3e7fffff','3e800000','3e800001','be7fffff','be800001']])) )
    elif op==44:
        d=copy.deepcopy(g);d['steps']=64;d['dt']=hex32(1/16);cases.append(('maximum_steps_ballistic',d))
        d=copy.deepcopy(g);d['states']=hx([[0,0,0,0,0,0]]);cases.append(('zero_force_stationary_origin',d))
        d=fixture(op);d['states']=hx([[1,0,0,0,1,0],[-1,0,0,0,-1,0]]);d['steps']=16;cases.append(('symmetric_circular_arcs',d))
    return cases
