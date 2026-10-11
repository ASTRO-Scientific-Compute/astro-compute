"""Analytic geometry, edge cases and explicitly labelled commissioning fixtures."""
import random
from fractions import Fraction
from . import f32 as f
from .triangle_reference import MISS


def job(triangles,rays,frames=None):
    d=dict(encoding='binary32-hex',triangles=[[[f.hex32(v) for v in p] for p in t] for t in triangles],rays=[dict(origin=[f.hex32(x) for x in o],direction=[f.hex32(x) for x in r]) for o,r in rays])
    if frames is not None:d['frames']=frames
    return d

T=[[[0,0,2],[2,0,2],[0,2,2]]]
R=[([.5,.5,0],[0,0,1]),([3,3,0],[0,0,1]),([1,1,0],[0,0,1]),([.5,.5,3],[0,0,-1])]
GOLDEN={37:(job(T,R),[f.TWO,MISS,f.TWO,f.ONE]),
38:(job(T,R[:2],[0,256,768,0]),[f.TWO,MISS,f.add(f.TWO,f.rounded(Fraction(1,400))),MISS,f.sub(f.TWO,f.rounded(Fraction(1,400))),MISS,f.TWO,MISS])}


def fixture(op,seed=271828,scale=1):
    rng=random.Random(seed);triangles=[];rays=[]
    for i in range(12*scale):
        x=(i%8)*2;y=(i//8)*2;z=rng.randrange(1,17)/4
        triangles.append([[x,y,z],[x+1,y,z],[x,y+1,z]])
        rays.append(([x+.25,y+.25,0],[0,0,1]))
        rays.append(([x+1.5,y+1.5,0],[0,0,1]))
    return job(triangles,rays,[0,17,91] if op==38 else None)


def edges(op):
    rows=[]
    def add(name,t,r):rows.append((name,job(t,r,[0,256,768,0] if op==38 else None)))
    add('closed_edges_and_vertices',T,[([0,0,0],[0,0,1]),([2,0,0],[0,0,1]),([0,2,0],[0,0,1]),([1,1,0],[0,0,1])])
    add('duplicate_and_reversed',T+[list(reversed(T[0]))]+T,R)
    add('degenerate_and_parallel',[[[0,0,1],[1,0,1],[2,0,1]]],R+[([0,0,0],[1,0,0])])
    add('nearest_and_behind',T+[[[0,0,1],[2,0,1],[0,2,1]],[[0,0,-1],[2,0,-1],[0,2,-1]]],R)
    add('oblique_normalization',T,[([0,0,0],[1,1,4]),([1,1,3],[-1,-1,-4]),([0,0,0],[1,1,1])])
    add('large_and_small_directions',T,[([.5,.5,0],[0,0,65536]),([.5,.5,0],[0,0,1/65536]),([.5,.5,0],[1/65536,0,65536])])
    add('thin_bounded_triangle',[[[0,0,2],[1/65536,0,2],[0,1,2]]],[([0,.5,0],[0,0,1])])
    rng=random.Random(1913);triangles=[];rays=[]
    for k in range(16):
        a,b,c=[[rng.randint(-16,16)/8 for _ in range(3)] for _ in range(3)]
        u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        d=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if not any(d):continue
        point=[(a[j]+b[j]+2*c[j])/4 for j in range(3)]
        triangles.append([a,b,c]);rays.append(([point[j]-d[j] for j in range(3)],d))
    add('general_3d_signed_determinants',triangles,rays)
    add('determinant_cutoff',[[[0,0,1],[1/8192,0,1],[0,1/8192,1]],[[0,0,2],[1/16384,0,2],[0,1/16384,2]]],[([0,0,0],[0,0,1])])
    for delta in (-1,0,1):
        d=job(T,R[:1],[0] if op==38 else None)
        for vertex in d['triangles'][0]:vertex[2]=f'{0x38d1b717+delta:08x}'
        rows.append(('distance_cutoff_'+str(delta),d))
    if op==37:add('large_coordinate',[[[65534,65534,65536],[65536,65534,65536],[65534,65536,65536]]],[([65534,65534,65534],[0,0,1])])
    if op==38:
        d=job(T,R,[0xffffffff,0,256,768,0xffffffff]);rows.append(('frame_wrap_and_revisit',d))
        # Offsets cross the original scene's Z bounds: stale TLAS must not hide hits.
        rows.append(('outside_initial_bvh',job([[[0,0,0],[2,0,0],[0,2,0]]],[([.25,.25,1/1024],[0,0,1])],[0,256,768,256])))
    return rows
