"""Independent integer/Fraction interpolation and Python-sort median oracle."""
from . import f32 as f
from .reference import Job, MAGIC, encode, integer, array, matrix
from .float_reference import values
from .space_statistics_reference import rectangular_float, masks


def interpolate(sources, data, valid, query, neighbors):
    distances = sorted(((x-query[0])**2+(y-query[1])**2, j) for j, (x, y) in enumerate(sources) if valid[j])[:neighbors]
    if not distances:
        return [1, 0, 0, 0]
    if distances[0][0] == 0:
        return [0, f.add(data[distances[0][1]], 0), 1, 0]
    numerator = denominator = 0
    for distance, index in distances:
        weight = f.div(f.ONE, f.rounded(distance))
        numerator = f.add(numerator, f.mul(weight, data[index]))
        denominator = f.add(denominator, weight)
    return [0, f.div(numerator, denominator), len(distances), distances[0][0]]


def masked_median(mesh, valid, cy, cx, window, minimum):
    radius = window//2
    gathered = sorted((mesh[y][x] for y in range(max(0, cy-radius), min(len(mesh), cy+radius+1))
                       for x in range(max(0, cx-radius), min(len(mesh[0]), cx+radius+1)) if valid[y][x]), key=f.rational)
    count = len(gathered)
    if count < minimum:
        return [1, count, 0]
    middle = count//2
    median = f.add(gathered[middle], 0) if count % 2 else f.add(f.mul(gathered[middle-1], f.HALF), f.mul(gathered[middle], f.HALF))
    return [0, count, median]


def prepare_space_background(wid, op, payload):
    if payload.get('encoding') != 'binary32-hex':
        raise ValueError('encoding=binary32-hex required')
    a, b, out = [], [], []
    n = m = p0 = p1 = 0
    if op == 61:
        sources = matrix(payload['sources'], 2, 0, 32767, 'source coordinates', 256)
        n = integer(len(sources), 1, 256, 'source count')
        if len({tuple(row) for row in sources}) != n:
            raise ValueError('unique source coordinates required')
        data = values(payload['values'], 256)
        valid = array(payload['valid'], 0, 1, 'valid', 256)
        queries = matrix(payload['queries'], 2, 0, 32767, 'query coordinates', 4096)
        records = integer(len(queries), 1, 4096, 'query count')
        p0 = integer(payload['neighbors'], 1, 16, 'neighbors')
        if len(data) != n or len(valid) != n:
            raise ValueError('source/value/mask shape mismatch')
        if n*records*p0 > 4194304:
            raise ValueError('IDW tile work limit')
        ow = 4
        a = [v for (x, y), value, keep in zip(sources, data, valid) for v in (x, y, value, keep)]
        b = [v for row in queries for v in row]
        for query in queries:
            out.extend(interpolate(sources, data, valid, query, p0))
    elif op == 62:
        mesh, n = rectangular_float(payload['mesh'], 64, 64)
        m = len(mesh)
        valid = masks(payload['valid'], m, n)
        p0 = integer(payload['window'], 1, 7, 'window')
        if p0 % 2 != 1:
            raise ValueError('window must be odd')
        p1 = integer(payload['minimum_valid'], 1, p0*p0, 'minimum_valid')
        records, ow = n*m, 3
        a = [v for row in mesh for v in row]
        b = [v for row in valid for v in row]
        for y in range(m):
            for x in range(n):
                out.extend(masked_median(mesh, valid, y, x, p0, p1))
    else:
        raise ValueError('unknown background opcode')
    assert len(out) == records*ow
    header = [MAGIC, 1, op, records, n, m, 0, 0, p0, p1, 0, 16+len(a), 16+len(a)+len(b), ow, 0, 0]
    return Job(wid, payload, header+a+b, records, ow, encode(out))
