from __future__ import annotations

import os
import unittest
from pathlib import Path

import numpy as np

from tools.data.protocol_r_access import ProtocolRAccessDenied, development_slices
from tools.rtm.run_direct_rtm_prototype import (
    causal_window_records,
    fit_train_only_binarizer,
    synthetic_smoke,
)


ROOT = Path(__file__).resolve().parents[2]


class _Slice:
    segment_id = "segment"
    block_id = "B2"
    house = 1
    row_start_inclusive = 100
    row_end_exclusive = 140
    valid_target_start_inclusive = 102
    valid_target_end_exclusive = 140


class _SpyBinarizer:
    fit_value: np.ndarray | None = None

    def __init__(self, max_bits_per_feature: int):
        self.max_bits_per_feature = max_bits_per_feature

    def fit(self, values: np.ndarray) -> None:
        type(self).fit_value = values.copy()

    def transform(self, values: np.ndarray) -> np.ndarray:
        return values > 0


class T006CausalityTests(unittest.TestCase):
    def test_window_ends_at_current_row_and_resets_at_boundary(self) -> None:
        first = _Slice()
        second = type(
            "SecondSlice",
            (),
            {
                **{
                    name: getattr(_Slice, name)
                    for name in (
                        "segment_id",
                        "block_id",
                        "house",
                        "row_start_inclusive",
                        "row_end_exclusive",
                        "valid_target_start_inclusive",
                        "valid_target_end_exclusive",
                    )
                },
                "segment_id": "other",
                "row_start_inclusive": 200,
                "row_end_exclusive": 240,
                "valid_target_start_inclusive": 202,
                "valid_target_end_exclusive": 240,
            },
        )()
        records = [
            (first, position, {"main": str(position), "fridge": "20"})
            for position in range(100, 105)
        ] + [
            (second, position, {"main": str(position), "fridge": "20"})
            for position in range(200, 205)
        ]
        rows = causal_window_records(records, window_length=3)
        self.assertEqual(rows.row_positions.tolist(), [102, 103, 104, 202, 203, 204])
        self.assertEqual(rows.windows[0].tolist(), [100.0, 101.0, 102.0])
        self.assertEqual(rows.windows[3].tolist(), [200.0, 201.0, 202.0])
        self.assertNotIn(103.0, rows.windows[0])

    def test_nonfinite_main_breaks_dependency_window(self) -> None:
        records = [
            (_Slice(), 100, {"main": "100", "fridge": "20"}),
            (_Slice(), 101, {"main": "nan", "fridge": "20"}),
            (_Slice(), 102, {"main": "102", "fridge": "20"}),
            (_Slice(), 103, {"main": "103", "fridge": "20"}),
            (_Slice(), 104, {"main": "104", "fridge": "20"}),
        ]
        rows = causal_window_records(records, window_length=3)
        self.assertEqual(rows.row_positions.tolist(), [104])
        self.assertEqual(rows.windows[0].tolist(), [102.0, 103.0, 104.0])

    def test_binarizer_fits_training_only(self) -> None:
        training = np.array([[1.0, 2.0], [3.0, 4.0]])
        validation = np.array([[100.0, 200.0]])
        fit_train_only_binarizer(
            training, validation, binarizer_type=_SpyBinarizer
        )
        np.testing.assert_array_equal(_SpyBinarizer.fit_value, training)


class T006AccessTests(unittest.TestCase):
    def test_development_loader_refuses_locked_and_protocol_x_requests(self) -> None:
        for role in ("B5", "locked_test", "protocol_x"):
            with self.subTest(role=role), self.assertRaises(ProtocolRAccessDenied):
                development_slices(ROOT, validation_fold=1, role=role)
        with self.assertRaises(ProtocolRAccessDenied):
            development_slices(
                ROOT, validation_fold=1, role="training", houses=(2, 4)
            )


class T006TMUIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("T006_REQUIRE_TMU") == "1",
        "run in the locked T006 TMU environment",
    )
    def test_synthetic_prediction_shape_and_finiteness(self) -> None:
        result = synthetic_smoke()
        self.assertTrue(result["passed"])
        self.assertTrue(result["prediction_finite"])
        self.assertGreater(result["prediction_unique_count"], 1)


if __name__ == "__main__":
    unittest.main()
