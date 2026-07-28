#!/usr/bin/env python3
"""Run the fixed T006 causal-window fridge regression-TM prototype."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import math
import subprocess
import sys
import time
from array import array
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

from tools.data.protocol_r_access import (
    DevelopmentSlice,
    ProtocolRAccessDenied,
    development_slices,
    iter_development_rows,
)


WORK_ID = "T006"
DIRECT_NAME = "Direct rTM NILM Prototype"
HOUSES = (1, 3, 5, 6)
WINDOW_LENGTH = 32
TRAINING_CAP = 50_000
ON_THRESHOLD_W = 15.0
VALIDATION_BATCH_SIZE = 10_000
MODEL_PARAMETERS = {
    "number_of_clauses": 200,
    "T": 200,
    "s": 3.0,
    "platform": "CPU",
    "feature_negation": True,
    "max_included_literals": 16,
    "number_of_state_bits_ta": 8,
    "weighted_clauses": False,
    "clause_drop_p": 0.0,
    "literal_drop_p": 0.0,
    "seed": 0,
}


@dataclass(frozen=True)
class CausalRows:
    """Compact row-level arrays kept only in memory during the run."""

    windows: np.ndarray
    targets: np.ndarray
    slice_numbers: np.ndarray
    row_positions: np.ndarray
    slice_labels: tuple[str, ...]
    rejected_nonfinite_main: int
    rejected_target: int


def finite_float(value: object) -> float | None:
    """Return one finite float, otherwise None."""

    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def causal_window_records(
    records: Iterable[tuple[DevelopmentSlice, int, dict[str, str]]],
    *,
    window_length: int = WINDOW_LENGTH,
    target_column: str = "fridge",
) -> CausalRows:
    """Build windows ending at t while resetting at every declared slice."""

    flat_windows = array("f")
    targets = array("f")
    slice_numbers = array("I")
    row_positions = array("I")
    slice_labels: list[str] = []
    label_to_number: dict[str, int] = {}
    history: deque[float] = deque(maxlen=window_length)
    previous_key: tuple[str, str, int, int] | None = None
    rejected_nonfinite_main = 0
    rejected_target = 0

    for data_slice, row_position, row in records:
        key = (
            data_slice.segment_id,
            data_slice.block_id,
            data_slice.row_start_inclusive,
            data_slice.row_end_exclusive,
        )
        if key != previous_key:
            history.clear()
            previous_key = key
            label = (
                f"H{data_slice.house}/{data_slice.segment_id}/{data_slice.block_id}"
            )
            if label not in label_to_number:
                label_to_number[label] = len(slice_labels)
                slice_labels.append(label)

        main = finite_float(row.get("main"))
        if main is None:
            history.clear()
            rejected_nonfinite_main += 1
            continue
        history.append(main)

        if not (
            data_slice.valid_target_start_inclusive
            <= row_position
            < data_slice.valid_target_end_exclusive
        ):
            continue
        target = finite_float(row.get(target_column))
        if target is None:
            rejected_target += 1
            continue
        if len(history) != window_length:
            # This can occur only after a non-finite aggregate value.
            rejected_nonfinite_main += 1
            continue

        flat_windows.extend(history)
        targets.append(max(0.0, target))
        label = f"H{data_slice.house}/{data_slice.segment_id}/{data_slice.block_id}"
        slice_numbers.append(label_to_number[label])
        row_positions.append(row_position)

    count = len(targets)
    windows = np.frombuffer(flat_windows, dtype=np.float32).reshape(
        count, window_length
    ).copy()
    return CausalRows(
        windows=windows,
        targets=np.frombuffer(targets, dtype=np.float32).copy(),
        slice_numbers=np.frombuffer(slice_numbers, dtype=np.uint32).copy(),
        row_positions=np.frombuffer(row_positions, dtype=np.uint32).copy(),
        slice_labels=tuple(slice_labels),
        rejected_nonfinite_main=rejected_nonfinite_main,
        rejected_target=rejected_target,
    )


def evenly_spaced_indices(row_count: int, cap: int = TRAINING_CAP) -> np.ndarray:
    """Select deterministic positions without consulting targets or labels."""

    if row_count <= cap:
        return np.arange(row_count, dtype=np.int64)
    return np.rint(np.linspace(0, row_count - 1, cap)).astype(np.int64)


def fit_train_only_binarizer(
    train_windows: np.ndarray,
    validation_windows: np.ndarray,
    *,
    binarizer_type: type | None = None,
) -> tuple[object, np.ndarray, np.ndarray]:
    """Fit thresholds on training windows, then transform both roles."""

    if binarizer_type is None:
        from tmu.preprocessing.standard_binarizer.binarizer import StandardBinarizer

        binarizer_type = StandardBinarizer
    binarizer = binarizer_type(max_bits_per_feature=8)
    binarizer.fit(train_windows)
    return (
        binarizer,
        np.asarray(binarizer.transform(train_windows), dtype=np.uint32),
        np.asarray(binarizer.transform(validation_windows), dtype=np.uint32),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def synthetic_smoke() -> dict[str, object]:
    """Exercise the installed TMU regression interface before REDD access."""

    from tmu.models.regression.vanilla_regressor import TMRegressor
    from tmu.preprocessing.standard_binarizer.binarizer import StandardBinarizer

    rng = np.random.default_rng(20260728)
    x_numeric = rng.uniform(-2.0, 2.0, size=(96, 3))
    y = (
        20.0
        + 5.0 * x_numeric[:, 0]
        - 3.0 * x_numeric[:, 1]
        + 2.0 * x_numeric[:, 2]
    )
    binarizer = StandardBinarizer(max_bits_per_feature=8)
    x = np.asarray(binarizer.fit_transform(x_numeric), dtype=np.uint32)
    model = TMRegressor(
        number_of_clauses=64,
        T=40,
        s=3.0,
        platform="CPU",
        max_included_literals=16,
        weighted_clauses=False,
        seed=20260728,
    )
    for _ in range(3):
        model.fit(x, y, shuffle=True)
    prediction = np.asarray(model.predict(x), dtype=float)
    model_path = Path(inspect.getfile(TMRegressor)).resolve()
    unique_count = int(np.unique(prediction).size)
    passed = (
        prediction.shape == y.shape
        and bool(np.all(np.isfinite(prediction)))
        and unique_count > 1
    )
    result = {
        "passed": passed,
        "tmu_version": importlib.metadata.version("tmu"),
        "vanilla_regressor_sha256": _sha256(model_path),
        "sample_count": int(y.size),
        "prediction_shape": list(prediction.shape),
        "prediction_finite": bool(np.all(np.isfinite(prediction))),
        "prediction_unique_count": unique_count,
        "prediction_min_w": float(np.min(prediction)),
        "prediction_max_w": float(np.max(prediction)),
    }
    if not passed:
        raise RuntimeError(f"synthetic TMU smoke failed: {result}")
    return result


def _predict_in_batches(model: object, binarizer: object, windows: np.ndarray) -> np.ndarray:
    predictions: list[np.ndarray] = []
    for start in range(0, windows.shape[0], VALIDATION_BATCH_SIZE):
        numeric = windows[start : start + VALIDATION_BATCH_SIZE]
        encoded = np.asarray(binarizer.transform(numeric), dtype=np.uint32)
        predictions.append(np.asarray(model.predict(encoded), dtype=float))
    return np.concatenate(predictions)


def prediction_metrics(
    truth: np.ndarray,
    prediction: np.ndarray,
    *,
    train_max: float,
) -> dict[str, float | int]:
    """Compute the compact fixed T006 regression/state metric set."""

    truth = np.asarray(truth, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    if truth.shape != prediction.shape or truth.size == 0:
        raise ValueError("truth and prediction must be non-empty and equally shaped")
    if not np.all(np.isfinite(truth)) or not np.all(np.isfinite(prediction)):
        raise ValueError("metrics require finite arrays")

    absolute_error = np.abs(prediction - truth)
    truth_on = truth > ON_THRESHOLD_W
    predicted_on = prediction > ON_THRESHOLD_W
    true_positive = int(np.sum(truth_on & predicted_on))
    false_positive = int(np.sum(~truth_on & predicted_on))
    false_negative = int(np.sum(truth_on & ~predicted_on))
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    truth_sum = float(np.sum(truth))
    off_prediction = np.maximum(0.0, prediction[~truth_on])
    return {
        "sample_count": int(truth.size),
        "on_sample_count": int(np.sum(truth_on)),
        "prediction_min_w": float(np.min(prediction)),
        "prediction_max_w": float(np.max(prediction)),
        "prediction_unique_count": int(np.unique(prediction).size),
        "outside_training_range_fraction": float(
            np.mean((prediction < 0.0) | (prediction > train_max))
        ),
        "mae_w": float(np.mean(absolute_error)),
        "median_absolute_error_w": float(np.median(absolute_error)),
        "pooled_nae": float(np.sum(absolute_error) / truth_sum)
        if truth_sum > 0
        else 0.0,
        "on_mae_w": float(np.mean(absolute_error[truth_on]))
        if np.any(truth_on)
        else 0.0,
        "state_precision": float(precision),
        "state_recall": float(recall),
        "state_f1": float(f1),
        "mean_off_false_positive_w": float(np.mean(off_prediction))
        if off_prediction.size
        else 0.0,
    }


def first_complete_on_excerpt(rows: CausalRows, context: int = 32) -> tuple[int, int]:
    """Return a label-selected excerpt around the first bounded ON interval."""

    target_on = rows.targets > ON_THRESHOLD_W
    for start in range(1, len(target_on) - 1):
        if not target_on[start] or target_on[start - 1]:
            continue
        end = start
        while (
            end + 1 < len(target_on)
            and target_on[end + 1]
            and rows.slice_numbers[end + 1] == rows.slice_numbers[start]
            and rows.row_positions[end + 1] == rows.row_positions[end] + 1
        ):
            end += 1
        complete = (
            end + 1 < len(target_on)
            and not target_on[end + 1]
            and rows.slice_numbers[start - 1] == rows.slice_numbers[start]
            and rows.slice_numbers[end + 1] == rows.slice_numbers[start]
            and rows.row_positions[start] == rows.row_positions[start - 1] + 1
            and rows.row_positions[end + 1] == rows.row_positions[end] + 1
        )
        if complete:
            left = max(0, start - context)
            right = min(len(target_on), end + context + 2)
            while left < start and rows.slice_numbers[left] != rows.slice_numbers[start]:
                left += 1
            while right > end + 1 and rows.slice_numbers[right - 1] != rows.slice_numbers[start]:
                right -= 1
            return left, right
    raise RuntimeError("no complete validation fridge ON interval was found")


def _polyline(values: np.ndarray, width: int, height: int, maximum: float) -> str:
    if values.size == 1:
        return f"0,{height / 2:.1f}"
    points = []
    for index, value in enumerate(values):
        x = index * width / (values.size - 1)
        y = height - min(max(float(value), 0.0), maximum) * height / maximum
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def write_excerpt_svg(
    path: Path,
    rows: CausalRows,
    clipped_prediction: np.ndarray,
) -> dict[str, object]:
    """Write one dependency-free, relative-time prototype figure."""

    left, right = first_complete_on_excerpt(rows)
    truth = rows.targets[left:right]
    prediction = clipped_prediction[left:right]
    aggregate = rows.windows[left:right, -1]
    plot_width, plot_height = 900, 360
    maximum = max(float(np.max(truth)), float(np.max(prediction)), 1.0)
    aggregate_scaled = aggregate * maximum / max(float(np.max(aggregate)), 1.0)
    label = rows.slice_labels[int(rows.slice_numbers[left])]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="470" viewBox="0 0 1000 470">
<rect width="1000" height="470" fill="white"/>
<text x="50" y="28" font-family="sans-serif" font-size="18">T006 first complete validation fridge ON interval ({label})</text>
<text x="50" y="50" font-family="sans-serif" font-size="13">Relative samples; aggregate is rescaled for context only</text>
<g transform="translate(50,70)">
<rect width="{plot_width}" height="{plot_height}" fill="#fafafa" stroke="#555"/>
<polyline fill="none" stroke="#9aa0a6" stroke-width="1.5" points="{_polyline(aggregate_scaled, plot_width, plot_height, maximum)}"/>
<polyline fill="none" stroke="#1a73e8" stroke-width="2.2" points="{_polyline(truth, plot_width, plot_height, maximum)}"/>
<polyline fill="none" stroke="#d93025" stroke-width="2.0" points="{_polyline(prediction, plot_width, plot_height, maximum)}"/>
<text x="10" y="20" font-family="sans-serif" font-size="12" fill="#9aa0a6">aggregate (rescaled)</text>
<text x="165" y="20" font-family="sans-serif" font-size="12" fill="#1a73e8">true fridge</text>
<text x="260" y="20" font-family="sans-serif" font-size="12" fill="#d93025">clipped rTM</text>
</g>
<text x="450" y="458" font-family="sans-serif" font-size="13">relative sample index (3 s nominal)</text>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")
    return {
        "path": "figures/direct_rtm_excerpt.svg",
        "selection": "first complete validation fridge ON interval with 32-sample context",
        "slice": label,
        "sample_count": int(right - left),
    }


def _clean_expected_head(project_root: Path, expected_head: str) -> None:
    head = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(project_root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != expected_head or status:
        raise RuntimeError("real run requires the exact clean pre-run implementation commit")


def _load_role(project_root: Path, redd_root: Path, role: str) -> CausalRows:
    slices = development_slices(
        project_root, validation_fold=1, role=role, houses=HOUSES
    )
    expected_blocks = {"B2", "B3", "B4"} if role == "training" else {"B1"}
    if {item.block_id for item in slices} != expected_blocks:
        raise ProtocolRAccessDenied(f"unexpected {role} block set")
    return causal_window_records(
        iter_development_rows(
            project_root,
            redd_root,
            validation_fold=1,
            role=role,
            houses=HOUSES,
        )
    )


def run_real(
    project_root: Path,
    redd_root: Path,
    output_root: Path,
    expected_head: str,
) -> dict[str, object]:
    """Execute the one authorised real-data configuration."""

    from tmu.models.regression.vanilla_regressor import TMRegressor
    from tmu.preprocessing.standard_binarizer.binarizer import StandardBinarizer

    _clean_expected_head(project_root, expected_head)
    smoke = synthetic_smoke()
    train_all = _load_role(project_root, redd_root, "training")
    validation = _load_role(project_root, redd_root, "validation")
    selected = evenly_spaced_indices(train_all.targets.size)
    train_x = train_all.windows[selected]
    train_y = train_all.targets[selected].astype(float)
    train_mean = float(np.mean(train_y))
    train_max = float(np.max(train_y))

    binarizer = StandardBinarizer(max_bits_per_feature=8)
    binarizer.fit(train_x)
    encoded_train = np.asarray(binarizer.transform(train_x), dtype=np.uint32)
    threshold_counts = [int(values.size) for values in binarizer.unique_values]

    model = TMRegressor(**MODEL_PARAMETERS)
    fit_start = time.perf_counter()
    for _ in range(5):
        model.fit(encoded_train, train_y, shuffle=True)
    fit_seconds = time.perf_counter() - fit_start
    predict_start = time.perf_counter()
    raw_prediction = _predict_in_batches(model, binarizer, validation.windows)
    predict_seconds = time.perf_counter() - predict_start
    clipped_prediction = np.clip(raw_prediction, 0.0, train_max)
    if (
        raw_prediction.shape != validation.targets.shape
        or not np.all(np.isfinite(raw_prediction))
        or not np.all(np.isfinite(clipped_prediction))
    ):
        raise RuntimeError("real prediction output is invalid")

    predictions = {
        "zero": np.zeros_like(validation.targets, dtype=float),
        "training_mean": np.full_like(validation.targets, train_mean, dtype=float),
        "rtm_raw": raw_prediction,
        "rtm_clipped": clipped_prediction,
    }
    metrics = {
        name: prediction_metrics(validation.targets, values, train_max=train_max)
        for name, values in predictions.items()
    }
    useful_signal = (
        metrics["rtm_clipped"]["pooled_nae"] < 1.0
        and metrics["rtm_clipped"]["prediction_unique_count"] > 1
    )
    figure = write_excerpt_svg(
        output_root / "figures" / "direct_rtm_excerpt.svg",
        validation,
        clipped_prediction,
    )
    result = {
        "work_id": WORK_ID,
        "name": DIRECT_NAME,
        "track": "T-series",
        "status": "complete",
        "claim_scope": "Protocol R F1 development feasibility only",
        "implementation_commit": expected_head,
        "protocol": {
            "fold": "F1",
            "houses": ["H1", "H3", "H5", "H6"],
            "training_blocks": ["B2", "B3", "B4"],
            "validation_block": "B1",
            "locked_test_access": False,
            "protocol_x_access": False,
        },
        "data": {
            "appliance": "fridge",
            "target": "max(0, fridge[t])",
            "on_threshold_w": ON_THRESHOLD_W,
            "input": "main[t-31:t+1]",
            "window_samples": WINDOW_LENGTH,
            "nominal_window_seconds": 96,
            "output_delay_samples": 0,
            "common_valid_target_rule": "block_start + 255 <= t < block_end - 8",
            "training_rows_admitted": int(train_all.targets.size),
            "training_rows_selected": int(selected.size),
            "validation_rows": int(validation.targets.size),
            "validation_on_rows": int(np.sum(validation.targets > ON_THRESHOLD_W)),
            "training_rejected_nonfinite_main": train_all.rejected_nonfinite_main,
            "training_rejected_target": train_all.rejected_target,
            "validation_rejected_nonfinite_main": validation.rejected_nonfinite_main,
            "validation_rejected_target": validation.rejected_target,
        },
        "preprocessing": {
            "type": "TMU StandardBinarizer",
            "max_bits_per_feature": 8,
            "fit_scope": "selected training rows only",
            "numeric_feature_count": WINDOW_LENGTH,
            "threshold_count_per_feature": threshold_counts,
            "boolean_feature_count": int(binarizer.number_of_features),
        },
        "model": {
            "type": "TMU vanilla TMRegressor",
            "parameters": MODEL_PARAMETERS,
            "explicit_one_epoch_fit_calls": 5,
            "shuffle": True,
            "selected_training_target_mean_w": train_mean,
            "selected_training_target_max_w": train_max,
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "tmu": smoke["tmu_version"],
            "lock": "docs/research_notes/2026-07-24-tmu-regression-smoke-test/uv.lock",
            "vanilla_regressor_sha256": smoke["vanilla_regressor_sha256"],
        },
        "synthetic_smoke": smoke,
        "metrics": metrics,
        "runtime_seconds": {
            "fit": fit_seconds,
            "predict": predict_seconds,
        },
        "figure": figure,
        "interpretation": {
            "operational": True,
            "useful_signal_rule": "clipped pooled NAE < 1 and non-constant predictions",
            "useful_signal": bool(useful_signal),
            "conclusion": (
                "showed useful signal under the fixed descriptive rule"
                if useful_signal
                else "did not yet show useful signal"
            ),
        },
        "limitations": [
            "One appliance, one development fold and one seed only.",
            "No tuning and no confirmatory or locked-test evaluation.",
            "No model export, host parity, Pico or hardware evidence.",
        ],
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-only", action="store_true")
    parser.add_argument("--redd-root", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("experiments/T006-direct-rtm-nilm-prototype"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.synthetic_only:
        print(json.dumps(synthetic_smoke(), indent=2))
        return
    if args.redd_root is None or args.expected_head is None:
        raise SystemExit("--redd-root and --expected-head are required for the real run")
    project_root = Path(__file__).resolve().parents[2]
    result = run_real(
        project_root,
        args.redd_root,
        (project_root / args.output_root).resolve(),
        args.expected_head,
    )
    print(json.dumps(result["interpretation"], indent=2))


if __name__ == "__main__":
    main()
