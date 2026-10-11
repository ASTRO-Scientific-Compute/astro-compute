"""Independent exact-rational finite-operation inference oracle."""
import hashlib
import json
import re
import struct
from . import f32 as f
from .reference import Job, MAGIC, encode, integer
from .float_reference import values, rows
from .space_statistics_reference import rectangular_float


def percentile_interval(replicates, confidence):
    ordered = sorted((f.add(x, 0) for x in replicates), key=f.rational)
    alpha = f.mul(f.sub(f.ONE, confidence), f.HALF)
    result = []
    for q in (alpha, f.sub(f.ONE, alpha)):
        h = f.mul(f.rounded(len(ordered)-1), q)
        j = int(f.rational(h))
        g = f.sub(h, f.rounded(j))
        if not g:
            result.append(ordered[j])
        else:
            result.append(f.add(f.mul(f.sub(f.ONE, g), ordered[j]),
                                f.mul(g, ordered[min(j+1, len(ordered)-1)])))
    return result


def sed_pair(y, weights, pair):
    t0, t1 = pair
    wt0 = [f.mul(w, t) for w, t in zip(weights, t0)]
    wt1 = [f.mul(w, t) for w, t in zip(weights, t1)]
    g00, g01, g11 = f.dot(wt0, t0), f.dot(wt0, t1), f.dot(wt1, t1)
    u, v = f.dot(wt0, y), f.dot(wt1, y)
    product = f.mul(g00, g11)
    det = f.sub(product, f.mul(g01, g01))
    if f.rational(det) <= f.rational(f.mul(product, 0x36800000)):
        return [1, 0, 0, 0]
    a0, b1 = f.div(u, g00), f.div(v, g11)
    candidates = [(0, 0), (a0 if f.rational(a0) > 0 else 0, 0),
                  (0, b1 if f.rational(b1) > 0 else 0)]
    a = f.div(f.sub(f.mul(u, g11), f.mul(v, g01)), det)
    b = f.div(f.sub(f.mul(v, g00), f.mul(u, g01)), det)
    if f.rational(a) >= 0 and f.rational(b) >= 0:
        candidates.append((a, b))
    best = None
    for a, b in candidates:
        residuals = [f.sub(yi, f.add(f.mul(a, x), f.mul(b, z))) for yi, x, z in zip(y, t0, t1)]
        chi = f.summation(f.mul(w, f.mul(d, d)) for w, d in zip(weights, residuals))
        if best is None or f.rational(chi) < f.rational(best[3]):
            best = [0, a, b, chi]
    return best


def prepare_space_inference(wid, op, payload):
    if payload.get('encoding') != 'binary32-hex':
        raise ValueError('encoding=binary32-hex required')
    a, b, c, out = [], [], [], []
    n = m = p0 = 0
    if op == 48:
        samples, n = rectangular_float(payload['replicates'], 128, 512)
        integer(n, 2, 512, 'replicate count')
        p0 = f.parse(payload['confidence'])
        if not 0 < f.rational(p0) <= 1:
            raise ValueError('confidence must be in (0,1]')
        records, ow = len(samples), 2
        for row in samples:
            a.extend(row)
            out.extend(percentile_interval(row, p0))
    elif op == 49:
        a = values(payload['observed'], 4096)
        b = values(payload['null_statistics'], 65535)
        n, records, ow = len(b), len(a), 4
        if n*records > 4194304:
            raise ValueError('tail tile exceeds 4M comparisons')
        model, grid = payload.get('null_model_id'), payload.get('search_grid_sha256')
        if not isinstance(model, str) or not model.strip() or len(model) > 256:
            raise ValueError('null_model_id required')
        if not isinstance(grid, str) or not re.fullmatch('[0-9a-f]{64}', grid):
            raise ValueError('search_grid_sha256 required')
        context = json.dumps(dict(null_model_id=model, search_grid_sha256=grid), sort_keys=True, separators=(',', ':')).encode()
        c = list(struct.unpack('<8I', hashlib.sha256(context).digest()))
        null = [f.rational(x) for x in b]
        for value in a:
            extreme = sum(x >= f.rational(value) for x in null)
            out.extend([extreme, n, extreme+1, n+1])
    elif op == 50:
        flux, n = rectangular_float(payload['flux'], 128, 64)
        integer(n, 2, 64, 'bands')
        weights = rows(payload['weights'], n, 128)
        if len(weights) != len(flux) or any(f.rational(x) < 0 for row in weights for x in row):
            raise ValueError('nonnegative weights matching flux required')
        raw = payload['template_pairs']
        if not isinstance(raw, list) or not 1 <= len(raw) <= 128:
            raise ValueError('template pair count')
        pairs = [rows(pair, n, 2) for pair in raw]
        if any(len(pair) != 2 for pair in pairs) or any(f.rational(x) < 0 for pair in pairs for row in pair for x in row):
            raise ValueError('two nonnegative templates per pair required')
        m, ow = len(pairs), 4
        records = len(flux)*m
        if records*n > 1048576:
            raise ValueError('SED tile too large')
        a = [x for y, w in zip(flux, weights) for pair in zip(y, w) for x in pair]
        b = [x for pair in pairs for row in pair for x in row]
        for y, w in zip(flux, weights):
            for pair in pairs:
                out.extend(sed_pair(y, w, pair))
    else:
        raise ValueError('unknown inference opcode')
    assert len(out) == records*ow
    header = [MAGIC, 1, op, records, n, m, 0, 0, p0, 0, 0,
              16+len(a), 16+len(a)+len(b), ow, 0, 0]
    return Job(wid, payload, header+a+b+c, records, ow, encode(out))
