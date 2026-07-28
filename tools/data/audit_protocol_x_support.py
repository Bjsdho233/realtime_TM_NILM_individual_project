#!/usr/bin/env python3
"""Audit aggregate H2+H4 Protocol X support without development access."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from audit_protocol_r_support import (
    MANIFEST_HASH_PATH,
    MANIFEST_PATH,
    MANIFEST_SHA256,
    SUPPORT_FIELDS,
    TARGET_APPLIANCES,
    aggregate,
    audit_source,
    verify_frozen_manifest,
)


PROTOCOL_R_AUDIT_PATH = Path(
    "artifacts/manifests/protocol_r_support_audit_v1.json"
)
PROTOCOL_R_AUDIT_SHA256 = (
    "c7fde29e9570417d12463e16f64ebf4eb1cb4736b775fc6fb2116e06fb68eed3"
)
AUDIT_PATH = Path("artifacts/manifests/protocol_x_support_audit_v1.json")
AUDIT_HASH_PATH = Path("artifacts/manifests/protocol_x_support_audit_v1.sha256")
TABLE_PATH = Path("artifacts/tables/protocol_x_support_audit_v1.csv")
GENERATOR_VERSION = "1.0.0"
PROTOCOL_X_HOUSES = (2, 4)
MINIMUM_COMPLETE_EPISODES = 10
MINIMUM_ON_DURATION_SECONDS = 600


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs(project_root: Path) -> dict[str, Any]:
    manifest = verify_frozen_manifest(project_root)
    if sha256_file(project_root / PROTOCOL_R_AUDIT_PATH) != PROTOCOL_R_AUDIT_SHA256:
        raise RuntimeError("Protocol X audit refuses a changed Protocol R support audit")
    if manifest["protocol_x"]["held_out_houses"] != list(PROTOCOL_X_HOUSES):
        raise RuntimeError("Protocol X composite population is not exactly H2+H4")
    return manifest


def per_appliance(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        appliance: aggregate(
            [record for record in records if record["appliance"] == appliance]
        )
        for appliance in TARGET_APPLIANCES
    }


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    houses = {
        f"H{house}": per_appliance(
            [record for record in records if record["house"] == house]
        )
        for house in PROTOCOL_X_HOUSES
    }
    pooled = per_appliance(records)
    eligibility = {}
    for appliance in TARGET_APPLIANCES:
        support = pooled[appliance]
        episodes_pass = (
            support["dependency_contained_complete_episodes"]
            >= MINIMUM_COMPLETE_EPISODES
        )
        duration_pass = (
            support["on_valid_target_duration_seconds"]
            >= MINIMUM_ON_DURATION_SECONDS
        )
        eligibility[appliance] = {
            "population": ["H2", "H4"],
            "population_selection_allowed": False,
            "minimum_dependency_contained_complete_episodes": MINIMUM_COMPLETE_EPISODES,
            "minimum_on_duration_seconds": MINIMUM_ON_DURATION_SECONDS,
            "episodes_pass": episodes_pass,
            "on_duration_pass": duration_pass,
            "future_locked_confirmatory_evaluation_eligible": (
                episodes_pass and duration_pass
            ),
            "development_access": False,
            "model_selection_use": False,
            "reporting_scope": "Protocol X cross-house evidence only; never Protocol R B5",
        }
    return {
        "per_house": houses,
        "pooled_h2_h4": pooled,
        "eligibility": eligibility,
    }


def flatten_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for record in records:
        row = {
            key: value
            for key, value in record.items()
            if key not in {"support", "training_folds"}
        }
        row["training_folds"] = ""
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
        "audit_id": "t004-protocol-x-h2-h4-support-audit-v1",
        "audit_status": "support-only; no model evaluation",
        "generator": {
            "name": "audit_protocol_x_support.py",
            "version": GENERATOR_VERSION,
        },
        "frozen_inputs": [
            {
                "path": MANIFEST_PATH.as_posix(),
                "sha256": MANIFEST_SHA256,
            },
            {
                "path": PROTOCOL_R_AUDIT_PATH.as_posix(),
                "sha256": PROTOCOL_R_AUDIT_SHA256,
            },
        ],
        "population": {
            "protocol": "Protocol X",
            "houses": ["H2", "H4"],
            "composite_population_fixed": True,
            "house_deletion_exchange_or_selection_allowed": False,
            "development_split_created": False,
        },
        "rules": {
            "maximum_history_samples": 256,
            "maximum_future_context_samples": 8,
            "active_threshold_watts": 15,
            "minimum_active_samples": 2,
            "minimum_dependency_contained_complete_episodes": MINIMUM_COMPLETE_EPISODES,
            "minimum_on_duration_seconds": MINIMUM_ON_DURATION_SECONDS,
            "segment_state": "reset at every source CSV",
            "dependency_containment": "rise - 255 >= segment start and final active row + 8 < segment end",
            "missing_values": "counted; break episode continuity; never backward-filled",
            "output_boundary": "aggregate support only; no target rows, time series, predictions, model metrics, or figures",
        },
        "summary": summary,
        "records": records,
    }
    payload = (json.dumps(audit, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    digest = hashlib.sha256(payload).hexdigest()
    audit_path = project_root / AUDIT_PATH
    hash_path = project_root / AUDIT_HASH_PATH
    table_path = project_root / TABLE_PATH
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    if audit_path.exists() and audit_path.read_bytes() != payload:
        raise RuntimeError("refusing to overwrite a different Protocol X support audit")
    audit_path.write_bytes(payload)
    hash_path.write_text(
        f"{digest}  {AUDIT_PATH.as_posix()}\n",
        encoding="ascii",
        newline="\n",
    )

    table_records = flatten_records(records)
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(table_records[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(table_records)
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--redd-root", required=True, type=Path)
    parser.add_argument("--project-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    redd_root = args.redd_root.resolve()
    manifest = verify_frozen_inputs(project_root)
    channel_mapping = {
        mapping["house"]: mapping for mapping in manifest["house_channel_mapping"]
    }
    sources = [
        source
        for source in manifest["source_files"]
        if source["protocol_role"] == "protocol_x_held_out_house"
    ]
    if {source["house"] for source in sources} != set(PROTOCOL_X_HOUSES):
        raise RuntimeError("Protocol X source set is not the fixed H2+H4 composite")

    records = []
    for source in sources:
        records.extend(audit_source(redd_root, source, channel_mapping))
    summary = build_summary(records)
    digest = write_outputs(project_root, records, summary)
    print(
        json.dumps(
            {
                "audit": AUDIT_PATH.as_posix(),
                "sha256": digest,
                "records": len(records),
                "eligibility": {
                    appliance: values[
                        "future_locked_confirmatory_evaluation_eligible"
                    ]
                    for appliance, values in summary["eligibility"].items()
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
