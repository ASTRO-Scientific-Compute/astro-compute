"""Hand-derived goldens and explicit edge cases, created before GPU kernels."""
import copy
import random
from .f32 import hex32


def hx(value):
    return [hx(x) for x in value] if isinstance(value, list) else hex32(value)


def payload(**kwargs):
    return dict(encoding='binary32-hex', **kwargs)


GOLDEN = {
    45: (payload(values=hx([1, 3, 5]), indices=[[0, 1], [2, 2], [0, 2]]),
         [int(x, 16) for x in hx([2, 2, 5, 0, 3, 8])]),
    46: (payload(samples=hx([[0, 0, 0, 8], [2, 2, 2, 2]]), valid=[[1]*4, [1]*4],
                 sigma_lower=hex32(1), sigma_upper=hex32(1), maxiters=4),
         [0, 3, 0, 0, 1, 1, 1, 0, 0, 4, int(hex32(2), 16), 0, 1, 1, 1, 1]),
    47: (payload(images=hx([[[2, 2, 0], [0, 0, 2], [2, 0, 2]]]),
                 valid=[[[1]*3 for _ in range(3)]], threshold=hex32(1), npixels=2, connectivity=4),
         [1, 1, 0, 0, 0, 6, 0, 0, 6]),
}


def fixture(op, seed=271828, scale=1):
    rng = random.Random(seed)
    if op == 45:
        return payload(values=hx([rng.randrange(-100, 101)/8 for _ in range(41)]),
                       indices=[[rng.randrange(41) for _ in range(23)] for _ in range(17*scale)])
    if op == 46:
        rows = [[rng.randrange(-16, 17)/16 for _ in range(31)] + [20] for _ in range(7*scale)]
        return payload(samples=hx(rows), valid=[[int(rng.random() > .1) for _ in row] for row in rows],
                       sigma_lower=hex32(2), sigma_upper=hex32(2.5), maxiters=8)
    if op == 47:
        images = [[[rng.randrange(4) for _ in range(11)] for _ in range(9)] for _ in range(7*scale)]
        return payload(images=hx(images), valid=[[[int(rng.random() > .15) for _ in row] for row in img] for img in images],
                       threshold=hex32(1), npixels=3, connectivity=8)
    raise ValueError(op)


def edges(op):
    g = copy.deepcopy(GOLDEN[op][0])
    cases = []
    if op == 45:
        cases.append(('single_source_repeated', payload(values=hx([-2]), indices=[[0]*512])))
        cases.append(('ordered_cancellation', payload(values=hx([16777216, 1, -16777216]), indices=[[0, 1, 2], [0, 2, 1]])))
        cases.append(('subnormal_signedzero', payload(values=['00000001', '80000000'], indices=[[0, 1], [1, 1]])))
        cases.append(('maximum_replicates', payload(values=hx([0, 2]), indices=[[0, 1]]*1024)))
    elif op == 46:
        def p(vals, keep, lo=1, hi=1, it=4):
            return payload(samples=hx(vals), valid=keep, sigma_lower=hex32(lo), sigma_upper=hex32(hi), maxiters=it)
        cases.extend([
            ('all_masked', p([[1, 2]], [[0, 0]])),
            ('singleton', p([[-2]], [[1]])),
            ('threshold_equality', p([[0, 2]], [[1, 1]])),
            ('empty_after_clipping', p([[0, 2]], [[1, 1]], 0, 0)),
            ('iteration_cap', p([[0, 0, 0, 8]], [[1]*4,], it=1)),
            ('asymmetric', p([[-8, 0, 0, 0, 8]], [[1]*5], lo=5, hi=1)),
            ('maximum_width', p([[2]*512], [[1]*512])),
        ])
        d=p([[0, 0, 0]], [[1]*3]);d['samples']=[['80000000', '00000001', '00000000']]
        cases.append(('subnormal_mask', d))
    elif op == 47:
        for conn in (4, 8):
            cases.append((f'diagonal_{conn}', payload(images=hx([[[2, 0], [0, 2]]]), valid=[[[1, 1], [1, 1]]], threshold=hex32(1), npixels=1, connectivity=conn)))
        d=copy.deepcopy(g);d['valid']=[[[0]*3 for _ in range(3)]];cases.append(('all_masked', d))
        d=copy.deepcopy(g);d['npixels']=9;cases.append(('all_components_too_small', d))
        cases.append(('maximum_connected', payload(images=hx([[[2]*32 for _ in range(32)]]), valid=[[[1]*32 for _ in range(32)]], threshold=hex32(1), npixels=1024, connectivity=8)))
        cases.append(('checkerboard', payload(images=hx([[[2*((x+y)%2) for x in range(32)] for y in range(32)]]), valid=[[[1]*32 for _ in range(32)]], threshold=hex32(1), npixels=1, connectivity=4)))
        cases.append(('zero_and_subnormal', payload(images=[[['80000000', '00000000', '00000001']]], valid=[[[1, 1, 1]]], threshold='00000000', npixels=1, connectivity=4)))
        cases.append(('masked_bridge', payload(images=hx([[[2, 2, 2]]]), valid=[[[1, 0, 1]]], threshold=hex32(1), npixels=1, connectivity=4)))
    return cases
