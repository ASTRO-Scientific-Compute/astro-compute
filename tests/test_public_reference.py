"""Public reference checks: analytic oracles, contract scope and rejection gates."""
import json
from pathlib import Path
import unittest
from science_library.catalog import SPECS
from science_library.reference import prepare, encode, compare_bytes
from science_library.vectors import GOLDEN
from science_library.vector_f32 import check_host

ROOT = Path(__file__).resolve().parents[1]


class ReferenceChecks(unittest.TestCase):
    def test_registry_coverage(self):
        inventory = json.loads((ROOT / 'registry_inventory.json').read_text())
        self.assertEqual(len(inventory['workloads']), 94)
        self.assertEqual(len({w['workload_id'] for w in inventory['workloads']}), 94)
        self.assertEqual(len(SPECS), 81)
        self.assertEqual(sum(s['domain'] == 'SPACE' for s in SPECS.values()), 66)
        self.assertEqual({w['workload_id'] for w in inventory['workloads']
                          if w['canonical_cpu_reference_in_this_release']}, set(SPECS))

    def test_binary32_host_contract(self):
        check_host()

    def test_invalid_job_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare('SPACE_IMAGE_MOMENTS_U16_V1', {'images': [[[1.5]]]})

    def test_corrupted_output_is_rejected(self):
        job = prepare('SPACE_IMAGE_MOMENTS_U16_V1', {'images': [[[1, 2], [3, 4]]]})
        damaged = bytes([job.reference[0] ^ 1]) + job.reference[1:]
        self.assertTrue(compare_bytes(job.reference, job.reference)['pass_exact'])
        for actual in (damaged, job.reference[:-1], job.reference + b'\x00'):
            self.assertFalse(compare_bytes(job.reference, actual)['pass_exact'])


def analytic_case(wid, spec):
    def test(self):
        payload, expected = GOLDEN[spec['opcode']]
        job = prepare(wid, payload)
        self.assertEqual(job.reference, encode(expected))
        saved = json.loads((ROOT / spec['MathSpec']).read_text())
        self.assertEqual(saved, spec)
        vector = json.loads((ROOT / spec['reference_test_vectors']).read_text())
        self.assertEqual(vector['payload'], payload)
        self.assertEqual(encode(vector['expected_output_u32']), job.reference)
    return test


for _wid, _spec in SPECS.items():
    setattr(ReferenceChecks, 'test_analytic_' + _wid.lower(), analytic_case(_wid, _spec))

if __name__ == '__main__':
    unittest.main()
