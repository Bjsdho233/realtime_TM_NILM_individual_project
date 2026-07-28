from __future__ import annotations

import unittest
from pathlib import Path

from tools.data.protocol_r_access import (
    ProtocolRAccessDenied,
    development_slices,
)


ROOT = Path(__file__).resolve().parents[2]


class T005AccessBoundaryTests(unittest.TestCase):
    def test_all_fixed_folds_are_only_b1_through_b4(self) -> None:
        observed_validation = []
        for fold in range(1, 5):
            training = development_slices(
                ROOT, validation_fold=fold, role="training"
            )
            validation = development_slices(
                ROOT, validation_fold=fold, role="validation"
            )
            self.assertTrue({item.block_id for item in training} <= {"B1", "B2", "B3", "B4"})
            self.assertNotIn("B5", {item.block_id for item in training + validation})
            observed_validation.extend(item.block_id for item in validation)
        self.assertEqual(sorted(set(observed_validation)), ["B1", "B2", "B3", "B4"])

    def test_combined_final_fit_and_unknown_aliases_fail_closed(self) -> None:
        for role in ("development", "combined_final_fit", "all", "locked_test", "protocol_x"):
            with self.subTest(role=role):
                with self.assertRaises(ProtocolRAccessDenied):
                    development_slices(ROOT, validation_fold=1, role=role)

    def test_unknown_or_protocol_x_houses_fail_closed(self) -> None:
        for houses in ((2,), (4,), (1, 2), (7,), ()):
            with self.subTest(houses=houses):
                with self.assertRaises(ProtocolRAccessDenied):
                    development_slices(
                        ROOT,
                        validation_fold=1,
                        role="training",
                        houses=houses,
                    )


if __name__ == "__main__":
    unittest.main()

