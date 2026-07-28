from __future__ import annotations

import unittest

import numpy as np

from tools.baseline.metrics import confusion_metrics, evaluate_scope
from tools.baseline.pipeline import (
    CandidateEvent,
    associate_targets,
    build_main_candidates,
    candidate_identity_sha256,
)
from tools.data.protocol_r_access import DevelopmentSlice


def synthetic_slice(length: int = 300) -> DevelopmentSlice:
    return DevelopmentSlice(
        source_relative_path="redd/redd_house1_0.csv",
        source_sha256="0" * 64,
        house=1,
        segment_id="H1-S000",
        block_id="B1",
        row_start_inclusive=1000,
        row_end_exclusive=1000 + length,
        valid_target_start_inclusive=1000,
        valid_target_end_exclusive=1000 + length,
        fold_id="F1",
        role="validation",
    )


class AggregateMainPipelineTests(unittest.TestCase):
    def test_fifo_candidate_is_contained_and_uses_23_slots(self) -> None:
        main = np.full(300, 100.0)
        main[40:80] += 80.0
        candidates, diagnostics = build_main_candidates(synthetic_slice(), main)
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.rise_row, 1040)
        self.assertEqual(candidate.fall_row, 1080)
        self.assertEqual(candidate.dependency_start_row, 1008)
        self.assertEqual(candidate.dependency_end_row, 1088)
        self.assertEqual(candidate.available_row, 1088)
        self.assertEqual(len(candidate.features), 23)
        self.assertEqual(candidate.features[1], candidate.features[6])
        self.assertEqual(diagnostics["paired_count"], 1)

    def test_non_finite_main_breaks_continuity_and_resets_rises(self) -> None:
        main = np.full(300, 100.0)
        main[40:60] += 80.0
        main[50] = np.nan
        candidates, diagnostics = build_main_candidates(synthetic_slice(), main)
        self.assertEqual(candidates, [])
        self.assertGreaterEqual(diagnostics["expired_rise_count"], 1)
        self.assertEqual(diagnostics["unmatched_fall_count"], 1)

    def test_labels_cannot_change_candidate_ids_or_features(self) -> None:
        main = np.full(300, 100.0)
        main[40:80] += 80.0
        first, _ = build_main_candidates(synthetic_slice(), main)
        unrelated_labels = np.arange(300, dtype=np.float64)
        unrelated_labels[:] = unrelated_labels[::-1]
        second, _ = build_main_candidates(synthetic_slice(), main.copy())
        self.assertEqual(candidate_identity_sha256(first), candidate_identity_sha256(second))

    def test_missing_label_is_unavailable_not_negative(self) -> None:
        candidate = CandidateEvent(
            "c1", 1, "H1-S000", "B1", 1040, 1080, 1008, 1088, 1088, (0.0,) * 23
        )
        association = associate_targets(
            [candidate],
            None,
            data_slice=synthetic_slice(),
            appliance="fridge",
        )
        self.assertFalse(association.label_available)
        self.assertIsNone(association.candidate_status["c1"])
        self.assertEqual(
            association.candidate_exclusion_reason["c1"], "label_unavailable"
        )

    def test_one_to_one_match_and_duplicate_candidate_status(self) -> None:
        candidates = [
            CandidateEvent(
                "c1", 1, "H1-S000", "B1", 1040, 1050, 1008, 1058, 1058, (0.0,) * 23
            ),
            CandidateEvent(
                "c2", 1, "H1-S000", "B1", 1041, 1051, 1009, 1059, 1059, (0.0,) * 23
            ),
        ]
        target = np.zeros(300)
        target[40:51] = 20.0
        association = associate_targets(
            candidates,
            target,
            data_slice=synthetic_slice(),
            appliance="fridge",
        )
        self.assertEqual(association.candidate_status["c1"], 1)
        self.assertEqual(association.candidate_status["c2"], 0)
        self.assertEqual(association.duplicate_candidate_ids, {"c2"})

    def test_unmatched_complete_target_is_explicit_false_negative(self) -> None:
        target = np.zeros(300)
        target[100:104] = 20.0
        association = associate_targets(
            [],
            target,
            data_slice=synthetic_slice(),
            appliance="fridge",
        )
        self.assertEqual(association.complete_episode_count, 1)
        self.assertEqual(association.unmatched_complete_episode_count, 1)


class MetricTests(unittest.TestCase):
    def test_zero_denominators_are_flagged(self) -> None:
        metrics = confusion_metrics(0, 0, 0, 0)
        self.assertEqual(metrics["f1"], 0.0)
        self.assertTrue(metrics["f1_zero_denominator"])
        self.assertTrue(metrics["accuracy_zero_denominator"])


if __name__ == "__main__":
    unittest.main()
