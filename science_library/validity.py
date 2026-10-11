"""Native GPU evidence gates; correctness, validity and confirmation stay separate.

Thresholds are local measurement policy, not hardware performance predictions.
No power/temperature value participates in these decisions.
"""
import math


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def positive_int(value):
    return type(value) is int and value > 0


def correctness_pass(row):
    fields = ['validation', 'warmup_validation']
    if row.get('workload_id') == 'RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1' or 'geometry_validation' in row:
        fields += ['geometry_validation', 'warmup_geometry_validation']
    return row.get('status') == 'PASS_ZERO_BIT' and all(
        isinstance(row.get(k), dict) and row[k].get('pass_exact') is True
        and row[k].get('differing_bits') == 0 for k in fields)


def assess(row, contract=None):
    """Recompute the verdict from evidence, never accept a saved PASS flag."""
    contract = contract or dict(warmup_ms=2000, measurement_ms=1000)
    reasons = []
    if not isinstance(row, dict):
        row = {}
    correct = correctness_pass(row)
    if not correct:
        reasons.append('INVALID_CORRECTNESS')
    proof = row.get('benchmark') if isinstance(row.get('benchmark'), dict) else {}
    if proof.get('evidence_kind') not in ('RELEASE_CANDIDATE', 'SUSTAINED_CANDIDATE'):
        reasons.append('INVALID_QUICK_SANITY_ONLY')
    if type(row.get('device_type')) is not int or row['device_type'] not in (1, 2, 3):
        reasons.append('INVALID_NON_HARDWARE_DEVICE')
    if (row.get('native_evidence_schema') != 'ASTRO_NATIVE_TIMING_V2'
            or row.get('gpu_time_source') != 'VULKAN_TIMESTAMP_QUERY'
            or row.get('gpu_time_scope') not in ('batch-including-barriers-and-AS-maintenance', 'resource-compute-and-barriers')
            or row.get('timing_protocol') != 'RESIDENT_BATCH_LOOP_V1'):
        reasons.append('INVALID_NATIVE_GPU_EVIDENCE')
    wall, gpu = row.get('wall_ms'), row.get('gpu_ms')
    ratio = gpu / wall if finite(gpu) and finite(wall) and wall > 0 else None
    for key, minimum in [('wall_ms', contract['measurement_ms']), ('warmup_wall_ms', contract['warmup_ms'])]:
        if not finite(row.get(key)) or row[key] < minimum:
            reasons.append('INVALID_' + key.upper())
    if ratio is None or not .50 <= ratio <= 1.01:
        reasons.append('INVALID_GPU_WALL_RATIO')
    for key in ('gpu_wall_ratio', 'queue_duty_pct'):
        expected = ratio * (100 if key == 'queue_duty_pct' else 1) if ratio is not None else None
        if expected is None or not finite(row.get(key)) or not math.isclose(row[key], expected, rel_tol=1e-8):
            reasons.append('INVALID_DUTY_EVIDENCE')
    if not finite(row.get('records_per_s')) or row['records_per_s'] <= 0:
        reasons.append('INVALID_RATE')
    counts = ('dispatch_count', 'queue_submit_count', 'measurement_batches', 'repeats', 'records')
    if any(not positive_int(row.get(k)) for k in counts):
        reasons.append('INVALID_EXECUTION_COUNTS')
    elif row['queue_submit_count'] != row['measurement_batches'] or row['measurement_batches'] < 2 or row['dispatch_count'] < row['repeats'] * row['measurement_batches']:
        reasons.append('INVALID_EXECUTION_COUNTS')
    if finite(wall) and wall > 0 and all(positive_int(row.get(k)) for k in ('records','repeats','measurement_batches')):
        expected = row['records'] * row['repeats'] * row['measurement_batches'] * 1000 / wall
        if not finite(row.get('records_per_s')) or not math.isclose(row['records_per_s'], expected, rel_tol=1e-8):
            reasons.append('INVALID_RATE_PROVENANCE')
    trace = row.get('measurement_trace')
    try:
        if not isinstance(trace, list) or len(trace) < 2 or len(trace) != row['queue_submit_count']:
            raise ValueError('missing trace')
        begin, end = row['measurement_begin_ns'], row['measurement_end_ns']
        if not positive_int(begin) or not positive_int(end) or end <= begin or not finite(wall) or abs((end-begin)/1e6-wall) > .01:
            raise ValueError('window')
        previous = begin
        for i, batch in enumerate(trace):
            if not all(positive_int(batch.get(k)) for k in ('begin_ns','end_ns','dispatches')) or not previous <= batch['begin_ns'] < batch['end_ns'] <= end:
                raise ValueError('ordering')
            previous = batch['end_ns']
            if any(not finite(batch.get(k)) or batch[k] < 0 for k in ('gpu_ms','record_ms','submit_ms','retire_ms','query_ms')):
                raise ValueError('invalid timing')
            if batch['gpu_ms'] > (batch['end_ns'] - batch['begin_ns']) / 1e6 * 1.01:
                raise ValueError('impossible batch GPU time')
            gap = batch.get('gap_before_ms')
            if not finite(gap) or (gap != -1 if i == 0 else gap < 0):
                raise ValueError('invalid gap')
        if sum(b['dispatches'] for b in trace) != row['dispatch_count'] or not finite(gpu) or not math.isclose(sum(b['gpu_ms'] for b in trace), gpu, rel_tol=1e-8):
            raise ValueError('totals')
        gaps = row['inter_dispatch_gaps']
        if (gaps.get('scope') != 'between-batches-GPU-timestamps' or gaps.get('count') != len(trace)-1
                or not finite(gaps.get('sum_ms')) or not finite(gaps.get('max_ms'))
                or not math.isclose(sum(b['gap_before_ms'] for b in trace[1:]), gaps['sum_ms'], rel_tol=1e-8, abs_tol=1e-9)
                or not math.isclose(max(b['gap_before_ms'] for b in trace[1:]), gaps['max_ms'], rel_tol=1e-8, abs_tol=1e-9)
                or gaps['sum_ms'] + gpu > wall * 1.01):
            raise ValueError('gaps')
    except (KeyError, TypeError, ValueError):
        reasons.append('INVALID_NATIVE_TRACE')
    telemetry = proof.get('telemetry') if isinstance(proof.get('telemetry'), dict) else {}
    measure = telemetry.get('measurement') if isinstance(telemetry.get('measurement'), dict) else {}
    if (telemetry.get('device_mapping') != 'VULKAN_PCI_BUS_ID'
            or not positive_int(measure.get('sample_count')) or measure['sample_count'] < 20
            or not finite(measure.get('coverage')) or not .9 <= measure['coverage'] <= 1
            or not finite(measure.get('max_gap_ms')) or not 0 <= measure['max_gap_ms'] <= 50
            or not finite(measure.get('duration_ms')) or not finite(wall) or abs(measure['duration_ms']-wall) > .01):
        reasons.append('INVALID_TELEMETRY_COVERAGE')
    return dict(CORRECTNESS='PASS' if correct else 'FAIL',
                PERFORMANCE_VALIDITY='PASS' if not reasons else 'INVALID',
                SUSTAINED_PERFORMANCE='CONFIRMATION_REQUIRED' if not reasons else 'UNVERIFIED',
                reasons=sorted(set(reasons)), gpu_wall_ratio=ratio,
                publication_status='INFORMATIONAL', production_ready=False)


def confirmed(rows, contract=None):
    """All initial/heldout/actual windows must pass; a single burst cannot confirm."""
    if len(rows) < 3 or not all(assess(row, contract)['PERFORMANCE_VALIDITY'] == 'PASS' for row in rows):
        return False
    keys = ('KERNEL_HASH', 'SPIRV_HASH', 'device_uuid', 'pci_bus_id', 'LOCAL', 'PACK', 'backend', 'driver_version', 'repeats_per_batch')
    first = rows[0].get('benchmark', {})
    if not all(first.get(k) is not None for k in keys):
        return False
    previous_end = 0
    paths = set()
    for row in rows:
        if (row['measurement_begin_ns'] < previous_end or not row.get('output_path')
                or row['output_path'] in paths or any(row['benchmark'].get(k) != first[k] for k in keys)):
            return False
        previous_end = row['measurement_end_ns']
        paths.add(row['output_path'])
    return True
