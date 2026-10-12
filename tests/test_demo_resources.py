import hashlib
import json
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from astro_demo import memory, recovered_codegen
from astro_demo.limits import WORKLOADS
from astro_demo.run import main, runtime_reuse, check_runtime_receipt
from astro_demo.support import sha
from science_library import f32
from science_library.catalog import SPECS
from science_library.reference import prepare
from science_library.vectors import GOLDEN


class ResourceChecks(unittest.TestCase):
    def test_cleanup_drops_only_pure_oracle_cache(self):
        expected = f32.rational(0x3f800000)
        f32.sqrt(0x40800000)
        self.assertGreater(f32.rational.cache_info().currsize, 0)
        receipt = memory.release_idle_memory()
        self.assertEqual(f32.rational.cache_info().currsize, 0)
        self.assertEqual(f32.sqrt.cache_info().currsize, 0)
        self.assertEqual(f32.rational(0x3f800000), expected)
        self.assertFalse(receipt['system_memory_modified'])
        self.assertEqual(receipt['gpu_memory'], 'UNAVAILABLE')

    def test_missing_memory_observation_is_not_zero(self):
        with patch.object(Path, 'read_text', side_effect=OSError):
            value = memory.process_memory()
        self.assertEqual(value['status'], 'UNAVAILABLE')
        self.assertIsNone(value['rss_bytes'])
        with patch('astro_demo.memory.ctypes.CDLL', side_effect=OSError):
            self.assertEqual(memory.trim_allocator(), 'UNAVAILABLE')

    def test_binding_hash_streamed_and_changes_detected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'source'
            data = b'canonical' * 300000
            path.write_bytes(data)
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('whole-file copy')):
                self.assertEqual(sha(path), hashlib.sha256(data).hexdigest())
            path.write_bytes(data + b'changed')
            self.assertNotEqual(sha(path), hashlib.sha256(data).hexdigest())

    def test_compile_keeps_binding_in_memory_without_manifest(self):
        job = prepare(WORKLOADS[0], GOLDEN[SPECS[WORKLOADS[0]]['opcode']][0])
        caps = {'limits': {'max_compute_workgroup_invocations': 64,
                           'max_compute_shared_memory_size': 32768}}
        def compiler(args, **kwargs):
            if args[0] == 'glslangValidator':
                Path(args[args.index('-o') + 1]).write_bytes(b'compiled fixture')
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        with tempfile.TemporaryDirectory() as d, patch.object(recovered_codegen.subprocess, 'run', side_effect=compiler):
            artifact = recovered_codegen.compile_candidate(job, dict(family='DIRECT', local_size=64, pack=1), Path(d) / 'kernel', caps)
            self.assertEqual({p.name for p in (Path(d) / 'kernel').iterdir()}, {'kernel.comp', 'kernel.spv'})
            recovered_codegen.check_job_binding(job, artifact)
            Path(artifact['spirv']).write_bytes(b'modified')
            with self.assertRaisesRegex(ValueError, 'artifact changed'):
                recovered_codegen.check_job_binding(job, artifact)

    def test_reuse_legal_only_for_supported_fixed_tasks(self):
        for i, wid in enumerate(WORKLOADS):
            job = SimpleNamespace(workload_id=wid)
            self.assertFalse(runtime_reuse(job, 'baseline'))
            self.assertEqual(runtime_reuse(job, 'reuse'), i < 3)
        with self.assertRaises(ValueError):
            runtime_reuse(SimpleNamespace(workload_id=WORKLOADS[0]), 'unlimited')

    def test_reuse_receipt_requires_actual_execution(self):
        for row in ({}, {'command_buffer_reuse_enabled': False},
                    {'command_buffer_reuse_enabled': True, 'command_buffer_reuses': 0}):
            with self.assertRaises(RuntimeError):
                check_runtime_receipt(row, True)
        check_runtime_receipt({'command_buffer_reuse_enabled': True, 'command_buffer_reuses': 2}, True)
        check_runtime_receipt({'command_buffer_reuse_enabled': False}, False)

    def test_each_task_checkpoints_after_cleanup_before_next_task(self):
        with tempfile.TemporaryDirectory() as d:
            profile = Path(d) / 'profile.json'
            def prepare_task(wid, payload):
                if wid == WORKLOADS[1]:
                    saved = json.loads(profile.read_text())
                    self.assertEqual(saved['completed_mathspecs'], 1)
                    self.assertEqual(len(saved['memory_cleanup']), 1)
                    self.assertEqual(saved['status'], 'INCOMPLETE')
                return SimpleNamespace(workload_id=wid)
            row = {'CORRECTNESS': 'PASS', 'execution_kind': 'PHYSICAL_GPU',
                   'diagnostic_work_units_per_s': 1, 'unit': 'unit/s', 'PPT_W': None}
            with patch('astro_demo.run.gpu_lock', return_value=nullcontext()), \
                 patch('astro_demo.run.build', return_value=('runner', 'probe')), \
                 patch('astro_demo.run.command', return_value=json.dumps({'device': {'device_type': 2}})), \
                 patch('astro_demo.run.prepare', side_effect=prepare_task), \
                 patch('astro_demo.run.fixture', return_value={}), \
                 patch('astro_demo.run.configs', return_value=[{'family': 'DIRECT'}]), \
                 patch('astro_demo.run.generator.compile_candidate', return_value={}), \
                 patch('astro_demo.run.execute', return_value=({}, True, {}, 0)), \
                 patch('astro_demo.run.compact_trial', return_value=row):
                self.assertEqual(main(['--tasks', '2', '--profile', str(profile)]), 0)
            saved = json.loads(profile.read_text())
            self.assertEqual(saved['status'], 'DEMO_COMPLETE')
            self.assertEqual(len(saved['memory_cleanup']), 2)

