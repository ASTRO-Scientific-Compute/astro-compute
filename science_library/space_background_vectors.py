"""Analytic vectors established before GPU code and bounded edge fixtures."""
import copy
import random
from .space_statistics_vectors import hx, payload

GOLDEN = {
    61: (payload(sources=[[0, 0], [2, 0], [0, 2]], values=hx([2, 6, 100]), valid=[1, 1, 0],
                 queries=[[0, 0], [1, 0], [2, 0]], neighbors=2),
         [0, int(hx(2), 16), 1, 0, 0, int(hx(4), 16), 2, 1, 0, int(hx(6), 16), 1, 0]),
    62: (payload(mesh=hx([[1, 100, 3], [4, 5, 6], [7, 8, 9]]), valid=[[1]*3 for _ in range(3)], window=3, minimum_valid=1),
         sum(([0, count, int(hx(median), 16)] for count, median in zip([4, 6, 4, 6, 9, 6, 4, 6, 4], [4.5, 4.5, 5.5, 6, 6, 7, 6, 6.5, 7])), [])),
}


def fixture(op, seed=271828, scale=1):
    rng = random.Random(seed)
    if op == 61:
        points = rng.sample(range(32*32), 23)
        return payload(sources=[[v % 32, v//32] for v in points], values=hx([rng.randrange(-32, 65)/8 for _ in points]),
                       valid=[int(j % 5 != 0) for j in range(len(points))], queries=[[rng.randrange(32), rng.randrange(32)] for _ in range(17*scale)], neighbors=5)
    if op == 62:
        return payload(mesh=hx([[rng.randrange(-64, 129)/8 for _ in range(11)] for _ in range(9*scale)]),
                       valid=[[int(rng.random() > .2) for _ in range(11)] for _ in range(9*scale)], window=5, minimum_valid=4)
    raise ValueError(op)


def edges(op):
    g = copy.deepcopy(GOLDEN[op][0]); cases = []
    if op == 61:
        for name, key, value in [('no_valid_source', 'valid', [0]*3), ('more_neighbors_than_sources', 'neighbors', 16),
                                 ('nearest_only_tie', 'neighbors', 1), ('invalid_coincident_source', 'queries', [[0, 2]]),
                                 ('negative_values', 'values', hx([-2, -6, -100]))]:
            p = copy.deepcopy(g); p[key] = value; cases.append((name, p))
        cases.append(('maximum_integer_distance', payload(sources=[[0, 0]], values=hx([2]), valid=[1], queries=[[32767, 32767]], neighbors=16)))
        p = copy.deepcopy(g); p['values'] = ['80000000', '00000001', '80000001']; cases.append(('signed_zero_subnormal', p))
        cases.append(('maximum_sources_neighbors', payload(sources=[[j%16, j//16] for j in range(256)], values=hx(list(range(256))), valid=[1]*256, queries=[[16, 16], [31, 31]], neighbors=16)))
        cases.append(('maximum_queries', payload(sources=[[0, 0]], values=hx([7]), valid=[1], queries=[[j, 0] for j in range(4096)], neighbors=1)))
    elif op == 62:
        for name, key, value in [('all_invalid', 'valid', [[0]*3 for _ in range(3)]), ('identity_window', 'window', 1),
                                 ('insufficient_at_edges', 'minimum_valid', 9), ('window_larger_than_mesh', 'window', 7)]:
            p = copy.deepcopy(g); p[key] = value; cases.append((name, p))
        cases.append(('even_masked_neighborhood', payload(mesh=hx([[1, 2, 100], [4, 8, 16]]), valid=[[1, 0, 1], [0, 1, 1]], window=3, minimum_valid=2)))
        cases.append(('extreme_even_without_overflow', payload(mesh=[['7f7fffff', '7f7fffff']], valid=[[1, 1]], window=3, minimum_valid=1)))
        cases.append(('subnormal_even_rounding', payload(mesh=[['00000001', '00000001']], valid=[[1, 1]], window=3, minimum_valid=1)))
        cases.append(('signed_zeros', payload(mesh=[['80000000', '00000000', '80000000']], valid=[[1, 1, 1]], window=3, minimum_valid=1)))
        cases.append(('maximum_mesh', payload(mesh=hx([[j%7 for j in range(64)] for _ in range(64)]), valid=[[1]*64 for _ in range(64)], window=7, minimum_valid=1)))
    return cases
