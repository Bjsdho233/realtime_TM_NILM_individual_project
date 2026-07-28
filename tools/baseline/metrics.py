"""T005 end-to-end confusion metrics and frozen aggregation helpers."""

from __future__ import annotations

import statistics
from collections import Counter
from typing import Iterable

import numpy as np

from tools.baseline.pipeline import BlockResult


def safe_ratio(numerator: int | float, denominator: int | float) -> tuple[float, bool]:
    if denominator == 0:
        return 0.0, True
    return float(numerator / denominator), False


def confusion_metrics(tp: int, tn: int, fp: int, fn: int) -> dict[str, object]:
    precision, precision_zero = safe_ratio(tp, tp + fp)
    recall, recall_zero = safe_ratio(tp, tp + fn)
    f1, f1_zero = safe_ratio(2 * tp, 2 * tp + fp + fn)
    accuracy, accuracy_zero = safe_ratio(tp + tn, tp + tn + fp + fn)
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "binary_accuracy": accuracy,
        "precision_zero_denominator": precision_zero,
        "recall_zero_denominator": recall_zero,
        "f1_zero_denominator": f1_zero,
        "accuracy_zero_denominator": accuracy_zero,
    }


def evaluate_scope(
    blocks: Iterable[BlockResult],
    *,
    appliance: str,
    predictions: dict[str, int],
    house: int | None,
) -> dict[str, object]:
    selected = [
        block
        for block in blocks
        if house is None or block.data_slice.house == house
    ]
    counts: Counter[str] = Counter()
    excluded: Counter[str] = Counter()
    for block in selected:
        association = block.associations[appliance]
        if not association.label_available:
            excluded["label_unavailable"] += len(block.candidates)
            continue
        for candidate in block.candidates:
            status = association.candidate_status[candidate.candidate_id]
            if status is None:
                excluded[
                    association.candidate_exclusion_reason[candidate.candidate_id]
                ] += 1
                continue
            prediction = int(predictions[candidate.candidate_id])
            if status == 1 and prediction == 1:
                counts["tp"] += 1
            elif status == 1:
                counts["fn"] += 1
            elif prediction == 1:
                counts["fp"] += 1
            else:
                counts["tn"] += 1
        counts["fn"] += association.unmatched_complete_episode_count
        counts["unmatched_target_episode_count"] += (
            association.unmatched_complete_episode_count
        )
        counts["matched_target_episode_count"] += len(
            association.matched_episode_to_candidate
        )
        counts["complete_episode_count"] += association.complete_episode_count
        counts["duplicate_candidate_count"] += len(
            association.duplicate_candidate_ids
        )
    values = confusion_metrics(
        counts["tp"], counts["tn"], counts["fp"], counts["fn"]
    )
    values.update(
        {
            "eligible_positive_support": counts["tp"] + counts["fn"],
            "eligible_negative_support": counts["tn"] + counts["fp"],
            "excluded_unavailable_count": sum(excluded.values()),
            "excluded_reasons": dict(sorted(excluded.items())),
            "matched_target_episode_count": counts["matched_target_episode_count"],
            "unmatched_target_episode_count": counts[
                "unmatched_target_episode_count"
            ],
            "duplicate_candidate_count": counts["duplicate_candidate_count"],
            "candidate_count": sum(len(block.candidates) for block in selected),
        }
    )
    coverage, coverage_zero = safe_ratio(
        counts["matched_target_episode_count"], counts["complete_episode_count"]
    )
    values["episode_coverage"] = coverage
    values["episode_coverage_zero_denominator"] = coverage_zero
    return values


def linear_percentile(values: Iterable[int | float], percentile: float) -> float:
    materialised = np.asarray(list(values), dtype=np.float64)
    if materialised.size == 0:
        return 0.0
    return float(np.percentile(materialised, percentile, method="linear"))


def mean_sample_std(values: Iterable[float]) -> tuple[float, float]:
    materialised = [float(value) for value in values]
    if not materialised:
        return 0.0, 0.0
    mean = statistics.fmean(materialised)
    sample_std = statistics.stdev(materialised) if len(materialised) > 1 else 0.0
    return mean, sample_std


def fold_seed_appliance_summary(
    pooled_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Aggregate pooled fold values to seed-fold means, then five-seed summaries."""

    by_appliance_seed: dict[tuple[str, int], list[float]] = {}
    for row in pooled_rows:
        if row["house"] != "ALL":
            continue
        key = (str(row["appliance"]), int(row["seed"]))
        by_appliance_seed.setdefault(key, []).append(float(row["f1"]))
    seed_means: dict[str, list[float]] = {}
    for (appliance, seed), values in sorted(by_appliance_seed.items()):
        if len(values) != 4:
            raise RuntimeError(
                f"{appliance} seed {seed} does not contain exactly four folds"
            )
        seed_means.setdefault(appliance, []).append(statistics.fmean(values))
    summaries = []
    for appliance, values in sorted(seed_means.items()):
        if len(values) != 5:
            raise RuntimeError(f"{appliance} does not contain exactly five seeds")
        mean, sample_std = mean_sample_std(values)
        summaries.append(
            {
                "scope": appliance,
                "metric": "seed_fold_mean_f1",
                "value": mean,
                "unit": "ratio",
                "aggregation": (
                    "unweighted F1-F4 mean within each seed; mean across five seeds"
                ),
                "sample_std": sample_std,
                "seed_values": values,
            }
        )
    lookup = {row["scope"]: row for row in summaries}
    for scope, appliances in (
        ("full_eligible_macro_2class", ("fridge", "microwave")),
        (
            "development_scope_macro_3class",
            ("fridge", "microwave", "dish washer"),
        ),
    ):
        appliance_means = [float(lookup[name]["value"]) for name in appliances]
        macro_seed_values = [
            statistics.fmean(
                float(lookup[name]["seed_values"][seed_index]) for name in appliances
            )
            for seed_index in range(5)
        ]
        mean, sample_std = mean_sample_std(macro_seed_values)
        summaries.append(
            {
                "scope": scope,
                "metric": "macro_seed_fold_mean_f1",
                "value": mean,
                "unit": "ratio",
                "aggregation": (
                    "appliance-unweighted macro of each seed's unweighted F1-F4 mean; "
                    "mean across five seeds"
                ),
                "sample_std": sample_std,
                "seed_values": macro_seed_values,
                "appliance_values": appliance_means,
            }
        )
    return summaries
