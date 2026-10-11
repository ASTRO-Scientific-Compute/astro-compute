"""Four canonical tasks, real recovered kernels, no production promotion."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import stat
import subprocess
import tempfile
import time

from science_library.catalog import SPECS
from science_library.reference import prepare, compare_bytes
from science_library.vectors import fixture
from science_library.performance import Telemetry
from tools.real_mathspec_metrics_v1 import work_definition, operations
from .limits import WORKLOADS, RunAdmission, select_workloads, require_workload
from . import recovered_codegen as generator
from .support import save

ROOT = Path(__file__).resolve().parents[1]


def command(args, timeout=90):
    return subprocess.run([str(x) for x in args], check=True, capture_output=True,
                          text=True, timeout=timeout).stdout


def build(directory):
    directory = Path(directory)
    runner, caps = directory / 'science-runner', directory / 'capabilities'
    include = ROOT / 'gpu_maxout_lab/native'
    command(['c++', '-std=c++17', '-O2', '-I', include, '-I',
             ROOT / 'runtime/native_science_library',
             ROOT / 'runtime/native_universal_search/science_runner.cpp',
             '-lvulkan', '-o', runner])
    command(['c++', '-std=c++17', '-O2', include / 'vk_caps.cpp', '-lvulkan', '-o', caps])
    return runner, caps


@contextmanager
def gpu_lock():
    # Shared across copies of this demo; never follow a lock-file symlink.
    path = Path(tempfile.gettempdir()) / f'astro-gpu-demo-{os.getuid()}.lock'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode):
            raise RuntimeError('Unsafe GPU demo lock')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(fd)


def acceptance(job, actual, warmup):
    """A rate can only be attached to a complete canonical byte match."""
    require_workload(job.workload_id)
    checks = [compare_bytes(job.reference, blob) for blob in (actual, warmup)]
    return all(c['pass_exact'] is True and c['differing_bits'] == 0 for c in checks)


def configs(job, caps):
    # Same input and canonical operation graph for both families.
    for family in ('DIRECT', 'TILED'):
        config = dict(family=family, local_size=64, pack=1)
        if generator.legal(job, config, caps):
            yield config


def compile_all(directory):
    """Build-only verification: no device selection, timestamps or GPU claims."""
    caps = {'limits': {'max_compute_workgroup_invocations': 64,
                       'max_compute_shared_memory_size': 32768}}
    for wid in WORKLOADS:
        job = prepare(wid, fixture(SPECS[wid]['opcode'], seed=271828, scale=1))
        for config in configs(job, caps):
            generator.compile_candidate(job, config, Path(directory) / (wid + config['family']), caps)


def check_native_rejections(runner, directory):
    # Both errors must occur before instance/device initialization; CI does not
    # need a GPU to verify the native boundary.
    packet = Path(directory) / 'rejected-packet.bin'
    wid = 'SPACE_IMAGE_MOMENTS_U16_V1'
    packet.write_bytes(prepare(wid, fixture(SPECS[wid]['opcode'])).input_bytes)
    common = [str(runner), '--input', str(packet), '--spv', 'unused.spv', '--output', 'unused.bin']
    for extra, reason in ((['--local', '0'], 'invalid demo configuration'),
                          ([], 'outside four-task demo allowlist')):
        cp = subprocess.run(common + extra, capture_output=True, text=True, timeout=10)
        if cp.returncode != 2 or reason not in cp.stderr:
            raise AssertionError('Native admission rejection failed')


def execute(job, artifact, runner, directory, gpu):
    generator.check_job_binding(job, artifact)
    inp, out = directory / 'input.bin', directory / 'output.bin'
    inp.write_bytes(job.input_bytes)
    args = [runner, '--input', inp, '--output', out, '--spv', artifact['spirv'],
            '--gpu', gpu, '--local', artifact['local'], '--pack', artifact['pack'],
            '--repeats', 8, '--warmup-ms', 2000, '--measurement-ms', 1000]
    if artifact['dispatch_mode'] == 'WORKGROUP_PER_RECORD':
        args.append('--workgroup-per-record')
    begin = time.monotonic()
    with Telemetry() as telemetry:
        native = json.loads(command(args, timeout=30))
    correct = acceptance(job, out.read_bytes(), Path(str(out) + '.warmup').read_bytes())
    generator.check_job_binding(job, artifact)
    elapsed = time.monotonic() - begin
    evidence = telemetry.evidence(native)
    return native, correct, evidence, elapsed


def compact_trial(job, config, native, correct, telemetry, pipeline_seconds):
    work, ops = work_definition(job), operations(job)
    wall = native.get('wall_ms', 0) / 1000
    gpu = native.get('gpu_ms', 0) / 1000
    repeats = native.get('repeats', 0) * native.get('measurement_batches', 0)
    measurable = (correct and repeats > 0 and wall > 0 and gpu > 0
                  and math.isfinite(wall) and math.isfinite(gpu))
    units = work['count_per_job'] * repeats
    window = telemetry['measurement']
    # A positive physical timestamp is diagnostic only. QUICK cannot become
    # sustained performance, including when clock coverage happens to be good.
    return dict(
        workload_id=job.workload_id, config=config, CORRECTNESS='PASS' if correct else 'FAIL',
        PERFORMANCE_VALIDITY='QUICK_DIAGNOSTIC_ONLY', SUSTAINED_PERFORMANCE='NOT_TESTED',
        hardware_device=native.get('device_type') in (1, 2, 3),
        execution_kind='PHYSICAL_GPU' if native.get('device_type') in (1, 2, 3) else 'SOFTWARE_VULKAN',
        work=work, algorithmic_operations=ops, unit=work['unit'] + '/s',
        diagnostic_work_units_per_s=units / wall if measurable else None,
        diagnostic_ops_per_s_by_type={k: v * repeats / wall for k, v in
            (ops['useful_ops_per_job_by_type'] or {}).items()} if measurable else {},
        one_job_end_to_end_units_per_s=work['count_per_job'] / pipeline_seconds if correct else None,
        end_to_end_scope='One validated job / prepare, compile, warmup, repeated execution, readback and validation time',
        legacy_science_per_s=native.get('records_per_s') if correct else None,
        gpu_ms=native.get('gpu_ms'), measurement_wall_ms=native.get('wall_ms'),
        gpu_wall_ratio=gpu / wall if wall > 0 else None,
        dispatch_count=native.get('dispatch_count'), queue_submissions=native.get('queue_submit_count'),
        inter_dispatch_gaps=native.get('inter_dispatch_gaps'),
        telemetry_coverage=window['coverage'], telemetry_samples=window['sample_count'],
        telemetry_status=telemetry['device_mapping'],
        SCLK_MHz=window['SCLK_AVG'], PPT_W=window.get('PPT_AVG_W_INFORMATIONAL'),
        power_scope=telemetry['power_scope'],
        resources='UNAVAILABLE', accepted_sustained_performance=False,
        compiler_binding='CHECKED_IN_MEMORY_AND_DISCARDED',
        full_output_validation='warmup and final output; repeated resident input, not unique research work')


def run_tasks(count, measure):
    admission = RunAdmission()
    for wid in select_workloads(count):
        admission.admit(wid)
        measure(wid)
    return len(admission.started)


def main(argv=None):
    parser = argparse.ArgumentParser(allow_abbrev=False, description='ASTRO GPU demo: maximum four fixed MathSpecs, then stop.')
    parser.add_argument('--tasks', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--profile', type=Path, default=Path('demo-profile.json'))
    parser.add_argument('--build-only', action='store_true', help='Compile native code and all eight demo shaders; do not run GPU work')
    parser.add_argument('--allow-software', action='store_true', help='Allow software Vulkan for correctness; never physical GPU performance')
    args = parser.parse_args(argv)
    if args.gpu < 0:
        parser.error('--gpu must be nonnegative')
    report = dict(schema='ASTRO_GPU_DEMO_V1', status='INCOMPLETE', limit=4, completed_mathspecs=0,
                  production_ready=False, promotion_allowed=False, sustained_performance='NOT_TESTED',
                  search_policy='FIXED_TWO_FAMILY_EVALUATION', census_fusion_search='NOT_INCLUDED',
                  retention='COMPACT_PROFILE_ONLY; transient binaries, inputs, outputs and hashes removed',
                  trials=[])

    def interrupted(signum, frame):
        raise TimeoutError('Demo stopped or five-minute limit reached')

    old_term = signal.signal(signal.SIGTERM, interrupted)
    old_alarm = signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(300)
    code = 0
    try:
        with gpu_lock(), tempfile.TemporaryDirectory(prefix='astro-demo-') as workspace:
            directory = Path(workspace)
            runner, probe = build(directory)
            if args.build_only:
                check_native_rejections(runner, directory)
                compile_all(directory)
                print('Native build and eight demo shader compilations PASS; no GPU measurement.')
                return 0
            caps = json.loads(command([probe, '--gpu', args.gpu], timeout=15))
            report['device'] = caps['device']
            if caps['device']['device_type'] not in (1, 2, 3) and not args.allow_software:
                raise RuntimeError('Software Vulkan requires --allow-software; no physical performance claim')

            def measure(wid):
                print(f'DEMO {wid} START', flush=True)
                start = time.monotonic()
                job = prepare(wid, fixture(SPECS[wid]['opcode'], seed=271828, scale=1))
                prepare_seconds = time.monotonic() - start
                candidates = list(configs(job, caps))
                if not candidates:
                    raise RuntimeError('No legal demo configuration on this device')
                for config in candidates:
                    with tempfile.TemporaryDirectory(prefix='trial-', dir=directory) as trial:
                        begin = time.monotonic()
                        artifact = generator.compile_candidate(job, config, Path(trial) / 'kernel', caps)
                        native, correct, evidence, elapsed = execute(job, artifact, runner, Path(trial), args.gpu)
                        row = compact_trial(job, config, native, correct, evidence,
                                            prepare_seconds + time.monotonic() - begin)
                        report['trials'].append(row)
                        print(f"  {config['family']} {row['execution_kind']} correctness={row['CORRECTNESS']} "
                              f"quick={row['diagnostic_work_units_per_s']} {row['unit']} "
                              f"PPT={row['PPT_W']} W", flush=True)
                        if not correct:
                            raise RuntimeError('Canonical full-output correctness failed; campaign stopped')
                report['completed_mathspecs'] += 1

            run_tasks(args.tasks, measure)
            report['status'] = 'DEMO_COMPLETE'
    except (Exception, KeyboardInterrupt) as exc:
        report['status'] = 'STOPPED'
        report['error_type'] = type(exc).__name__
        # Native diagnostics stay on screen; never retain raw paths/data in profile.
        print(f'Demo stopped: {exc}', flush=True)
        if isinstance(exc, subprocess.CalledProcessError):
            print(exc.stderr[-2000:], flush=True)
        code = 1
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGALRM, old_alarm)
        if not args.build_only:
            save(args.profile, report)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
