"""Hand-derived reference vectors before GPU code; no historical speed seeds."""
import copy
import random
from .space_statistics_vectors import hx, payload
from .f32 import hex32

CONTEXT = dict(null_model_id='CONTROLLED_TEST_NULL_NOT_LIVE_SCIENCE', search_grid_sha256='0'*64)
GOLDEN = {
    48: (payload(replicates=hx([[8, 0, 6, 2, 4], [-4, -2, 0, 2, 4]]), confidence=hex32(.5)),
         [int(x, 16) for x in hx([2, 6, -2, 2])]),
    49: (payload(observed=hx([0, 2, 4]), null_statistics=hx([1, 2, 2, 3]), **CONTEXT),
         [4, 4, 5, 5, 3, 4, 4, 5, 0, 4, 1, 5]),
    50: (payload(flux=hx([[2, 3], [-2, 3]]), weights=hx([[1, 1], [1, 1]]), template_pairs=hx([[[1, 0], [0, 1]]])),
         [0, int(hex32(2),16), int(hex32(3),16), 0, 0, 0, int(hex32(3),16), int(hex32(4),16)]),
}


def fixture(op, seed=271828, scale=1):
    r = random.Random(seed)
    if op == 48:
        return payload(replicates=hx([[r.randrange(-128, 129)/16 for _ in range(37)] for _ in range(13*scale)]), confidence=hex32(.875))
    if op == 49:
        return payload(observed=hx([r.randrange(-128, 129)/16 for _ in range(23*scale)]),
                       null_statistics=hx([r.randrange(-128, 129)/16 for _ in range(137)]), **CONTEXT)
    if op == 50:
        return payload(flux=hx([[r.randrange(-8, 65)/8 for _ in range(9)] for _ in range(5*scale)]),
                       weights=hx([[r.randrange(1, 5)/2 for _ in range(9)] for _ in range(5*scale)]),
                       template_pairs=hx([[[1+(j%3)/4 for j in range(9)], [(j+1)/8+k/32 for j in range(9)]] for k in range(3)]))
    raise ValueError(op)


def edges(op):
    g = copy.deepcopy(GOLDEN[op][0])
    cases = []
    if op == 48:
        for name, data, level in [('two_values', [[-2, 2]], .5), ('duplicates', [[2]*7], .875),
                                   ('full_interval', [[-8, 2, 8]], 1), ('maximum_length', [list(range(511, -1, -1))], .875),
                                   ('mixed_odd', [[-3, -1, 1, 7, 3, 5, -7]], .75)]:
            cases.append((name, payload(replicates=hx(data), confidence=hex32(level))))
        cases.append(('signedzero_subnormal', payload(replicates=[['80000000', '00000000', '00000001', '80000001']], confidence=hex32(.5))))
        cases.append(('extreme_endpoints', payload(replicates=[['ff7fffff', '7f7fffff']], confidence=hex32(1))))
    elif op == 49:
        cases.append(('one_simulation_ties', payload(observed=hx([-1, 0, 1]), null_statistics=hx([0]), **CONTEXT)))
        cases.append(('maximum_null', payload(observed=hx([0, 1, 2]), null_statistics=hx([1]*65535), **CONTEXT)))
        cases.append(('zeros_subnormals', payload(observed=['80000000','00000001','80000001'], null_statistics=['00000000','80000000','00000001','80000001'], **CONTEXT)))
        cases.append(('adjacent_floats', payload(observed=['3f800000','3f800001'], null_statistics=['3f7fffff','3f800000','3f800001'], **CONTEXT)))
    elif op == 50:
        for name, key, value in [('zero_weight','weights',hx([[0,0],[0,0]])),
                                 ('singular','template_pairs',hx([[[1,1],[2,2]]])),
                                 ('origin_optimum','flux',hx([[-2,-3],[-4,-1]])),
                                 ('axis_optima','flux',hx([[2,-3],[-2,3]])),
                                 ('masked_band','weights',hx([[1,0],[0,1]]))]:
            p=copy.deepcopy(g);p[key]=value;cases.append((name,p))
        p=copy.deepcopy(g);p['template_pairs']=[[['3f800000','3f800000'],['3f800000','3f800001']]];cases.append(('near_singular',p))
        p=payload(flux=hx([[2,3]*32]), weights=hx([[1]*64]), template_pairs=hx([[[1,0]*32,[0,1]*32]]));cases.append(('maximum_bands',p))
        p=copy.deepcopy(g);p['flux']=[['00000001','80000000'],['80000001','00000000']];cases.append(('subnormal_flux',p))
    return cases
