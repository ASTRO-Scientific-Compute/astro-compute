"""Analytic vectors fixed before GPU implementation, plus adversarial inputs."""
import copy
import random
from .space_statistics_vectors import hx, payload

GOLDEN={
 51:(payload(mesh=hx([[0,2],[4,6]]),points=hx([[0,0],[.5,.5],[1,1],[-1,.5],[.5,2]])),[int(x,16) for x in hx([0,3,6,2,5])]),
 52:(dict(encoding='uint32',component_ids=[10,2,7,30],pixel_counts=[2,3,1,1],edges=[[0,1],[1,2]],npixels=3),[2,6,2,2,6,2,2,6,2,30,1,0]),
 53:(payload(image=hx([[3,3],[1,-1]]),background=hx([[1,1],[1,1]]),variance=hx([[1,1],[1,1]]),labels=[[5,5],[5,9]],valid=[[1,1],[1,1]],source_ids=[5,9,8]),
     [0,3]+[int(x,16) for x in hx([4,3,4,.5,0,.25,0,0])]+[2,1]+[int(x,16) for x in hx([-2,1,0,0,0,0,0,0])]+[1,0,0,0,0,0,0,0,0,0]),
}


def fixture(op,seed=271828,scale=1):
    r=random.Random(seed)
    if op==51:
        return payload(mesh=hx([[r.randrange(-64,129)/8 for x in range(9)] for y in range(7)]),points=hx([[r.randrange(-8,81)/8,r.randrange(-8,65)/8] for _ in range(71*scale)]))
    if op==52:
        n=37*scale
        return dict(encoding='uint32',component_ids=r.sample(range(1,100000),n),pixel_counts=[r.randrange(1,21) for _ in range(n)],edges=[[r.randrange(n-3),r.randrange(n-3)] for _ in range(n)],npixels=12)
    if op==53:
        h,w=9,13
        return payload(image=hx([[r.randrange(-8,129)/8 for x in range(w)] for y in range(h)]),background=hx([[r.randrange(0,17)/8 for x in range(w)] for y in range(h)]),variance=hx([[r.randrange(0,17)/16 for x in range(w)] for y in range(h)]),labels=[[r.randrange(0,8) for x in range(w)] for y in range(h)],valid=[[int(r.random()>.15) for x in range(w)] for y in range(h)],source_ids=list(range(1,9)))
    raise ValueError(op)


def edges(op):
    g=copy.deepcopy(GOLDEN[op][0]); cases=[]
    if op==51:
        for name,mesh,points in [('flat',[[3,3],[3,3]],[[-100,100],[.25,.75]]),('maximum_mesh',[[x+2*y for x in range(64)] for y in range(64)],[[63,63],[62.5,62.5],[1,1]]),('linear_plane',[[-4,0,4],[2,6,10]],[[.25,.75],[1.5,.25]])]:
            cases.append((name,payload(mesh=hx(mesh),points=hx(points))))
        cases.append(('subnormal_zeros',payload(mesh=[['00000001','80000001'],['80000000','00000000']],points=hx([[0,0],[.5,.5],[1,0]]))))
        cases.append(('extreme_clamping',payload(mesh=hx([[1,2],[3,4]]),points=[['ff7fffff','7f7fffff'],['7f7fffff','ff7fffff']])) )
    elif op==52:
        for name,ids,counts,links,minimum in [('isolated',[9,1],[1,2],[],1),('duplicates_self',[7,2,4],[1,1,1],[[0,1],[1,0],[0,0],[1,2],[2,2]],3),('max_chain',list(range(512,0,-1)),[1]*512,[[j,j+1] for j in range(511)],512),('uint32_max',[0xffffffff],[0xffffffff],[],0xffffffff),('all_rejected',[9,4],[1,1],[[0,1]],3)]:
            cases.append((name,dict(encoding='uint32',component_ids=ids,pixel_counts=counts,edges=links,npixels=minimum)))
    elif op==53:
        p=copy.deepcopy(g);p['valid']=[[0,0],[0,0]];cases.append(('all_masked',p))
        p=copy.deepcopy(g);p['image']=hx([[1,1],[1,1]]);cases.append(('zero_residual',p))
        p=copy.deepcopy(g);p['image']=hx([[-1,-2],[-3,-4]]);cases.append(('negative_flux',p))
        p=copy.deepcopy(g);p['labels']=[[0xffffffff,0],[0,0]];p['source_ids']=[0xffffffff];cases.append(('single_pixel_max_label',p))
        p=copy.deepcopy(g);p['image']=[['00000001','80000000'],['80000001','00000000']];p['background']=hx([[0,0],[0,0]]);cases.append(('subnormal',p))
        p=payload(image=hx([[2]*128 for _ in range(128)]),background=hx([[1]*128 for _ in range(128)]),variance=hx([[0]*128 for _ in range(128)]),labels=[[1]*128 for _ in range(128)],valid=[[1]*128 for _ in range(128)],source_ids=[1,2]);cases.append(('maximum_image',p))
    return cases
