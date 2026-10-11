"""Independent Fraction-based RN32 PSF/mixture reference."""
from . import f32 as f
from .reference import Job, MAGIC, encode, integer
from .float_reference import rows
from .space_statistics_reference import rectangular_float


def psf_scan(image, background, weights, psf, cy, cx):
    h, w = len(image), len(image[0])
    ph, pw = len(psf), len(psf[0])
    ry, rx = ph//2, pw//2
    if cy < ry or cx < rx or cy+ry >= h or cx+rx >= w:
        return [2, 0, 0, 0, 0, 0]
    numerator = denominator = count = 0
    samples = []
    for y in range(ph):
        for x in range(pw):
            iy, ix = cy+y-ry, cx+x-rx
            v, p = weights[iy][ix], psf[y][x]
            d = f.sub(image[iy][ix], background[iy][ix])
            wp = f.mul(v, p)
            numerator = f.add(numerator, f.mul(wp, d))
            denominator = f.add(denominator, f.mul(wp, p))
            count += f.rational(v) > 0
            samples.append((d, v, p))
    if not denominator:
        return [1, 0, 0, 0, 0, 0]
    amplitude = f.div(numerator, denominator)
    variance = f.div(f.ONE, denominator)
    snr = f.div(amplitude, f.sqrt(variance))
    chi = 0
    for d, v, p in samples:
        residual = f.sub(d, f.mul(amplitude, p))
        chi = f.add(chi, f.mul(v, f.mul(residual, residual)))
    return [0, amplitude, variance, snr, chi, count]


def principal_solve(gram, rhs, active, threshold):
    n = len(active)
    lower = [[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(a+1):
            product = f.summation(f.mul(lower[a][k], lower[b][k]) for k in range(b))
            d = f.sub(gram[active[a]][active[b]], product)
            if a == b:
                if f.rational(d) <= f.rational(threshold):
                    return None
                lower[a][b] = f.sqrt(d)
            else:
                lower[a][b] = f.div(d, lower[b][b])
    u = [0]*n
    coefficients = [0]*n
    for a in range(n):
        u[a] = f.div(f.sub(rhs[active[a]], f.summation(f.mul(lower[a][b], u[b]) for b in range(a))), lower[a][a])
    for a in range(n-1, -1, -1):
        coefficients[a] = f.div(f.sub(u[a], f.summation(f.mul(lower[b][a], coefficients[b]) for b in range(a+1, n))), lower[a][a])
    return coefficients


def template_nnls(flux, weights, templates):
    m = len(templates)
    gram = [[0]*m for _ in range(m)]
    rhs = [0]*m
    for a in range(m):
        wt = [f.mul(w, t) for w, t in zip(weights, templates[a])]
        rhs[a] = f.dot(wt, flux)
        for b in range(a+1):
            gram[a][b] = gram[b][a] = f.dot(wt, templates[b])
    scale = max((gram[a][a] for a in range(m)), key=f.rational)
    if not scale:
        return [1]+[0]*(m+2)
    threshold = f.mul(scale, 0x36800000)  # 2^-18

    def objective(coefficients):
        total = 0
        for j, (y, w) in enumerate(zip(flux, weights)):
            prediction = f.summation(f.mul(coefficients[k], templates[k][j]) for k in range(m))
            d = f.sub(y, prediction)
            total = f.add(total, f.mul(w, f.mul(d, d)))
        return total

    best = [0]*m
    chi = objective(best)
    for mask in range(1, 1 << m):
        active = [k for k in range(m) if mask & (1 << k)]
        solution = principal_solve(gram, rhs, active, threshold)
        if solution is None:
            return [2]+[0]*(m+2)
        if any(f.rational(v) < 0 for v in solution):
            continue
        candidate = [0]*m
        for k, value in zip(active, solution):
            candidate[k] = value
        score = objective(candidate)
        if f.rational(score) < f.rational(chi):
            best, chi = candidate, score
    mask = sum(1 << k for k, value in enumerate(best) if f.rational(value) > 0)
    return [0, mask, chi]+best


def prepare_space_psf(wid, op, payload):
    if payload.get('encoding') != 'binary32-hex':
        raise ValueError('encoding=binary32-hex required')
    a, b, c, out = [], [], [], []
    n = m = p0 = p1 = 0
    if op == 59:
        image, n = rectangular_float(payload['image'], 64, 64)
        background, bw = rectangular_float(payload['background'], 64, 64)
        weights, ww = rectangular_float(payload['weights'], 64, 64)
        psf, p0 = rectangular_float(payload['psf'], 9, 9)
        m, p1 = len(image), len(psf)
        if bw != n or ww != n or len(background) != m or len(weights) != m:
            raise ValueError('image/background/weight shape mismatch')
        if p0 % 2 != 1 or p1 % 2 != 1:
            raise ValueError('PSF dimensions must be odd')
        if any(f.rational(v) < 0 for plane in (weights, psf) for row in plane for v in row):
            raise ValueError('nonnegative weights and PSF required')
        if not f.summation(v for row in psf for v in row):
            raise ValueError('positive PSF sum required')
        records, ow = n*m, 6
        a = [v for y in range(m) for x in range(n) for v in (image[y][x], background[y][x], weights[y][x])]
        b = [v for row in psf for v in row]
        for y in range(m):
            for x in range(n):
                out.extend(psf_scan(image, background, weights, psf, y, x))
    elif op == 60:
        templates, n = rectangular_float(payload['templates'], 5, 128)
        m = integer(len(templates), 3, 5, 'template count')
        integer(n, m, 128, 'sample count')
        flux = rows(payload['flux'], n, 64)
        weights = rows(payload['weights'], n, 64)
        records = len(flux)
        if len(weights) != records or any(f.rational(v) < 0 for plane in (templates, weights) for row in plane for v in row):
            raise ValueError('nonnegative templates/weights with matching flux rows required')
        if records*(1 << m)*(n*m+m**3) > 2097152:
            raise ValueError('mixture tile work limit')
        ow = m+3
        a = [v for y, w in zip(flux, weights) for pair in zip(y, w) for v in pair]
        b = [v for row in templates for v in row]
        for y, w in zip(flux, weights):
            out.extend(template_nnls(y, w, templates))
    else:
        raise ValueError('unknown PSF/mixture opcode')
    assert len(out) == records*ow
    header = [MAGIC, 1, op, records, n, m, 0, 0, p0, p1, 0, 16+len(a), 16+len(a)+len(b), ow, 0, 0]
    return Job(wid, payload, header+a+b+c, records, ow, encode(out))
