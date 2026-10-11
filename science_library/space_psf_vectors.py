"""Analytic results fixed before GPU implementation, plus edge fixtures."""
import copy
import random
from .space_statistics_vectors import hx, payload

GOLDEN = {
    59: (payload(image=hx([[5, 1], [3, -1]]), background=hx([[1, 1], [1, 1]]),
                 weights=hx([[1, 1], [1, 1]]), psf=hx([[1]])),
         sum(([0]+[int(v, 16) for v in hx([a, 1, a, 0])]+[1] for a in [4, 0, 2, -2]), [])),
    60: (payload(templates=hx([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                 flux=hx([[2, -3, 4], [0, 0, 0]]), weights=hx([[1, 1, 1], [1, 1, 1]])),
         [0, 5]+[int(v, 16) for v in hx([9, 2, 0, 4])]+[0, 0, 0, 0, 0, 0]),
}


def fixture(op, seed=271828, scale=1):
    rng = random.Random(seed)
    if op == 59:
        h, w = 11*scale, 13
        return payload(image=hx([[rng.randrange(-8, 65)/8 for _ in range(w)] for _ in range(h)]),
                       background=hx([[1/4]*w for _ in range(h)]),
                       weights=hx([[rng.randrange(5)/2 for _ in range(w)] for _ in range(h)]),
                       psf=hx([[0, .125, 0], [.125, .5, .125], [0, .125, 0]]))
    if op == 60:
        m, n = 4, 13
        templates = [[(1 if j == k else 0)+rng.randrange(3)/16 for j in range(n)] for k in range(m)]
        return payload(templates=hx(templates),
                       flux=hx([[rng.randrange(-8, 49)/8 for _ in range(n)] for _ in range(5*scale)]),
                       weights=hx([[rng.randrange(1, 5)/2 for _ in range(n)] for _ in range(5*scale)]))
    raise ValueError(op)


def edges(op):
    g = copy.deepcopy(GOLDEN[op][0])
    cases = []
    if op == 59:
        for name, key, value in [('zero_information', 'weights', hx([[0, 0], [0, 0]])),
                                 ('support_outside_image', 'psf', hx([[0, 0, 0], [0, 1, 0], [0, 0, 0]])),
                                 ('subnormal_signal', 'image', [['00000001', '80000001'], ['80000000', '00000000']])]:
            p = copy.deepcopy(g); p[key] = value
            if name == 'subnormal_signal': p['background'] = hx([[0, 0], [0, 0]])
            cases.append((name, p))
        p = fixture(op); p['psf'] = hx([[1, 2, 1]]); cases.append(('asymmetric_support_unnormalized', p))
        p = fixture(op); p['weights'] = hx([[0]*13 for _ in range(11)]); p['weights'][5][6] = '3f800000'; cases.append(('one_valid_pixel', p))
        p = payload(image=hx([[1]*64 for _ in range(64)]), background=hx([[0]*64 for _ in range(64)]), weights=hx([[1]*64 for _ in range(64)]), psf=hx([[1]])); cases.append(('maximum_image', p))
        p = payload(image=hx([[1]*9 for _ in range(9)]), background=hx([[0]*9 for _ in range(9)]), weights=hx([[1]*9 for _ in range(9)]), psf=hx([[1]*9 for _ in range(9)])); cases.append(('maximum_psf', p))
    elif op == 60:
        for name, key, value in [('zero_information', 'weights', hx([[0]*3]*2)),
                                 ('singular_templates', 'templates', hx([[1, 0, 0]]*3)),
                                 ('origin_optimum', 'flux', hx([[-2, -3, -4]]*2)),
                                 ('masked_band_rank_failure', 'weights', hx([[1, 0, 1]]*2)),
                                 ('all_active', 'flux', hx([[2, 3, 4]]*2))]:
            p = copy.deepcopy(g); p[key] = value; cases.append((name, p))
        p = copy.deepcopy(g); p['templates'] = hx([[1, 0, 0], [1, 1/1024, 0], [0, 0, 1]]); cases.append(('near_singular_rejected', p))
        p = copy.deepcopy(g); p['flux'] = [['00000001', '80000001', '80000000']]*2; cases.append(('subnormal_objective_tie', p))
        p = payload(templates=hx([[int(j == k) for j in range(128)] for k in range(5)]), flux=hx([[1, -2, 3, 0, 4]+[0]*123]), weights=hx([[1]*128])); cases.append(('maximum_templates_and_samples', p))
    return cases
