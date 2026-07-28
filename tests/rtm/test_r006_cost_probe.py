from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from tools.rtm import run_r006_cost_probe as probe


ROOT = Path(__file__).resolve().parents[2]


class R006SpecificationTests(unittest.TestCase):
    def test_only_c8_and_c11_are_defined(self) -> None:
        self.assertEqual(set(probe.CANDIDATE_FEATURES), {"C8", "C11"})
        self.assertEqual(len(probe.CANDIDATE_FEATURES["C8"]), 8)
        self.assertEqual(len(probe.CANDIDATE_FEATURES["C11"]), 11)
        self.assertNotIn("C14", probe.CANDIDATE_FEATURES)

    def test_frozen_spec_hash_and_candidate_counts(self) -> None:
        spec = probe.verify_spec(ROOT)
        self.assertEqual(spec["candidates"]["C8"]["boolean_bit_count"], 56)
        self.assertEqual(spec["candidates"]["C11"]["boolean_bit_count"], 74)
        self.assertEqual(spec["model"]["weighted_clauses"], False)
        self.assertEqual(spec["model"]["number_of_clauses"], 200)

    def test_full_gate_refuses_c8_and_unstable_c11(self) -> None:
        with self.assertRaises(RuntimeError):
            probe.validate_full_gate(
                "C8",
                {"candidate": "C8", "scaling": {"stable": True, "full_c11_time_gate_pass": True}},
            )
        with self.assertRaises(RuntimeError):
            probe.validate_full_gate(
                "C11",
                {"candidate": "C11", "scaling": {"stable": False, "full_c11_time_gate_pass": True}},
            )


class R006FeatureTests(unittest.TestCase):
    def _raw_slice(self) -> probe.RawSlice:
        main = np.arange(300, dtype=np.float64)
        target = np.arange(300, dtype=np.float64) - 280.0
        data_slice = SimpleNamespace(
            house=1,
            segment_id="segment",
            block_id="B2",
            valid_target_start_inclusive=255,
            valid_target_end_exclusive=300,
        )
        return probe.RawSlice(
            data_slice=data_slice,
            positions=np.arange(300, dtype=np.int64),
            main=main,
            target=target,
        )

    def test_c8_and_c11_share_exact_rows_and_target_stimulus(self) -> None:
        c8 = probe.build_feature_rows((self._raw_slice(),), "C8")
        c11 = probe.build_feature_rows((self._raw_slice(),), "C11")
        self.assertEqual(c8.features.shape, (45, 8))
        self.assertEqual(c11.features.shape, (45, 11))
        self.assertEqual(c8.identity_sha256, c11.identity_sha256)
        self.assertTrue(np.array_equal(c8.targets, c11.targets))
        self.assertEqual(float(c8.targets[0]), 0.0)

    def test_causal_means_residuals_and_ranges(self) -> None:
        rows = probe.build_feature_rows((self._raw_slice(),), "C11")
        first = dict(zip(probe.CANDIDATE_FEATURES["C11"], rows.features[0]))
        self.assertEqual(first["level_t"], 255.0)
        self.assertEqual(first["delta_1"], 1.0)
        self.assertEqual(first["mean_4"], 253.5)
        self.assertEqual(first["residual_4"], 1.5)
        self.assertEqual(first["range_4"], 3.0)
        self.assertEqual(first["mean_64"], 223.5)
        self.assertEqual(first["residual_64"], 31.5)
        self.assertEqual(first["range_64"], 63.0)

    def test_deterministic_selection_has_exact_size(self) -> None:
        first = probe.evenly_spaced_indices(10_000, 2_048)
        second = probe.evenly_spaced_indices(10_000, 2_048)
        self.assertEqual(np.unique(first).size, 2_048)
        self.assertTrue(np.array_equal(first, second))
        self.assertEqual(probe.index_sha256(first), probe.index_sha256(second))


class R006BooleaniserTests(unittest.TestCase):
    def test_transform_emits_declared_uint32_bits(self) -> None:
        fitted = probe.FittedBooleaniser(
            feature_names=("level_t", "delta_1"),
            bit_names=("level", "positive", "negative"),
            feature_indices=np.asarray([0, 1, 1], dtype=np.int16),
            directions=("ge", "positive_ge", "negative_ge"),
            thresholds=np.asarray([10.0, 2.0, 3.0]),
        )
        values = np.asarray([[9.0, -4.0], [10.0, 2.0]], dtype=np.float32)
        encoded = fitted.transform(values)
        self.assertEqual(encoded.dtype, np.uint32)
        self.assertTrue(
            np.array_equal(encoded, np.asarray([[0, 0, 1], [1, 1, 0]], dtype=np.uint32))
        )


if __name__ == "__main__":
    unittest.main()
