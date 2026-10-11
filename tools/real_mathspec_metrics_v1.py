"""Experimental accounting of useful canonical work, never hardware instructions.

This module does not change a MathSpec, oracle, shader or production search.
Counts describe one complete supplied job, and are frozen before timing.
"""
from collections import Counter
from contextlib import contextmanager
import hashlib
import json

from science_library.catalog import SPECS
from science_library.reference import prepare
from science_library import f32


# Each output record has the following scientific meaning in the canonical
# contract. Exceptions below count input work, not padded output slots.
UNITS = dict(enumerate(('',
    'image_moment_set', 'aperture_query', 'period_bin_statistics',
    'weighted_fit_statistics', 'catalog_pair_evaluation', 'DP_cell',
    'contact_pair_evaluation', 'squared_distance', 'radial_pair_classification',
    'lattice_site_observation', 'filtered_sample', 'sparse_matrix_row',
    'orientation_predicate', 'convolution_sample', 'correlation_lag',
    'normalized_correlation_lag', 'complex_transform', 'weighted_linear_fit',
    'transformed_vector', 'integrated_curve', 'directed_body_interaction',
    'body_drift_step', 'image_centroid', 'periodogram_transform',
    'kmer_window_query', 'Lennard_Jones_pair', 'heat_cell_update',
    'resampled_sample', 'matrix_output_element', 'FFT256_window',
    'convolution_sample', 'cross_correlation_lag', 'normalized_correlation_lag',
    'catalog_row_filtered', 'Welch_spectrum', 'whitened_segment_spectrum',
    'nearest_triangle_ray', 'nearest_triangle_ray_frame', 'trial_frequency',
    'BLS_trial_period', 'peak_mask_pixel', 'object_template_fit',
    'spherical_coordinate', 'integrated_trajectory', 'bootstrap_replicate',
    'sigma_clipped_window', 'segmented_image', 'percentile_interval',
    'Monte_Carlo_tail_query', 'two_template_fit', 'background_query',
    'component_node_merge', 'source_catalog_entry', 'J2_acceleration',
    'adaptive_orbit_trajectory', 'orbit_diagnostic_state',
    'multiharmonic_trial_frequency', 'phase_dispersion_trial_period',
    'PSF_scan_center', 'nonnegative_template_fit', 'IDW_query',
    'median_mesh_center', 'biweight_window', 'half_sample_mode_window',
    'noise_map_pixel', 'linear_flux_covariance', 'correlated_template_fit',
    'joint_template_fit', 'coupled_Nbody_trajectory', 'Nbody_invariant_system',
    'swept_sphere_pair', 'Kalman_state_update', 'RTS_smoother_update',
    'precessed_epoch_vector', 'elliptic_orbit_state', 'hyperbolic_orbit_state',
    'parabolic_orbit_state', 'coherence_bin', 'gnomonic_projection',
    'tangent_unit_vector', 'SIP_offset_transform')))
UNITS.pop(0)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


@contextmanager
def count_canonical_fp32():
    """Count public RN32 primitives, excluding nested sub->add implementation.

    Only used by this serial experimental process. Wrappers preserve returned
    bits and count cached sqrt *requests*, not cache misses. CPU big-integer
    implementation operations and GPU soft32 instructions are not counted.
    """
    names = ('add', 'sub', 'mul', 'div', 'sqrt', 'neg')
    originals = {name: getattr(f32, name) for name in names}
    counts = Counter(); depth = 0

    def wrapper(name, original):
        def call(*args):
            nonlocal depth
            if depth == 0:
                counts[name] += 1
            depth += 1
            try:
                return original(*args)
            finally:
                depth -= 1
        return call

    try:
        for name, original in originals.items():
            setattr(f32, name, wrapper(name, original))
        yield counts
    finally:
        for name, original in originals.items():
            setattr(f32, name, original)


def work_definition(job):
    op = SPECS[job.workload_id]['opcode']; p = job.payload
    count = job.records; formula = 'canonical output record count'
    if op in (5, 7, 8, 9):
        count = len(p['queries']) * len(p['catalog'])
        formula = 'len(queries)*len(catalog); once per pair, independent of bins/path'
    elif op == 6:
        count = sum(len(a)*len(b) for a, b in p['pairs'])
        formula = 'sum(len(sequence_A)*len(sequence_B)); no DP boundary cells'
    elif op == 21:
        count = len(p['bodies'])*(len(p['bodies'])-1)
        formula = 'N*(N-1) directed non-self interactions'
    elif op == 25:
        count = sum(max(0, len(s)-len(q)+1) for s in p['sequences'] for q in p['kmers'])
        formula = 'sum(max(0,len(sequence)-len(kmer)+1)) over supplied sequence/query pairs'
    elif op == 34:
        count = len(p['packed_rows']); formula = 'input catalog rows, not count header/padded output'
    elif op == 35:
        count = 1; formula = 'one full 129-bin Welch spectrum per supplied stream'
    return dict(unit=UNITS[op], count_per_job=count, formula=formula,
                records_per_job=job.records, repeated_input=True,
                scope='Repeated completion of the same canonical task; not unique research credit')


def operations(job):
    """Useful typed primitive counts. Unknown types/algorithms stay unavailable."""
    op = SPECS[job.workload_id]['opcode']; p = job.payload
    typed = {}; detail = {}; source = 'UNAVAILABLE'; macs = None
    # All of these references use the scalar RN32 API for their FP mathematics.
    # Vector spectral expansion and exact-rational triangle algorithms are
    # explicitly excluded: counting their low-level expansion would inflate work.
    if 14 <= op <= 29 and op != 25 or 39 <= op <= 81:
        prepare(job.workload_id, p)  # settle imports/constants outside accounting
        with count_canonical_fp32() as counts:
            counted = prepare(job.workload_id, p)
        if counted.reference != job.reference or counted.input_bytes != job.input_bytes:
            raise AssertionError('operation observer changed canonical bits')
        detail = dict(counts)
        typed['FP32'] = sum(counts[k] for k in ('add', 'sub', 'mul', 'div'))
        source = 'Observed public RN32 primitive requests in canonical CPU reference on this exact input'
    elif op in (30, 31, 32):
        if op == 30:
            butterflies = job.records * 128 * 8
            detail = dict(mul=4*butterflies, add=3*butterflies, sub=3*butterflies)
            source = 'legacy_reference.py/vector_f32.py radix-2 FFT: 1024 butterflies/window, 4 mul + 6 add/sub'
        elif op == 31:
            macs = 9*len(p['strain']); detail = dict(mul=macs, add=macs)
            source = 'legacy_reference.py op31: nine clamped taps per input sample, sum starts at zero'
        else:
            macs = sum(len(p['h1'])-abs(lag) for lag in range(-64, 65))
            detail = dict(mul=macs, add=macs-129)
            source = 'legacy_reference.py op32/vector_f32.total: sum(N-abs(lag)), lag=-64..64; cumsum has length-1 additions per nonempty lag'
        typed['FP32'] = sum(detail.values())
    elif op == 6:
        cells = work_definition(job)['count_per_job']
        typed['INT32'] = 3*cells
        detail = dict(add=cells, sub=2*cells)
        source = 'reference.py op6: one score add and two gap subtracts per DP cell; max/comparison separate'
    elif op in (11, 12):
        macs = sum(min(i+1, len(p['coefficients'])) for i in range(len(p['samples']))) if op == 11 else len(p['values'])
        typed = {'INT32': macs, 'INT64': macs}
        detail = {'INT16xINT16_to_INT32_mul': macs, 'INT64_add': macs}
        source = 'reference.py: actual nonzero-padding taps/CSR entries, signed16 product fits32 and widens into64 accumulator'
    elif op == 10:
        typed['INT32'] = 3*job.records
        detail = dict(add=job.records, neg=job.records, mul=job.records)
        source = 'reference.py op10 local energy: neighbor sum, spin negation, multiply; magnetization copy excluded'
    elif op == 13:
        typed['INT32'] = 7*job.records
        detail = dict(sub=5*job.records, mul=2*job.records)
        source = 'reference.py op13 determinant: four coordinate differences, two products, one subtraction; sign separate'
    return dict(status='AVAILABLE_TYPED_ARITHMETIC_SUBSET' if typed else 'UNAVAILABLE',
                useful_ops_per_job_by_type=typed or None, canonical_primitive_counts=detail or None,
                MACs_per_job=macs, provenance=source,
                unsupported_types='UNAVAILABLE, not zero',
                FMA_convention='FMA=2 mathematical ops; RN32 oracle uses separately rounded mul/add, no fused FMA claim',
                exclusions='Address/control/compare/bitcast/packing ops omitted. sqrt and sign requests shown separately for FP32; no instruction estimate.',
                hardware_executed_instructions='UNAVAILABLE',
                scope='Canonical algorithm primitive arithmetic, input-dependent; same frozen count for every executor. No sum across datatypes.')


def rates(work, ops, row, pipeline_ms=None):
    correct = row.get('status') == 'PASS_ZERO_BIT'
    executions = row.get('repeats', 0)*row.get('measurement_batches', 0)
    wall = row.get('wall_ms', 0)
    ok = correct and executions > 0 and wall > 0
    factor = executions*1000/wall if ok else None
    units = work['count_per_job']
    return dict(correctness='PASS' if correct else 'FAIL', unit=work['unit']+'/s',
                completed_jobs=executions if correct else 0,
                real_work_units_per_s=units*factor if ok else None,
                effective_ops_per_s_by_type={k: v*factor for k, v in (ops.get('useful_ops_per_job_by_type') or {}).items()} if ok else {},
                effective_ops_status=ops['status'] if ok else 'UNAVAILABLE',
                legacy_science_per_s=row.get('records_per_s') if correct else None,
                end_to_end_one_job_units_per_s=units*1000/pipeline_ms if correct and pipeline_ms and pipeline_ms > 0 else None,
                accepted_sustained_performance=False, publication='QUICK_DIAGNOSTIC_ONLY')
