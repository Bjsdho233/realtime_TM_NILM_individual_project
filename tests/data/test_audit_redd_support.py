import importlib.util
import math
import pathlib
import tempfile
import unittest


MODULE_PATH = pathlib.Path(__file__).parents[2] / "tools" / "data" / "audit_redd_support.py"
SPEC = importlib.util.spec_from_file_location("audit_redd_support", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


def stats(values):
    result = audit.SupportStats()
    for value in values:
        result.consume(value)
    result.finish()
    return result.as_dict()


class SupportStatsTests(unittest.TestCase):
    def test_threshold_is_strictly_greater_than_fifteen(self):
        result = stats([0.0, 15.0, 15.0001, 15.0001, 0.0])
        self.assertEqual(result["active_samples"], 2)
        self.assertEqual(result["complete_cycles"], 1)

    def test_one_sample_run_is_not_a_cycle(self):
        result = stats([0.0, 20.0, 0.0])
        self.assertEqual(result["complete_cycles"], 0)
        self.assertEqual(result["active_duration_seconds"], 3)

    def test_complete_cycle_requires_inactive_edges(self):
        result = stats([0.0, 20.0, 20.0, 0.0])
        self.assertEqual(result["rising_transitions"], 1)
        self.assertEqual(result["falling_transitions"], 1)
        self.assertEqual(result["complete_cycles"], 1)

    def test_left_and_right_censoring(self):
        left = stats([20.0, 20.0, 0.0])
        right = stats([0.0, 20.0, 20.0])
        both = stats([20.0, 20.0])
        self.assertEqual(left["left_censored_runs"], 1)
        self.assertEqual(right["right_censored_runs"], 1)
        self.assertEqual(both["left_censored_runs"], 1)
        self.assertEqual(both["right_censored_runs"], 1)
        self.assertEqual(left["complete_cycles"] + right["complete_cycles"] + both["complete_cycles"], 0)

    def test_missing_value_breaks_observation_continuity(self):
        result = stats([0.0, 20.0, 20.0, None, 20.0, 20.0, 0.0])
        self.assertEqual(result["missing_samples"], 1)
        self.assertEqual(result["complete_cycles"], 0)
        self.assertEqual(result["right_censored_runs"], 1)
        self.assertEqual(result["left_censored_runs"], 1)

    def test_non_finite_value_is_missing(self):
        result = stats([0.0, math.nan, math.inf, 0.0])
        self.assertEqual(result["finite_samples"], 2)
        self.assertEqual(result["missing_samples"], 2)

    def test_chunk_reset_prevents_cross_chunk_cycle(self):
        first = stats([0.0, 20.0, 20.0])
        second = stats([20.0, 20.0, 0.0])
        self.assertEqual(first["complete_cycles"] + second["complete_cycles"], 0)
        self.assertEqual(first["right_censored_runs"], 1)
        self.assertEqual(second["left_censored_runs"], 1)

    def test_block_boundary_containment_discards_crossing_run(self):
        values = [0.0, 20.0, 20.0, 20.0, 0.0, 0.0]
        first = stats(values[:3])
        second = stats(values[3:])
        self.assertEqual(first["complete_cycles"] + second["complete_cycles"], 0)
        self.assertEqual(first["right_censored_runs"], 1)
        self.assertEqual(second["left_censored_runs"], 0)

    def test_three_block_ranges_are_contiguous_and_complete(self):
        self.assertEqual(audit.block_ranges(8), [(0, 3), (3, 6), (6, 8)])


class SyntheticCsvTests(unittest.TestCase):
    def test_missing_cell_and_absent_column_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "redd_house1_0.csv"
            path.write_text(
                ",fridge,main\n0,0,100\n1,20,120\n2,,110\n",
                encoding="utf-8",
            )
            records = audit.audit_file(path, 3)
        fridge = next(record for record in records if record["appliance"] == "fridge" and record["validation_fold"] == 3)
        furnace = next(record for record in records if record["appliance"] == "electric furnace" and record["validation_fold"] == 1)
        self.assertEqual(fridge["missing_samples"], 1)
        self.assertTrue(fridge["column_present"])
        self.assertFalse(furnace["column_present"])
        self.assertEqual(furnace["missing_samples"], 0)


if __name__ == "__main__":
    unittest.main()
