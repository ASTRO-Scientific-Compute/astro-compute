"""Analytic complex pairs and bounded adversarial records."""
import random
from .space_statistics_vectors import hx


def make(bins=None):
    if bins is None:bins=[[[1,0,2,0],[1,0,2,0]]]
    return dict(encoding='binary32-hex',cross_convention='CONJ_X_TIMES_Y',replicate_contract='MATCHED_ORDERED_SEGMENTS',power_normalization='MEAN_SUPPLIED_BIN_PRODUCTS',spectrum_unit_x='amplitude_x',spectrum_unit_y='amplitude_y',frequency_grid_id='declared-matched-grid',bins=hx(bins))


GOLDEN={78:(make(),[0,0x3f800000,0x40800000,0x40000000,0,0x3f800000])}


def fixture(op=78,seed=271828,scale=1):
    if op!=78:raise ValueError(op)
    rng=random.Random(seed)
    return make([[[rng.randrange(-128,129)/16 for _ in range(4)] for _ in range(13)] for _ in range(min(17*scale,256))])


def edges(op=78):
    if op!=78:raise ValueError(op)
    out=[('quadrature',make([[[1,0,0,2],[0,1,-2,0]]])),
         ('negative_gain',make([[[1,0,-2,0],[0,1,0,-2]]])),
         ('orthogonal_pairs',make([[[1,0,1,0],[1,0,-1,0]]])),
         ('zero_channels',make([[[0,0,1,2]]*2,[[1,2,0,0]]*2,[[0,0,0,0]]*2])),
         ('minimum_components',make([[[2**-28,0,2**-28,0]]*2])),
         ('maximum_components',make([[[2**16,2**16,2**16,-2**16]]*64])),
         ('reciprocal_scales',make([[[2**-28,0,2**16,0]]*2,[[2**16,0,2**-28,0]]*2])),
         ('sparse_minimum_power',make([[[2**-28,0,2**-28,0]]+[[0,0,0,0]]*63])),
         ('mixed_dynamic_range',make([[[2**16,2**-28,-2**-28,2**16],[2**-28,-2**16,2**16,2**-28]]*32])),
         ('maximum_replicates',make([[[((j*7)%31)-15,j%3,(j%11)-5,((j*3)%17)-8] for j in range(64)]])),
         ('tiny_cross_cancellation',make([[[1,0,1,0],[1,0,-1,2**-28]]])),
         ('maximum_bins_replicates',make([[[1+(b%4),j%3,((j+b)%7)-3,1] for j in range(64)] for b in range(256)]))]
    p=make([[[0,0,0,0]]*2]);p['bins'][0][0]=['80000000']*4;out.append(('signed_zero',p))
    return out
