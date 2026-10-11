"""Read-only clock evidence and a fail-closed release comparison policy.

Correctness is independent. No historical performance is imported into search.
Unsupported telemetry preserves execution but forbids performance publication.
"""
from __future__ import annotations
import hashlib
import json
import math
import statistics
import threading
import time
from pathlib import Path
from .validity import assess

POLICY = 'ASTRO_RELEASE_BENCHMARK_POLICY_V1'
MIN_WARMUP_MS = 2000
MIN_MEASUREMENT_MS = 1000
MIN_PAIRS = 4
CLOCK_TOLERANCE = .05
MAX_CV = .05
INTERVAL_S = .01


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def governor_state(device):
    """Known driver policy + optional locally installed external controller.

This is not a claim that every possible third-party controller was discovered.
Only read operations; no systemctl writes, SMU commands or sysfs writes.
"""
    mode = read(device / 'power_dpm_force_performance_level')
    driver = (device / 'driver').resolve().name if (device / 'driver').exists() else None
    state = {'driver': driver, 'driver_policy': mode, 'known_controllers': []}
    config = Path('/etc/cyan-skillfish-governor-smu/config.toml')
    if config.exists():
        data = read(config)
        pids = read('/sys/fs/cgroup/system.slice/cyan-skillfish-governor-smu.service/cgroup.procs')
        state['known_controllers'].append({
            'name': 'cyan-skillfish-governor-smu',
            'config_sha256': hashlib.sha256(data.encode()).hexdigest() if data else None,
            'active': bool(pids) if pids is not None else None})
    state['available'] = bool(mode and driver and all(
        x['config_sha256'] and x['active'] is not None for x in state['known_controllers']))
    return state


class Telemetry:
    def __init__(self, sysfs=Path('/sys/class/drm')):
        self.devices = {}
        for card in sorted(sysfs.glob('card[0-9]*')):
            if not card.name[4:].isdigit():
                continue
            device = card / 'device'
            pci = device.resolve().name
            frequency = None
            power = None
            for hw in (device / 'hwmon').glob('hwmon*'):
                for label in hw.glob('freq*_label'):
                    if (read(label) or '').lower() in ('sclk', 'gfx', 'gfxclk', 'graphics'):
                        frequency = label.with_name(label.name.replace('_label', '_input'))
                for label in hw.glob('power*_label'):
                    if read(label) == 'PPT':
                        power = label.with_name(label.name.replace('_label', '_average'))
            self.devices[pci] = dict(path=device, clock=frequency, power=power)
        self.samples = []
        self.stop = threading.Event()
        self.thread = None
        self.before = {}
        self.after = {}

    def __enter__(self):
        self.before = {pci: governor_state(d['path']) for pci, d in self.devices.items()}
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        return self

    def _monitor(self):
        while not self.stop.is_set():
            for pci, d in self.devices.items():
                begin = time.monotonic_ns()
                values = {}
                for key, path in [('sclk_mhz', d['clock']), ('ppt_w', d['power'])]:
                    try:
                        values[key] = int(read(path)) / 1e6 if path else None
                    except (ValueError, TypeError):
                        values[key] = None
                self.samples.append(dict(pci_bus_id=pci, begin_ns=begin,
                                         end_ns=time.monotonic_ns(), **values))
            self.stop.wait(INTERVAL_S)

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join()
        self.after = {pci: governor_state(d['path']) for pci, d in self.devices.items()}

    def evidence(self, native):
        pci = native.get('pci_bus_id')
        samples = [s for s in self.samples if s['pci_bus_id'] == pci]
        warm_end = native.get('warmup_end_ns', 0)
        warm_begin = native.get('warmup_begin_ns', 0)
        result = {
            'device_mapping': 'VULKAN_PCI_BUS_ID' if pci in self.devices else 'UNAVAILABLE',
            'clock_source': str(self.devices[pci]['clock']) if pci in self.devices else None,
            'sample_interval_ms': INTERVAL_S * 1000,
            'measurement': window(samples, native.get('measurement_begin_ns', 0), native.get('measurement_end_ns', 0)),
            'warmup_tail': window(samples, max(warm_begin, warm_end - 1_000_000_000), warm_end),
            'GOVERNOR_STATE': {'before': self.before.get(pci), 'after': self.after.get(pci)},
            'power_scope': 'PPT driver samples; not an isolated SoC rail or validated joules/record',
        }
        return result


def window(samples, begin, end):
    rows = [s for s in samples if begin <= s['begin_ns'] <= s['end_ns'] <= end
            and finite(s.get('sclk_mhz')) and s['sclk_mhz'] > 0]
    duration = (end - begin) / 1e6
    result = dict(begin_ns=begin, end_ns=end, duration_ms=duration, sample_count=len(rows),
                  SCLK_MIN=None, SCLK_AVG=None, SCLK_MAX=None, coverage=0, max_gap_ms=None)
    if len(rows) < 2 or duration <= 0:
        return result
    times = [(s['begin_ns'] + s['end_ns']) / 2 for s in rows]
    clocks = [s['sclk_mhz'] for s in rows]
    gaps = [b - a for a, b in zip(times, times[1:])]
    span = times[-1] - times[0]
    result.update(SCLK_MIN=min(clocks), SCLK_MAX=max(clocks),
                  SCLK_AVG=sum((a + b) / 2 * dt for a, b, dt in zip(clocks, clocks[1:], gaps)) / span,
                  coverage=span / (end - begin),
                  max_gap_ms=max([times[0] - begin, end - times[-1]] + gaps) / 1e6)
    power = [s['ppt_w'] for s in rows if finite(s.get('ppt_w'))]
    result['PPT_AVG_W_INFORMATIONAL'] = statistics.mean(power) if power else None
    return result


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def measurement_metadata(row, artifact, spec_sha256, telemetry, kind):
    return dict(
        schema=POLICY, evidence_kind=kind, publication_status='INFORMATIONAL',
        MEASUREMENT_DURATION=row.get('wall_ms'), WARMUP_DURATION=row.get('warmup_wall_ms'),
        duration_unit='ms', clock_unit='MHz',
        KERNEL_HASH=artifact['source_sha256'], SPIRV_HASH=artifact['spirv_sha256'],
        INPUT_HASH=row['input_sha256'], MATHSPEC_HASH=spec_sha256,
        LOCAL=artifact['local'], PACK=artifact['pack'], backend=artifact['backend'],
        device_uuid=row.get('device_uuid'), pci_bus_id=row.get('pci_bus_id'),
        timing_protocol=row.get('timing_protocol'), metric_scope=row['metric_scope'],
        repeats_per_batch=row['repeats'], records=row['records'], partition=row['partition'],
        reference_sha256=row['cpu_reference_sha256'], driver_version=row.get('driver_version'),
        SCLK_MIN=telemetry['measurement']['SCLK_MIN'],
        SCLK_AVG=telemetry['measurement']['SCLK_AVG'],
        SCLK_MAX=telemetry['measurement']['SCLK_MAX'],
        GOVERNOR_STATE=telemetry['GOVERNOR_STATE'], telemetry=telemetry,
        PERFORMANCE_COMPARISON_VALID=False,
        reason='PAIR_AND_REPEATED_EVIDENCE_REQUIRED' if kind == 'RELEASE_CANDIDATE' else 'QUICK_SANITY_ONLY')


def clock_window_valid(w):
    if not w or w.get('sample_count', 0) < 20 or w.get('coverage', 0) < .90:
        return False
    if not finite(w.get('max_gap_ms')) or w['max_gap_ms'] > 50:
        return False
    values = [w.get(k) for k in ('SCLK_MIN', 'SCLK_AVG', 'SCLK_MAX')]
    return all(finite(v) and v > 0 for v in values) and values[0] <= values[1] <= values[2]


def relative_difference(a, b):
    return abs(a - b) / min(a, b)


def run_reasons(row):
    reasons = list(assess(row)['reasons'])
    proof = row.get('benchmark', {})
    if proof.get('schema') != POLICY:
        return ['INVALID_MISSING_PROVENANCE']
    if proof.get('evidence_kind') != 'RELEASE_CANDIDATE':
        reasons.append('INVALID_QUICK_SANITY_ONLY')
    for key in ('KERNEL_HASH', 'SPIRV_HASH', 'INPUT_HASH', 'MATHSPEC_HASH', 'reference_sha256', 'telemetry_sha256'):
        value = proof.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            reasons.append('INVALID_MISSING_PROVENANCE')
    for key in ('LOCAL', 'PACK', 'repeats_per_batch', 'records'):
        if type(proof.get(key)) is not int or proof[key] <= 0:
            reasons.append('INVALID_MISSING_PROVENANCE')
    if not all(proof.get(k) for k in ('device_uuid', 'pci_bus_id', 'metric_scope', 'backend', 'partition', 'driver_version')):
        reasons.append('INVALID_MISSING_PROVENANCE')
    if proof.get('timing_protocol') != 'RESIDENT_BATCH_LOOP_V1':
        reasons.append('INVALID_TIMING_SCOPE')
    if not finite(proof.get('MEASUREMENT_DURATION')) or proof['MEASUREMENT_DURATION'] < MIN_MEASUREMENT_MS:
        reasons.append('INVALID_MEASUREMENT_DURATION')
    if not finite(proof.get('WARMUP_DURATION')) or proof['WARMUP_DURATION'] < MIN_WARMUP_MS:
        reasons.append('INVALID_WARMUP_DURATION')
    if row.get('status') != 'PASS_ZERO_BIT' or any(row.get(k, {}).get('pass_exact') is not True
            or row.get(k, {}).get('differing_bits') != 0 for k in ('validation', 'warmup_validation')):
        reasons.append('INVALID_CORRECTNESS')
    for key in ('geometry_validation', 'warmup_geometry_validation'):
        if (key in row or row.get('workload_id') == 'RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1') and (
                row.get(key, {}).get('pass_exact') is not True or row.get(key, {}).get('differing_bits') != 0):
            reasons.append('INVALID_CORRECTNESS')
    if not finite(row.get('records_per_s')) or row['records_per_s'] <= 0:
        reasons.append('INVALID_RATE')
    telemetry = proof.get('telemetry', {})
    measure, warmup = telemetry.get('measurement'), telemetry.get('warmup_tail')
    if telemetry.get('device_mapping') != 'VULKAN_PCI_BUS_ID' or not all(clock_window_valid(w) for w in (measure, warmup)):
        reasons.append('INVALID_MISSING_CLOCK_EVIDENCE')
    else:
        if any(relative_difference(w['SCLK_MIN'], w['SCLK_MAX']) > CLOCK_TOLERANCE for w in (measure, warmup)):
            reasons.append('INVALID_UNSTABLE_CLOCK')
        if relative_difference(measure['SCLK_AVG'], warmup['SCLK_AVG']) > CLOCK_TOLERANCE:
            reasons.append('INVALID_CLOCK_STATE_MISMATCH')
    governor = proof.get('GOVERNOR_STATE', {})
    if not isinstance(governor.get('before'), dict) or not governor['before'].get('available'):
        reasons.append('INVALID_MISSING_GOVERNOR_STATE')
    if governor.get('before') != governor.get('after'):
        reasons.append('INVALID_GOVERNOR_STATE_MISMATCH')
    if clock_window_valid(measure) and any(proof.get(k) != measure[k] for k in ('SCLK_MIN', 'SCLK_AVG', 'SCLK_MAX')):
        reasons.append('INVALID_CLOCK_PROVENANCE')
    for phase, field in [('measurement', 'MEASUREMENT_DURATION')]:
        w=telemetry.get(phase, {})
        if not finite(w.get('duration_ms')) or not finite(proof.get(field)) or abs(w['duration_ms']-proof[field]) > .01:
            reasons.append('INVALID_TIMING_PROVENANCE')
    return sorted(set(reasons))


def evidence_reasons(row):
    """Re-read stored bytes/trace; a hand-edited summary is not evidence."""
    proof=row.get('benchmark', {})
    reasons=[]
    try:
        for path_key,hash_key in [('kernel_path','KERNEL_HASH'),('spirv_path','SPIRV_HASH'),('telemetry_path','telemetry_sha256')]:
            data=Path(proof[path_key]).read_bytes()
            if hashlib.sha256(data).hexdigest()!=proof[hash_key]:reasons.append('INVALID_EVIDENCE_HASH')
        if hashlib.sha256(Path(proof['native_path']).read_bytes()).hexdigest()!=row['native_binary_sha256']:
            reasons.append('INVALID_EVIDENCE_HASH')
        output=Path(row['output_path']);reference=(output.parent/'cpu-reference.bin').read_bytes()
        if hashlib.sha256(reference).hexdigest()!=proof['reference_sha256'] or hashlib.sha256((output.parent/'input.bin').read_bytes()).hexdigest()!=proof['INPUT_HASH']:
            reasons.append('INVALID_EVIDENCE_HASH')
        if output.read_bytes()!=reference or Path(str(output)+'.warmup').read_bytes()!=reference:
            reasons.append('INVALID_CORRECTNESS')
        if 'geometry_validation' in row or row.get('workload_id')=='RT_DYNAMIC_NEAREST_TRIANGLE_HIT_V1':
            geometry=(output.parent/'geometry-reference.bin').read_bytes()
            if any(Path(str(output)+s).read_bytes()!=geometry for s in ('.geometry','.geometry.warmup')):
                reasons.append('INVALID_CORRECTNESS')
        native=json.loads((output.parent/'native.json').read_text())
        if any(row.get(k) != value for k, value in native.items()):
            reasons.append('INVALID_NATIVE_EVIDENCE_PROVENANCE')
        samples=json.loads(Path(proof['telemetry_path']).read_text())
        samples=[s for s in samples if s['pci_bus_id']==proof['pci_bus_id']]
        timing=[row[k] for k in ('process_begin_ns','warmup_begin_ns','warmup_end_ns','measurement_begin_ns','measurement_end_ns','process_end_ns')]
        if timing!=sorted(timing) or any(type(t) is not int or t<=0 for t in timing):
            reasons.append('INVALID_TIMING_PROVENANCE')
        if abs((row['warmup_end_ns']-row['warmup_begin_ns'])/1e6-proof['WARMUP_DURATION'])>.01:
            reasons.append('INVALID_TIMING_PROVENANCE')
        measure=window(samples,row['measurement_begin_ns'],row['measurement_end_ns'])
        warmup=window(samples,max(row['warmup_begin_ns'],row['warmup_end_ns']-1_000_000_000),row['warmup_end_ns'])
        if measure!=proof['telemetry']['measurement'] or warmup!=proof['telemetry']['warmup_tail']:
            reasons.append('INVALID_CLOCK_PROVENANCE')
        expected=row['records']*row['repeats']*row['measurement_batches']*1000/row['wall_ms']
        if not math.isclose(expected,row['records_per_s'],rel_tol=1e-9):reasons.append('INVALID_RATE_PROVENANCE')
    except (KeyError,OSError,ValueError,TypeError,ZeroDivisionError):
        reasons.append('INVALID_MISSING_EVIDENCE_FILES')
    return sorted(set(reasons))


def compare_release(pairs):
    return _compare_rules(pairs,verify_files=True)


def _compare_rules(pairs,verify_files=False):
    """Pairs must be an ordered, serialized AB/BA acquisition, not two tables.

    Invalid comparisons deliberately contain no percentage, including a raw one.
    Percentages become available only after every prerequisite has passed.
    """
    result = dict(schema=POLICY, PERFORMANCE_COMPARISON_VALID=False,
                  verdict='INVALID_COMPARISON', publication_status='INFORMATIONAL',
                  gain_pct=None, reasons=[], pairs=len(pairs), statistics={})
    reasons = []
    if len(pairs) < MIN_PAIRS:
        reasons.append('INVALID_INSUFFICIENT_PAIRS')
    rows = []
    previous_end = 0
    expected_contract = None
    session = None
    keys = ('INPUT_HASH', 'MATHSPEC_HASH', 'LOCAL', 'PACK', 'backend', 'device_uuid', 'pci_bus_id',
            'driver_version', 'metric_scope', 'timing_protocol', 'repeats_per_batch', 'records',
            'partition', 'reference_sha256')
    for index, pair in enumerate(pairs):
        order = ['old', 'new'] if index % 2 == 0 else ['new', 'old']
        if pair.get('order') != order:
            reasons.append('INVALID_PAIR_ORDER')
        for side in order:
            row = pair.get(side, {})
            rows.append((side, row))
            reasons.extend(run_reasons(row))
            if verify_files:reasons.extend(evidence_reasons(row))
            p = row.get('benchmark', {})
            acquisition=row.get('benchmark_pair', {})
            identity=(acquisition.get('session_id'),acquisition.get('clock_domain'))
            if not all(identity) or acquisition.get('side')!=side or acquisition.get('pair_index')!=index:
                reasons.append('INVALID_PAIR_PROVENANCE')
            if session is None:session=identity
            elif session!=identity:reasons.append('INVALID_PAIR_PROVENANCE')
            contract = (row.get('workload_id'), {key: p.get(key) for key in keys})
            if expected_contract is None:
                expected_contract = contract
            elif contract != expected_contract:
                reasons.append('INVALID_MEASUREMENT_CONTRACT_MISMATCH')
            # A kernel or native binary may change between versions. Its hash is
            # mandatory, and must remain fixed within each side of this session.
            start, end = row.get('process_begin_ns', 0), row.get('process_end_ns', 0)
            if not 0 < previous_end <= start < end and previous_end:
                reasons.append('INVALID_PAIR_TIMING')
            if not 0 < start < end or (previous_end and start - previous_end > 10_000_000_000):
                reasons.append('INVALID_PAIR_TIMING')
            previous_end = end
        a, b = pair.get('old', {}).get('benchmark', {}), pair.get('new', {}).get('benchmark', {})
        if all(finite(x.get('SCLK_AVG')) and x['SCLK_AVG'] > 0 for x in (a, b)):
            if any(relative_difference(a[k], b[k]) > CLOCK_TOLERANCE for k in ('SCLK_MIN', 'SCLK_AVG', 'SCLK_MAX')
                   if all(finite(x.get(k)) and x[k] > 0 for x in (a, b))):
                reasons.append('INVALID_CLOCK_STATE_MISMATCH')
        if a.get('GOVERNOR_STATE') != b.get('GOVERNOR_STATE'):
            reasons.append('INVALID_GOVERNOR_STATE_MISMATCH')
    for side in ('old', 'new'):
        values = [r for s, r in rows if s == side]
        fingerprints = {(r.get('benchmark', {}).get('KERNEL_HASH'), r.get('benchmark', {}).get('SPIRV_HASH'), r.get('native_binary_sha256')) for r in values}
        if len(fingerprints) != 1 or any(not v[2] for v in fingerprints):
            reasons.append('INVALID_ARTIFACT_CHANGED_WITHIN_SIDE')
        rates = [r['records_per_s'] for r in values if finite(r.get('records_per_s')) and r['records_per_s'] > 0]
        if rates:
            cv = statistics.stdev(rates) / statistics.mean(rates) if len(rates) > 1 else None
            result['statistics'][side] = dict(samples=len(rates), median=statistics.median(rates),
                variance=statistics.variance(rates) if len(rates) > 1 else None, coefficient_of_variation=cv)
            if cv is None or cv > MAX_CV:
                reasons.append('INCONCLUSIVE_HIGH_VARIANCE')
    reasons = sorted(set(reasons))
    result['reasons'] = reasons
    if reasons:
        if all(r.startswith('INCONCLUSIVE') for r in reasons):
            result['verdict'] = 'INCONCLUSIVE'
        return result
    result.update(PERFORMANCE_COMPARISON_VALID=True, publication_status='RELEASE_EVIDENCE')
    result['gain_pct'] = 100 * (result['statistics']['new']['median'] / result['statistics']['old']['median'] - 1)
    result['verdict'] = 'REGRESSION' if result['gain_pct'] < -10 else 'IMPROVEMENT' if result['gain_pct'] > 10 else 'NO_MATERIAL_CHANGE'
    result['verdict_scope'] = 'Local paired benchmark; 10% material-change threshold; not universal performance or a statistical confidence interval'
    return result
