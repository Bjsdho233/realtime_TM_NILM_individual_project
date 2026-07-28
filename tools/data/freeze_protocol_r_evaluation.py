#!/usr/bin/env python3
"""Freeze the deterministic T004 Protocol R evaluation manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


GENERATOR_NAME = "freeze_protocol_r_evaluation.py"
GENERATOR_VERSION = "1.0.0"
MANIFEST_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.json")
HASH_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.sha256")
PREDECESSOR_PATH = Path("artifacts/manifests/protocol_r_approved_split.json")
INVENTORY_PATH = Path("artifacts/manifests/redd_inventory.json")
PROTOCOL_R_HOUSES = (1, 3, 5, 6)
PROTOCOL_X_HOUSES = (2, 4)
TARGET_APPLIANCES = ("fridge", "microwave", "dish washer", "washer dryer")
REDD_COMMIT = "a621bbd6399e49c6798550618fe43b113149455b"
UPSTREAM_COMMIT = "8c5e90df34236ba0afcc4ec46ac083d829de4d51"
INVENTORY_TREE_SHA256 = "5e1ee53cdce2a5ad2d5007a08527bd1fc9486130d56dc008cf8c8ba8e336e73d"
CADENCE_SECONDS = 3
HISTORY_SAMPLES = 256
FUTURE_SAMPLES = 8
STATE_THRESHOLD_WATTS = 15.0
SEEDS = (0, 1, 2, 3, 4)
FILE_RE = re.compile(r"redd_house(?P<house>[1-6])_(?P<chunk>\d+)\.csv$")


def strict_json(path: Path) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant in {path}: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def byte_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_bytes(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def git_output(directory: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(directory), *args],
        text=True,
        encoding="utf-8",
    ).strip()


def file_identity(name: str) -> tuple[int, int]:
    match = FILE_RE.fullmatch(name)
    if not match:
        raise ValueError(f"unexpected REDD source filename: {name}")
    return int(match.group("house")), int(match.group("chunk"))


def five_block_ranges(row_count: int) -> list[tuple[int, int]]:
    if row_count < 0:
        raise ValueError("row_count must be non-negative")
    return [
        (row_count * (block - 1) // 5, row_count * block // 5)
        for block in range(1, 6)
    ]


def valid_target_range(start: int, end: int) -> dict[str, int]:
    valid_start = start + HISTORY_SAMPLES - 1
    valid_end = end - FUTURE_SAMPLES
    return {
        "row_start_inclusive": valid_start,
        "row_end_exclusive": valid_end,
        "target_count": max(0, valid_end - valid_start),
    }


def count_rows_and_header(path: Path) -> tuple[int, list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        row_count = sum(1 for _ in reader)
    if not header or header[0] != "":
        raise ValueError(f"expected unnamed source-index column: {path.name}")
    if len(header) != len(set(header)):
        raise ValueError(f"duplicate CSV columns: {path.name}")
    return row_count, header[1:]


def source_set_sha256(records: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: item["relative_path"]):
        digest.update(record["relative_path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def verify_external_snapshot(redd_root: Path) -> None:
    if not redd_root.is_dir():
        raise FileNotFoundError(f"REDD root does not exist: {redd_root}")
    if git_output(redd_root, "rev-parse", "HEAD") != REDD_COMMIT:
        raise RuntimeError("REDD source does not match the accepted D003 commit")
    if git_output(redd_root, "status", "--porcelain"):
        raise RuntimeError("REDD source worktree is not clean")


def verified_sources(project_root: Path, redd_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    predecessor = strict_json(project_root / PREDECESSOR_PATH)
    inventory = strict_json(project_root / INVENTORY_PATH)
    if predecessor["redd_submodule_commit"] != REDD_COMMIT:
        raise RuntimeError("predecessor REDD commit does not match D003")
    if predecessor["redd_content_tree_sha256"] != INVENTORY_TREE_SHA256:
        raise RuntimeError("predecessor content-tree identity does not match T002")
    if inventory["fingerprint"]["content_tree_sha256"] != INVENTORY_TREE_SHA256:
        raise RuntimeError("inventory content-tree identity does not match T002")

    expected = {
        Path(record["path"]).name: record for record in predecessor["source_files"]
    }
    actual_names = {
        path.name for path in redd_root.iterdir() if path.is_file() and path.suffix == ".csv"
    }
    if actual_names != set(expected):
        missing = sorted(set(expected) - actual_names)
        extra = sorted(actual_names - set(expected))
        raise RuntimeError(f"REDD file set mismatch; missing={missing}, extra={extra}")

    sources: list[dict[str, Any]] = []
    headers_by_house: dict[int, list[str]] = {}
    for name in sorted(expected, key=file_identity):
        path = redd_root / name
        expected_record = expected[name]
        house, chunk = file_identity(name)
        row_count, header = count_rows_and_header(path)
        content_hash = sha256_file(path)
        if row_count != expected_record["row_count"]:
            raise RuntimeError(f"row-count mismatch: {name}")
        if content_hash != expected_record["sha256"]:
            raise RuntimeError(f"source fingerprint mismatch: {name}")
        if house != expected_record["house"] or chunk != expected_record["chunk"]:
            raise RuntimeError(f"source identity mismatch: {name}")
        prior_header = headers_by_house.setdefault(house, header)
        if prior_header != header:
            raise RuntimeError(f"inconsistent channel mapping within H{house}: {name}")
        sources.append(
            {
                "relative_path": f"redd/{name}",
                "sha256": content_hash,
                "segment_id": f"redd_house{house}_{chunk}",
                "house": house,
                "chunk": chunk,
                "row_count": row_count,
            }
        )

    channels = []
    for house in range(1, 7):
        header = headers_by_house[house]
        if "main" not in header:
            raise RuntimeError(f"H{house} has no aggregate main column")
        channels.append(
            {
                "house": house,
                "source_columns": header,
                "aggregate_main_column": "main",
                "target_columns": {
                    appliance: appliance if appliance in header else None
                    for appliance in TARGET_APPLIANCES
                },
            }
        )
    return sources, channels


def fold_contract() -> list[dict[str, Any]]:
    return [
        {
            "fold_id": f"F{fold}",
            "validation_block": f"B{fold}",
            "training_blocks": [
                f"B{block}" for block in range(1, 5) if block != fold
            ],
        }
        for fold in range(1, 5)
    ]


def build_manifest(
    sources: list[dict[str, Any]],
    house_channel_mapping: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(sources) != 35:
        raise ValueError("the frozen input must contain exactly 35 source segments")
    if {record["house"] for record in sources} != set(range(1, 7)):
        raise ValueError("the frozen input must contain H1-H6")

    manifest_sources = []
    for source in sources:
        record = dict(source)
        if source["house"] in PROTOCOL_R_HOUSES:
            record["protocol_role"] = "protocol_r_population"
            record["blocks"] = [
                {
                    "block_id": f"B{index}",
                    "row_start_inclusive": start,
                    "row_end_exclusive": end,
                    "row_count": end - start,
                    "valid_target_range": valid_target_range(start, end),
                    "role": "development" if index < 5 else "locked_test",
                }
                for index, (start, end) in enumerate(
                    five_block_ranges(source["row_count"]), 1
                )
            ]
        else:
            record["protocol_role"] = "protocol_x_held_out_house"
            record["source_range"] = {
                "row_start_inclusive": 0,
                "row_end_exclusive": source["row_count"],
            }
            record["valid_target_range"] = valid_target_range(
                0, source["row_count"]
            )
            record["blocks"] = []
        manifest_sources.append(record)

    return {
        "schema_version": "1.0",
        "manifest_id": "t004-protocol-r-evaluation-v1",
        "manifest_status": "frozen evaluation contract; B5 locked until T011",
        "generator": {
            "name": GENERATOR_NAME,
            "version": GENERATOR_VERSION,
            "determinism": "no generation timestamp; UTF-8 LF JSON; source order is numeric house/chunk",
        },
        "source_dataset": {
            "identity": "Han preprocessed synchronized REDD submodule CSV chunks",
            "upstream_commit": UPSTREAM_COMMIT,
            "redd_submodule_commit": REDD_COMMIT,
            "t002_inventory_content_tree_sha256": INVENTORY_TREE_SHA256,
            "source_file_set_sha256": source_set_sha256(sources),
            "canonical_root_locator": "${HAN_UPSTREAM_SNAPSHOT}/redd",
            "absolute_path_stored": False,
            "docs_redd_used": False,
            "original_raw_redd_provenance": "unresolved",
        },
        "time_contract": {
            "name": "sequence-first, row-position blocked",
            "nominal_cadence_seconds": CADENCE_SECONDS,
            "row_identity": [
                "house",
                "segment_id",
                "zero_based_row_position",
            ],
            "original_timestamp_claimed": False,
            "cross_segment_order_defined": False,
        },
        "protocol_r": {
            "version": "1.0",
            "population_houses": list(PROTOCOL_R_HOUSES),
            "evaluation_type": "mixed-house within-population",
            "block_formula": {
                "count": 5,
                "start_k": "floor(n * (k - 1) / 5)",
                "end_k": "floor(n * k / 5)",
                "interval": "half-open [start_k, end_k)",
            },
            "development_blocks": ["B1", "B2", "B3", "B4"],
            "locked_test_block": "B5",
            "blocked_cv": fold_contract(),
            "final_development_fit": "after method freeze only, B1-B4 may be combined",
            "locked_test_authority": "T011 one-time final Protocol R evaluation only",
        },
        "protocol_x": {
            "version": "1.0",
            "held_out_houses": list(PROTOCOL_X_HOUSES),
            "role": "separate optional held-out-house generalisation",
            "development_access": False,
            "model_selection_use": False,
            "t004_access": "source identity and aggregate support audit only; no model evaluation",
        },
        "dependency_contract": {
            "maximum_history_samples": HISTORY_SAMPLES,
            "maximum_future_context_samples": FUTURE_SAMPLES,
            "valid_target_rule": "block_start + 255 <= t < block_end - 8",
            "containment": "all history, future context, lag, rolling state, event pairing, and post-context must remain inside one segment and block",
            "crossing_episode_policy": "discard",
            "state_reset_boundaries": ["house", "segment", "block", "split"],
            "fit_scope": "current training blocks only",
            "fit_forbidden_roles": ["validation", "locked_test", "protocol_x"],
            "larger_dependency_policy": "requires a new protocol version and manifest",
        },
        "target_contract": {
            "approved_appliances": list(TARGET_APPLIANCES),
            "missing_column": "label unavailable; exclude that house-appliance unit; never impute all-zero ground truth",
            "missing_or_non_finite_label": "exclude affected target/episode for that appliance and break episode continuity",
            "overlap": "retain independent multi-label positives when every contributing approved appliance label is observable",
            "ambiguous_or_incomplete_episode": "exclude from event-level scoring and report exclusion count",
            "on_state_threshold_watts": STATE_THRESHOLD_WATTS,
        },
        "binary_classification_contract": {
            "model_family": "one binary TM per appliance",
            "scoring_unit": "eligible event with an availability mask over appliance labels",
            "simultaneous_positives": "retained as independent positives",
            "multiple_positive_predictions": "retained; no forced single-class resolver",
            "all_negative_prediction": "background/reject",
            "decision_rule": "signed vote > 0 is positive; signed vote <= 0 is negative",
            "tie_rule": "zero signed vote is negative",
            "confusion_representation": "one TP/FP/FN/TN matrix per appliance over eligible units",
            "accuracy_name": "per-appliance binary accuracy; event exact-match accuracy may be reported only where all four labels are observable",
            "macro_rule": "unweighted mean over the four frozen appliances; unavailable house-appliance units do not become zero-support classes",
        },
        "regression_contract": {
            "target": "y_t = max(0, appliance submeter power at row t)",
            "pre_threshold_target": False,
            "state_threshold_use": "15 W is used only for derived ON/OFF metrics",
            "target_time": "t",
            "available_time": "t + D",
            "raw_prediction_required": True,
            "clipped_prediction_upper_bound": "maximum target fitted from the current training blocks only",
            "raw_and_clipped_metrics_separate": True,
            "metrics": [
                "pooled NAE (constant-zero prediction is exactly 1 when true energy is positive)",
                "full-stream MAE",
                "full-stream median absolute error",
                "ON-only MAE",
                "state precision, recall, and F1 at 15 W",
                "OFF false-positive watts and energy",
                "symmetric absolute energy error (SAE)",
                "missed energy",
                "episode energy error",
                "error stratified by frozen true-power bins",
                "fraction of raw predictions outside the training target range",
            ],
            "reporting_slices": ["fold", "house", "appliance", "pooled"],
        },
        "ctm_timing_contract": {
            "source_episode": "inclusive [rise, fall] rows within one segment and block",
            "event_classification_time": "row/time at which the binary class decision is emitted",
            "post_context_completion_time": "fall row/time plus declared post-context D",
            "model_computation_time": "measured compute duration excluding event waiting",
            "onset_to_output_latency": "classification output time minus rise time",
            "fall_to_output_latency": "classification output time minus fall time",
            "summary": ["median", "P95"],
            "sample_level_backfill": "prohibited unless separately defined and validated",
        },
        "metric_and_uncertainty_contract": {
            "development_metrics": "B1-B4 validation folds only",
            "locked_test_metrics": "B5, T011 only",
            "protocol_x_metrics": "separate report; never used for Protocol R model selection",
            "seeds": list(SEEDS),
            "seed_summary": ["per-seed values", "mean", "sample standard deviation"],
            "fold_summary": ["per-fold values", "unweighted mean across F1-F4"],
            "house_and_appliance_reporting": True,
            "pooled_reporting": True,
            "weak_support_rule": "always report eligible support and exclusions; do not suppress or replace weak units",
            "power_bins_watts": [
                {"label": "[0,15)", "start_inclusive": 0, "end_exclusive": 15},
                {"label": "[15,100)", "start_inclusive": 15, "end_exclusive": 100},
                {"label": "[100,500)", "start_inclusive": 100, "end_exclusive": 500},
                {"label": "[500,+inf)", "start_inclusive": 500, "end_exclusive": None},
            ],
            "model_size": ["per-model serialized bytes", "ensemble serialized bytes"],
            "latency": [
                "per-model compute latency",
                "full-ensemble compute latency",
                "feature-to-decision latency",
                "event/post-context waiting time",
            ],
        },
        "access_contract": {
            "development_roles": ["training", "validation"],
            "development_houses": list(PROTOCOL_R_HOUSES),
            "development_blocks": ["B1", "B2", "B3", "B4"],
            "denied_roles": ["B5", "locked_test", "protocol_x"],
            "denied_houses": list(PROTOCOL_X_HOUSES),
            "ordinary_entry_has_locked_test_switch": False,
            "formal_test_entry": "future independent T011 command with explicit authority",
        },
        "house_channel_mapping": house_channel_mapping,
        "source_files": manifest_sources,
        "known_limitations": [
            "original calendar timestamps and recording gaps are not recovered",
            "historical raw-to-preprocessed REDD provenance is incomplete",
            "H2/H4 support labels were inspected during T002 and H2/H4 were used by Protocol H compatibility work",
            "Protocol X remains optional and is not a Protocol R model-selection source",
        ],
    }


def write_frozen_outputs(project_root: Path, manifest: dict[str, Any]) -> str:
    payload = json_bytes(manifest)
    digest = byte_sha256(payload)
    manifest_path = project_root / MANIFEST_PATH
    hash_path = project_root / HASH_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if manifest_path.exists() and manifest_path.read_bytes() != payload:
        raise RuntimeError(f"refusing to overwrite different frozen manifest: {MANIFEST_PATH}")
    sidecar = f"{digest}  {MANIFEST_PATH.as_posix()}\n".encode("ascii")
    if hash_path.exists() and hash_path.read_bytes() != sidecar:
        raise RuntimeError(f"refusing to overwrite different frozen hash: {HASH_PATH}")

    manifest_path.write_bytes(payload)
    hash_path.write_bytes(sidecar)
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redd-root", required=True, type=Path)
    parser.add_argument("--project-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    redd_root = args.redd_root.resolve()
    verify_external_snapshot(redd_root)
    sources, channels = verified_sources(project_root, redd_root)
    manifest = build_manifest(sources, channels)
    digest = write_frozen_outputs(project_root, manifest)
    print(
        json.dumps(
            {
                "manifest": MANIFEST_PATH.as_posix(),
                "sha256": digest,
                "source_segments": len(sources),
                "protocol_r_houses": list(PROTOCOL_R_HOUSES),
                "protocol_x_houses": list(PROTOCOL_X_HOUSES),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
