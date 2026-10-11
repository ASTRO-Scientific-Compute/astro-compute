"""Analytic golden cases plus deterministic stress inputs; no performance seeds."""
import json
import random
from .catalog import ROOT, SPECS
from .reference import prepare, encode, words64

SPATIAL=dict(queries=[[0,0,0],[10,0,0]],catalog=[[-1,0,0],[1,0,0],[0,0,0]],coordinate_unit='one explicitly supplied coordinate tick')
GOLDEN={
 1:({'images':[[[1,2],[3,4]]]},sum((words64(x) for x in [10,6,7,6,4,7]),[])),
 2:({'image':[[1,2,3],[4,5,6],[7,8,9]],'apertures':[[1,1,1,1],[0,0,0,2]]},[20,5,-1,1]),
 3:({'times':[0,1,2,3],'flux':[1,2,3,4],'periods':[2],'bins':2},[2,4,0,10,0,2,6,0,20,0]),
 4:({'samples':[[[0,1,1],[1,3,2]]]},sum((words64(x) for x in [3,2,7,2,6,19]),[])),
 5:({**SPATIAL,'squared_radius':1},[3,2,0,0,0,0xffffffff,0xffffffff,0xffffffff]),
 6:({'pairs':[['ACGT','ACGT'],['A','T'],['','AC'],['ACGT','AGT']]},[8,0,0,4]),
 7:({**SPATIAL,'squared_radius':1},[3,0]),
 8:(SPATIAL,sum((words64(x) for x in [1,1,0,121,81,100]),[])),
 9:({**SPATIAL,'squared_edges':[0,1,2]},[1,2,0,0]),
 10:({'spins':[[1]*3 for _ in range(3)]},[-2,1]*9),
 11:({'samples':[1,-2,3],'coefficients':[2,-1]},sum((words64(x) for x in [2,-5,8]),[])),
 12:({'rowptr':[0,2,2,3],'col':[0,1,1],'values':[2,-1,3],'vector':[4,5]},sum((words64(x) for x in [3,0,15]),[])),
 13:({'triangles':[[[0,0],[1,0],[0,1]],[[0,0],[0,1],[1,0]],[[0,0],[1,1],[2,2]]]},[1,1,-1,-1,0,0]),
}


from .float_vectors import GOLDEN as FLOAT_GOLDEN, fixture as float_fixture
GOLDEN.update(FLOAT_GOLDEN)
from .legacy_vectors import GOLDEN as LEGACY_GOLDEN, fixture as legacy_fixture
GOLDEN.update(LEGACY_GOLDEN)

from .triangle_vectors import GOLDEN as TRIANGLE_GOLDEN
GOLDEN.update(TRIANGLE_GOLDEN)

from .space_search_vectors import GOLDEN as SPACE_SEARCH_GOLDEN
GOLDEN.update(SPACE_SEARCH_GOLDEN)

from .space_statistics_vectors import GOLDEN as SPACE_STATISTICS_GOLDEN
GOLDEN.update(SPACE_STATISTICS_GOLDEN)

from .space_inference_vectors import GOLDEN as SPACE_INFERENCE_GOLDEN
GOLDEN.update(SPACE_INFERENCE_GOLDEN)

from .space_imaging_vectors import GOLDEN as SPACE_IMAGING_GOLDEN
GOLDEN.update(SPACE_IMAGING_GOLDEN)

from .space_dynamics_vectors import GOLDEN as SPACE_DYNAMICS_GOLDEN
GOLDEN.update(SPACE_DYNAMICS_GOLDEN)

from .space_period_vectors import GOLDEN as SPACE_PERIOD_GOLDEN
GOLDEN.update(SPACE_PERIOD_GOLDEN)

from .space_psf_vectors import GOLDEN as SPACE_PSF_GOLDEN
GOLDEN.update(SPACE_PSF_GOLDEN)

from .space_background_vectors import GOLDEN as SPACE_BACKGROUND_GOLDEN
GOLDEN.update(SPACE_BACKGROUND_GOLDEN)

from .space_biweight_vectors import GOLDEN as SPACE_BIWEIGHT_GOLDEN
GOLDEN.update(SPACE_BIWEIGHT_GOLDEN)
from .space_mode_vectors import GOLDEN as SPACE_MODE_GOLDEN
GOLDEN.update(SPACE_MODE_GOLDEN)
from .space_uncertainty_vectors import GOLDEN as SPACE_UNCERTAINTY_GOLDEN
GOLDEN.update(SPACE_UNCERTAINTY_GOLDEN)
from .space_gls_vectors import GOLDEN as SPACE_GLS_GOLDEN
GOLDEN.update(SPACE_GLS_GOLDEN)

from .space_joint_gls_vectors import GOLDEN as SPACE_JOINT_GLS_GOLDEN
GOLDEN.update(SPACE_JOINT_GLS_GOLDEN)

from .space_nbody_vectors import GOLDEN as SPACE_NBODY_GOLDEN
GOLDEN.update(SPACE_NBODY_GOLDEN)

from .space_encounter_vectors import GOLDEN as SPACE_ENCOUNTER_GOLDEN
GOLDEN.update(SPACE_ENCOUNTER_GOLDEN)

from .space_kalman_vectors import GOLDEN as SPACE_KALMAN_GOLDEN
GOLDEN.update(SPACE_KALMAN_GOLDEN)

from .space_rts_vectors import GOLDEN as SPACE_RTS_GOLDEN
GOLDEN.update(SPACE_RTS_GOLDEN)

from .space_precession_vectors import GOLDEN as SPACE_PRECESSION_GOLDEN
GOLDEN.update(SPACE_PRECESSION_GOLDEN)

from .space_kepler_vectors import GOLDEN as SPACE_KEPLER_GOLDEN
GOLDEN.update(SPACE_KEPLER_GOLDEN)
from .space_hyperbolic_vectors import GOLDEN as SPACE_HYPERBOLIC_GOLDEN
GOLDEN.update(SPACE_HYPERBOLIC_GOLDEN)
from .space_parabolic_vectors import GOLDEN as SPACE_PARABOLIC_GOLDEN
GOLDEN.update(SPACE_PARABOLIC_GOLDEN)

from .space_coherence_vectors import GOLDEN as SPACE_COHERENCE_GOLDEN
GOLDEN.update(SPACE_COHERENCE_GOLDEN)

from .space_gnomonic_vectors import GOLDEN as SPACE_GNOMONIC_GOLDEN
GOLDEN.update(SPACE_GNOMONIC_GOLDEN)

from .space_tangent_vector_vectors import GOLDEN as SPACE_TANGENT_VECTOR_GOLDEN
GOLDEN.update(SPACE_TANGENT_VECTOR_GOLDEN)

from .space_sip_vectors import GOLDEN as SPACE_SIP_GOLDEN
GOLDEN.update(SPACE_SIP_GOLDEN)

def fixture(op, seed=271828, scale=1):
    if op==81:
        from .space_sip_vectors import fixture as sip_fixture
        return sip_fixture(op,seed,scale)
    if op==80:
        from .space_tangent_vector_vectors import fixture as tangent_vector_fixture
        return tangent_vector_fixture(op,seed,scale)
    if op==79:
        from .space_gnomonic_vectors import fixture as gnomonic_fixture
        return gnomonic_fixture(op,seed,scale)
    if op==78:
        from .space_coherence_vectors import fixture as coherence_fixture
        return coherence_fixture(op,seed,scale)
    if op==77:
        from .space_parabolic_vectors import fixture as parabolic_fixture
        return parabolic_fixture(op,seed,scale)
    if op==76:
        from .space_hyperbolic_vectors import fixture as hyperbolic_fixture
        return hyperbolic_fixture(op,seed,scale)
    if op==75:
        from .space_kepler_vectors import fixture as kepler_fixture
        return kepler_fixture(op,seed,scale)
    if op==74:
        from .space_precession_vectors import fixture as precession_fixture
        return precession_fixture(op,seed,scale)
    if op==73:
        from .space_rts_vectors import fixture as rts_fixture
        return rts_fixture(op,seed,scale)
    if op==72:
        from .space_kalman_vectors import fixture as kalman_fixture
        return kalman_fixture(op,seed,scale)
    if op==71:
        from .space_encounter_vectors import fixture as encounter_fixture
        return encounter_fixture(op,seed,scale)
    if op in (69,70):
        from .space_nbody_vectors import fixture as nbody_fixture
        return nbody_fixture(op,seed,scale)
    if op==68:
        from .space_joint_gls_vectors import fixture as joint_gls_fixture
        return joint_gls_fixture(op,seed,scale)
    if op==67:
        from .space_gls_vectors import fixture as space_gls_fixture
        return space_gls_fixture(op,seed,scale)
    if 65<=op<=66:
        from .space_uncertainty_vectors import fixture as space_uncertainty_fixture
        return space_uncertainty_fixture(op,seed,scale)
    if op==64:
        from .space_mode_vectors import fixture as space_mode_fixture
        return space_mode_fixture(op,seed,scale)
    if op==63:
        from .space_biweight_vectors import fixture as space_biweight_fixture
        return space_biweight_fixture(op,seed,scale)
    if op>=61:
        from .space_background_vectors import fixture as space_background_fixture
        return space_background_fixture(op,seed,scale)
    if op>=59:
        from .space_psf_vectors import fixture as space_psf_fixture
        return space_psf_fixture(op,seed,scale)
    if op>=57:
        from .space_period_vectors import fixture as space_period_fixture
        return space_period_fixture(op,seed,scale)
    if op>=54:
        from .space_dynamics_vectors import fixture as space_dynamics_fixture
        return space_dynamics_fixture(op,seed,scale)
    if op>=51:
        from .space_imaging_vectors import fixture as space_imaging_fixture
        return space_imaging_fixture(op,seed,scale)
    if op>=48:
        from .space_inference_vectors import fixture as space_inference_fixture
        return space_inference_fixture(op,seed,scale)
    if op>=45:
        from .space_statistics_vectors import fixture as space_statistics_fixture
        return space_statistics_fixture(op,seed,scale)
    if op>=39:
        from .space_search_vectors import fixture as space_search_fixture
        return space_search_fixture(op,seed,scale)
    if op>=37:
        from .triangle_vectors import fixture as triangle_fixture
        return triangle_fixture(op,seed,scale)
    if op>=30:return legacy_fixture(op,seed,scale)
    if op>=14:return float_fixture(op,seed,scale)
    r=random.Random(seed);count=17*scale
    if op==1:return {'images':[[[r.randrange(65536) for _ in range(9)] for _ in range(7)] for _ in range(count)]}
    if op==2:return {'image':[[r.randint(-500,500) for _ in range(23)] for _ in range(19)],'apertures':[[r.randrange(23),r.randrange(19),r.randrange(12),r.randint(-40,40)] for _ in range(count)]}
    if op==3:return dict(times=sorted(r.randrange(100000) for _ in range(137)),flux=[r.randint(-1000,1000) for _ in range(137)],periods=[r.randint(7,600) for _ in range(count)],bins=11)
    if op==4:return dict(samples=[[[r.randint(-1000,1000),r.randint(-1000,1000),r.randrange(101)] for _ in range(97)] for _ in range(count)])
    if op in (5,7,8,9):
        queries=[[r.randint(-10000,10000) for _ in range(3)] for _ in range(count)]
        points=[[r.randint(-10000,10000) for _ in range(3)] for _ in range(149)]
        # Exact boundary, tie, coincident, high-word distance and broadphase precision cases.
        queries[:4]=[[0,0,0],[1000000000]*3,[-1000000000]*3,[999999937,0,0]]
        points[:8]=[[0,0,0],[3000,4000,0],[-3000,-4000,0],[1000000000]*3,[-1000000000]*3,[999999936,0,0],[999999938,0,0],[0,0,5001]]
        d=dict(queries=queries,catalog=points,coordinate_unit='1 nm/tick for molecular data; 1e-9 unit/tick for a supplied unit-sphere catalog')
        if op in (5,7):d['squared_radius']=25000000
        if op==9:d['squared_edges']=[0,1,25000000,25010001,400000000,12000000000000000000]
        return d
    if op==6:return dict(pairs=[[''.join(r.choice('ACGT') for _ in range(r.randrange(1,65))),''.join(r.choice('ACGT') for _ in range(r.randrange(1,65)))] for _ in range(count)])
    if op==10:return dict(spins=[[r.choice((-1,1)) for _ in range(29)] for _ in range(23*scale)])
    if op==11:return dict(samples=[r.randint(-32768,32767) for _ in range(257*scale)],coefficients=[r.randint(-32768,32767) for _ in range(37)])
    if op==12:
        ptr=[0];col=[];values=[]
        for _ in range(count):
            k=r.randrange(9);col.extend(r.randrange(31) for _ in range(k));values.extend(r.randint(-32768,32767) for _ in range(k));ptr.append(len(col))
        return dict(rowptr=ptr,col=col,values=values,vector=[r.randint(-32768,32767) for _ in range(31)])
    if op==13:return dict(triangles=[[[r.randint(-10000,10000) for _ in range(2)] for _ in range(3)] for _ in range(count)])
    raise ValueError(op)


def write_vectors():
    for wid,spec in SPECS.items():
        payload,expected=GOLDEN[spec['opcode']]
        job=prepare(wid,payload)
        assert job.reference==encode(expected),wid
        record=dict(schema='ASTRO_ANALYTIC_TEST_VECTOR_V1',workload_id=wid,
                    provenance='Small analytic examples, derived independently of GPU code; not a research dataset.',
                    payload=payload,expected_output_u32=[x&0xffffffff for x in expected])
        (ROOT/spec['reference_test_vectors']).write_text(json.dumps(record,indent=2)+'\n')
        prepare(wid,fixture(spec['opcode']))
    print(f'CPU_REFERENCE_GOLDEN: {len(SPECS)}/{len(SPECS)} PASS')

if __name__=='__main__':write_vectors()
