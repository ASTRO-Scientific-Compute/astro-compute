"""Independent Fraction/RN32 implicit solve and perifocal state reference."""
from fractions import Fraction
from . import f32 as f
from .reference import Job, MAGIC, encode
from .float_reference import rows
from .space_search_reference import sincos, TAU
WID = 'SPACE_ELLIPTIC_KEPLER_STATE_F32_V1'


def state(a, e, mean, mu):
    mean = f.add(mean, 0)
    e = f.add(e, 0)
    if e == 0 or mean in (0, f.HALF):
        eccentric = mean
    else:
        reflected = f.rational(mean) > Fraction(1, 2)
        target = f.sub(f.ONE, mean) if reflected else mean
        lo, hi = 0, f.HALF
        for _ in range(32):
            mid = f.mul(f.add(lo, hi), f.HALF)
            sn, _ = sincos(mid)
            residual = f.sub(f.mul(TAU, f.sub(mid, target)), f.mul(e, sn))
            if f.rational(residual) < 0:
                lo = mid
            else:
                hi = mid
        u = f.mul(f.add(lo, hi), f.HALF)
        eccentric = f.sub(f.ONE, u) if reflected else u
    sn, cs = sincos(eccentric)
    beta = f.sqrt(f.sub(f.ONE, f.mul(e, e)))
    d = f.sub(f.ONE, f.mul(e, cs))
    radius = f.mul(a, d)
    scale = f.div(f.sqrt(f.div(mu, a)), d)
    return [eccentric, radius, f.mul(a, f.sub(cs, e)), f.mul(f.mul(a, beta), sn), 0,
            f.neg(f.mul(scale, sn)), f.mul(f.mul(scale, beta), cs), 0]


def prepare_space_kepler(wid, payload):
    if payload.get('encoding') != 'binary32-hex' or payload.get('angle_unit') != 'turn' or payload.get('frame') != 'PERIFOCAL':
        raise ValueError('explicit binary32/turn/PERIFOCAL contract required')
    for key in ('distance_unit', 'time_unit'):
        text = payload.get(key)
        if not isinstance(text, str) or not text.strip() or len(text) > 64:
            raise ValueError('explicit distance/time units required')
    elements = rows(payload['elements'], 3, 1024)
    mu = f.parse(payload['mu'])
    lo, hi = Fraction(1, 1 << 32), Fraction(1 << 32)
    if not lo <= f.rational(mu) <= hi:
        raise ValueError('mu outside bounded numerical scale')
    output = []
    for a, e, mean in elements:
        if not lo <= f.rational(a) <= hi or not 0 <= f.rational(e) <= Fraction(15,16) or not 0 <= f.rational(mean) < 1:
            raise ValueError('a/e/mean anomaly outside bounded elliptic contract')
        output.extend(state(a, e, mean, mu))
    n = len(elements)
    header = [MAGIC, 1, 75, n, 3, 0, 0, 0, mu, 0, 0, 16+3*n, 16+3*n, 8, 0, 0]
    return Job(wid, payload, header+sum(elements, []), n, 8, encode(output))
