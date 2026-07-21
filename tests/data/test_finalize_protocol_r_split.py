import copy
import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[2]
MODULE_PATH = ROOT / "tools" / "data" / "finalize_protocol_r_split.py"
SPEC = importlib.util.spec_from_file_location("finalize_protocol_r_split", MODULE_PATH)
finalizer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(finalizer)


class FinalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = json.loads((ROOT / finalizer.PREDECESSOR_PATH).read_text(encoding="utf-8"))
        cls.audit = json.loads((ROOT / finalizer.SUPPORT_AUDIT_PATH).read_text(encoding="utf-8"))

    def test_canonical_hash_is_reproducible(self):
        approved = finalizer.finalize(self.candidate, self.audit)
        self.assertEqual(finalizer.canonical_sha256(approved), approved["canonical_sha256"])

    def test_source_identity_and_ranges_are_preserved(self):
        approved = finalizer.finalize(self.candidate, self.audit)
        self.assertEqual(approved["source_files"], self.candidate["source_files"])

    def test_approved_classes_must_pass_audit(self):
        changed = copy.deepcopy(self.audit)
        changed["support_summary"]["washer dryer"]["full_standard_pass"] = False
        with self.assertRaisesRegex(ValueError, "approved class"):
            finalizer.finalize(self.candidate, changed)

    def test_missing_column_is_unavailable_not_zero(self):
        approved = finalizer.finalize(self.candidate, self.audit)
        house_four = next(item for item in approved["house_target_column_availability"] if item["house"] == 4)
        self.assertFalse(house_four["target_columns"]["fridge"])
        self.assertIn("do not fill all-zero ground truth", approved["missing_target_column_policy"])

    def test_electric_furnace_failure_remains_traceable(self):
        approved = finalizer.finalize(self.candidate, self.audit)
        excluded = approved["excluded_class"]
        self.assertEqual(excluded["candidate_test_complete_cycles"], 1)
        self.assertEqual(excluded["candidate_minimum_complete_cycles"], 10)
        self.assertFalse(excluded["model_performance_failure"])


if __name__ == "__main__":
    unittest.main()
