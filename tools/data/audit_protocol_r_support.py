#!/usr/bin/env python3
"""Create aggregate-only T004 support evidence after the split is frozen."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MANIFEST_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.json")
MANIFEST_HASH_PATH = Path("artifacts/manifests/protocol_r_evaluation_v1.sha256")
MANIFEST_SHA256 = "501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5"
AUDIT_PATH = Path("artifacts/manifests/protocol_r_support_audit_v1.json")
AUDIT_HASH_PATH = Path("artifacts/manifests/protocol_r_support_audit_v1.sha256")
TABLE_PATH = Path("artifacts/tables/protocol_r_support_audit_v1.csv")
GENERATOR_VERSION = "1.0.0"
TARGET_APPLIANCES = ("fridge", "microwave", "dish washer", "washer dryer")
ACTIVE_THRESHOLD_WATTS = 15.0
MINIMUM_ACTIVE_SAMPLES = 2
HISTORY_SAMPLES = 256
FUTURE_SAMPLES = 8
CADENCE_SECONDS = 3


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_power(text: str) -> float | None:
    if not text.strip():
        return None
    value = float(text)
    return value if math.isfinite(value) else None


@dataclass
class EpisodeSupport:
    block_start: int
    block_end: int
    valid_start: int
    valid_end: int
    finite_valid_targets: int = 0
    missing_valid_targets: int = 0
    on_valid_target_samples: int = 0
    complete_episodes: int = 0
    dependency_contained_complete_episodes: int = 0
    left_censored_runs: int = 0
    right_censored_runs: int = 0
    _previous: bool | None = None
    _run_start: int | None = None
    _run_length: int = 0
    _run_has_inactive_lead: bool = False

    def consume(self, row_position: int, value: float | None) -> None:
        if self.valid_start <= row_position < self.valid_end:
            if value is None:
                self.missing_valid_targets += 1
            else:
                self.finite_valid_targets += 1
                if value > ACTIVE_THRESHOLD_WATTS:
                    self.on_valid_target_samples += 1

        if value is None:
            self._close_unknown()
            self._previous = None
            return

        active = value > ACTIVE_THRESHOLD_WATTS
        if active:
            if self._previous is not True:
                self._run_start = row_position
                self._run_length = 0
                self._run_has_inactive_lead = self._previous is False
            self._run_length += 1
        elif self._previous is True:
            self._close_with_trailer(row_position - 1)
        self._previous = active

    def finish(self) -> None:
        self._close_unknown()
        self._previous = None

    def _qualifying(self) -> bool:
        return self._run_length >= MINIMUM_ACTIVE_SAMPLES

    def _close_with_trailer(self, run_end: int) -> None:
        if self._qualifying():
            if self._run_has_inactive_lead:
                self.complete_episodes += 1
                assert self._run_start is not None
                if (
                    self._run_start - (HISTORY_SAMPLES - 1) >= self.block_start
                    and run_end + FUTURE_SAMPLES < self.block_end
                ):
                    self.dependency_contained_complete_episodes += 1
            else:
                self.left_censored_runs += 1
        self._clear_run()

    def _close_unknown(self) -> None:
        if self._qualifying():
            if not self._run_has_inactive_lead:
                self.left_censored_runs += 1
            self.right_censored_runs += 1
        self._clear_run()

    def _clear_run(self) -> None:
        self._run_start = None
        self._run_length = 0
        self._run_has_inactive_lead = False

    def as_dict(self) -> dict[str, int]:
        return {
            "finite_valid_targets": self.finite_valid_targets,
            "missing_valid_targets": self.missing_valid_targets,
            "on_valid_target_samples": self.on_valid_target_samples,
            "on_valid_target_duration_seconds": self.on_valid_target_samples
            * CADENCE_SECONDS,
            "complete_episodes": self.complete_episodes,
            "dependency_contained_complete_episodes": self.dependency_contained_complete_episodes,
            "left_censored_runs": self.left_censored_runs,
            "right_censored_runs": self.right_censored_runs,
        }


def verify_frozen_manifest(project_root: Path) -> dict[str, Any]:
    manifest_path = project_root / MANIFEST_PATH
    sidecar_path = project_root / MANIFEST_HASH_PATH
    if sha256_file(manifest_path) != MANIFEST_SHA256:
        raise RuntimeError("support audit refuses an unfrozen or changed manifest")
    expected = f"{MANIFEST_SHA256}  {MANIFEST_PATH.as_posix()}\n"
    if sidecar_path.read_text(encoding="ascii") != expected:
        raise RuntimeError("support audit refuses a changed manifest sidecar")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["manifest_status"] != "frozen evaluation contract; B5 locked until T011":
        raise RuntimeError("support audit requires the frozen T004 lifecycle state")
    return manifest


def audit_source(
    redd_root: Path,
    source: dict[str, Any],
    channel_mapping: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    path = redd_root / Path(source["relative_path"]).name
    if sha256_file(path) != source["sha256"]:
        raise RuntimeError(f"source fingerprint changed: {source['relative_path']}")
    expected_mapping = channel_mapping[source["house"]]["target_columns"]

    if source["protocol_role"] == "protocol_r_population":
        boundaries = source["blocks"]
    else:
        source_range = source["source_range"]
        boundaries = [
            {
                "block_id": "PX",
                "row_start_inclusive": source_range["row_start_inclusive"],
                "row_end_exclusive": source_range["row_end_exclusive"],
                "valid_target_range": source["valid_target_range"],
                "role": "protocol_x",
            }
        ]

    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or ())
        for appliance in TARGET_APPLIANCES:
            expected_column = expected_mapping[appliance]
            if (appliance in headers) != (expected_column is not None):
                raise RuntimeError(
                    f"channel mapping changed for H{source['house']} {appliance}"
                )

        states = []
        for boundary in boundaries:
            valid = boundary["valid_target_range"]
            states.append(
                {
                    appliance: EpisodeSupport(
                        block_start=boundary["row_start_inclusive"],
                        block_end=boundary["row_end_exclusive"],
                        valid_start=valid["row_start_inclusive"],
                        valid_end=valid["row_end_exclusive"],
                    )
                    for appliance in TARGET_APPLIANCES
                    if expected_mapping[appliance] is not None
                }
            )

        boundary_index = 0
        rows_seen = 0
        for row_position, row in enumerate(reader):
            while (
                boundary_index + 1 < len(boundaries)
                and row_position >= boundaries[boundary_index]["row_end_exclusive"]
            ):
                for state in states[boundary_index].values():
                    state.finish()
                boundary_index += 1
            boundary = boundaries[boundary_index]
            if not (
                boundary["row_start_inclusive"]
                <= row_position
                < boundary["row_end_exclusive"]
            ):
                raise RuntimeError("manifest boundaries do not cover the source rows")
            for appliance, state in states[boundary_index].items():
                state.consume(row_position, parse_power(row[appliance]))
            rows_seen += 1
        for state in states[boundary_index].values():
            state.finish()

    if rows_seen != source["row_count"]:
        raise RuntimeError(f"row-count changed: {source['relative_path']}")

    for boundary, block_states in zip(boundaries, states):
        valid = boundary["valid_target_range"]
        block_id = boundary["block_id"]
        for appliance in TARGET_APPLIANCES:
            present = expected_mapping[appliance] is not None
            validation_fold = (
                f"F{block_id[1:]}"
                if source["protocol_role"] == "protocol_r_population"
                and block_id in {"B1", "B2", "B3", "B4"}
                else None
            )
            training_folds = (
                [
                    f"F{fold}"
                    for fold in range(1, 5)
                    if block_id != f"B{fold}"
                ]
                if validation_fold is not None
                else []
            )
            stats = block_states[appliance].as_dict() if present else None
            records.append(
                {
                    "house": source["house"],
                    "segment_id": source["segment_id"],
                    "source_file": source["relative_path"],
                    "protocol_role": source["protocol_role"],
                    "block_id": block_id,
                    "block_role": boundary["role"],
                    "validation_fold": validation_fold,
                    "training_folds": training_folds,
                    "row_start_inclusive": boundary["row_start_inclusive"],
                    "row_end_exclusive": boundary["row_end_exclusive"],
                    "row_count": boundary["row_end_exclusive"]
                    - boundary["row_start_inclusive"],
                    "valid_target_start_inclusive": valid["row_start_inclusive"],
                    "valid_target_end_exclusive": valid["row_end_exclusive"],
                    "valid_target_count": valid["target_count"],
                    "appliance": appliance,
                    "column_present": present,
                    "support": stats,
                }
            )
    return records


SUPPORT_FIELDS = (
    "finite_valid_targets",
    "missing_valid_targets",
    "on_valid_target_samples",
    "on_valid_target_duration_seconds",
    "complete_episodes",
    "dependency_contained_complete_episodes",
    "left_censored_runs",
    "right_censored_runs",
)


def aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    present = [record for record in records if record["column_present"]]
    return {
        "segments_or_blocks_with_column": len(present),
        "row_count": sum(record["row_count"] for record in present),
        "valid_target_count": sum(record["valid_target_count"] for record in present),
        **{
            field: sum(record["support"][field] for record in present)
            for field in SUPPORT_FIELDS
        },
    }


def per_appliance(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        appliance: aggregate(
            [record for record in records if record["appliance"] == appliance]
        )
        for appliance in TARGET_APPLIANCES
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    development = [
        record
        for record in records
        if record["protocol_role"] == "protocol_r_population"
        and record["block_id"] in {"B1", "B2", "B3", "B4"}
    ]
    folds = {}
    for fold in range(1, 5):
        fold_id = f"F{fold}"
        folds[fold_id] = {
            "training": per_appliance(
                [record for record in development if fold_id in record["training_folds"]]
            ),
            "validation": per_appliance(
                [record for record in development if record["validation_fold"] == fold_id]
            ),
        }
    b5 = per_appliance([record for record in records if record["block_id"] == "B5"])
    protocol_x = per_appliance(
        [record for record in records if record["protocol_role"] == "protocol_x_held_out_house"]
    )

    support_checks = {}
    for appliance in TARGET_APPLIANCES:
        validation_checks = {
            fold_id: folds[fold_id]["validation"][appliance][
                "dependency_contained_complete_episodes"
            ]
            >= 5
            for fold_id in folds
        }
        b5_cycles = b5[appliance]["dependency_contained_complete_episodes"]
        b5_duration = b5[appliance]["on_valid_target_duration_seconds"]
        support_checks[appliance] = {
            "minimum_each_validation_fold_complete_episodes": 5,
            "validation_folds_pass": validation_checks,
            "minimum_b5_complete_episodes": 10,
            "b5_complete_episodes_pass": b5_cycles >= 10,
            "minimum_b5_on_duration_seconds": 600,
            "b5_on_duration_pass": b5_duration >= 600,
            "full_support_pass": (
                all(validation_checks.values())
                and b5_cycles >= 10
                and b5_duration >= 600
            ),
        }
    return {
        "folds": folds,
        "locked_b5": b5,
        "protocol_x_support_only": protocol_x,
        "support_checks": support_checks,
        "all_approved_appliances_pass": all(
            check["full_support_pass"] for check in support_checks.values()
        ),
    }


def flatten_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for record in records:
        row = {
            key: value
            for key, value in record.items()
            if key not in {"support", "training_folds"}
        }
        row["training_folds"] = ";".join(record["training_folds"])
        if record["support"] is None:
            row.update({field: "" for field in SUPPORT_FIELDS})
        else:
            row.update(record["support"])
        flattened.append(row)
    return flattened


def write_outputs(
    project_root: Path,
    records: list[dict[str, Any]],
    summary: dict[str, Any],
) -> str:
    audit = {
        "schema_version": "1.0",
        "audit_id": "t004-protocol-r-support-audit-v1",
        "evidence_type": "aggregate label-support and boundary audit only; no model execution",
        "generator": {
            "name": "audit_protocol_r_support.py",
            "version": GENERATOR_VERSION,
        },
        "frozen_manifest": {
            "path": MANIFEST_PATH.as_posix(),
            "sha256": MANIFEST_SHA256,
            "verified_before_data_access": True,
        },
        "rules": {
            "active_sample": "finite appliance power strictly greater than 15 W",
            "minimum_active_samples": MINIMUM_ACTIVE_SAMPLES,
            "valid_target": "block_start + 255 <= t < block_end - 8",
            "complete_episode": "qualifying active run with finite inactive samples before and after inside one block",
            "dependency_contained_complete_episode": "complete episode with rise - 255 >= block_start and final active row + 8 < block_end",
            "missing_values": "counted; break episode continuity; never backward-filled",
            "output_boundary": "aggregate counts only; no sample values, target series, predictions, metrics, or figures",
        },
        "summary": summary,
        "records": records,
    }
    audit_payload = (
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    audit_hash = hashlib.sha256(audit_payload).hexdigest()
    table_records = flatten_records(records)

    audit_path = project_root / AUDIT_PATH
    hash_path = project_root / AUDIT_HASH_PATH
    table_path = project_root / TABLE_PATH
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if audit_path.exists() and audit_path.read_bytes() != audit_payload:
        raise RuntimeError("refusing to overwrite a different T004 support audit")
    audit_path.write_bytes(audit_payload)
    hash_path.write_text(
        f"{audit_hash}  {AUDIT_PATH.as_posix()}\n",
        encoding="ascii",
        newline="\n",
    )
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(table_records[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(table_records)
    return audit_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redd-root", required=True, type=Path)
    parser.add_argument("--project-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    redd_root = args.redd_root.resolve()
    manifest = verify_frozen_manifest(project_root)
    channel_mapping = {
        mapping["house"]: mapping for mapping in manifest["house_channel_mapping"]
    }
    records = []
    for source in manifest["source_files"]:
        records.extend(audit_source(redd_root, source, channel_mapping))
    summary = build_summary(records)
    audit_hash = write_outputs(project_root, records, summary)
    print(
        json.dumps(
            {
                "audit": AUDIT_PATH.as_posix(),
                "sha256": audit_hash,
                "records": len(records),
                "all_approved_appliances_pass": summary[
                    "all_approved_appliances_pass"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
