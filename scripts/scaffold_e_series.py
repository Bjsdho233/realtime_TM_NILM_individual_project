#!/usr/bin/env python3
"""Create a frozen, isolated E-series experiment skeleton."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import re
import subprocess
from pathlib import Path, PurePosixPath

from repo_governance import (
    DESIGN_HASH_NAME,
    DESIGN_NAME,
    DESIGN_SCHEMA_PATH,
    IGNORED_LOCAL_ENVIRONMENT_SEGMENTS,
    RESULT_SCHEMA_PATH,
    SCHEMA_VERSION,
    GovernanceError,
    MUTABLE_OUTPUT_SEGMENTS,
    _validate_archive_path,
    _is_link_or_reparse,
    atomic_write_text,
    canonical_file_sha256,
    load_active_e_registry,
    load_work_index_e_entries,
    repository_root,
    sha256_file,
    strict_json_loads,
    validate_development_data_manifest,
    validate_design_directory,
    validate_learned_artifact_manifest,
    validate_tree_has_no_links,
    write_json,
)


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def nonempty(value: str) -> str:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("value cannot be empty")
    return value


def relative_input(value: str) -> str:
    candidate = value.replace("\\", "/").strip()
    if (
        not candidate
        or candidate.startswith("/")
        or re.match(r"^[A-Za-z]:/", candidate)
        or ".." in Path(candidate).parts
    ):
        raise argparse.ArgumentTypeError("input must be a repository-relative path")
    return candidate


def aggregate_table_spec(value: str) -> dict:
    try:
        parsed = strict_json_loads(value, "--aggregate-table")
    except GovernanceError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("--aggregate-table must be one JSON object")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="unique E-series ID, for example E002")
    parser.add_argument("--slug", required=True, help="short kebab-case direct name")
    parser.add_argument("--name", required=True, type=nonempty, help="human-readable direct name")
    parser.add_argument("--owner", default="Tianhang Tan")
    parser.add_argument("--workflow-layer", required=True, type=nonempty)
    parser.add_argument(
        "--freeze-existing",
        action="store_true",
        help="freeze an already prepared, registered directory after safety checks",
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=("comparison", "diagnostic", "feasibility"),
    )
    parser.add_argument("--hypothesis", required=True, type=nonempty)
    parser.add_argument("--protocol-name", default="Development-only exploratory")
    parser.add_argument("--data-scope", default="Development data only; sealed test excluded")
    parser.add_argument(
        "--data-manifest",
        action="append",
        default=[],
        type=relative_input,
        help="hashed repository-relative data manifest; may be repeated",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        type=relative_input,
        help="planned source file to hash; may be repeated",
    )
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        type=relative_input,
        help="planned configuration file to hash; may be repeated",
    )
    parser.add_argument(
        "--reused-artifact-manifest",
        action="append",
        default=[],
        type=relative_input,
        help="tracked portable learned-artifact manifest; may be repeated",
    )
    parser.add_argument(
        "--preprocessing-fit-scope",
        choices=("train_only", "not_applicable"),
        default="not_applicable",
    )
    parser.add_argument("--task-definition", default="Defined by this frozen exploratory design")
    parser.add_argument(
        "--output-policy",
        default="Report only the pre-registered exploratory claim; no formal output semantics inferred",
    )
    parser.add_argument(
        "--aggregate-table",
        action="append",
        default=[],
        type=aggregate_table_spec,
        help=(
            "predeclared aggregate CSV contract as strict JSON with path, columns, "
            "max_rows, purpose, and aggregation_unit; may be repeated"
        ),
    )
    parser.add_argument("--pass-rule", required=True, type=nonempty)
    parser.add_argument("--fail-rule", required=True, type=nonempty)
    parser.add_argument("--inconclusive-rule", required=True, type=nonempty)
    parser.add_argument("--validity-condition", action="append", default=[])
    parser.add_argument("--seed", action="append", default=[], type=int)
    parser.add_argument("--fold", action="append", default=[])
    parser.add_argument("--repeat-count", type=int, default=1)
    parser.add_argument(
        "--repeat-policy",
        default="One deterministic execution unless seeds or folds are declared",
    )

    comparison = parser.add_argument_group("comparison")
    comparison.add_argument("--baseline")
    comparison.add_argument("--baseline-id")
    comparison.add_argument("--baseline-evidence", type=relative_input)
    comparison.add_argument("--candidate")
    comparison.add_argument("--primary-metric")
    comparison.add_argument("--metric-direction", choices=("maximize", "minimize"))
    comparison.add_argument("--delta-rule")
    comparison.add_argument("--controlled-variable", action="append", default=[])

    diagnostic = parser.add_argument_group("diagnostic")
    diagnostic.add_argument("--question")
    diagnostic.add_argument("--observation-plan")
    diagnostic.add_argument("--check", action="append", default=[])

    feasibility = parser.add_argument_group("feasibility")
    feasibility.add_argument("--capability")
    feasibility.add_argument("--feasibility-check")
    feasibility.add_argument("--success-condition")
    return parser.parse_args()


def _require(args: argparse.Namespace, names: tuple[str, ...]) -> None:
    missing = [name for name in names if not getattr(args, name)]
    if missing:
        flags = ", ".join("--" + name.replace("_", "-") for name in missing)
        raise GovernanceError(f"{args.kind} experiments require {flags}")


def method_from_args(args: argparse.Namespace) -> dict:
    if args.kind == "comparison":
        _require(
            args,
            (
                "baseline",
                "baseline_id",
                "baseline_evidence",
                "candidate",
                "primary_metric",
                "metric_direction",
                "delta_rule",
                "controlled_variable",
                "seed",
            ),
        )
        return {
            "kind": "comparison",
            "baseline": {"name": args.baseline, "description": args.baseline},
            "candidate": {"name": args.candidate, "description": args.candidate},
            "primary_metric": {
                "name": args.primary_metric,
                "direction": args.metric_direction,
            },
            "delta_rule": args.delta_rule,
            "controlled_variables": args.controlled_variable,
        }
    if args.kind == "diagnostic":
        _require(args, ("question", "observation_plan", "check"))
        return {
            "kind": "diagnostic",
            "question": args.question,
            "observation_plan": args.observation_plan,
            "checks": args.check,
        }
    _require(args, ("capability", "feasibility_check", "success_condition"))
    return {
        "kind": "feasibility",
        "capability": args.capability,
        "check": args.feasibility_check,
        "success_condition": args.success_condition,
    }


def _git_state(root: Path) -> tuple[str, bool]:
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=normal"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return commit, bool(status.strip())


def _hashed_record(root: Path, relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "sha256": canonical_file_sha256(root, relative, "registered provenance"),
    }


def _validate_registration(
    root: Path,
    work_id: str,
    name: str,
    owner: str,
    directory_name: str,
) -> None:
    mutable_root = f"experiments/{directory_name}/"
    records = [record for record in load_active_e_registry(root) if record.work_id == work_id]
    if len(records) != 1:
        raise GovernanceError(f"CURRENT_STATE.md must contain one active row for {work_id}")
    record = records[0]
    expected = (
        name,
        owner,
        "registered",
        mutable_root,
        "Pending",
        "Pending",
    )
    actual = (
        record.direct_name,
        record.owner,
        record.status,
        record.mutable_root,
        record.design_sha256,
        record.design_commit,
    )
    if actual != expected:
        raise GovernanceError(
            f"CURRENT_STATE.md active row mismatch for {work_id}: "
            f"expected {expected}, got {actual}"
        )
    if load_work_index_e_entries(root).get(work_id) != name:
        raise GovernanceError(f"WORK_INDEX.md does not register exact identity {work_id} — {name}")


def build_design(
    root: Path,
    args: argparse.Namespace,
    directory_name: str,
    created_at: str,
    base_commit: str,
    worktree_dirty: bool,
    environment_record: dict[str, str],
) -> dict:
    sources = []
    for path in args.data_manifest:
        manifest, manifest_hash = validate_development_data_manifest(root, path)
        sources.append(
            {
                "name": Path(path).name,
                "path": path,
                "role": "data_manifest",
                "fit_scope": "development roles declared by the validated manifest",
                "sha256": manifest_hash,
                "manifest_id": manifest["manifest_id"],
                "development_roles": sorted(
                    {entry["role"] for entry in manifest["entries"]}
                ),
            }
        )
    baseline = None
    if args.baseline_evidence:
        baseline = {
            "id": args.baseline_id,
            "evidence_path": args.baseline_evidence,
            "sha256": canonical_file_sha256(
                root, args.baseline_evidence, "baseline evidence"
            ),
        }
    reused_artifacts = []
    for path in args.reused_artifact_manifest:
        manifest, manifest_hash = validate_learned_artifact_manifest(root, path)
        reused_artifacts.append(
            {
                "id": manifest["artifact_id"],
                "manifest_path": path,
                "manifest_sha256": manifest_hash,
                "content_sha256": manifest["content_sha256"],
                "locator": manifest["locator"],
                "origin": manifest["origin"],
                "availability_limits": manifest["availability_limits"],
                "fit_data_roles": manifest["fit_data_roles"],
                "candidate_or_locked_test_derived": False,
            }
        )
    return {
        "$schema": DESIGN_SCHEMA_PATH.as_posix(),
        "schema_version": SCHEMA_VERSION,
        "work_id": args.id,
        "name": args.name,
        "owner": args.owner,
        "registered_at": created_at,
        "design_frozen_at": created_at,
        "track": "E-series",
        "experiment_kind": args.kind,
        "workflow_layer": args.workflow_layer,
        "status": "design_frozen",
        "hypothesis": args.hypothesis,
        "protocol": {
            "name": args.protocol_name,
            "data_scope": args.data_scope,
            "claim_scope": "exploratory",
            "sealed_test_access": False,
        },
        "task_definition": args.task_definition,
        "output_policy": args.output_policy,
        "input_contract": {
            "uses_data": bool(sources),
            "sources": sources,
        },
        "baseline": baseline,
        "reused_learned_artifacts": reused_artifacts,
        "reproducibility": {
            "seeds": args.seed,
            "folds": args.fold,
            "repeat_count": args.repeat_count,
            "repeat_policy": args.repeat_policy,
        },
        "execution_plan": {
            "base_git_commit": base_commit,
            "worktree_dirty": worktree_dirty,
            "source_files": [_hashed_record(root, path) for path in args.source],
            "config_files": [_hashed_record(root, path) for path in args.config],
            "environment": environment_record,
            "commands_file": f"experiments/{directory_name}/commands.log",
        },
        "safety_assertions": {
            "no_candidate_or_locked_test_feedback": True,
            "no_candidate_or_locked_test_derived_learned_state": True,
            "preprocessing_fit_scope": args.preprocessing_fit_scope,
            "shared_inputs_are_immutable_and_hashed": True,
            "mutable_paths_are_exclusive": True,
        },
        "registered_mutable_paths": [f"experiments/{directory_name}/"],
        "method": method_from_args(args),
        "acceptance_rule": {
            "supported": args.pass_rule,
            "not_supported": args.fail_rule,
            "inconclusive": args.inconclusive_rule,
            "validity_conditions": args.validity_condition,
        },
        "output_contract": {
            "result_schema": RESULT_SCHEMA_PATH.as_posix(),
            "archive_policy": "reviewed_whitelist",
            "row_level_outputs_allowed": False,
            "archive_directories": ["scripts", "configs", "tables", "figures", "docs"],
            "aggregate_tables": args.aggregate_table,
        },
    }


def _validate_prepared_directory(root: Path, directory: Path, args: argparse.Namespace) -> None:
    skipped = IGNORED_LOCAL_ENVIRONMENT_SEGMENTS
    validate_tree_has_no_links(directory, skipped)
    forbidden = {
        governance_name
        for governance_name in (DESIGN_NAME, DESIGN_HASH_NAME, "result.json")
        if (directory / governance_name).exists()
    }
    if forbidden:
        raise GovernanceError(f"prepared directory already contains {sorted(forbidden)}")
    for path in sorted(directory.rglob("*")):
        relative = PurePosixPath(path.relative_to(directory).as_posix())
        if IGNORED_LOCAL_ENVIRONMENT_SEGMENTS.intersection(relative.parts):
            continue
        if _is_link_or_reparse(path):
            raise GovernanceError(f"prepared directory contains a link/reparse path: {relative}")
        if not path.is_file():
            continue
        forbidden = MUTABLE_OUTPUT_SEGMENTS.intersection(relative.parts)
        if forbidden:
            raise GovernanceError(
                f"prepared directory contains pre-freeze output segment {sorted(forbidden)}"
            )
        allowed_pre_freeze = (
            (len(relative.parts) == 1 and relative.name == "environment.txt")
            or (len(relative.parts) == 2 and relative.parts[0] in {"scripts", "configs"})
        )
        if not allowed_pre_freeze:
            raise GovernanceError(
                f"prepared directory contains lifecycle/result file before freeze: {relative}"
            )
        _validate_archive_path(directory, relative)

    planned_sources = set(args.source)
    planned_configs = set(args.config)
    local_sources = {
        path.relative_to(root).as_posix()
        for path in (directory / "scripts").glob("*")
        if path.is_file()
    }
    local_configs = {
        path.relative_to(root).as_posix()
        for path in (directory / "configs").glob("*")
        if path.is_file()
    }
    if not local_sources.issubset(planned_sources):
        raise GovernanceError(
            f"prepared source files missing from --source: {sorted(local_sources - planned_sources)}"
        )
    if not local_configs.issubset(planned_configs):
        raise GovernanceError(
            f"prepared config files missing from --config: {sorted(local_configs - planned_configs)}"
        )

def scaffold(root: Path, args: argparse.Namespace) -> Path:
    if not re.fullmatch(r"E\d{3}", args.id):
        raise GovernanceError("--id must match E###")
    if not SLUG_RE.fullmatch(args.slug):
        raise GovernanceError("--slug must be lowercase kebab-case")
    if args.repeat_count < 1:
        raise GovernanceError("--repeat-count must be at least 1")
    if args.seed and any(seed < 0 for seed in args.seed):
        raise GovernanceError("--seed values must be non-negative")
    if args.data_manifest and args.preprocessing_fit_scope != "train_only":
        raise GovernanceError(
            "data-using designs must declare --preprocessing-fit-scope train_only"
        )
    if bool(args.baseline_evidence) != bool(args.baseline_id):
        raise GovernanceError("--baseline-id and --baseline-evidence must be supplied together")
    experiment_root = root / "experiments"
    if _is_link_or_reparse(experiment_root) or not experiment_root.is_dir():
        raise GovernanceError("experiments/: must be an ordinary repository directory")

    existing = sorted((root / "experiments").glob(f"{args.id}-*"))
    directory_name = f"{args.id}-{args.slug}"
    _validate_registration(root, args.id, args.name, args.owner, directory_name)
    directory = root / "experiments" / directory_name
    if existing:
        if not args.freeze_existing or existing != [directory] or not directory.is_dir():
            raise GovernanceError(f"{args.id} is already present at {existing[0]}")
        _validate_prepared_directory(root, directory, args)
    elif args.freeze_existing:
        raise GovernanceError("--freeze-existing requires the exact prepared directory")

    created_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    base_commit, worktree_dirty = _git_state(root)
    created_directory = not directory.exists()
    created_paths: list[Path] = []
    if created_directory:
        os.mkdir(directory)
    try:
        environment_path = directory / "environment.txt"
        if not environment_path.exists():
            atomic_write_text(
                environment_path,
                "\n".join(
                    [
                        f"python={platform.python_version()}",
                        f"implementation={platform.python_implementation()}",
                        f"system={platform.system()}",
                        f"release={platform.release()}",
                        f"machine={platform.machine()}",
                        f"base_git_commit={base_commit}",
                        f"worktree_dirty_before_scaffold={str(worktree_dirty).lower()}",
                        "",
                    ]
                ),
            )
            created_paths.append(environment_path)
        environment_record = {
            "path": environment_path.relative_to(root).as_posix(),
            "sha256": sha256_file(environment_path),
        }
        design = build_design(
            root,
            args,
            directory_name,
            created_at,
            base_commit,
            worktree_dirty,
            environment_record,
        )
        write_json(directory / DESIGN_NAME, design)
        created_paths.append(directory / DESIGN_NAME)
        digest = sha256_file(directory / DESIGN_NAME)
        atomic_write_text(directory / DESIGN_HASH_NAME, f"{digest}  {DESIGN_NAME}\n")
        created_paths.append(directory / DESIGN_HASH_NAME)
        validate_design_directory(root, directory)
    except Exception:
        for path in reversed(created_paths):
            if path.is_file():
                path.unlink()
        if created_directory and directory.exists():
            directory.rmdir()
        raise
    return directory


def main() -> int:
    args = parse_args()
    try:
        root = repository_root()
        directory = scaffold(root, args)
    except (GovernanceError, subprocess.CalledProcessError) as exc:
        print(f"[FAIL] {exc}")
        return 1
    relative = directory.relative_to(root)
    print(f"[PASS] Prepared frozen E-series design: {relative}")
    print(
        "[NEXT] Commit only design_manifest.json, design_manifest.sha256, "
        "environment.txt, and the declared local source/config snapshots."
    )
    print(
        "[NEXT] Update the Active E-series Registry row with the design SHA-256 "
        "and design-only commit, then run: python scripts/check_repo.py"
    )
    print(
        "[NEXT] Only after that check passes, initialise EXPERIMENT.md and commands.log."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
