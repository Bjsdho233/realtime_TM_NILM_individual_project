#!/usr/bin/env python3
"""Execute the one authorised T005 canonical matrix and sentinel rerun."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

from tools.baseline.encoding import GaussianCdfEncoder, canonical_json_bytes
from tools.baseline.metrics import (
    evaluate_scope,
    fold_seed_appliance_summary,
    linear_percentile,
)
from tools.baseline.model import BinaryTsetlinMachine
from tools.baseline.pipeline import (
    APPLIANCES,
    BlockResult,
    candidate_identity_sha256,
    feature_schema_sha256,
    process_block,
)
from tools.data.protocol_r_access import (
    FROZEN_MANIFEST_SHA256,
    DevelopmentSlice,
    iter_development_rows,
    sha256_file,
)


BASELINE_MANIFEST = Path("artifacts/manifests/protocol_r_baseline_v1.json")
BASELINE_HASH = Path("artifacts/manifests/protocol_r_baseline_v1.sha256")
ELIGIBILITY_MANIFEST = Path(
    "artifacts/manifests/protocol_r_class_eligibility_v1.json"
)
FROZEN_AUDIT = Path("artifacts/manifests/protocol_r_support_audit_v1.json")
ARCHIVE = Path("experiments/T005-protocol-r-baseline-implementation")
LOCAL_MODEL_ROOT = Path("models/T005-protocol-r-baseline-implementation")
LOCAL_OUTPUT_ROOT = Path("outputs/T005-protocol-r-baseline-implementation")
SEEDS = (0, 1, 2, 3, 4)
FOLDS = (1, 2, 3, 4)
HOUSES = (1, 3, 5, 6)
FULL_SCOPE = ("fridge", "microwave")
DEVELOPMENT_SCOPE = ("fridge", "microwave", "dish washer")


def _json_dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _relative_sha256(root: Path, relative: str) -> str:
    return sha256_file(root / Path(relative))


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def verify_frozen_execution(root: Path, design_commit: str) -> tuple[dict, str]:
    if _git(root, "rev-parse", "HEAD") != design_commit:
        raise RuntimeError("HEAD is not the declared T005 pre-run commit")
    if _git(root, "status", "--short") != "":
        raise RuntimeError("tracked or untracked worktree content exists before execution")
    manifest_path = root / BASELINE_MANIFEST
    manifest_hash = sha256_file(manifest_path)
    sidecar = (
        f"{manifest_hash}  {BASELINE_MANIFEST.as_posix()}\n"
    )
    if (root / BASELINE_HASH).read_text(encoding="ascii") != sidecar:
        raise RuntimeError("T005 baseline manifest hash sidecar mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_status") != "frozen before canonical REDD model execution":
        raise RuntimeError("T005 baseline manifest is not frozen")
    if manifest["frozen_inputs"]["protocol_r_evaluation_sha256"] != FROZEN_MANIFEST_SHA256:
        raise RuntimeError("T005 references an unexpected Protocol R manifest")
    if sha256_file(root / Path("artifacts/manifests/protocol_r_evaluation_v1.json")) != FROZEN_MANIFEST_SHA256:
        raise RuntimeError("frozen Protocol R manifest changed")
    if sha256_file(root / FROZEN_AUDIT) != manifest["frozen_inputs"]["protocol_r_support_audit_sha256"]:
        raise RuntimeError("frozen Protocol R support audit changed")
    if sha256_file(root / ELIGIBILITY_MANIFEST) != manifest["frozen_inputs"]["class_eligibility_sha256"]:
        raise RuntimeError("class eligibility record changed")
    for source in manifest["source_identity"]:
        if _relative_sha256(root, source["path"]) != source["sha256"]:
            raise RuntimeError(f"frozen T005 source changed: {source['path']}")
    return manifest, manifest_hash


def load_role_blocks(
    root: Path,
    redd_root: Path,
    *,
    fold: int,
    role: str,
) -> list[BlockResult]:
    blocks: list[BlockResult] = []
    current_slice: DevelopmentSlice | None = None
    rows: list[dict[str, str]] = []
    for data_slice, _row_position, row in iter_development_rows(
        root,
        redd_root,
        validation_fold=fold,
        role=role,
        houses=HOUSES,
    ):
        if current_slice is not None and data_slice != current_slice:
            blocks.append(process_block(current_slice, rows))
            rows = []
        current_slice = data_slice
        rows.append(row)
    if current_slice is not None:
        blocks.append(process_block(current_slice, rows))
    if not blocks:
        raise RuntimeError(f"F{fold} {role} returned no blocks")
    if any(block.data_slice.block_id == "B5" for block in blocks):
        raise RuntimeError("protected B5 entered the T005 pipeline")
    return blocks


def candidate_matrix(blocks: list[BlockResult]) -> tuple[list, np.ndarray]:
    candidates = [
        candidate
        for block in blocks
        for candidate in block.candidates
    ]
    if not candidates:
        raise RuntimeError("aggregate-main pipeline emitted no candidates")
    return candidates, np.asarray(
        [candidate.features for candidate in candidates], dtype=np.float64
    )


def training_labels(
    blocks: list[BlockResult],
    candidates: list,
    appliance: str,
) -> tuple[np.ndarray, np.ndarray]:
    by_id = {
        candidate.candidate_id: index for index, candidate in enumerate(candidates)
    }
    indexes = []
    labels = []
    for block in blocks:
        association = block.associations[appliance]
        if not association.label_available:
            continue
        for candidate in block.candidates:
            status = association.candidate_status[candidate.candidate_id]
            if status in (0, 1):
                indexes.append(by_id[candidate.candidate_id])
                labels.append(status)
    label_array = np.asarray(labels, dtype=np.uint8)
    if not np.any(label_array == 1) or not np.any(label_array == 0):
        raise RuntimeError(
            f"training fold has no usable positive or negative candidate: {appliance}"
        )
    return np.asarray(indexes, dtype=np.int64), label_array


def prediction_payload(candidates: list, predictions: np.ndarray, votes: np.ndarray) -> bytes:
    lines = []
    for candidate, prediction, vote in zip(candidates, predictions, votes):
        lines.append(
            json.dumps(
                {
                    "candidate_id": candidate.candidate_id,
                    "prediction": int(prediction),
                    "signed_vote": int(vote),
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def metric_hash(metrics: dict[str, object]) -> str:
    return _sha256_bytes(canonical_json_bytes(metrics))


def benchmark(
    call: Callable[[int], object],
    *,
    input_count: int,
    warmups: int = 100,
    repetitions: int = 1000,
) -> tuple[float, float]:
    if input_count <= 0:
        raise RuntimeError("latency benchmark requires validation inputs")
    for index in range(warmups):
        call(index % input_count)
    timings = []
    for index in range(repetitions):
        started = time.perf_counter_ns()
        call(index % input_count)
        timings.append(time.perf_counter_ns() - started)
    return linear_percentile(timings, 50), linear_percentile(timings, 95)


def _write_csv(path: Path, columns: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def run_matrix(
    root: Path,
    redd_root: Path,
    *,
    folds: tuple[int, ...],
    seeds: tuple[int, ...],
    run_name: str,
    write_costs: bool,
) -> dict[str, object]:
    metrics_rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []
    cost_rows: list[dict[str, object]] = []
    artifact_rows: list[dict[str, object]] = []
    reproducibility: dict[str, dict[str, object]] = {}
    schema_hash = feature_schema_sha256()

    for fold in folds:
        print(f"[T005] F{fold}: loading admitted training/validation blocks", flush=True)
        training_blocks = load_role_blocks(root, redd_root, fold=fold, role="training")
        validation_blocks = load_role_blocks(root, redd_root, fold=fold, role="validation")
        training_candidates, training_features = candidate_matrix(training_blocks)
        validation_candidates, validation_features = candidate_matrix(validation_blocks)
        encoder = GaussianCdfEncoder.fit(
            training_features, feature_schema_sha256=schema_hash
        )
        encoded_training = encoder.transform(training_features)
        encoded_validation = encoder.transform(validation_features)
        encoder_relative = (
            LOCAL_MODEL_ROOT / run_name / "encoders" / f"F{fold}.json"
        )
        encoder_path = root / encoder_relative
        encoder_path.parent.mkdir(parents=True, exist_ok=True)
        encoder_path.write_bytes(encoder.serialize())
        artifact_rows.append(
            {
                "artifact_type": "encoder",
                "run": run_name,
                "fold": f"F{fold}",
                "seed": None,
                "appliance": None,
                "locator": encoder_relative.as_posix(),
                "sha256": encoder.sha256(),
                "bytes": len(encoder.serialize()),
                "tracked": False,
            }
        )
        for role, blocks in (
            ("training", training_blocks),
            ("validation", validation_blocks),
        ):
            by_house: dict[int, Counter[str]] = {}
            for block in blocks:
                counter = by_house.setdefault(block.data_slice.house, Counter())
                counter.update(block.diagnostics)
                for appliance in APPLIANCES:
                    association = block.associations[appliance]
                    for key, value in association.excluded_counts.items():
                        counter[f"{appliance}:{key}"] += int(value)
            for house, values in sorted(by_house.items()):
                diagnostic_rows.append(
                    {
                        "fold": f"F{fold}",
                        "role": role,
                        "house": f"H{house}",
                        "main_edge_count": values["main_edge_count"],
                        "rising_edge_count": values["rising_edge_count"],
                        "falling_edge_count": values["falling_edge_count"],
                        "paired_count": values["paired_count"],
                        "candidate_count": values["candidate_count"],
                        "expired_rise_count": values["expired_rise_count"],
                        "unmatched_fall_count": values["unmatched_fall_count"],
                        "contained_exclusion_count": values[
                            "contained_candidate_exclusion_count"
                        ],
                        "non_finite_main_count": values["non_finite_main_count"],
                        "target_diagnostics_json": json.dumps(
                            {
                                key: value
                                for key, value in sorted(values.items())
                                if ":" in key
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    }
                )

        for seed in seeds:
            print(f"[T005] F{fold} seed {seed}: training three fresh models", flush=True)
            models: dict[str, BinaryTsetlinMachine] = {}
            model_sizes: dict[str, int] = {}
            run_record: dict[str, object] = {
                "training_candidate_sha256": candidate_identity_sha256(
                    training_candidates
                ),
                "validation_candidate_sha256": candidate_identity_sha256(
                    validation_candidates
                ),
                "encoder_sha256": encoder.sha256(),
                "appliances": {},
            }
            for appliance in APPLIANCES:
                train_indexes, train_targets = training_labels(
                    training_blocks, training_candidates, appliance
                )
                model = BinaryTsetlinMachine(seed=seed)
                if not model.state_action_consistent():
                    raise RuntimeError("model initial state/action consistency failed")
                training_started = time.perf_counter()
                order_hashes = model.fit(
                    encoded_training[train_indexes],
                    train_targets,
                    epochs=10,
                    shuffle_seed=seed,
                )
                training_seconds = time.perf_counter() - training_started
                inference = model.to_inference_bytes()
                reloaded = BinaryTsetlinMachine.from_inference_bytes(
                    inference, seed=seed
                )
                predictions, signed_votes = model.predict(encoded_validation)
                reload_predictions, reload_votes = reloaded.predict(encoded_validation)
                if not np.array_equal(predictions, reload_predictions) or not np.array_equal(
                    signed_votes, reload_votes
                ):
                    raise RuntimeError("canonical inference save/reload parity failed")
                model_relative = (
                    LOCAL_MODEL_ROOT
                    / run_name
                    / f"F{fold}"
                    / f"seed_{seed}"
                    / f"{appliance.replace(' ', '_')}.t5tm.bin"
                )
                model_path = root / model_relative
                model_path.parent.mkdir(parents=True, exist_ok=True)
                model_path.write_bytes(inference)
                prediction = prediction_payload(
                    validation_candidates, predictions, signed_votes
                )
                prediction_relative = (
                    LOCAL_OUTPUT_ROOT
                    / run_name
                    / "predictions"
                    / f"F{fold}"
                    / f"seed_{seed}"
                    / f"{appliance.replace(' ', '_')}.jsonl"
                )
                prediction_path = root / prediction_relative
                prediction_path.parent.mkdir(parents=True, exist_ok=True)
                prediction_path.write_bytes(prediction)
                model_hash = _sha256_bytes(inference)
                prediction_hash = _sha256_bytes(prediction)
                artifact_rows.extend(
                    [
                        {
                            "artifact_type": "inference_model",
                            "run": run_name,
                            "fold": f"F{fold}",
                            "seed": seed,
                            "appliance": appliance,
                            "locator": model_relative.as_posix(),
                            "sha256": model_hash,
                            "bytes": len(inference),
                            "tracked": False,
                        },
                        {
                            "artifact_type": "row_level_prediction",
                            "run": run_name,
                            "fold": f"F{fold}",
                            "seed": seed,
                            "appliance": appliance,
                            "locator": prediction_relative.as_posix(),
                            "sha256": prediction_hash,
                            "bytes": len(prediction),
                            "tracked": False,
                        },
                    ]
                )
                pooled_metrics = None
                prediction_map = {
                    candidate.candidate_id: int(value)
                    for candidate, value in zip(validation_candidates, predictions)
                }
                for house in (*HOUSES, None):
                    values = evaluate_scope(
                        validation_blocks,
                        appliance=appliance,
                        predictions=prediction_map,
                        house=house,
                    )
                    row = {
                        "fold": f"F{fold}",
                        "seed": seed,
                        "house": "ALL" if house is None else f"H{house}",
                        "appliance": appliance,
                        **values,
                    }
                    row["excluded_reasons_json"] = json.dumps(
                        row.pop("excluded_reasons"),
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    metrics_rows.append(row)
                    if house is None:
                        pooled_metrics = values
                assert pooled_metrics is not None
                run_record["appliances"][appliance] = {
                    "model_sha256": model_hash,
                    "prediction_sha256": prediction_hash,
                    "pooled_metric_sha256": metric_hash(pooled_metrics),
                    "order_sha256_by_epoch": order_hashes,
                    "training_seconds": training_seconds,
                    "training_positive_candidates": int(np.sum(train_targets == 1)),
                    "training_negative_candidates": int(np.sum(train_targets == 0)),
                }
                models[appliance] = model
                model_sizes[appliance] = len(inference)

            if write_costs:
                for appliance, model in models.items():
                    median, p95 = benchmark(
                        lambda index, current=model: current.predict_one(
                            encoded_validation[index]
                        ),
                        input_count=len(validation_candidates),
                    )
                    cost_rows.append(
                        {
                            "fold": f"F{fold}",
                            "seed": seed,
                            "scope": appliance,
                            "boundary": "TM evaluation only",
                            "median_value": median,
                            "p95_value": p95,
                            "unit": "ns",
                            "serialized_inference_bytes": model_sizes[appliance],
                            "shared_encoder_bytes": len(encoder.serialize()),
                            "complete_bundle_bytes": (
                                model_sizes[appliance] + len(encoder.serialize())
                            ),
                            "warmups": 100,
                            "timed_calls": 1000,
                            "batch_size": 1,
                        }
                    )
                for scope, appliances in (
                    ("full_eligible_macro_2class", FULL_SCOPE),
                    ("development_scope_macro_3class", DEVELOPMENT_SCOPE),
                ):
                    median, p95 = benchmark(
                        lambda index, names=appliances: tuple(
                            models[name].predict_one(encoded_validation[index])
                            for name in names
                        ),
                        input_count=len(validation_candidates),
                    )
                    cost_rows.append(
                        {
                            "fold": f"F{fold}",
                            "seed": seed,
                            "scope": scope,
                            "boundary": "named ensemble TM evaluations",
                            "median_value": median,
                            "p95_value": p95,
                            "unit": "ns",
                            "serialized_inference_bytes": sum(
                                model_sizes[name] for name in appliances
                            ),
                            "shared_encoder_bytes": len(encoder.serialize()),
                            "complete_bundle_bytes": (
                                sum(model_sizes[name] for name in appliances)
                                + len(encoder.serialize())
                            ),
                            "warmups": 100,
                            "timed_calls": 1000,
                            "batch_size": 1,
                        }
                    )
                    def feature_ensemble(index: int, names=appliances) -> tuple[int, ...]:
                        encoded = encoder.transform(
                            validation_features[index : index + 1]
                        )[0]
                        return tuple(models[name].predict_one(encoded) for name in names)

                    median, p95 = benchmark(
                        feature_ensemble,
                        input_count=len(validation_candidates),
                    )
                    cost_rows.append(
                        {
                            "fold": f"F{fold}",
                            "seed": seed,
                            "scope": scope,
                            "boundary": "Booleanisation plus named ensemble",
                            "median_value": median,
                            "p95_value": p95,
                            "unit": "ns",
                            "serialized_inference_bytes": sum(
                                model_sizes[name] for name in appliances
                            ),
                            "shared_encoder_bytes": len(encoder.serialize()),
                            "complete_bundle_bytes": (
                                sum(model_sizes[name] for name in appliances)
                                + len(encoder.serialize())
                            ),
                            "warmups": 100,
                            "timed_calls": 1000,
                            "batch_size": 1,
                        }
                    )
                waits = [
                    candidate.onset_to_output_samples for candidate in validation_candidates
                ]
                cost_rows.append(
                    {
                        "fold": f"F{fold}",
                        "seed": seed,
                        "scope": "algorithmic_waiting",
                        "boundary": "onset-to-output samples",
                        "median_value": linear_percentile(waits, 50),
                        "p95_value": linear_percentile(waits, 95),
                        "unit": "samples",
                        "serialized_inference_bytes": "",
                        "shared_encoder_bytes": "",
                        "complete_bundle_bytes": "",
                        "warmups": 0,
                        "timed_calls": len(waits),
                        "batch_size": 1,
                    }
                )
                cost_rows.append(
                    {
                        "fold": f"F{fold}",
                        "seed": seed,
                        "scope": "algorithmic_waiting",
                        "boundary": "fall-to-output samples; 24 nominal seconds",
                        "median_value": 8.0,
                        "p95_value": 8.0,
                        "unit": "samples",
                        "serialized_inference_bytes": "",
                        "shared_encoder_bytes": "",
                        "complete_bundle_bytes": "",
                        "warmups": 0,
                        "timed_calls": len(waits),
                        "batch_size": 1,
                    }
                )
            reproducibility[f"F{fold}|seed={seed}"] = run_record
    return {
        "metrics_rows": metrics_rows,
        "diagnostic_rows": diagnostic_rows,
        "cost_rows": cost_rows,
        "artifact_rows": artifact_rows,
        "reproducibility": reproducibility,
    }


def compare_sentinel(canonical: dict, sentinel: dict) -> dict[str, object]:
    expected = canonical["reproducibility"]["F1|seed=0"]
    observed = sentinel["reproducibility"]["F1|seed=0"]
    comparisons = {
        "training_candidate_sha256": (
            expected["training_candidate_sha256"]
            == observed["training_candidate_sha256"]
        ),
        "validation_candidate_sha256": (
            expected["validation_candidate_sha256"]
            == observed["validation_candidate_sha256"]
        ),
        "encoder_sha256": expected["encoder_sha256"] == observed["encoder_sha256"],
    }
    for appliance in APPLIANCES:
        for field in ("model_sha256", "prediction_sha256", "pooled_metric_sha256"):
            comparisons[f"{appliance}:{field}"] = (
                expected["appliances"][appliance][field]
                == observed["appliances"][appliance][field]
            )
    return {
        "scope": "F1 seed 0 all three authorised models",
        "all_exact": all(comparisons.values()),
        "comparisons": comparisons,
    }


def aggregate_diagnostic_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return rows


def artifact_manifest(
    manifest_hash: str,
    design_commit: str,
    canonical: dict,
    sentinel: dict,
    sentinel_check: dict,
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "work_id": "T005",
        "baseline_manifest_sha256": manifest_hash,
        "pre_run_commit": design_commit,
        "artifact_policy": (
            "models and row-level predictions remain ignored local artefacts; "
            "only hashes, sizes and non-absolute locators are tracked"
        ),
        "canonical_artifacts": canonical["artifact_rows"],
        "sentinel_artifacts": sentinel["artifact_rows"],
        "sentinel_reproducibility": sentinel_check,
    }


def write_archive(
    root: Path,
    *,
    design_commit: str,
    manifest_hash: str,
    canonical: dict,
    sentinel: dict,
    sentinel_check: dict,
) -> None:
    archive = root / ARCHIVE
    tables = archive / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    summary_rows = fold_seed_appliance_summary(canonical["metrics_rows"])
    metric_columns = [
        "fold",
        "seed",
        "house",
        "appliance",
        "tp",
        "tn",
        "fp",
        "fn",
        "eligible_positive_support",
        "eligible_negative_support",
        "excluded_unavailable_count",
        "precision",
        "recall",
        "f1",
        "binary_accuracy",
        "precision_zero_denominator",
        "recall_zero_denominator",
        "f1_zero_denominator",
        "accuracy_zero_denominator",
        "matched_target_episode_count",
        "unmatched_target_episode_count",
        "duplicate_candidate_count",
        "candidate_count",
        "episode_coverage",
        "episode_coverage_zero_denominator",
        "excluded_reasons_json",
    ]
    _write_csv(
        tables / "development_metrics.csv",
        metric_columns,
        canonical["metrics_rows"],
    )
    _write_csv(
        tables / "development_summary.csv",
        ["scope", "metric", "value", "unit", "aggregation", "sample_std", "seed_values"],
        [
            {
                **row,
                "seed_values": json.dumps(row["seed_values"], separators=(",", ":")),
            }
            for row in summary_rows
        ],
    )
    _write_csv(
        tables / "model_costs.csv",
        [
            "fold",
            "seed",
            "scope",
            "boundary",
            "median_value",
            "p95_value",
            "unit",
            "serialized_inference_bytes",
            "shared_encoder_bytes",
            "complete_bundle_bytes",
            "warmups",
            "timed_calls",
            "batch_size",
        ],
        canonical["cost_rows"],
    )
    _write_csv(
        tables / "pipeline_diagnostics.csv",
        [
            "fold",
            "role",
            "house",
            "main_edge_count",
            "rising_edge_count",
            "falling_edge_count",
            "paired_count",
            "candidate_count",
            "expired_rise_count",
            "unmatched_fall_count",
            "contained_exclusion_count",
            "non_finite_main_count",
            "target_diagnostics_json",
        ],
        aggregate_diagnostic_rows(canonical["diagnostic_rows"]),
    )
    artifacts = artifact_manifest(
        manifest_hash, design_commit, canonical, sentinel, sentinel_check
    )
    _json_dump(archive / "model_artifacts.json", artifacts)
    environment_lines = [
        f"platform={platform.platform()}",
        f"python={platform.python_version()}",
        f"python_implementation={platform.python_implementation()}",
        f"numpy={np.__version__}",
        f"timer=time.perf_counter_ns",
        "latency_batch_size=1",
        "latency_warmups=100",
        "latency_timed_calls=1000",
        "percentile_interpolation=linear",
        "data_root=${REDD_ROOT}",
    ]
    (archive / "environment.txt").write_text(
        "\n".join(environment_lines) + "\n", encoding="utf-8", newline="\n"
    )
    commands = [
        "python -m unittest discover -s tests/baseline -t . -v",
        "python scripts/check_repo.py",
        "git diff --check",
        (
            "python -m tools.baseline.run_protocol_r_baseline "
            "--redd-root ${REDD_ROOT} --design-commit ${T005_PRE_RUN_COMMIT}"
        ),
    ]
    (archive / "commands.log").write_text(
        "\n".join(commands) + "\n", encoding="utf-8", newline="\n"
    )
    summary_lookup = {row["scope"]: row for row in summary_rows}
    primary = summary_lookup["full_eligible_macro_2class"]
    supplemental = summary_lookup["development_scope_macro_3class"]
    report = f"""# T005 — Protocol R Baseline Implementation

## Agent Brief

- Lifecycle outcome: completed development baseline
- Protocol scope: B1–B4 development only
- Primary summary: `full_eligible_macro_2class`
- Supplemental summary: `development_scope_macro_3class`
- Locked-test/Protocol X access: none
- Python-reference only: yes

## Result

固定 aggregate-main baseline 已完成四个 folds、五个 seeds 和三个 authorised
appliance。`washer dryer` 未训练或评分。

- `full_eligible_macro_2class` mean F1:
  `{primary['value']:.12f}`，sample std `{primary['sample_std']:.12f}`；
- `development_scope_macro_3class` mean F1:
  `{supplemental['value']:.12f}`，sample std
  `{supplemental['sample_std']:.12f}`。

第二项包含 development-only `dish washer`，不能称为完整或 confirmatory
Protocol R evidence。完整 fold × seed × house × appliance counts 和 metrics 见
`tables/development_metrics.csv`。

## Method boundary

使用 50 W first-difference detector、causal FIFO pairing、32-sample pre-history、
8-sample post-context、23-slot Han-compatible aggregate-main features、training-only
Gaussian-CDF 8-bit Booleanisation，以及每 appliance 独立的 200-clause、50-state、
`T=20`、`s=6.0`、10-epoch binary TM。

项目自有 TM repair 只修复 Han 初始化后 action/mask 未同步的问题，并将所有 RNG
绑定到 declared seed；学习规则和固定参数未改变。zero signed-vote tie 预测为
negative。

## Reproducibility

F1 / seed 0 / three-model clean sentinel exact match:
`{str(sentinel_check['all_exact']).lower()}`。比较覆盖 candidate、encoder、model、
prediction 和 aggregate metric hashes。

## Limitations

- 这是 development evidence，不是 B5 locked-test result；
- latency 和 bytes 是 Python-reference/inference-serialization measurement，
  不是 host-native 或 Pico measurement；
- detector/pairer misses 作为 explicit no-output false negatives 进入指标；
- 没有根据结果进行 tuning 或第二方法运行。
"""
    (archive / "BASELINE_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )

    checksum_targets = [
        archive / "BASELINE_REPORT.md",
        archive / "environment.txt",
        archive / "commands.log",
        archive / "model_artifacts.json",
        *sorted(tables.glob("*.csv")),
    ]
    checksum_lines = [
        f"{sha256_file(path)}  {path.relative_to(archive).as_posix()}"
        for path in checksum_targets
    ]
    (archive / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="ascii", newline="\n"
    )
    archive_files = []
    role_by_name = {
        "BASELINE_REPORT.md": "narrative",
        "environment.txt": "environment",
        "commands.log": "command_log",
        "model_artifacts.json": "configuration",
        "CHECKSUMS.sha256": "checksum",
    }
    for path in sorted(
        [item for item in archive.rglob("*") if item.is_file() and item.name != "result.json"]
    ):
        relative = path.relative_to(archive).as_posix()
        archive_files.append(
            {
                "path": relative,
                "role": (
                    "aggregate_table"
                    if relative.startswith("tables/")
                    else role_by_name[path.name]
                ),
                "sha256": sha256_file(path),
                "contains_row_level_data": False,
                "contains_sensitive_data": False,
            }
        )
    completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {
        "$schema": "schemas/work-result.schema.json",
        "schema_version": "1.0",
        "work_id": "T005",
        "name": "Protocol R Baseline Implementation",
        "owner": "Tianhang Tan",
        "completed_at": completed_at,
        "lifecycle_status": "completed",
        "superseded_by": None,
        "track": "T-series",
        "work_kind": "formal_implementation",
        "experiment_kind": "not_applicable",
        "workflow_layer": "aggregate-main classification-TM development baseline",
        "protocol": {
            "name": "Protocol R v1",
            "data_scope": "H1/H3/H5/H6 B1-B4 four-fold development CV",
            "claim_scope": "formal development",
            "sealed_test_access": False,
        },
        "status": "complete",
        "design_sha256": None,
        "design_commit": None,
        "task_definition": "docs/tasks/T005-protocol-r-baseline-implementation.md",
        "output_policy": "compact aggregate evidence and hashes only",
        "execution": {
            "status": "succeeded",
            "notes": "one canonical matrix and one F1 seed-0 sentinel rerun",
        },
        "validity": {
            "status": "valid",
            "notes": "fixed method, protected access guard, exact sentinel hashes",
        },
        "provenance": {
            "base_git_commit": design_commit,
            "worktree_dirty_at_execution": False,
            "executed_source_files": [
                {
                    "path": record["path"],
                    "sha256": record["sha256"],
                }
                for record in json.loads(
                    (root / BASELINE_MANIFEST).read_text(encoding="utf-8")
                )["source_identity"]
            ],
            "config_files": [
                {"path": BASELINE_MANIFEST.as_posix(), "sha256": manifest_hash}
            ],
            "environment": {
                "path": "experiments/T005-protocol-r-baseline-implementation/environment.txt",
                "sha256": sha256_file(archive / "environment.txt"),
            },
            "data_manifests": [],
            "reused_learned_artifacts": [],
        },
        "reproducibility": {
            "seeds": list(SEEDS),
            "folds": [f"F{fold}" for fold in FOLDS],
            "repeat_count": 2,
        },
        "safety_assertions": {
            "no_candidate_or_locked_test_feedback": True,
            "no_candidate_or_locked_test_derived_learned_state": True,
            "preprocessing_fit_scope": "train_only",
            "shared_inputs_are_immutable_and_hashed": True,
        },
        "outcome": "completed",
        "result_summary": (
            "Fixed Protocol R B1-B4 development baseline completed with two named "
            "macro scopes and exact F1/seed-0 sentinel reproducibility."
        ),
        "metrics": [
            {
                "name": "macro_seed_fold_mean_f1",
                "value": float(primary["value"]),
                "unit": "ratio",
                "scope": "full_eligible_macro_2class",
                "definition": "macro F1 for fridge and microwave",
                "aggregation": str(primary["aggregation"]),
                "measurement_boundary": "end-to-end candidate plus no-output target misses",
            },
            {
                "name": "macro_seed_fold_mean_f1",
                "value": float(supplemental["value"]),
                "unit": "ratio",
                "scope": "development_scope_macro_3class",
                "definition": "macro F1 including development-only dish washer",
                "aggregation": str(supplemental["aggregation"]),
                "measurement_boundary": "end-to-end candidate plus no-output target misses",
            },
        ],
        "observations": [
            "No method or parameter was selected using the result.",
            "F1 seed-0 sentinel reproduced candidate, encoder, model, prediction and metric hashes.",
        ],
        "evidence": [
            {
                "claim": "T005 development baseline result",
                "path": "BASELINE_REPORT.md",
                "scope": "formal_development",
                "limitations": "B1-B4 only; dish washer is development-only",
            },
            {
                "claim": "Full fold-seed-house-appliance aggregate metrics",
                "path": "tables/development_metrics.csv",
                "scope": "formal_development",
                "limitations": "No row-level predictions or locked-test data",
            },
        ],
        "archive": {"files": archive_files},
        "decision": {
            "action": "complete",
            "notes": "Close T005 without tuning or starting another task.",
        },
        "limitations": [
            "No B5 or Protocol X model evaluation.",
            "Dish washer evidence is development-only.",
            "Python-reference latency is not host-native or Pico performance.",
        ],
    }
    _json_dump(archive / "result.json", result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redd-root", type=Path, required=True)
    parser.add_argument("--design-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    redd_root = args.redd_root.resolve()
    manifest, manifest_hash = verify_frozen_execution(root, args.design_commit)
    print("[T005] frozen design and source identities verified", flush=True)
    canonical = run_matrix(
        root,
        redd_root,
        folds=FOLDS,
        seeds=SEEDS,
        run_name="canonical",
        write_costs=True,
    )
    print("[T005] canonical matrix complete; starting clean sentinel", flush=True)
    sentinel = run_matrix(
        root,
        redd_root,
        folds=(1,),
        seeds=(0,),
        run_name="sentinel",
        write_costs=False,
    )
    sentinel_check = compare_sentinel(canonical, sentinel)
    if not sentinel_check["all_exact"]:
        raise RuntimeError("F1 seed-0 sentinel did not reproduce exact hashes")
    write_archive(
        root,
        design_commit=args.design_commit,
        manifest_hash=manifest_hash,
        canonical=canonical,
        sentinel=sentinel,
        sentinel_check=sentinel_check,
    )
    print("[T005] archive written; sentinel exact", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
