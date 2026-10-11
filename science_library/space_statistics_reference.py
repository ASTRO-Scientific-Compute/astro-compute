"""Independent Fraction statistics and flood-fill segmentation oracle."""
from . import f32 as f
from .float_reference import values, rows
from .reference import Job, MAGIC, encode, integer, matrix


def statistics(values_, sample=False):
    if not values_:
        return 0, 0
    mean = f.div(f.summation(values_), f.rounded(len(values_)))
    residuals = [f.sub(x, mean) for x in values_]
    variance = f.div(f.summation(f.mul(d, d) for d in residuals),
                     f.rounded(len(values_) - int(sample)))
    return mean, variance


def clipped_statistics(row, valid, lower, upper, maxiters):
    keep = valid[:]
    status = 2
    for _ in range(maxiters):
        current = [x for x, k in zip(row, keep) if k]
        if not current:
            status = 1
            break
        mean, variance = statistics(current)
        std = f.sqrt(variance)
        lo = f.rational(f.sub(mean, f.mul(lower, std)))
        hi = f.rational(f.add(mean, f.mul(upper, std)))
        next_keep = [int(k and lo <= f.rational(x) <= hi) for x, k in zip(row, keep)]
        if next_keep == keep:
            status = 0
            break
        keep = next_keep
    current = [x for x, k in zip(row, keep) if k]
    if not current:
        status = 1
    mean, variance = statistics(current)
    return [status, len(current), mean, variance] + keep


def segment(image, valid, width, height, threshold, npixels, connectivity):
    foreground = [bool(k and f.rational(x) > f.rational(threshold)) for x, k in zip(image, valid)]
    visited = set()
    output = [0] * len(image)
    offsets = [(0, -1), (-1, 0), (1, 0), (0, 1)]
    if connectivity == 8:
        offsets += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for start in range(len(image)):
        if not foreground[start] or start in visited:
            continue
        visited.add(start)
        component = [start]
        cursor = 0
        while cursor < len(component):
            node = component[cursor]
            cursor += 1
            x, y = node % width, node // width
            for dx, dy in offsets:
                xx, yy = x + dx, y + dy
                if 0 <= xx < width and 0 <= yy < height:
                    other = yy * width + xx
                    if foreground[other] and other not in visited:
                        visited.add(other)
                        component.append(other)
        if len(component) >= npixels:
            label = min(component) + 1
            for node in component:
                output[node] = label
    return output


def rectangular_float(raw, maxrows, maxcols):
    if not isinstance(raw, list) or not raw or not isinstance(raw[0], list):
        raise ValueError('nonempty rectangular rows required')
    width = integer(len(raw[0]), 1, maxcols, 'row width')
    return rows(raw, width, maxrows), width


def masks(raw, height, width):
    result = matrix(raw, width, 0, 1, 'valid', height)
    if len(result) != height:
        raise ValueError('valid mask shape')
    return result


def prepare_space_statistics(wid, op, payload):
    if payload.get('encoding') != 'binary32-hex':
        raise ValueError('encoding=binary32-hex required')
    a, b, out = [], [], []
    n = m = w = h = p0 = p1 = p2 = 0
    if op == 45:
        a = values(payload['values'], 4096)
        raw = payload['indices']
        if not isinstance(raw, list) or not raw or not isinstance(raw[0], list):
            raise ValueError('nonempty resample indices required')
        n = integer(len(raw[0]), 2, 512, 'resample size')
        indices = matrix(raw, n, 0, len(a) - 1, 'indices', 1024)
        records = len(indices)
        m = len(a)
        ow = 2
        if records * n > 262144:
            raise ValueError('bootstrap tile too large')
        for replicate in indices:
            b.extend(replicate)
            out.extend(statistics([a[j] for j in replicate], sample=True))
    elif op == 46:
        samples, n = rectangular_float(payload['samples'], 128, 512)
        valid = masks(payload['valid'], len(samples), n)
        p0 = f.parse(payload['sigma_lower'])
        p1 = f.parse(payload['sigma_upper'])
        p2 = integer(payload['maxiters'], 1, 16, 'maxiters')
        if f.rational(p0) < 0 or f.rational(p1) < 0:
            raise ValueError('nonnegative sigma bounds required')
        records = len(samples)
        ow = n + 4
        if records * n * p2 > 1048576:
            raise ValueError('clipping tile too large')
        for row, mask in zip(samples, valid):
            a.extend(row)
            b.extend(mask)
            out.extend(clipped_statistics(row, mask, p0, p1, p2))
    elif op == 47:
        raw, valid = payload['images'], payload['valid']
        if not isinstance(raw, list) or not 1 <= len(raw) <= 128:
            raise ValueError('image batch count')
        if not isinstance(valid, list) or len(valid) != len(raw):
            raise ValueError('valid batch shape')
        first, w = rectangular_float(raw[0], 32, 32)
        h = len(first)
        n = w * h
        records = len(raw)
        ow = n
        if records * n > 65536:
            raise ValueError('segmentation tile too large')
        p0 = f.parse(payload['threshold'])
        p1 = integer(payload['npixels'], 1, n, 'npixels')
        p2 = integer(payload['connectivity'], 4, 8, 'connectivity')
        if p2 not in (4, 8):
            raise ValueError('connectivity must be 4 or 8')
        for raw_image, raw_mask in zip(raw, valid):
            image, width = rectangular_float(raw_image, 32, 32)
            if width != w or len(image) != h:
                raise ValueError('uniform image shapes required')
            mask = masks(raw_mask, h, w)
            flat = [x for row in image for x in row]
            flat_mask = [x for row in mask for x in row]
            a.extend(flat)
            b.extend(flat_mask)
            out.extend(segment(flat, flat_mask, w, h, p0, p1, p2))
    else:
        raise ValueError('unknown SPACE statistics opcode')
    assert len(out) == records * ow
    header = [MAGIC, 1, op, records, n, m, w, h, p0, p1, p2,
              16 + len(a), 16 + len(a) + len(b), ow, 0, 0]
    return Job(wid, payload, header + a + b, records, ow, encode(out))
