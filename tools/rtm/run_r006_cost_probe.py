#!/usr/bin/env python3
"""Measure C8/C11 TMU computation cost without evaluating prediction quality."""

from __future__ import annotations

import argparse
import csv
import ctypes
import gc
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from tools.data.protocol_r_access import DevelopmentSlice, iter_development_rows


WORK_ID = "R006"
SPEC_PATH = Path("docs/reviews/R006-probe-spec.json")
SPEC_HASH_PATH = Path("docs/reviews/R006-probe-spec.sha256")
SPEC_SHA256 = "43636376d2f598052c1fbbdc2b1cd4b1381bd60ca8a392df4603c700eb7dfc89"
R005_BIT_TABLE = Path("docs/reviews/R005-bit-audit.csv")
HOUSES = (1, 3, 5, 6)
STAIRCASE = (2_048, 8_192, 32_768, 131_072)
PREDICTION_ROWS = 2_048
ON_THRESHOLD_W = 15.0
MIN_AVAILABLE_BYTES = 1_073_741_824
STEP_WALL_LIMIT_SECONDS = 600.0
MODEL_PARAMETERS = {
    "number_of_clauses": 200,
    "T": 200,
    "s": 3.0,
    "platform": "CPU",
    "feature_negation": True,
    "boost_true_positive_feedback": 1,
    "reuse_random_feedback": 0,
    "max_included_literals": 16,
    "number_of_state_bits_ta": 8,
    "weighted_clauses": False,
    "clause_drop_p": 0.0,
    "literal_drop_p": 0.0,
    "seed": 0,
}
CANDIDATE_FEATURES = {
    "C8": (
        "level_t",
        "delta_1",
        "mean_4",
        "residual_4",
        "mean_16",
        "residual_16",
        "mean_64",
        "residual_64",
    ),
    "C11": (
        "level_t",
        "delta_1",
        "mean_4",
        "residual_4",
        "range_4",
        "mean_16",
        "residual_16",
        "range_16",
        "mean_64",
        "residual_64",
        "range_64",
    ),
}
NONNEGATIVE_FEATURES = {
    "level_t",
    "mean_4",
    "range_4",
    "mean_16",
    "range_16",
    "mean_64",
    "range_64",
}
NONNEGATIVE_QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90, 0.99)
SIGNED_QUANTILES = (0.50, 0.90, 0.99, 0.999)


@dataclass(frozen=True)
class RawSlice:
    """One admitted block kept in memory for causal feature construction."""

    data_slice: DevelopmentSlice
    positions: np.ndarray
    main: np.ndarray
    target: np.ndarray


@dataclass(frozen=True)
class FeatureRows:
    """Aggregate-only candidate inputs and engineering target stimulus."""

    features: np.ndarray
    targets: np.ndarray
    identity_sha256: str


@dataclass(frozen=True)
class FittedBooleaniser:
    """Exact R005 threshold list in emitted-bit order."""

    feature_names: tuple[str, ...]
    bit_names: tuple[str, ...]
    feature_indices: np.ndarray
    directions: tuple[str, ...]
    thresholds: np.ndarray

    def transform(self, values: np.ndarray) -> np.ndarray:
        encoded = np.empty((values.shape[0], self.thresholds.size), dtype=np.uint32)
        for bit, (feature_index, direction, threshold) in enumerate(
            zip(self.feature_indices, self.directions, self.thresholds)
        ):
            column = values[:, int(feature_index)]
            if direction in {"ge", "positive_ge"}:
                encoded[:, bit] = column >= threshold
            elif direction == "negative_ge":
                encoded[:, bit] = column <= -threshold
            else:
                raise ValueError(f"unsupported direction: {direction}")
        return encoded


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def finite_float(value: object) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if math.isfinite(parsed) else math.nan


def verify_spec(project_root: Path) -> dict[str, object]:
    spec_path = project_root / SPEC_PATH
    hash_path = project_root / SPEC_HASH_PATH
    if sha256_file(spec_path) != SPEC_SHA256:
        raise RuntimeError("R006 probe specification hash mismatch")
    expected_sidecar = f"{SPEC_SHA256}  {SPEC_PATH.as_posix()}\n"
    if hash_path.read_text(encoding="ascii") != expected_sidecar:
        raise RuntimeError("R006 probe specification sidecar mismatch")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("status") != "frozen cost-probe-only execution specification":
        raise RuntimeError("R006 probe specification is not frozen")
    return spec


def verify_repository(project_root: Path, expected_head: str) -> None:
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=project_root, text=True
    ).strip()
    if head != expected_head:
        raise RuntimeError(f"expected HEAD {expected_head}, found {head}")
    status = subprocess.check_output(
        ["git", "status", "--short"], cwd=project_root, text=True
    )
    if status:
        raise RuntimeError("R006 requires a clean worktree")
    current_state = (project_root / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    if "Active T-series: T006 — Direct rTM NILM Prototype (paused" not in current_state:
        raise RuntimeError("T006 is not recorded as paused")


def load_training_slices(project_root: Path, redd_root: Path) -> tuple[RawSlice, ...]:
    slices: list[RawSlice] = []
    current_key: tuple[object, ...] | None = None
    current_slice: DevelopmentSlice | None = None
    positions: list[int] = []
    main: list[float] = []
    target: list[float] = []

    def flush() -> None:
        if current_slice is None:
            return
        slices.append(
            RawSlice(
                data_slice=current_slice,
                positions=np.asarray(positions, dtype=np.int64),
                main=np.asarray(main, dtype=np.float64),
                target=np.asarray(target, dtype=np.float64),
            )
        )

    for data_slice, row_position, row in iter_development_rows(
        project_root,
        redd_root,
        validation_fold=1,
        role="training",
        houses=HOUSES,
    ):
        key = (
            data_slice.segment_id,
            data_slice.block_id,
            data_slice.row_start_inclusive,
            data_slice.row_end_exclusive,
        )
        if current_key is not None and key != current_key:
            flush()
            positions.clear()
            main.clear()
            target.clear()
        current_key = key
        current_slice = data_slice
        positions.append(row_position)
        main.append(finite_float(row.get("main")))
        target.append(finite_float(row.get("fridge")))
    flush()
    if not slices:
        raise RuntimeError("R006 admitted no training slices")
    return tuple(slices)


def _feature_columns(
    main: np.ndarray,
    eligible_indices: np.ndarray,
    feature_names: tuple[str, ...],
) -> dict[str, np.ndarray]:
    columns: dict[str, np.ndarray] = {
        "level_t": main[eligible_indices],
        "delta_1": main[eligible_indices] - main[eligible_indices - 1],
    }
    for horizon in (4, 16, 64):
        required = {
            f"mean_{horizon}",
            f"residual_{horizon}",
            f"range_{horizon}",
        } & set(feature_names)
        if not required:
            continue
        windows = np.lib.stride_tricks.sliding_window_view(main, horizon)
        selected = windows[eligible_indices - horizon + 1]
        means = selected.mean(axis=1)
        if f"mean_{horizon}" in required:
            columns[f"mean_{horizon}"] = means
        if f"residual_{horizon}" in required:
            columns[f"residual_{horizon}"] = main[eligible_indices] - means
        if f"range_{horizon}" in required:
            columns[f"range_{horizon}"] = (
                selected.max(axis=1) - selected.min(axis=1)
            )
    return columns


def build_feature_rows(
    raw_slices: Iterable[RawSlice],
    candidate: str,
) -> FeatureRows:
    feature_names = CANDIDATE_FEATURES[candidate]
    matrices: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    identity = hashlib.sha256()

    for raw in raw_slices:
        invalid = (~np.isfinite(raw.main)).astype(np.int64)
        prefix = np.concatenate(([0], np.cumsum(invalid)))
        local_indices = np.arange(raw.main.size, dtype=np.int64)
        complete_history = np.zeros(raw.main.size, dtype=bool)
        can_have_history = local_indices >= 255
        high = local_indices[can_have_history] + 1
        low = local_indices[can_have_history] - 255
        complete_history[can_have_history] = (prefix[high] - prefix[low]) == 0
        eligible = (
            (raw.positions >= raw.data_slice.valid_target_start_inclusive)
            & (raw.positions < raw.data_slice.valid_target_end_exclusive)
            & complete_history
            & np.isfinite(raw.target)
        )
        selected = np.flatnonzero(eligible)
        if selected.size == 0:
            continue
        columns = _feature_columns(raw.main, selected, feature_names)
        matrix = np.column_stack([columns[name] for name in feature_names]).astype(
            np.float32
        )
        stimulus = np.maximum(0.0, raw.target[selected]).astype(np.float32)
        if not (np.isfinite(matrix).all() and np.isfinite(stimulus).all()):
            raise RuntimeError("non-finite candidate data")
        matrices.append(matrix)
        targets.append(stimulus)
        for row_position in raw.positions[selected]:
            identity.update(
                f"{raw.data_slice.house}|{raw.data_slice.segment_id}|"
                f"{raw.data_slice.block_id}|{int(row_position)}\n".encode("utf-8")
            )

    features = np.concatenate(matrices)
    target_array = np.concatenate(targets)
    if features.shape[0] != target_array.size:
        raise RuntimeError("feature/target row mismatch")
    return FeatureRows(
        features=features,
        targets=target_array,
        identity_sha256=identity.hexdigest(),
    )


def _threshold_label(feature: str, direction: str, quantile: float) -> str:
    return f"{feature}:{direction}:q{int(round(quantile * 1000)):03d}"


def fit_booleaniser(
    project_root: Path,
    candidate: str,
    features: np.ndarray,
) -> FittedBooleaniser:
    feature_names = CANDIDATE_FEATURES[candidate]
    bit_names: list[str] = []
    feature_indices: list[int] = []
    directions: list[str] = []
    thresholds: list[float] = []
    for feature_index, feature in enumerate(feature_names):
        values = features[:, feature_index].astype(np.float64)
        if feature in NONNEGATIVE_FEATURES:
            fitted = np.quantile(values, NONNEGATIVE_QUANTILES, method="linear")
            for quantile, threshold in zip(NONNEGATIVE_QUANTILES, fitted):
                bit_names.append(_threshold_label(feature, "ge", quantile))
                feature_indices.append(feature_index)
                directions.append("ge")
                thresholds.append(float(threshold))
        else:
            positive = values[values > 0]
            negative = -values[values < 0]
            positive_fitted = np.quantile(positive, SIGNED_QUANTILES, method="linear")
            negative_fitted = np.quantile(negative, SIGNED_QUANTILES, method="linear")
            for quantile, threshold in zip(SIGNED_QUANTILES, positive_fitted):
                bit_names.append(_threshold_label(feature, "positive_ge", quantile))
                feature_indices.append(feature_index)
                directions.append("positive_ge")
                thresholds.append(float(threshold))
            for quantile, threshold in zip(SIGNED_QUANTILES, negative_fitted):
                bit_names.append(_threshold_label(feature, "negative_ge", quantile))
                feature_indices.append(feature_index)
                directions.append("negative_ge")
                thresholds.append(float(threshold))

    expected = {}
    with (project_root / R005_BIT_TABLE).open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            expected[row["bit_name"]] = float(row["threshold_w"])
    for name, threshold in zip(bit_names, thresholds):
        if name not in expected or threshold != expected[name]:
            raise RuntimeError(f"R005 threshold parity failed for {name}")
    expected_bits = 56 if candidate == "C8" else 74
    if len(bit_names) != expected_bits:
        raise RuntimeError("unexpected Boolean bit count")
    return FittedBooleaniser(
        feature_names=feature_names,
        bit_names=tuple(bit_names),
        feature_indices=np.asarray(feature_indices, dtype=np.int16),
        directions=tuple(directions),
        thresholds=np.asarray(thresholds, dtype=np.float64),
    )


def evenly_spaced_indices(row_count: int, requested: int) -> np.ndarray:
    if requested <= 0 or requested > row_count:
        raise ValueError("requested rows must be within the available population")
    if requested == row_count:
        return np.arange(row_count, dtype=np.int64)
    indices = np.rint(np.linspace(0, row_count - 1, requested)).astype(np.int64)
    if np.unique(indices).size != requested:
        raise RuntimeError("deterministic selection contains duplicate positions")
    return indices


def index_sha256(indices: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(indices.astype("<i8")).tobytes()
    ).hexdigest()


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class _ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def available_physical_bytes() -> int:
    if os.name != "nt":
        return 0
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError()
    return int(status.ullAvailPhys)


def process_memory() -> dict[str, int]:
    if os.name != "nt":
        return {
            "working_set_bytes": 0,
            "private_bytes": 0,
            "pagefile_bytes": 0,
            "page_fault_count": 0,
        }
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    if not ctypes.windll.psapi.GetProcessMemoryInfo(
        handle, ctypes.byref(counters), counters.cb
    ):
        raise ctypes.WinError()
    return {
        "working_set_bytes": int(counters.WorkingSetSize),
        "private_bytes": int(counters.PrivateUsage),
        "pagefile_bytes": int(counters.PagefileUsage),
        "page_fault_count": int(counters.PageFaultCount),
    }


class ResourceMonitor:
    """Sample this process and available physical memory during one step."""

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        current = process_memory()
        self.peak_working_set = current["working_set_bytes"]
        self.peak_private = current["private_bytes"]
        self.min_available = available_physical_bytes()
        self.start_faults = current["page_fault_count"]
        self.end_faults = self.start_faults

    def _run(self) -> None:
        while not self._stop.wait(0.05):
            current = process_memory()
            self.peak_working_set = max(
                self.peak_working_set, current["working_set_bytes"]
            )
            self.peak_private = max(self.peak_private, current["private_bytes"])
            available = available_physical_bytes()
            if available:
                self.min_available = min(self.min_available, available)
            self.end_faults = current["page_fault_count"]

    def __enter__(self) -> ResourceMonitor:
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join()
        current = process_memory()
        self.peak_working_set = max(
            self.peak_working_set, current["working_set_bytes"]
        )
        self.peak_private = max(self.peak_private, current["private_bytes"])
        self.end_faults = current["page_fault_count"]


def paging_samples(sample_count: int = 2) -> dict[str, float | int | None]:
    if os.name != "nt":
        return {
            "samples": 0,
            "pages_input_mean": None,
            "pages_input_max": None,
            "page_reads_mean": None,
            "page_reads_max": None,
        }
    command = [
        "typeperf",
        r"\Memory\Pages Input/sec",
        r"\Memory\Page Reads/sec",
        "-sc",
        str(sample_count),
        "-si",
        "1",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        timeout=sample_count + 10,
    )
    rows = list(csv.reader(line for line in completed.stdout.splitlines() if line))
    values: list[tuple[float, float]] = []
    for row in rows[1:]:
        if len(row) < 3:
            continue
        try:
            values.append((float(row[1]), float(row[2])))
        except ValueError:
            continue
    if not values:
        return {
            "samples": 0,
            "pages_input_mean": None,
            "pages_input_max": None,
            "page_reads_mean": None,
            "page_reads_max": None,
        }
    pages = np.asarray([item[0] for item in values])
    reads = np.asarray([item[1] for item in values])
    return {
        "samples": len(values),
        "pages_input_mean": float(pages.mean()),
        "pages_input_max": float(pages.max()),
        "page_reads_mean": float(reads.mean()),
        "page_reads_max": float(reads.max()),
    }


def calculated_model_sizes(model: object) -> dict[str, int]:
    clause_bank = model.clause_bank
    learned = (
        int(clause_bank.clause_bank.nbytes)
        + int(model.weight_bank.weights.nbytes)
        + 16
    )
    clause_runtime_arrays = [
        value
        for value in vars(clause_bank).values()
        if isinstance(value, np.ndarray)
    ]
    unique_arrays = {id(array): array for array in clause_runtime_arrays}
    runtime = sum(int(array.nbytes) for array in unique_arrays.values())
    runtime += int(model.weight_bank.weights.nbytes) + 16
    training_cache = int(model.X_train.nbytes) + int(model.encoded_X_train.nbytes)
    return {
        "calculated_learned_state_bytes": learned,
        "tmu_clause_runtime_numpy_bytes_excluding_training_cache": runtime,
        "tmu_training_cache_bytes": training_cache,
    }


class UnsupervisedExecutionDenied(RuntimeError):
    """Legacy R006 fitting must be launched through the bounded supervisor."""


def model_factory() -> None:
    raise UnsupervisedExecutionDenied(
        "direct R006 TMU construction is disabled; use bounded_supervisor.py"
    )


def unmeasured_warmup(encoded: np.ndarray, targets: np.ndarray) -> None:
    del encoded, targets
    model_factory()


def measure_step(*_: object, **__: object) -> dict[str, object]:
    model_factory()
    raise AssertionError("unreachable")


def scaling_analysis(
    steps: list[dict[str, object]],
    full_rows: int,
) -> dict[str, object]:
    completed = [step for step in steps if step.get("status") == "completed"]
    if not completed:
        return {"stable": False, "reason": "no completed steps"}
    largest = completed[-1]
    per_row = float(largest["fit_wall_seconds"]) / int(largest["rows"])
    recent = completed[-3:]
    recent_per_row = [
        float(step["fit_wall_seconds"]) / int(step["rows"]) for step in recent
    ]
    coefficient_of_variation = (
        float(np.std(recent_per_row) / np.mean(recent_per_row))
        if len(recent_per_row) >= 2
        else None
    )
    stable = bool(
        len(completed) == len(STAIRCASE)
        and coefficient_of_variation is not None
        and coefficient_of_variation <= 0.25
        and not any(bool(step["probe_induced_paging"]) for step in completed)
        and min(
            int(step["minimum_available_physical_bytes"]) for step in completed
        )
        >= MIN_AVAILABLE_BYTES
    )
    projected_one_epoch = per_row * full_rows
    return {
        "basis": "largest completed step seconds per row; conservative first-epoch projection",
        "completed_steps": len(completed),
        "recent_seconds_per_row": recent_per_row,
        "recent_seconds_per_row_coefficient_of_variation": coefficient_of_variation,
        "stable": stable,
        "projected_full_rows": full_rows,
        "projected_full_seconds": {
            "1_epoch": projected_one_epoch,
            "5_epochs": projected_one_epoch * 5,
            "10_epochs": projected_one_epoch * 10,
            "20_epochs": projected_one_epoch * 20,
        },
        "full_c11_time_gate_pass": projected_one_epoch <= 300.0,
    }


def run_staircase(
    project_root: Path,
    redd_root: Path,
    candidate: str,
) -> dict[str, object]:
    if candidate not in CANDIDATE_FEATURES:
        raise ValueError("R006 permits only C8 or C11")
    data_wall_start = time.perf_counter()
    data_cpu_start = time.process_time()
    raw_slices = load_training_slices(project_root, redd_root)
    data_cpu = time.process_time() - data_cpu_start
    data_wall = time.perf_counter() - data_wall_start

    feature_wall_start = time.perf_counter()
    feature_cpu_start = time.process_time()
    rows = build_feature_rows(raw_slices, candidate)
    feature_cpu = time.process_time() - feature_cpu_start
    feature_wall = time.perf_counter() - feature_wall_start
    del raw_slices
    gc.collect()

    threshold_wall_start = time.perf_counter()
    threshold_cpu_start = time.process_time()
    booleaniser = fit_booleaniser(
        project_root, candidate, rows.features
    )
    threshold_cpu = time.process_time() - threshold_cpu_start
    threshold_wall = time.perf_counter() - threshold_wall_start

    prediction_indices = evenly_spaced_indices(rows.features.shape[0], PREDICTION_ROWS)
    prediction_boolean_start = time.perf_counter()
    prediction_encoded = booleaniser.transform(rows.features[prediction_indices])
    prediction_boolean_seconds = time.perf_counter() - prediction_boolean_start

    baseline_paging = paging_samples(3)
    warmup_indices = evenly_spaced_indices(rows.features.shape[0], 128)
    warmup_encoded = booleaniser.transform(rows.features[warmup_indices])
    unmeasured_warmup(warmup_encoded, rows.targets)
    del warmup_encoded
    gc.collect()

    steps: list[dict[str, object]] = []
    previous_per_row: float | None = None
    for requested in STAIRCASE:
        boolean_wall_start = time.perf_counter()
        selected = evenly_spaced_indices(rows.features.shape[0], requested)
        encoded = booleaniser.transform(rows.features[selected])
        boolean_wall = time.perf_counter() - boolean_wall_start
        step = measure_step(
            encoded,
            rows.targets[selected],
            prediction_encoded,
            requested,
            baseline_paging,
        )
        step["selection_sha256"] = index_sha256(selected)
        step["booleanisation_wall_seconds"] = boolean_wall
        step["booleanisation_rows_per_second"] = requested / boolean_wall
        step["status"] = "completed"
        stop_reasons = []
        if float(step["fit_wall_seconds"]) > STEP_WALL_LIMIT_SECONDS:
            stop_reasons.append("fit wall time exceeded 10 minutes")
        if int(step["minimum_available_physical_bytes"]) < MIN_AVAILABLE_BYTES:
            stop_reasons.append("available physical memory fell below 1 GiB")
        if bool(step["probe_induced_paging"]):
            stop_reasons.append("probe-induced paging threshold was crossed")
        current_per_row = float(step["fit_wall_seconds"]) / requested
        if (
            previous_per_row is not None
            and requested >= 32_768
            and current_per_row > previous_per_row * 2.0
        ):
            stop_reasons.append("per-row runtime growth exceeded 2x")
        previous_per_row = current_per_row
        if stop_reasons:
            step["stop_reasons"] = stop_reasons
            steps.append(step)
            break
        step["stop_reasons"] = []
        steps.append(step)
        del encoded
        gc.collect()

    scaling = scaling_analysis(steps, rows.features.shape[0])
    return {
        "schema_version": "1.0",
        "work_id": WORK_ID,
        "candidate": candidate,
        "claim_scope": "engineering computation cost only",
        "spec_sha256": SPEC_SHA256,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "tmu": importlib.metadata.version("tmu"),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
        },
        "data": {
            "fold": "F1",
            "role": "training",
            "houses": list(HOUSES),
            "full_rows": int(rows.features.shape[0]),
            "row_identity_sha256": rows.identity_sha256,
            "data_access_wall_seconds": data_wall,
            "data_access_cpu_seconds": data_cpu,
            "feature_construction_wall_seconds": feature_wall,
            "feature_construction_cpu_seconds": feature_cpu,
        },
        "feature_spec": {
            "features_in_order": list(CANDIDATE_FEATURES[candidate]),
            "numeric_feature_count": len(CANDIDATE_FEATURES[candidate]),
        },
        "booleaniser_spec": {
            "bit_count": int(booleaniser.thresholds.size),
            "threshold_fit_and_parity_wall_seconds": threshold_wall,
            "threshold_fit_and_parity_cpu_seconds": threshold_cpu,
            "prediction_sample_booleanisation_wall_seconds": prediction_boolean_seconds,
            "threshold_sha256": hashlib.sha256(
                np.ascontiguousarray(booleaniser.thresholds.astype("<f8")).tobytes()
            ).hexdigest(),
        },
        "model_spec": MODEL_PARAMETERS,
        "target_stimulus": {
            "project_transform": "max(0, finite fridge[t]); float32 storage; float64 passed to TMU",
            "tmu_internal_transform": "fresh-step min_y/max_y linear map to int32 [0,T]",
        },
        "baseline_paging": baseline_paging,
        "warmup": {"rows": 128, "measured": False},
        "steps": steps,
        "scaling": scaling,
        "forbidden_metrics_computed": False,
        "saved_model": False,
        "t006_method_approved": False,
    }


def validate_full_gate(candidate: str, gate_result: dict[str, object]) -> None:
    if candidate != "C11":
        raise RuntimeError("a full C8 fit is prohibited")
    if gate_result.get("candidate") != "C11":
        raise RuntimeError("full C11 gate requires a C11 staircase result")
    scaling = gate_result.get("scaling", {})
    if not isinstance(scaling, dict):
        raise RuntimeError("C11 staircase scaling record is missing")
    if not scaling.get("stable") or not scaling.get("full_c11_time_gate_pass"):
        raise RuntimeError("C11 staircase did not pass the full-run gate")


def run_full_c11(
    project_root: Path,
    redd_root: Path,
    gate_result: dict[str, object],
) -> dict[str, object]:
    validate_full_gate("C11", gate_result)
    raw_slices = load_training_slices(project_root, redd_root)
    rows = build_feature_rows(raw_slices, "C11")
    booleaniser = fit_booleaniser(project_root, "C11", rows.features)
    boolean_start = time.perf_counter()
    encoded = booleaniser.transform(rows.features)
    boolean_seconds = time.perf_counter() - boolean_start
    prediction_indices = evenly_spaced_indices(rows.features.shape[0], PREDICTION_ROWS)
    prediction_encoded = np.ascontiguousarray(encoded[prediction_indices])
    baseline_paging = paging_samples(3)
    step = measure_step(
        encoded,
        rows.targets,
        prediction_encoded,
        rows.features.shape[0],
        baseline_paging,
    )
    step["booleanisation_wall_seconds"] = boolean_seconds
    step["booleanisation_rows_per_second"] = rows.features.shape[0] / boolean_seconds
    stop_reasons = []
    if float(step["fit_wall_seconds"]) > STEP_WALL_LIMIT_SECONDS:
        stop_reasons.append("fit wall time exceeded 10 minutes")
    if int(step["minimum_available_physical_bytes"]) < MIN_AVAILABLE_BYTES:
        stop_reasons.append("available physical memory fell below 1 GiB")
    if bool(step["probe_induced_paging"]):
        stop_reasons.append("probe-induced paging threshold was crossed")
    return {
        "schema_version": "1.0",
        "work_id": WORK_ID,
        "candidate": "C11",
        "run_kind": "full_training_rows_one_epoch",
        "spec_sha256": SPEC_SHA256,
        "rows": int(rows.features.shape[0]),
        "row_identity_sha256": rows.identity_sha256,
        "baseline_paging": baseline_paging,
        "step": step,
        "stop_reasons": stop_reasons,
        "forbidden_metrics_computed": False,
        "saved_model": False,
        "t006_method_approved": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--redd-root", type=Path, required=True)
    parser.add_argument("--candidate", choices=("C8", "C11"), required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--gate-result", type=Path)
    return parser.parse_args()


def main() -> None:
    raise UnsupervisedExecutionDenied(
        "legacy multi-step R006 execution is disabled; use bounded_supervisor.py "
        "with r006_tmu_step_worker.py"
    )


if __name__ == "__main__":
    main()
