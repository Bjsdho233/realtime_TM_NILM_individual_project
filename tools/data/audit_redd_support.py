#!/usr/bin/env python3
"""Audit label-assisted REDD support under the D003 sequence contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path


CADENCE_SECONDS = 3
ACTIVE_THRESHOLD_WATTS = 15.0
MIN_ACTIVE_SAMPLES = 2
BASE_CLASSES = ("fridge", "microwave", "dish washer", "electric furnace")
OPTIONAL_CLASSES = ("washer dryer",)
TARGET_CLASSES = BASE_CLASSES + OPTIONAL_CLASSES
POOL_HOUSES = {1, 3, 5, 6}
CANDIDATE_HOUSES = {2, 4}
UPSTREAM_COMMIT = "8c5e90df34236ba0afcc4ec46ac083d829de4d51"
SUBMODULE_COMMIT = "a621bbd6399e49c6798550618fe43b113149455b"
CONTENT_TREE_SHA256 = "5e1ee53cdce2a5ad2d5007a08527bd1fc9486130d56dc008cf8c8ba8e336e73d"
SEQUENCE_CONTRACT_COMMIT = "5fb7f0e38c8e983969976dc4214038c77b5cafd9"
FILE_RE = re.compile(r"redd_house(?P<house>[1-6])_(?P<chunk>\d+)\.csv$")


class SupportStats:
    """Track threshold runs without carrying state across an audit boundary."""

    def __init__(self) -> None:
        self.row_count = 0
        self.finite_samples = 0
        self.missing_samples = 0
        self.active_samples = 0
        self.rising_transitions = 0
        self.falling_transitions = 0
        self.complete_cycles = 0
        self.left_censored_runs = 0
        self.right_censored_runs = 0
        self._previous: bool | None = None
        self._run_length = 0
        self._run_has_inactive_lead = False

    def consume(self, value: float | None) -> None:
        self.row_count += 1
        if value is None or not math.isfinite(value):
            self.missing_samples += 1
            self._close_at_unknown_boundary()
            self._previous = None
            return

        self.finite_samples += 1
        active = value > ACTIVE_THRESHOLD_WATTS
        if active:
            self.active_samples += 1
            if self._previous is not True:
                self._run_length = 0
                self._run_has_inactive_lead = self._previous is False
                if self._previous is False:
                    self.rising_transitions += 1
            self._run_length += 1
        elif self._previous is True:
            self.falling_transitions += 1
            self._close_with_inactive_trailer()

        self._previous = active

    def finish(self) -> None:
        self._close_at_unknown_boundary()
        self._previous = None

    def _qualifying_run(self) -> bool:
        return self._run_length >= MIN_ACTIVE_SAMPLES

    def _close_with_inactive_trailer(self) -> None:
        if self._qualifying_run():
            if self._run_has_inactive_lead:
                self.complete_cycles += 1
            else:
                self.left_censored_runs += 1
        self._run_length = 0
        self._run_has_inactive_lead = False

    def _close_at_unknown_boundary(self) -> None:
        if self._run_length and self._qualifying_run():
            if not self._run_has_inactive_lead:
                self.left_censored_runs += 1
            self.right_censored_runs += 1
        self._run_length = 0
        self._run_has_inactive_lead = False

    def as_dict(self) -> dict[str, int | float]:
        active_duration = self.active_samples * CADENCE_SECONDS
        on_rate = self.active_samples / self.finite_samples if self.finite_samples else 0.0
        return {
            "row_count": self.row_count,
            "nominal_duration_seconds": self.row_count * CADENCE_SECONDS,
            "finite_samples": self.finite_samples,
            "missing_samples": self.missing_samples,
            "active_samples": self.active_samples,
            "active_duration_seconds": active_duration,
            "on_rate": on_rate,
            "rising_transitions": self.rising_transitions,
            "falling_transitions": self.falling_transitions,
            "complete_cycles": self.complete_cycles,
            "left_censored_runs": self.left_censored_runs,
            "right_censored_runs": self.right_censored_runs,
        }


def block_ranges(row_count: int, blocks: int = 3) -> list[tuple[int, int]]:
    quotient, remainder = divmod(row_count, blocks)
    ranges = []
    start = 0
    for index in range(blocks):
        end = start + quotient + (1 if index < remainder else 0)
        ranges.append((start, end))
        start = end
    return ranges


def parse_power(text: str) -> float | None:
    if not text.strip():
        return None
    value = float(text)
    return value if math.isfinite(value) else None


def file_identity(path: Path) -> tuple[int, int]:
    match = FILE_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"unexpected source filename: {path.name}")
    return int(match.group("house")), int(match.group("chunk"))


def count_rows_and_hash(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        rows = sum(1 for _ in reader)
    return rows, digest.hexdigest()


def audit_file(path: Path, row_count: int) -> list[dict[str, object]]:
    house, chunk = file_identity(path)
    segment_id = f"redd_house{house}_{chunk}"
    is_pool = house in POOL_HOUSES
    ranges = block_ranges(row_count) if is_pool else [(0, row_count)]
    stats = [{name: SupportStats() for name in TARGET_CLASSES} for _ in ranges]

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or ())
        block_index = 0
        for sample_index, row in enumerate(reader):
            while block_index + 1 < len(ranges) and sample_index >= ranges[block_index][1]:
                block_index += 1
            for appliance in TARGET_CLASSES:
                if appliance in headers:
                    stats[block_index][appliance].consume(parse_power(row[appliance]))

    records: list[dict[str, object]] = []
    for block_index, ((start, end), block_stats) in enumerate(zip(ranges, stats), 1):
        for appliance in TARGET_CLASSES:
            present = appliance in headers
            current = block_stats[appliance]
            if present:
                current.finish()
                values = current.as_dict()
            else:
                values = {
                    "row_count": end - start,
                    "nominal_duration_seconds": (end - start) * CADENCE_SECONDS,
                    "finite_samples": 0,
                    "missing_samples": 0,
                    "active_samples": 0,
                    "active_duration_seconds": 0,
                    "on_rate": 0.0,
                    "rising_transitions": 0,
                    "falling_transitions": 0,
                    "complete_cycles": 0,
                    "left_censored_runs": 0,
                    "right_censored_runs": 0,
                }
            records.append(
                {
                    "house": house,
                    "chunk": chunk,
                    "segment_id": segment_id,
                    "source_file": f"redd/{path.name}",
                    "appliance": appliance,
                    "class_type": "base" if appliance in BASE_CLASSES else "optional_exploratory",
                    "protocol_role": "train_validation_pool" if is_pool else "sealed_candidate_test",
                    "validation_fold": block_index if is_pool else None,
                    "row_start_inclusive": start,
                    "row_end_exclusive": end,
                    "column_present": present,
                    **values,
                }
            )
    return records


def aggregate(records: list[dict[str, object]]) -> dict[str, int | float]:
    fields = (
        "row_count",
        "nominal_duration_seconds",
        "finite_samples",
        "missing_samples",
        "active_samples",
        "active_duration_seconds",
        "rising_transitions",
        "falling_transitions",
        "complete_cycles",
        "left_censored_runs",
        "right_censored_runs",
    )
    present = [record for record in records if record["column_present"]]
    result = {field: sum(int(record[field]) for record in present) for field in fields}
    finite = result["finite_samples"]
    result["on_rate"] = result["active_samples"] / finite if finite else 0.0
    result["segments_with_column"] = len(present)
    return result


def support_summary(records: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for appliance in TARGET_CLASSES:
        class_records = [record for record in records if record["appliance"] == appliance]
        pool = [record for record in class_records if record["protocol_role"] == "train_validation_pool"]
        candidate = [record for record in class_records if record["protocol_role"] == "sealed_candidate_test"]
        pool_total = aggregate(pool)
        candidate_total = aggregate(candidate)
        folds = {
            str(fold): aggregate([record for record in pool if record["validation_fold"] == fold])
            for fold in (1, 2, 3)
        }
        pool_pass = pool_total["complete_cycles"] >= 30
        fold_pass = {fold: values["complete_cycles"] >= 5 for fold, values in folds.items()}
        candidate_cycles_pass = candidate_total["complete_cycles"] >= 10
        candidate_duration_pass = candidate_total["active_duration_seconds"] >= 600
        summary[appliance] = {
            "class_type": "base" if appliance in BASE_CLASSES else "optional_exploratory",
            "train_validation_pool": {**pool_total, "minimum_complete_cycles": 30, "pass": pool_pass},
            "validation_folds": {
                fold: {**values, "minimum_complete_cycles": 5, "pass": fold_pass[fold]}
                for fold, values in folds.items()
            },
            "sealed_candidate_test": {
                **candidate_total,
                "minimum_complete_cycles": 10,
                "minimum_active_duration_seconds": 600,
                "cycles_pass": candidate_cycles_pass,
                "active_duration_pass": candidate_duration_pass,
                "pass": candidate_cycles_pass and candidate_duration_pass,
            },
            "full_standard_pass": (
                pool_pass
                and all(fold_pass.values())
                and candidate_cycles_pass
                and candidate_duration_pass
            ),
        }
    return summary


def canonical_sha256(document: dict[str, object]) -> str:
    unhashed = {key: value for key, value in document.items() if key != "canonical_sha256"}
    payload = json.dumps(unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_output(directory: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(directory), *args], text=True, encoding="utf-8"
    ).strip()


def verify_snapshot(redd_root: Path) -> None:
    upstream_root = redd_root.parent
    if git_output(upstream_root, "rev-parse", "HEAD") != UPSTREAM_COMMIT:
        raise RuntimeError("upstream commit does not match the D003 pin")
    if git_output(redd_root, "rev-parse", "HEAD") != SUBMODULE_COMMIT:
        raise RuntimeError("redd submodule commit does not match the D003 pin")
    if git_output(upstream_root, "status", "--porcelain"):
        raise RuntimeError("upstream worktree is not clean")
    if git_output(redd_root, "status", "--porcelain"):
        raise RuntimeError("redd submodule worktree is not clean")


def write_json(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_table(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(records[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def build_outputs(redd_root: Path) -> tuple[dict[str, object], dict[str, object], list[dict[str, object]]]:
    verify_snapshot(redd_root)
    paths = sorted(
        redd_root.glob("redd_house*.csv"),
        key=lambda path: file_identity(path),
    )
    if len(paths) != 35:
        raise RuntimeError(f"expected 35 REDD chunk files, found {len(paths)}")

    source_files = []
    records: list[dict[str, object]] = []
    for path in paths:
        house, chunk = file_identity(path)
        row_count, file_hash = count_rows_and_hash(path)
        ranges = block_ranges(row_count) if house in POOL_HOUSES else []
        source_files.append(
            {
                "path": f"redd/{path.name}",
                "sha256": file_hash,
                "segment_id": f"redd_house{house}_{chunk}",
                "house": house,
                "chunk": chunk,
                "row_count": row_count,
                "nominal_cadence_seconds": CADENCE_SECONDS,
                "protocol_role": "train_validation_pool" if house in POOL_HOUSES else "sealed_candidate_test",
                "fold_blocks": [
                    {"validation_fold": index, "row_start_inclusive": start, "row_end_exclusive": end}
                    for index, (start, end) in enumerate(ranges, 1)
                ],
            }
        )
        records.extend(audit_file(path, row_count))

    summary = support_summary(records)
    for record in records:
        class_summary = summary[str(record["appliance"])]
        if record["protocol_role"] == "train_validation_pool":
            fold = str(record["validation_fold"])
            record["support_pass"] = class_summary["validation_folds"][fold]["pass"]
        else:
            record["support_pass"] = class_summary["sealed_candidate_test"]["pass"]

    audit = {
        "schema_version": "1.0",
        "audit_id": "t002-protocol-r-support-audit-2026-07-21",
        "evidence_type": "label-assisted oracle support preflight only",
        "sequence_contract_commit": SEQUENCE_CONTRACT_COMMIT,
        "upstream_commit": UPSTREAM_COMMIT,
        "redd_submodule_commit": SUBMODULE_COMMIT,
        "redd_content_tree_sha256": CONTENT_TREE_SHA256,
        "rules": {
            "active_sample": "finite appliance power strictly greater than 15 W",
            "active_threshold_watts": ACTIVE_THRESHOLD_WATTS,
            "minimum_active_samples": MIN_ACTIVE_SAMPLES,
            "nominal_cadence_seconds": CADENCE_SECONDS,
            "complete_cycle": "qualifying active run with observable finite inactive samples before and after within the same segment/block",
            "missing_values": "counted explicitly; break observation continuity; no backward fill",
            "segment_state": "reset for every source CSV",
            "block_state": "reset for every validation block",
            "cross_boundary_items": "discarded",
        },
        "support_summary": summary,
        "base_classes_pass": all(bool(summary[name]["full_standard_pass"]) for name in BASE_CLASSES),
        "records": records,
    }

    manifest = {
        "schema_version": "1.0",
        "manifest_id": "protocol-r-candidate-d003-2026-07-21",
        "protocol": "Protocol R",
        "candidate_status": "preflight candidate; not locked test",
        "sequence_contract_commit": SEQUENCE_CONTRACT_COMMIT,
        "upstream_commit": UPSTREAM_COMMIT,
        "redd_submodule_commit": SUBMODULE_COMMIT,
        "redd_content_tree_sha256": CONTENT_TREE_SHA256,
        "canonical_input": "redd submodule CSV chunks",
        "docs_redd_used": False,
        "nominal_cadence_seconds": CADENCE_SECONDS,
        "time_identity": ["segment_id", "sample_index", "nominal_offset_seconds = sample_index * 3"],
        "original_timestamp_claimed": False,
        "target_classes": {
            "base": list(BASE_CLASSES),
            "optional_exploratory": list(OPTIONAL_CLASSES),
            "forbidden_mapping": "electric space heater must not be mapped to electric furnace",
        },
        "train_validation_pool_houses": sorted(POOL_HOUSES),
        "candidate_test": {"houses": sorted(CANDIDATE_HOUSES), "sealed": True, "label_support_only": True},
        "fold_policy": "each train/validation segment independently partitioned into three contiguous half-open row blocks by quotient/remainder",
        "boundary_policy": "reset at every segment and block; complete dependency interval must remain within one block; crossing items discarded",
        "purge_policy": "dependency-aware full containment; no fixed numerical purge",
        "cross_segment_time_order": None,
        "source_files": source_files,
        "support_audit": "artifacts/manifests/redd_support_audit.json",
        "unresolved": [
            "calendar-time coverage and original gaps",
            "per-file original channel-to-column generation chain",
            "docs/redd generation command",
            "whether natural numeric order equals historical chronology",
            "historical preprocessing path from raw REDD to every pinned CSV",
            "future detector, pairer, window, event, and feature dependency horizons",
        ],
        "canonical_hash_method": "SHA-256 of UTF-8 canonical JSON with sorted keys and compact separators, omitting canonical_sha256",
    }
    manifest["canonical_sha256"] = canonical_sha256(manifest)
    return audit, manifest, records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redd-root", required=True, type=Path)
    parser.add_argument("--output-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    output_root = args.output_root.resolve()
    contract_subject = git_output(output_root, "show", "-s", "--format=%s", SEQUENCE_CONTRACT_COMMIT)
    if contract_subject != "docs: define T002 REDD sequence-time contract":
        raise RuntimeError("sequence contract commit is unavailable or has the wrong subject")
    audit, manifest, records = build_outputs(args.redd_root.resolve())
    write_json(output_root / "artifacts/manifests/redd_support_audit.json", audit)
    write_table(output_root / "artifacts/tables/redd_support_audit.csv", records)
    write_json(output_root / "artifacts/manifests/protocol_r_candidate_split.json", manifest)
    print(json.dumps({
        "base_classes_pass": audit["base_classes_pass"],
        "manifest_canonical_sha256": manifest["canonical_sha256"],
        "records": len(records),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
