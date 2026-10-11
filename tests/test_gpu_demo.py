import tempfile
from contextlib import nullcontext
from pathlib import Path
import unittest
from unittest.mock import patch

from astro_demo.limits import WORKLOADS, RunAdmission
from astro_demo.run import run_tasks, acceptance, configs, main, compact_trial
from astro_demo import recovered_codegen
from science_library.catalog import SPECS
from science_library.reference import prepare
from science_library.vectors import GOLDEN
from science_library.shaders import shader


class DemoChecks(unittest.TestCase):
    def test_fixed_four_and_no_fifth_callback(self):
        seen = []
        self.assertEqual(run_tasks(4, seen.append), 4)
        self.assertEqual(tuple(seen), WORKLOADS)
        for count in (0, 5, -1, True, 1.0):
            with self.assertRaises(ValueError):
                run_tasks(count, seen.append)
        self.assertEqual(len(seen), 4)

    def test_no_unknown_or_repeated_admission(self):
        admission = RunAdmission()
        for wid in WORKLOADS:
            admission.admit(wid)
        for wid in (WORKLOADS[0], 'SPACE_IMAGE_MOMENTS_U16_V1'):
            with self.assertRaises(ValueError):
                admission.admit(wid)

    def test_cli_rejects_unlimited_modes(self):
        for args in (['--tasks', '5'], ['--all'], ['--wid', 'anything']):
            with patch('astro_demo.run.build') as build, self.assertRaises(SystemExit) as error:
                main(args)
            self.assertEqual(error.exception.code, 2)
            build.assert_not_called()

    def test_shader_rejects_other_workload(self):
        with self.assertRaises(ValueError):
            shader('SPACE_IMAGE_MOMENTS_U16_V1')

    def test_real_acceptance_rejects_each_bad_output(self):
        job = prepare(WORKLOADS[0], GOLDEN[SPECS[WORKLOADS[0]]['opcode']][0])
        self.assertTrue(acceptance(job, job.reference, job.reference))
        for actual in (bytes([job.reference[0] ^ 1]) + job.reference[1:],
                       job.reference[:-1], job.reference + b'\x00'):
            self.assertFalse(acceptance(job, actual, job.reference))
            self.assertFalse(acceptance(job, job.reference, actual))

    def test_canonical_generator_changes_execution_source(self):
        caps = {'limits': {'max_compute_workgroup_invocations': 64,
                           'max_compute_shared_memory_size': 32768}}
        for wid in WORKLOADS:
            job = prepare(wid, GOLDEN[SPECS[wid]['opcode']][0])
            variants = list(configs(job, caps))
            self.assertEqual(len(variants), 2)
            direct, tiled = [recovered_codegen.source(job, c) for c in variants]
            self.assertNotEqual(direct, tiled)
            self.assertIn('barrier()', tiled)

    def test_interruption_and_failure_cleanup(self):
        for error in (KeyboardInterrupt(), RuntimeError('build failure')):
            workspaces = []
            def fail(directory):
                workspaces.append(Path(directory))
                (Path(directory) / 'input.bin').write_bytes(b'transient')
                raise error
            with tempfile.TemporaryDirectory() as output, patch('astro_demo.run.build', side_effect=fail), patch('astro_demo.run.gpu_lock', return_value=nullcontext()):
                self.assertEqual(main(['--profile', str(Path(output) / 'profile.json')]), 1)
                self.assertTrue((Path(output) / 'profile.json').exists())
            self.assertTrue(workspaces)
            self.assertTrue(all(not p.exists() for p in workspaces))

    def test_failed_correctness_never_retains_throughput(self):
        job = prepare(WORKLOADS[0], GOLDEN[SPECS[WORKLOADS[0]]['opcode']][0])
        native = dict(wall_ms=1000, gpu_ms=900, repeats=8, measurement_batches=2,
                      records_per_s=1000, device_type=4)
        telemetry = dict(measurement=dict(coverage=0, sample_count=0, SCLK_AVG=None),
                         device_mapping='UNAVAILABLE', power_scope='UNAVAILABLE')
        row = compact_trial(job, {}, native, False, telemetry, 4)
        self.assertEqual(row['CORRECTNESS'], 'FAIL')
        for key in ('diagnostic_work_units_per_s', 'one_job_end_to_end_units_per_s', 'legacy_science_per_s'):
            self.assertIsNone(row[key])
        self.assertEqual(row['diagnostic_ops_per_s_by_type'], {})
        self.assertFalse(row['hardware_device'])
        self.assertEqual(row['execution_kind'], 'SOFTWARE_VULKAN')
        self.assertFalse(row['accepted_sustained_performance'])
