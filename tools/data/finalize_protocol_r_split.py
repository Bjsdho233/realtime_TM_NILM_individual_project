#!/usr/bin/env python3
"""Derive the approved Protocol R manifest from tracked T002 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PREDECESSOR_PATH = "artifacts/manifests/protocol_r_candidate_split.json"
PREDECESSOR_HASH = "480a738ad799860f6cdecbba9affb1d76c365a71468b276b8b0669ea55bba11a"
DECISION_PATH = "docs/decisions/D004-protocol-r-class-fallback.md"
DECISION_COMMIT = "c6ceb9a81da1fe24d79c935a0e9ffea3022fa0c2"
SUPPORT_AUDIT_PATH = "artifacts/manifests/redd_support_audit.json"
SUPPORT_AUDIT_COMMIT = "cf8b6796799cca6c0d3100760aa0b1b24753b9a8"
APPROVED_CLASSES = ("fridge", "microwave", "dish washer", "washer dryer")
EXCLUDED_CLASS = "electric furnace"


def canonical_sha256(document: dict[str, object]) -> str:
    unhashed = {key: value for key, value in document.items() if key != "canonical_sha256"}
    payload = json.dumps(unhashed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_predecessor(candidate: dict[str, object]) -> None:
    calculated = canonical_sha256(candidate)
    if candidate.get("canonical_sha256") != PREDECESSOR_HASH or calculated != PREDECESSOR_HASH:
        raise ValueError("predecessor canonical hash mismatch")
    if len(candidate.get("source_files", [])) != 35:
        raise ValueError("predecessor must contain exactly 35 source files")
    if candidate.get("docs_redd_used") is not False:
        raise ValueError("predecessor unexpectedly uses docs/redd")


def derive_support(audit: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    summary = audit["support_summary"]
    approved: dict[str, object] = {}
    for appliance in APPROVED_CLASSES:
        evidence = summary[appliance]
        if evidence["full_standard_pass"] is not True:
            raise ValueError(f"approved class does not pass frozen support standard: {appliance}")
        approved[appliance] = {
            "train_validation_pool_complete_cycles": evidence["train_validation_pool"]["complete_cycles"],
            "validation_fold_complete_cycles": [
                evidence["validation_folds"][str(fold)]["complete_cycles"] for fold in (1, 2, 3)
            ],
            "candidate_test_complete_cycles": evidence["sealed_candidate_test"]["complete_cycles"],
            "candidate_test_active_duration_seconds": evidence["sealed_candidate_test"]["active_duration_seconds"],
            "full_standard_pass": True,
        }

    excluded = summary[EXCLUDED_CLASS]
    if excluded["full_standard_pass"] is not False:
        raise ValueError("excluded electric furnace unexpectedly passes the frozen standard")
    exclusion = {
        "class": EXCLUDED_CLASS,
        "status": "unsupported for the approved Protocol R candidate test under the frozen support standard",
        "reason": "sealed candidate test has fewer than 10 complete cycles",
        "train_validation_pool_complete_cycles": excluded["train_validation_pool"]["complete_cycles"],
        "validation_fold_complete_cycles": [
            excluded["validation_folds"][str(fold)]["complete_cycles"] for fold in (1, 2, 3)
        ],
        "candidate_test_complete_cycles": excluded["sealed_candidate_test"]["complete_cycles"],
        "candidate_test_active_duration_seconds": excluded["sealed_candidate_test"]["active_duration_seconds"],
        "candidate_minimum_complete_cycles": excluded["sealed_candidate_test"]["minimum_complete_cycles"],
        "model_performance_failure": False,
    }
    return approved, exclusion


def derive_house_availability(audit: dict[str, object]) -> list[dict[str, object]]:
    records = audit["records"]
    availability = []
    for house in range(1, 7):
        columns: dict[str, bool] = {}
        for appliance in APPROVED_CLASSES:
            matching = [
                record
                for record in records
                if record["house"] == house and record["appliance"] == appliance
            ]
            if not matching:
                raise ValueError(f"audit contains no records for H{house} {appliance}")
            present_values = {record["column_present"] for record in matching}
            if len(present_values) != 1:
                raise ValueError(f"inconsistent column availability for H{house} {appliance}")
            columns[appliance] = bool(present_values.pop())
        availability.append({"house": house, "target_columns": columns})
    return availability


def derive_support_standard(audit: dict[str, object]) -> dict[str, object]:
    summary = audit["support_summary"]
    pool_minima = {summary[name]["train_validation_pool"]["minimum_complete_cycles"] for name in summary}
    fold_minima = {
        summary[name]["validation_folds"][str(fold)]["minimum_complete_cycles"]
        for name in summary
        for fold in (1, 2, 3)
    }
    candidate_cycle_minima = {
        summary[name]["sealed_candidate_test"]["minimum_complete_cycles"] for name in summary
    }
    candidate_duration_minima = {
        summary[name]["sealed_candidate_test"]["minimum_active_duration_seconds"] for name in summary
    }
    if not all(len(values) == 1 for values in (pool_minima, fold_minima, candidate_cycle_minima, candidate_duration_minima)):
        raise ValueError("support minima are inconsistent across audited classes")
    return {
        **audit["rules"],
        "minimum_train_validation_pool_complete_cycles": pool_minima.pop(),
        "minimum_each_validation_fold_complete_cycles": fold_minima.pop(),
        "minimum_candidate_test_complete_cycles": candidate_cycle_minima.pop(),
        "minimum_candidate_test_active_duration_seconds": candidate_duration_minima.pop(),
    }


def finalize(candidate: dict[str, object], audit: dict[str, object]) -> dict[str, object]:
    verify_predecessor(candidate)
    approved_support, exclusion = derive_support(audit)
    source_files = candidate["source_files"]

    manifest: dict[str, object] = {
        "schema_version": "1.0",
        "manifest_version": "T002-approved-fallback-1",
        "manifest_status": "approved T002 preflight split; candidate test remains sealed for model development",
        "protocol": "Protocol R",
        "predecessor": {"path": PREDECESSOR_PATH, "canonical_sha256": PREDECESSOR_HASH},
        "fallback_decision": {"path": DECISION_PATH, "commit": DECISION_COMMIT},
        "support_audit": {"path": SUPPORT_AUDIT_PATH, "commit": SUPPORT_AUDIT_COMMIT},
        "upstream_commit": candidate["upstream_commit"],
        "redd_submodule_commit": candidate["redd_submodule_commit"],
        "redd_content_tree_sha256": candidate["redd_content_tree_sha256"],
        "canonical_input": candidate["canonical_input"],
        "docs_redd_used": candidate["docs_redd_used"],
        "nominal_cadence_seconds": candidate["nominal_cadence_seconds"],
        "time_identity": candidate["time_identity"],
        "original_timestamp_claimed": candidate["original_timestamp_claimed"],
        "train_validation_pool_houses": candidate["train_validation_pool_houses"],
        "candidate_test_houses": candidate["candidate_test"]["houses"],
        "source_files": source_files,
        "fold_policy": candidate["fold_policy"],
        "boundary_policy": candidate["boundary_policy"],
        "purge_policy": candidate["purge_policy"],
        "cross_segment_time_order": candidate["cross_segment_time_order"],
        "frozen_support_standard": derive_support_standard(audit),
        "approved_target_classes": list(APPROVED_CLASSES),
        "approved_class_support": approved_support,
        "excluded_class": exclusion,
        "house_target_column_availability": derive_house_availability(audit),
        "missing_target_column_policy": "label unavailable; do not infer appliance absence and do not fill all-zero ground truth",
        "candidate_test_sealing_scope": {
            "support_labels_inspected": True,
            "model_predictions_observed": False,
            "model_metrics_observed": False,
            "sealed_for_model_development": True,
        },
        "evaluation_inputs_pending": [
            "cross-house scoring policy",
            "missing-label eligibility policy",
            "macro aggregation policy",
        ],
        "unresolved": candidate["unresolved"],
        "canonical_hash_method": "SHA-256 of UTF-8 canonical JSON with sorted keys and compact separators, omitting canonical_sha256",
    }
    manifest["canonical_sha256"] = canonical_sha256(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.project_root.resolve()

    candidate = json.loads((root / PREDECESSOR_PATH).read_text(encoding="utf-8"))
    audit = json.loads((root / SUPPORT_AUDIT_PATH).read_text(encoding="utf-8"))
    approved = finalize(candidate, audit)
    output = root / "artifacts/manifests/protocol_r_approved_split.json"
    output.write_text(json.dumps(approved, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "approved_classes": approved["approved_target_classes"],
        "canonical_sha256": approved["canonical_sha256"],
        "source_files": len(approved["source_files"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
