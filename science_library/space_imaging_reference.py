"""Independent Fraction interpolation/moments and breadth-first graph oracle."""
from . import f32 as f
from .reference import Job, MAGIC, encode, integer, array, matrix
from .float_reference import rows
from .space_statistics_reference import rectangular_float, masks


def bilinear(mesh, x, y):
    w, h = len(mesh[0]), len(mesh)
    x = f.rounded(min(max(f.rational(x), 0), w-1))
    y = f.rounded(min(max(f.rational(y), 0), h-1))
    j, k = int(f.rational(x)), int(f.rational(y))
    tx, ty = f.sub(x, f.rounded(j)), f.sub(y, f.rounded(k))
    def lerp(a, b, t):
        return f.add(a, 0) if not t else f.add(f.mul(f.sub(f.ONE, t), a), f.mul(t, b))
    return lerp(lerp(mesh[k][j], mesh[k][min(j+1,w-1)], tx),
                lerp(mesh[min(k+1,h-1)][j], mesh[min(k+1,h-1)][min(j+1,w-1)], tx), ty)


def component_merge(ids, counts, edges, npixels):
    adjacency = [set() for _ in ids]
    for a,b in edges:
        adjacency[a].add(b); adjacency[b].add(a)
    result, visited = [None]*len(ids), set()
    for start in range(len(ids)):
        if start in visited: continue
        queue = [start]; visited.add(start)
        for node in queue:
            for other in adjacency[node]:
                if other not in visited:
                    visited.add(other); queue.append(other)
        root, count = min(ids[j] for j in queue), sum(counts[j] for j in queue)
        for j in queue: result[j] = [root, count, root if count >= npixels else 0]
    return [v for row in result for v in row]


def source_catalog(image, background, variance, labels, valid, ids, width):
    out = []
    for label in ids:
        selected = [(j, f.sub(x, b), v) for j,(x,b,v,l,k) in enumerate(zip(image,background,variance,labels,valid)) if k and l==label]
        flux = f.summation(d for j,d,v in selected)
        var = f.summation(v for j,d,v in selected)
        positive = [(j,d) for j,d,v in selected if f.rational(d)>0]
        weight = f.summation(d for j,d in positive)
        if not weight:
            out.extend([1 if not selected else 2,len(selected),flux,var,0,0,0,0,0,0]); continue
        cx = f.div(f.summation(f.mul(d,f.rounded(j%width)) for j,d in positive),weight)
        cy = f.div(f.summation(f.mul(d,f.rounded(j//width)) for j,d in positive),weight)
        moments = [0,0,0]
        for j,d in positive:
            dx, dy = f.sub(f.rounded(j%width),cx), f.sub(f.rounded(j//width),cy)
            for k,(u,v) in enumerate(((dx,dx),(dx,dy),(dy,dy))):
                moments[k] = f.add(moments[k],f.mul(d,f.mul(u,v)))
        out.extend([0,len(selected),flux,var,weight,cx,cy]+[f.div(v,weight) for v in moments])
    return out


def prepare_space_imaging(wid, op, payload):
    if payload.get('encoding') != ('uint32' if op==52 else 'binary32-hex'):
        raise ValueError('explicit encoding required')
    a,b,c,out = [],[],[],[]
    n=m=w=h=p0=0
    if op==51:
        mesh,w = rectangular_float(payload['mesh'],64,64); h=len(mesh)
        integer(w,2,64,'mesh width'); integer(h,2,64,'mesh height')
        points = rows(payload['points'],2,65536)
        records,ow = len(points),1
        a = [x for row in mesh for x in row]; b = [x for point in points for x in point]
        out = [bilinear(mesh,*point) for point in points]
    elif op==52:
        ids = array(payload['component_ids'],1,0xffffffff,'component_ids',512)
        n = integer(len(ids),1,512,'component count')
        if len(set(ids))!=n: raise ValueError('unique component IDs required')
        counts = array(payload['pixel_counts'],1,0xffffffff,'pixel_counts',512)
        if len(counts)!=n or sum(counts)>0xffffffff: raise ValueError('component counts shape/overflow')
        edges = matrix(payload['edges'],2,0,n-1,'edges',8192)
        p0 = integer(payload['npixels'],1,0xffffffff,'npixels')
        m,records,ow = len(edges),n,3
        a = [x for pair in zip(ids,counts) for x in pair]; b=[x for edge in edges for x in edge]
        out = component_merge(ids,counts,edges,p0)
    elif op==53:
        image,w = rectangular_float(payload['image'],128,128); h=len(image); n=w*h
        bg = rows(payload['background'],w,128); var=rows(payload['variance'],w,128)
        labels = matrix(payload['labels'],w,0,0xffffffff,'labels',128)
        valid = masks(payload['valid'],h,w)
        if any(len(x)!=h for x in (bg,var,labels)): raise ValueError('matching image shapes required')
        if any(f.rational(x)<0 for row in var for x in row): raise ValueError('nonnegative variance required')
        c = array(payload['source_ids'],1,0xffffffff,'source_ids',256)
        records = integer(len(c),1,256,'source count'); ow=10
        if len(set(c))!=records: raise ValueError('unique source IDs required')
        if n*records>1048576: raise ValueError('source catalog tile too large')
        image,bg,var,labels,valid = [[x for row in v for x in row] for v in (image,bg,var,labels,valid)]
        a = [x for row in zip(image,bg,var) for x in row]; b=[x for row in zip(labels,valid) for x in row]
        out = source_catalog(image,bg,var,labels,valid,c,w)
    else: raise ValueError('unknown imaging opcode')
    assert len(out)==records*ow
    header=[MAGIC,1,op,records,n,m,w,h,p0,0,0,16+len(a),16+len(a)+len(b),ow,0,0]
    return Job(wid,payload,header+a+b+c,records,ow,encode(out))
