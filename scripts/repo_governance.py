#!/usr/bin/env python3
"""Repository governance checks shared by the command-line tools."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence
from urllib.parse import unquote


SCHEMA_VERSION = "1.0"
DESIGN_SCHEMA_PATH = Path("schemas/e-series-design.schema.json")
RESULT_SCHEMA_PATH = Path("schemas/work-result.schema.json")
DEVELOPMENT_DATA_SCHEMA_PATH = Path("schemas/development-data-manifest.schema.json")
SCAN_ALLOWLIST_PATH = Path("schemas/repository-scan-allowlist.json")
LEGACY_CHECKSUM_PATH = Path("schemas/legacy-archive-checksums.json")
DESIGN_NAME = "design_manifest.json"
DESIGN_HASH_NAME = "design_manifest.sha256"
RESULT_NAME = "result.json"
MAX_TRACKED_FILE_BYTES = 5 * 1024 * 1024
GOVERNED_TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".csv",
    ".h",
    ".hpp",
    ".ino",
    ".json",
    ".log",
    ".md",
    ".patch",
    ".ps1",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
MUTABLE_OUTPUT_SEGMENTS = {
    "work",
    "cache",
    "models",
    "outputs",
    "results",
    "raw",
    "predictions",
    "logs",
    "captures",
    "checkpoints",
    "exports",
    "__pycache__",
}
IGNORED_LOCAL_ENVIRONMENT_SEGMENTS = {".venv"}

WORK_ID_RE = re.compile(r"^E\d{3}$")
T_WORK_ID_RE = re.compile(r"^T\d{3}$")
EXPERIMENT_DIR_RE = re.compile(r"^[ETR]\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
RELATIVE_PATH_RE = re.compile(r"^(?!/)(?![A-Za-z]:[\\/])(?!.*(?:^|/)\.\.(?:/|$)).+")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ABSOLUTE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9+.-])(?:[A-Za-z]:[\\/]|/(?:home|Users|root|workspace|tmp)/)"
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")
SECRET_ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    (?<![a-z0-9_])["']?((?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?key[_-]?id|
    access[_-]?token|auth[_-]?token|bearer[_-]?token|client[_-]?secret|
    private[_-]?token|refresh[_-]?token|secret[_-]?access[_-]?key|
    password|token|secret))["']?
    \s*[:=]\s*
    ["']?([^"'\s,;]+)
    """
)
SAFE_SECRET_VALUE_RE = re.compile(
    r"(?i)^(?:\$\{[^}]+\}|<[^>]+>|redacted|placeholder|example|dummy|test|"
    r"not[-_ ]?set|none|null)$"
)
SENSITIVE_FILE_RE = re.compile(
    r"(?i)(?:^|/)(?:\.env(?:\..+)?|credentials[^/]*\.json|secrets?[^/]*\.json|"
    r"[^/]+\.(?:pem|key|p12|pfx))$"
)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}

MAX_AGGREGATE_TABLE_ROWS = 2000
AGGREGATE_TABLE_CONTRACTS: dict[str, tuple[set[str], set[str]]] = {
    "per_class.csv": (
        {"class", "precision", "recall", "f1", "support"},
        {
            "class",
            "precision",
            "recall",
            "f1",
            "support",
            "split",
            "seed",
            "fold",
            "repeat",
            "mean",
            "std",
            "ci_lower",
            "ci_upper",
        },
    ),
    "confusion_matrix.csv": (
        {"actual_class", "predicted_class", "count"},
        {"actual_class", "predicted_class", "count", "split", "seed", "fold"},
    ),
    "runs.csv": (
        {"run_id", "metric", "value"},
        {
            "run_id",
            "seed",
            "fold",
            "repeat",
            "split",
            "variant",
            "metric",
            "value",
            "unit",
            "baseline",
            "candidate",
            "delta",
        },
    ),
    "run_summary.csv": (
        {"metric", "value"},
        {
            "metric",
            "value",
            "unit",
            "scope",
            "aggregation",
            "mean",
            "std",
            "min",
            "max",
            "median",
            "p95",
            "count",
            "baseline",
            "candidate",
            "delta",
            "seed",
            "fold",
            "run_id",
        },
    ),
    "resource_summary.csv": (
        {"resource", "value", "unit"},
        {
            "resource",
            "statistic",
            "value",
            "unit",
            "repetitions",
            "scope",
            "mean",
            "std",
            "min",
            "max",
            "median",
            "p95",
        },
    ),
}
GENERIC_SUMMARY_REQUIRED = {"metric", "value"}
GENERIC_SUMMARY_ALLOWED = {
    "metric",
    "value",
    "unit",
    "scope",
    "aggregation",
    "mean",
    "std",
    "min",
    "max",
    "median",
    "p95",
    "count",
    "baseline",
    "candidate",
    "delta",
    "seed",
    "fold",
    "run_id",
    "class",
    "precision",
    "recall",
    "f1",
    "support",
}
FORBIDDEN_ROW_LEVEL_COLUMN_RE = re.compile(
    r"(?i)(?:^|_)(?:prediction|predictions|pred|y_pred|label|labels|target|"
    r"truth|ground_truth|sample|sample_id|event|event_id|timestamp|row|row_id)(?:$|_)"
)
SAFE_AGGREGATE_ROW_TOKEN_COLUMNS = {
    "matched_target_episode_count",
    "sample_std",
    "unmatched_target_episode_count",
    "target_diagnostics_json",
}
MAX_AGGREGATE_CELL_LENGTH = 4096
DEPRECATED_TEMPLATE_PATHS = {
    Path("docs/templates") / ("EXPERIMENT_DESIGN_MANIFEST_" + "TEMPLATE.json"),
    Path("docs/templates") / ("WORK_RESULT_" + "TEMPLATE.json"),
}
DEPRECATED_CONTRACT_TOKENS = {
    "DESIGN" + ".sha256": "design_manifest.sha256",
    "results/" + "result.json": "result.json",
    "docs/templates/" + "WORK_RESULT_TEMPLATE.json": "schemas/work-result.schema.json",
}

LEGACY_ARCHIVE_FILES: dict[str, set[str]] = {
    "E002-tm-training-dynamics-probe": {
        "CHECKSUMS.sha256",
        "README.md",
        "experiment_manifest.json",
        "results/tm_balance_coverage_results.json",
        "results/tm_balance_sweep_results.json",
        "results/tm_mechanism_confirmation_results.json",
        "results/tm_mechanism_followup_results.json",
        "results/tm_mechanism_probe_results.json",
        "scripts/tm_balance_sweep.py",
        "scripts/tm_mechanism_confirm.py",
        "scripts/tm_mechanism_followup.py",
        "scripts/tm_mechanism_probe.py",
    },
    "E001-booleanization-ab-probe": {
        "REPORT.md",
        "SHA256SUMS.txt",
        "SOURCE_FILE_SHA256SUMS.txt",
        "experiment.py",
        "per_seed_metrics.csv",
        "summary.json",
    },
    "T003-local-reproduction": {
        "LOCAL_REPRODUCTION_REPORT.md",
        "SHA256SUMS.txt",
        "SOURCE_FILE_SHA256SUMS.txt",
        "SOURCE_RUN_SHA256SUMS.txt",
        "commands.log",
        "environment.txt",
        "local_reproduction_manifest.json",
    },
}

LEGACY_MISSING_FINAL_NEWLINE_SHA256: dict[str, str] = {
    "experiments/E002-tm-training-dynamics-probe/results/tm_balance_coverage_results.json":
        "e8437b08cc046653adc1341998ec7bc22738c8ceefd5f6d231c91dd59769499e",
    "experiments/E002-tm-training-dynamics-probe/results/tm_balance_sweep_results.json":
        "e8f41b7d32cc2edc0f636d8666a7191d3839a34baa8833eaaa8a420c5f30b52a",
    "experiments/E002-tm-training-dynamics-probe/results/tm_mechanism_confirmation_results.json":
        "a0d7e4bad4db7b307b10a75809ce106ae24964cfae95e10a4eab490e83aa47cc",
    "experiments/E002-tm-training-dynamics-probe/results/tm_mechanism_followup_results.json":
        "d93565efba0b2159e2ebdb7db92716d033e5796dbc9b9393b43126b5dbe56173",
    "experiments/E002-tm-training-dynamics-probe/results/tm_mechanism_probe_results.json":
        "e91412ea4ed4ee775d607ce3390fa2cd9535a78c3d1d18716a52801f42736829",
}

ALLOWED_NEW_ARCHIVE_PATHS: dict[str, set[str]] = {
    ".": {
        "EXPERIMENT.md",
        "REPORT.md",
        "README.md",
        "commands.log",
        "environment.txt",
        DESIGN_NAME,
        DESIGN_HASH_NAME,
        RESULT_NAME,
        "SHA256SUMS.txt",
        "SOURCE_FILE_SHA256SUMS.txt",
    },
    "scripts": {
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
        ".ino",
        ".cmake",
        ".py",
        ".sh",
        ".ps1",
    },
    "configs": {".json", ".toml", ".yaml", ".yml"},
    "tables": {".csv"},
    "figures": {".png", ".jpg", ".jpeg", ".svg", ".pdf"},
    "docs": {".md"},
}
ALLOWED_SCRIPT_BUILD_FILES = {"CMakeLists.txt", "Makefile"}
NUMERIC_AGGREGATE_COLUMNS = {
    "value",
    "precision",
    "recall",
    "f1",
    "support",
    "count",
    "mean",
    "std",
    "min",
    "max",
    "median",
    "p95",
    "ci_lower",
    "ci_upper",
    "delta",
    "repetitions",
    "seed",
    "repeat",
    "sample_std",
    "tp",
    "tn",
    "fp",
    "fn",
    "eligible_positive_support",
    "eligible_negative_support",
    "excluded_unavailable_count",
    "binary_accuracy",
    "matched_target_episode_count",
    "unmatched_target_episode_count",
    "duplicate_candidate_count",
    "candidate_count",
    "episode_coverage",
    "median_value",
    "p95_value",
    "serialized_inference_bytes",
    "shared_encoder_bytes",
    "complete_bundle_bytes",
    "warmups",
    "timed_calls",
    "batch_size",
    "main_edge_count",
    "rising_edge_count",
    "falling_edge_count",
    "paired_count",
    "expired_rise_count",
    "unmatched_fall_count",
    "contained_exclusion_count",
    "non_finite_main_count",
}
BOOLEAN_AGGREGATE_COLUMNS = {
    "precision_zero_denominator",
    "recall_zero_denominator",
    "f1_zero_denominator",
    "accuracy_zero_denominator",
    "episode_coverage_zero_denominator",
}
OPTIONAL_AGGREGATE_MEASURE_COLUMNS = {
    "serialized_inference_bytes",
    "shared_encoder_bytes",
    "complete_bundle_bytes",
}
MEASURE_AGGREGATE_COLUMNS = NUMERIC_AGGREGATE_COLUMNS - {"seed", "repeat"}

ROLE_DIRECTORIES: dict[str, set[str]] = {
    "narrative": {".", "docs"},
    "source": {"scripts"},
    "configuration": {"configs"},
    "aggregate_table": {"tables"},
    "figure": {"figures"},
    "checksum": {"."},
    "environment": {"."},
    "command_log": {"."},
}

T_SERIES_ARCHIVE_CONFIGS = {
    "T005": Path("artifacts/manifests/protocol_r_baseline_v1.json"),
}
PROTOTYPE_T_SERIES_ARCHIVES = {
    "T006-direct-rtm-nilm-prototype": {
        "PROTOTYPE_REPORT.md",
        "result.json",
        "figures/direct_rtm_excerpt.svg",
    },
}


class GovernanceError(RuntimeError):
    """Raised when repository governance validation fails."""


@dataclass(frozen=True)
class CheckResult:
    name: str
    details: str


@dataclass(frozen=True)
class ActiveERecord:
    work_id: str
    direct_name: str
    owner: str
    status: str
    mutable_root: str
    design_sha256: str
    design_commit: str


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reject_cr_bytes(path: Path, content: bytes) -> None:
    if path.suffix.lower() in GOVERNED_TEXT_SUFFIXES and b"\r" in content:
        raise GovernanceError(f"{path}: governed text contains CR/non-LF bytes")


def _reject_json_constant(value: str) -> None:
    raise GovernanceError(f"non-standard JSON constant is forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GovernanceError(f"duplicate JSON object key is forbidden: {key!r}")
        result[key] = value
    return result


def strict_json_loads(content: str, label: str) -> Any:
    try:
        return json.loads(
            content,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, GovernanceError) as exc:
        if isinstance(exc, GovernanceError):
            raise GovernanceError(f"{label}: {exc}") from exc
        raise GovernanceError(f"{label}: invalid JSON: {exc}") from exc


def index_file_bytes(root: Path, relative: str | Path, label: str) -> bytes:
    path = safe_repository_file(root, relative, label)
    relative_text = path.relative_to(root).as_posix()
    completed = subprocess.run(
        ["git", "-C", str(root), "show", f":{relative_text}"],
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        raise GovernanceError(
            f"{label}: {relative_text} must be Git-tracked or staged before freezing"
        )
    _reject_cr_bytes(path, completed.stdout)
    return completed.stdout


def canonical_index_bytes(root: Path, relative: str | Path, label: str) -> bytes:
    path = safe_repository_file(root, relative, label)
    relative_text = path.relative_to(root).as_posix()
    index_bytes = index_file_bytes(root, relative, label)
    worktree_bytes = path.read_bytes()
    _reject_cr_bytes(path, worktree_bytes)
    if worktree_bytes != index_bytes:
        raise GovernanceError(
            f"{label}: worktree bytes differ from the staged canonical bytes: {relative_text}"
        )
    return index_bytes


def canonical_file_sha256(root: Path, relative: str | Path, label: str) -> str:
    return sha256_bytes(canonical_index_bytes(root, relative, label))


def _is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return path.is_symlink()
    if stat.S_ISLNK(metadata.st_mode):
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(metadata, "st_file_attributes", 0) & reparse_flag)


def _validate_relative_path(value: str, label: str) -> None:
    if "\\" in value or not RELATIVE_PATH_RE.fullmatch(value):
        raise GovernanceError(f"{label}: path must be repository-relative and cannot traverse parents")
    for part in PurePosixPath(value).parts:
        if part.endswith((" ", ".")):
            raise GovernanceError(
                f"{label}: path is not Windows-portable (trailing dot/space): {value}"
            )
        stem = part.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_NAMES:
            raise GovernanceError(
                f"{label}: path uses a Windows-reserved name: {value}"
            )


def safe_repository_file(root: Path, relative: str | Path, label: str) -> Path:
    relative_text = Path(relative).as_posix()
    _validate_relative_path(relative_text, label)
    relative_path = PurePosixPath(relative_text)
    current = root
    for part in relative_path.parts:
        current = current / part
        if _is_link_or_reparse(current):
            raise GovernanceError(f"{label}: symlink/junction/reparse path is forbidden: {relative_text}")
        if not current.exists():
            raise GovernanceError(f"{label}: file is missing: {relative_text}")
    if not current.is_file():
        raise GovernanceError(f"{label}: expected an ordinary file: {relative_text}")
    resolved_root = root.resolve(strict=True)
    resolved = current.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise GovernanceError(f"{label}: path escapes the repository: {relative_text}") from exc
    return current


def validate_tree_has_no_links(
    directory: Path, skip_segments: set[str] | frozenset[str] = frozenset()
) -> None:
    if _is_link_or_reparse(directory):
        raise GovernanceError(f"{directory}: experiment root cannot be a link/reparse point")
    if not directory.exists():
        return
    pending = [directory]
    while pending:
        parent = pending.pop()
        try:
            entries = list(os.scandir(parent))
        except OSError as exc:
            raise GovernanceError(f"{parent}: cannot inspect experiment tree: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            if entry.name in skip_segments:
                continue
            if _is_link_or_reparse(path):
                raise GovernanceError(f"{path}: links/reparse points are forbidden")
            if entry.is_dir(follow_symlinks=False):
                pending.append(path)


def atomic_write_text(path: Path, content: str) -> None:
    if path.exists() or path.is_symlink():
        raise GovernanceError(f"{path}: refusing to overwrite an existing path")
    if _is_link_or_reparse(path.parent):
        raise GovernanceError(f"{path.parent}: parent cannot be a link/reparse point")
    path.parent.mkdir(parents=False, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=False,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            encoded = content.encode("utf-8")
            if b"\r" in encoded:
                raise GovernanceError(f"{path}: CR bytes are forbidden in governed text")
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise GovernanceError(f"{path}: target appeared during atomic write")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise GovernanceError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    return strict_json_loads(text, str(path))


def write_json(path: Path, content: Any) -> None:
    try:
        encoded = json.dumps(
            content,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise GovernanceError(f"{path}: cannot serialise strict JSON: {exc}") from exc
    atomic_write_text(path, encoded + "\n")


def repository_root(start: Path | None = None) -> Path:
    candidate = (start or Path.cwd()).resolve()
    for path in (candidate, *candidate.parents):
        if (path / ".git").exists() and (path / "AGENTS.md").is_file():
            return path
    raise GovernanceError("run this command inside the repository")


def _git_paths(root: Path) -> list[Path]:
    command = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    ]
    completed = subprocess.run(command, check=False, capture_output=True)
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GovernanceError(f"git ls-files failed: {stderr}")
    paths: list[Path] = []
    for raw_path in completed.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(os.fsdecode(raw_path))
        paths.append(relative)
    return sorted(set(paths), key=lambda path: path.as_posix())


def trackable_paths(root: Path) -> list[Path]:
    return _git_paths(root)


def validate_path_safety(root: Path, paths: Sequence[Path]) -> CheckResult:
    portable_names: dict[str, str] = {}
    for relative in paths:
        relative_text = relative.as_posix()
        _validate_relative_path(relative_text, f"trackable path {relative_text}")
        folded = relative_text.casefold()
        previous = portable_names.get(folded)
        if previous is not None and previous != relative_text:
            raise GovernanceError(
                f"case-fold path collision is not portable: {previous}, {relative_text}"
            )
        portable_names[folded] = relative_text
        safe_repository_file(root, relative, f"trackable path {relative.as_posix()}")
    return CheckResult("Path safety", f"{len(paths)} trackable paths contained; no links")


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise GovernanceError(f"unsupported schema type: {expected}")


def _json_category(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _json_equal(left: Any, right: Any) -> bool:
    return _json_category(left) == _json_category(right) and left == right


SUPPORTED_SCHEMA_KEYWORDS = {
    "$id",
    "$schema",
    "additionalProperties",
    "const",
    "description",
    "enum",
    "items",
    "minItems",
    "minLength",
    "minimum",
    "oneOf",
    "pattern",
    "properties",
    "required",
    "title",
    "type",
    "uniqueItems",
}


def schema_errors(instance: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    """Validate the JSON Schema subset used by this repository."""

    errors: list[str] = []
    unsupported = sorted(set(schema) - SUPPORTED_SCHEMA_KEYWORDS)
    if unsupported:
        return [f"{location}: unsupported schema keywords {unsupported}"]
    if "oneOf" in schema:
        branch_results = [
            schema_errors(instance, branch, location) for branch in schema["oneOf"]
        ]
        matches = sum(not branch_errors for branch_errors in branch_results)
        if matches != 1:
            errors.append(f"{location}: expected exactly one oneOf branch, matched {matches}")
            if matches == 0 and branch_results:
                nearest = min(branch_results, key=len)
                errors.extend(nearest)
            return errors

    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"{location}: expected constant {schema['const']!r}")
    if "enum" in schema and not any(
        _json_equal(instance, allowed) for allowed in schema["enum"]
    ):
        errors.append(f"{location}: {instance!r} is not an allowed value")

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = [expected_type] if isinstance(expected_type, str) else expected_type
        if not any(_json_type_matches(instance, item) for item in expected_types):
            errors.append(f"{location}: expected type {expected_types}, got {type(instance).__name__}")
            return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{location}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(schema_errors(value, properties[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}: unexpected property {key!r}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{location}: expected at least {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{location}: duplicate array items are not allowed")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                errors.extend(schema_errors(item, item_schema, f"{location}[{index}]"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{location}: string is shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{location}: value does not match {schema['pattern']!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if not math.isfinite(instance):
            errors.append(f"{location}: number must be finite")
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{location}: value is below {schema['minimum']}")

    return errors


def validate_with_schema(instance: Any, schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    errors = schema_errors(instance, schema)
    if errors:
        formatted = "\n".join(f"  - {error}" for error in errors)
        raise GovernanceError(f"{label} does not match {schema_path.name}:\n{formatted}")


def validate_development_data_manifest(
    root: Path, relative: str
) -> tuple[dict[str, Any], str]:
    path = safe_repository_file(root, relative, "development data manifest")
    content = canonical_index_bytes(root, relative, "development data manifest")
    manifest = load_json(path)
    validate_with_schema(
        manifest,
        root / DEVELOPMENT_DATA_SCHEMA_PATH,
        f"development data manifest {relative}",
    )
    _validate_development_manifest_semantics(manifest, relative)
    return manifest, sha256_bytes(content)


def _validate_development_manifest_semantics(
    manifest: dict[str, Any], label: str
) -> None:
    _validate_data_role_disjointness([manifest], label)
    seen_ids: set[str] = set()
    for entry in manifest["entries"]:
        if entry["id"] in seen_ids:
            raise GovernanceError(f"{label}: duplicate data entry ID {entry['id']!r}")
        seen_ids.add(entry["id"])
        role = entry["role"]
        fit_allowed = entry["fit_allowed"]
        if role == "development_train" and not fit_allowed:
            raise GovernanceError(
                f"{label}: development_train entry {entry['id']!r} must allow fit"
            )
        if role != "development_train" and fit_allowed:
            raise GovernanceError(
                f"{label}: only development_train entries may allow fit"
            )


def _validate_data_role_disjointness(
    manifests: Sequence[dict[str, Any]], label: str
) -> None:
    seen_locators: dict[str, tuple[str, str]] = {}
    seen_hashes: dict[str, tuple[str, str]] = {}
    for manifest in manifests:
        manifest_id = manifest["manifest_id"]
        for entry in manifest["entries"]:
            role = entry["role"]
            for identity, seen, identity_label in (
                (entry["path_or_locator"], seen_locators, "path_or_locator"),
                (entry["content_sha256"], seen_hashes, "content_sha256"),
            ):
                previous = seen.get(identity)
                if previous is not None:
                    previous_manifest, previous_role = previous
                    raise GovernanceError(
                        f"{label}: data {identity_label} is declared more than once "
                        f"({previous_manifest}:{previous_role}, {manifest_id}:{role})"
                    )
                seen[identity] = (manifest_id, role)


def validate_learned_artifact_manifest(
    root: Path, relative: str
) -> tuple[dict[str, Any], str]:
    path = safe_repository_file(root, relative, "learned artifact manifest")
    content = canonical_index_bytes(root, relative, "learned artifact manifest")
    manifest = load_json(path)
    schema_path = root / "schemas" / "learned-artifact-manifest.schema.json"
    validate_with_schema(manifest, schema_path, f"learned artifact manifest {relative}")
    data_reference = manifest["data_manifest"]
    _, data_hash = validate_development_data_manifest(root, data_reference["path"])
    if data_hash != data_reference["sha256"]:
        raise GovernanceError(
            f"{relative}: learned artifact references the wrong data-manifest hash"
        )
    return manifest, sha256_bytes(content)


def validate_schema_documents(root: Path, paths: Sequence[Path]) -> CheckResult:
    json_paths = [path for path in paths if path.suffix.lower() == ".json"]
    for relative in json_paths:
        load_json(root / relative)

    schema_paths = sorted((root / "schemas").glob("*.schema.json"))
    if not schema_paths:
        raise GovernanceError("schemas/: no JSON Schema files found")
    for schema_path in schema_paths:
        schema = load_json(schema_path)
        if not isinstance(schema, dict):
            raise GovernanceError(f"{schema_path}: schema root must be an object")
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise GovernanceError(f"{schema_path}: unsupported or missing $schema")
        if not schema.get("$id") or schema.get("type") != "object":
            raise GovernanceError(f"{schema_path}: $id and object root type are required")

    return CheckResult(
        "JSON and schema",
        f"{len(json_paths)} JSON documents parsed; {len(schema_paths)} schemas loaded",
    )


def validate_contract_references(root: Path, paths: Sequence[Path]) -> CheckResult:
    present_deprecated = sorted(
        path.as_posix() for path in paths if path in DEPRECATED_TEMPLATE_PATHS
    )
    errors = [
        f"{path}: deprecated duplicate template must be removed"
        for path in present_deprecated
    ]
    checked = 0
    for relative in paths:
        path = root / relative
        if path.stat().st_size > MAX_TRACKED_FILE_BYTES or not _is_probably_text(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked += 1
        for old, replacement in DEPRECATED_CONTRACT_TOKENS.items():
            if old in text:
                errors.append(
                    f"{relative.as_posix()}: deprecated {old!r}; use {replacement!r}"
                )
    if errors:
        raise GovernanceError(
            "schema/tooling contract drift:\n"
            + "\n".join(f"  - {item}" for item in errors)
        )
    return CheckResult("Contract references", f"{checked} text files checked")


def _strip_fenced_code(markdown: str) -> str:
    lines: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence = True
            fence_marker = stripped[:3]
            lines.append("")
            continue
        if in_fence and stripped.startswith(fence_marker):
            in_fence = False
            fence_marker = ""
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    return "\n".join(lines)


def markdown_destinations(markdown: str) -> Iterable[str]:
    text = _strip_fenced_code(markdown)
    inline = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)")
    reference = re.compile(r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)")
    for match in inline.finditer(text):
        yield match.group(1).strip("<>")
    for match in reference.finditer(text):
        yield match.group(1).strip("<>")


def _is_external_destination(destination: str) -> bool:
    lowered = destination.lower()
    return (
        not destination
        or destination.startswith("#")
        or lowered.startswith(("http://", "https://", "mailto:", "data:", "sandbox:"))
    )


def validate_markdown_links(root: Path, paths: Sequence[Path]) -> CheckResult:
    markdown_paths = [path for path in paths if path.suffix.lower() == ".md"]
    checked = 0
    errors: list[str] = []
    for relative in markdown_paths:
        source = root / relative
        text = source.read_text(encoding="utf-8")
        for destination in markdown_destinations(text):
            if _is_external_destination(destination):
                continue
            decoded = unquote(destination.split("#", 1)[0].split("?", 1)[0])
            if not decoded:
                continue
            candidate = Path(decoded)
            target = candidate if candidate.is_absolute() else source.parent / candidate
            checked += 1
            if not target.exists():
                errors.append(f"{relative.as_posix()}: missing link target {decoded!r}")
    if errors:
        raise GovernanceError("broken Markdown links:\n" + "\n".join(f"  - {item}" for item in errors))
    return CheckResult("Markdown links", f"{checked} relative links resolved")


def _parse_markdown_table(
    text: str,
    section_heading: str,
    expected_headers: tuple[str, ...],
    label: str,
) -> list[tuple[str, ...]]:
    lines = text.splitlines()
    section_indexes = [
        index for index, line in enumerate(lines) if line.strip() == section_heading
    ]
    if len(section_indexes) != 1:
        raise GovernanceError(
            f"{label}: expected exactly one {section_heading!r} section"
        )
    start = section_indexes[0] + 1
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or not lines[start].strip().startswith("|"):
        raise GovernanceError(f"{label}: section must begin with its canonical table")

    def cells(line: str) -> tuple[str, ...]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            raise GovernanceError(f"{label}: malformed Markdown table row")
        return tuple(cell.strip() for cell in stripped[1:-1].split("|"))

    headers = cells(lines[start])
    if headers != expected_headers:
        raise GovernanceError(
            f"{label}: table headers must be exactly {expected_headers}, got {headers}"
        )
    if start + 1 >= len(lines):
        raise GovernanceError(f"{label}: missing Markdown separator row")
    separators = cells(lines[start + 1])
    if len(separators) != len(expected_headers) or not all(
        re.fullmatch(r":?-{3,}:?", item) for item in separators
    ):
        raise GovernanceError(f"{label}: invalid Markdown separator row")

    rows: list[tuple[str, ...]] = []
    for line in lines[start + 2 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped:
            if rows:
                break
            continue
        if not stripped.startswith("|"):
            break
        row = cells(line)
        if len(row) != len(expected_headers):
            raise GovernanceError(f"{label}: row has the wrong number of columns")
        rows.append(row)
    return rows


def load_active_e_registry(root: Path) -> list[ActiveERecord]:
    path = root / "docs" / "CURRENT_STATE.md"
    rows = _parse_markdown_table(
        path.read_text(encoding="utf-8"),
        "## Active E-series Registry",
        (
            "ID",
            "Direct name",
            "Owner",
            "Status",
            "Mutable root",
            "Design SHA-256",
            "Design commit",
        ),
        str(path),
    )
    records: list[ActiveERecord] = []
    for row in rows:
        record = ActiveERecord(*row)
        if not WORK_ID_RE.fullmatch(record.work_id):
            raise GovernanceError(f"{path}: invalid active E-series ID {record.work_id!r}")
        if not record.direct_name or not record.owner:
            raise GovernanceError(f"{path}: direct name and owner cannot be empty")
        if record.status not in {"registered", "design_frozen"}:
            raise GovernanceError(f"{path}: invalid status for {record.work_id}")
        expected_prefix = f"experiments/{record.work_id}-"
        if (
            not record.mutable_root.startswith(expected_prefix)
            or not record.mutable_root.endswith("/")
            or not re.fullmatch(
                r"experiments/E[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*/",
                record.mutable_root,
            )
        ):
            raise GovernanceError(f"{path}: invalid mutable root for {record.work_id}")
        if record.status == "registered":
            if record.design_sha256 != "Pending" or record.design_commit != "Pending":
                raise GovernanceError(
                    f"{path}: registered row {record.work_id} requires Pending anchors"
                )
        else:
            if not SHA256_RE.fullmatch(record.design_sha256) or not re.fullmatch(
                r"[0-9a-f]{40}", record.design_commit
            ):
                raise GovernanceError(
                    f"{path}: design_frozen row {record.work_id} needs hash and commit"
                )
        records.append(record)

    for attribute in ("work_id", "direct_name", "mutable_root"):
        values = [getattr(record, attribute) for record in records]
        if len(values) != len(set(values)):
            raise GovernanceError(f"{path}: duplicate active registry {attribute}")
    roots = [PurePosixPath(record.mutable_root.rstrip("/")) for record in records]
    for index, left in enumerate(roots):
        for right in roots[index + 1 :]:
            if left.parts == right.parts[: len(left.parts)] or right.parts == left.parts[: len(right.parts)]:
                raise GovernanceError(f"{path}: overlapping active mutable roots")
    return records


def load_work_index_e_entries(root: Path) -> dict[str, str]:
    return {
        work_id: row[0]
        for work_id, row in load_work_index_e_records(root).items()
    }


def load_work_index_e_records(root: Path) -> dict[str, tuple[str, str, str]]:
    path = root / "docs" / "WORK_INDEX.md"
    rows = _parse_markdown_table(
        path.read_text(encoding="utf-8"),
        "## E-series",
        (
            "ID and direct name",
            "Layer",
            "Status",
            "Outcome / evidence",
        ),
        str(path),
    )
    entries: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        match = re.fullmatch(r"(E[0-9]{3}) — (.+)", row[0])
        if not match:
            raise GovernanceError(f"{path}: malformed E-series identity cell {row[0]!r}")
        work_id, direct_name = match.groups()
        if work_id in entries:
            raise GovernanceError(f"{path}: duplicate E-series ID {work_id}")
        entries[work_id] = (direct_name, row[2], row[3])
    return entries


def _git_output(root: Path, arguments: Sequence[str], label: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GovernanceError(f"{label}: git command failed: {stderr}")
    return completed.stdout


def require_full_git_history(root: Path) -> None:
    shallow = _git_output(
        root, ["rev-parse", "--is-shallow-repository"], "Git history check"
    ).decode("ascii").strip()
    if shallow == "true":
        raise GovernanceError(
            "design anchors require full Git history; use checkout fetch-depth: 0"
        )


def validate_design_commit_anchor(
    root: Path,
    directory: Path,
    design_sha256: str,
    design_commit: str,
    *,
    verify_current_shared_inputs: bool = True,
) -> None:
    require_full_git_history(root)
    commit_object = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{design_commit}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    if commit_object.returncode:
        raise GovernanceError(
            f"{directory}: design commit does not exist; fetch full history with depth 0"
        )
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", design_commit, "HEAD"],
        check=False,
        capture_output=True,
    )
    if ancestor.returncode:
        raise GovernanceError(f"{directory}: design commit is not an ancestor of HEAD")
    directory_relative = directory.relative_to(root).as_posix()
    design_relative = f"{directory_relative}/{DESIGN_NAME}"
    sidecar_relative = f"{directory_relative}/{DESIGN_HASH_NAME}"
    committed_design = _git_output(
        root, ["show", f"{design_commit}:{design_relative}"], "committed design"
    )
    committed_sidecar = _git_output(
        root, ["show", f"{design_commit}:{sidecar_relative}"], "committed design hash"
    )
    _reject_cr_bytes(directory / DESIGN_NAME, committed_design)
    _reject_cr_bytes(directory / DESIGN_HASH_NAME, committed_sidecar)
    committed_hash = sha256_bytes(committed_design)
    expected_sidecar = f"{committed_hash}  {DESIGN_NAME}\n".encode("ascii")
    if committed_sidecar != expected_sidecar or committed_hash != design_sha256:
        raise GovernanceError(f"{directory}: design commit hash anchor is inconsistent")
    try:
        committed_design_text = committed_design.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GovernanceError(f"{directory}: committed design is not valid UTF-8 JSON") from exc
    committed_design_json = strict_json_loads(
        committed_design_text, f"{directory}: committed design"
    )
    validate_with_schema(
        committed_design_json,
        root / DESIGN_SCHEMA_PATH,
        f"{directory}: committed design",
    )

    parents = _git_output(
        root, ["rev-list", "--parents", "-n", "1", design_commit], "design commit"
    ).decode("ascii").split()
    if len(parents) != 2:
        raise GovernanceError(
            f"{directory}: design-only commit must have exactly one parent"
        )
    if parents[1] != committed_design_json["execution_plan"]["base_git_commit"]:
        raise GovernanceError(
            f"{directory}: design commit parent differs from execution_plan.base_git_commit"
        )

    current_design = canonical_index_bytes(root, design_relative, "current design")
    current_sidecar = canonical_index_bytes(
        root, sidecar_relative, "current design hash"
    )
    if current_design != committed_design or current_sidecar != committed_sidecar:
        raise GovernanceError(f"{directory}: frozen design drifted from its design commit")

    changed_lines = _git_output(
        root,
        [
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "--no-renames",
            "-r",
            design_commit,
        ],
        "design commit changed paths",
    ).decode("utf-8").splitlines()
    changed: dict[str, str] = {}
    for line in changed_lines:
        try:
            status, changed_path = line.split("\t", 1)
        except ValueError as exc:
            raise GovernanceError(
                f"{directory}: cannot parse design commit change {line!r}"
            ) from exc
        changed[changed_path] = status
    prefix = directory_relative + "/"
    if changed.get(design_relative) != "A" or changed.get(sidecar_relative) != "A":
        raise GovernanceError(
            f"{directory}: design manifest and sidecar must be Added by the design commit"
        )

    immutable_local_paths: set[str] = set()
    for group, section in (("source_files", "scripts"), ("config_files", "configs")):
        for record in committed_design_json["execution_plan"][group]:
            path = record["path"]
            if not path.startswith(prefix):
                continue
            local = PurePosixPath(path[len(prefix) :])
            if len(local.parts) != 2 or local.parts[0] != section:
                raise GovernanceError(
                    f"{directory}: local {group} must be a direct {section}/ snapshot: {path}"
                )
            immutable_local_paths.add(path)
    environment_path = committed_design_json["execution_plan"]["environment"]["path"]
    if environment_path != f"{directory_relative}/environment.txt":
        raise GovernanceError(
            f"{directory}: environment snapshot must be {directory_relative}/environment.txt"
        )
    immutable_local_paths.add(environment_path)
    expected_commands = f"{directory_relative}/commands.log"
    if committed_design_json["execution_plan"]["commands_file"] != expected_commands:
        raise GovernanceError(
            f"{directory}: commands_file must be the post-anchor path {expected_commands}"
        )

    allowed_changed = {
        design_relative,
        sidecar_relative,
        *immutable_local_paths,
    }
    for changed_path, status in changed.items():
        if changed_path not in allowed_changed:
            raise GovernanceError(
                f"{directory}: design-only commit changed non-immutable path {changed_path}"
            )
        if status != "A":
            raise GovernanceError(
                f"{directory}: design-only path must be Added, got {status}: {changed_path}"
            )
    missing_local = sorted(immutable_local_paths - set(changed))
    if missing_local:
        raise GovernanceError(
            f"{directory}: design-only commit omitted local immutable inputs {missing_local}"
        )
    tree_paths = set(
        _git_output(
            root,
            ["ls-tree", "-r", "--name-only", design_commit, "--", directory_relative],
            "design commit experiment tree",
        )
        .decode("utf-8")
        .splitlines()
    )
    if tree_paths != allowed_changed:
        raise GovernanceError(
            f"{directory}: design commit tree contains non-design lifecycle/evidence files; "
            f"expected={sorted(allowed_changed)}, actual={sorted(tree_paths)}"
        )

    immutable_records: list[tuple[str, str, str]] = []
    for group in ("source_files", "config_files"):
        for record in committed_design_json["execution_plan"][group]:
            immutable_records.append((record["path"], record["sha256"], group))
    environment = committed_design_json["execution_plan"]["environment"]
    immutable_records.append(
        (environment["path"], environment["sha256"], "environment")
    )
    for record in committed_design_json["input_contract"]["sources"]:
        immutable_records.append((record["path"], record["sha256"], "data manifest"))
    baseline = committed_design_json["baseline"]
    if baseline is not None:
        immutable_records.append(
            (baseline["evidence_path"], baseline["sha256"], "baseline evidence")
        )
    for record in committed_design_json["reused_learned_artifacts"]:
        immutable_records.append(
            (
                record["manifest_path"],
                record["manifest_sha256"],
                "learned-artifact manifest",
            )
        )

    record_paths = [record[0] for record in immutable_records]
    if len(record_paths) != len(set(record_paths)):
        raise GovernanceError(
            f"{directory}: immutable provenance paths must be unique across roles"
        )
    committed_blobs: dict[str, bytes] = {}
    for relative_path, expected_hash, role in immutable_records:
        committed_bytes = _git_output(
            root,
            ["show", f"{design_commit}:{relative_path}"],
            f"{role} at design commit",
        )
        governed_path = root / PurePosixPath(relative_path)
        _reject_cr_bytes(governed_path, committed_bytes)
        if sha256_bytes(committed_bytes) != expected_hash:
            raise GovernanceError(
                f"{directory}: committed {role} hash mismatch for {relative_path}"
            )
        committed_blobs[relative_path] = committed_bytes
        is_archive_local = relative_path.startswith(prefix)
        if verify_current_shared_inputs or is_archive_local:
            current_hash = canonical_file_sha256(
                root, relative_path, f"current frozen {role}"
            )
            if current_hash != expected_hash:
                raise GovernanceError(
                    f"{directory}: current {role} drift for {relative_path}"
                )

    committed_data_manifests: dict[str, dict[str, Any]] = {}
    for record in committed_design_json["input_contract"]["sources"]:
        relative_path = record["path"]
        try:
            text = committed_blobs[relative_path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GovernanceError(
                f"{directory}: committed data manifest is not UTF-8: {relative_path}"
            ) from exc
        manifest = strict_json_loads(text, f"committed data manifest {relative_path}")
        validate_with_schema(
            manifest,
            root / DEVELOPMENT_DATA_SCHEMA_PATH,
            f"committed data manifest {relative_path}",
        )
        _validate_development_manifest_semantics(manifest, relative_path)
        roles = sorted({entry["role"] for entry in manifest["entries"]})
        if (
            manifest["manifest_id"] != record["manifest_id"]
            or roles != record["development_roles"]
        ):
            raise GovernanceError(
                f"{directory}: committed data-manifest identity/roles mismatch"
            )
        committed_data_manifests[relative_path] = manifest

    artifact_schema_path = root / "schemas" / "learned-artifact-manifest.schema.json"
    for record in committed_design_json["reused_learned_artifacts"]:
        relative_path = record["manifest_path"]
        try:
            text = committed_blobs[relative_path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise GovernanceError(
                f"{directory}: committed artifact manifest is not UTF-8: {relative_path}"
            ) from exc
        manifest = strict_json_loads(text, f"committed artifact manifest {relative_path}")
        validate_with_schema(
            manifest,
            artifact_schema_path,
            f"committed artifact manifest {relative_path}",
        )
        expected_artifact = {
            "id": manifest["artifact_id"],
            "manifest_path": relative_path,
            "manifest_sha256": sha256_bytes(committed_blobs[relative_path]),
            "content_sha256": manifest["content_sha256"],
            "locator": manifest["locator"],
            "origin": manifest["origin"],
            "availability_limits": manifest["availability_limits"],
            "fit_data_roles": manifest["fit_data_roles"],
            "candidate_or_locked_test_derived": False,
        }
        if record != expected_artifact:
            raise GovernanceError(
                f"{directory}: committed learned-artifact lineage mismatch"
            )
        data_reference = manifest["data_manifest"]
        data_path = data_reference["path"]
        if data_path not in committed_data_manifests:
            data_bytes = _git_output(
                root,
                ["show", f"{design_commit}:{data_path}"],
                "artifact data manifest at design commit",
            )
            _reject_cr_bytes(root / PurePosixPath(data_path), data_bytes)
            if sha256_bytes(data_bytes) != data_reference["sha256"]:
                raise GovernanceError(
                    f"{directory}: artifact data-manifest hash mismatch at design commit"
                )
            try:
                data_text = data_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise GovernanceError(
                    f"{directory}: artifact data manifest is not UTF-8"
                ) from exc
            data_manifest = strict_json_loads(
                data_text, f"artifact data manifest {data_path}"
            )
            validate_with_schema(
                data_manifest,
                root / DEVELOPMENT_DATA_SCHEMA_PATH,
                f"artifact data manifest {data_path}",
            )
            _validate_development_manifest_semantics(data_manifest, data_path)
            committed_data_manifests[data_path] = data_manifest
            committed_blobs[data_path] = data_bytes
            is_archive_local = data_path.startswith(prefix)
            if verify_current_shared_inputs or is_archive_local:
                if canonical_file_sha256(
                    root, data_path, "current artifact data manifest"
                ) != data_reference["sha256"]:
                    raise GovernanceError(
                        f"{directory}: current artifact data manifest drift"
                    )
        elif (
            sha256_bytes(committed_blobs[data_path])
            != data_reference["sha256"]
        ):
            raise GovernanceError(
                f"{directory}: artifact references the wrong committed data-manifest hash"
            )
    if committed_data_manifests:
        _validate_data_role_disjointness(
            list(committed_data_manifests.values()),
            f"{directory}: committed development data manifests",
        )


def validate_active_e_registry(root: Path) -> CheckResult:
    records = load_active_e_registry(root)
    work_index = load_work_index_e_entries(root)
    for record in records:
        if work_index.get(record.work_id) != record.direct_name:
            raise GovernanceError(
                f"WORK_INDEX.md does not contain exact identity "
                f"{record.work_id} — {record.direct_name}"
            )
        directory = root / PurePosixPath(record.mutable_root.rstrip("/"))
        if record.status == "registered":
            if (directory / DESIGN_NAME).exists() or (directory / DESIGN_HASH_NAME).exists():
                raise GovernanceError(
                    f"{record.work_id}: generated design awaits coordinator hash/commit anchor"
                )
            continue
        if not directory.is_dir():
            raise GovernanceError(f"{record.work_id}: frozen experiment directory is missing")
        validate_design_commit_anchor(
            root, directory, record.design_sha256, record.design_commit
        )
    return CheckResult("Active E registry", f"{len(records)} active E-series rows validated")


def _parse_hash_sidecar(path: Path) -> str:
    raw = path.read_bytes()
    _reject_cr_bytes(path, raw)
    try:
        content = raw.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise GovernanceError(f"{path}: hash sidecar must be UTF-8") from exc
    match = re.fullmatch(r"([0-9a-f]{64})  design_manifest\.json", content)
    if not match:
        raise GovernanceError(f"{path}: expected '<sha256>  design_manifest.json'")
    return match.group(1)


def _validate_design_invariants(
    root: Path,
    directory: Path,
    design: dict[str, Any],
    *,
    verify_current_shared_inputs: bool = True,
) -> None:
    expected_work_id = directory.name.split("-", 1)[0]
    if design["work_id"] != expected_work_id:
        raise GovernanceError(
            f"{directory}: work_id {design['work_id']!r} does not match directory"
        )
    if design["track"] != "E-series":
        raise GovernanceError(f"{directory}: E-series design must use track 'E-series'")
    if design["method"]["kind"] != design["experiment_kind"]:
        raise GovernanceError(f"{directory}: method.kind must match experiment_kind")
    if design["protocol"]["sealed_test_access"] is not False:
        raise GovernanceError(f"{directory}: exploratory design cannot authorise sealed-test access")

    expected_mutable_path = f"experiments/{directory.name}/"
    if design["registered_mutable_paths"] != [expected_mutable_path]:
        raise GovernanceError(
            f"{directory}: registered_mutable_paths must contain only {expected_mutable_path!r}"
        )
    if design["output_contract"]["result_schema"] != RESULT_SCHEMA_PATH.as_posix():
        raise GovernanceError(f"{directory}: output_contract.result_schema is not authoritative")

    directory_prefix = directory.relative_to(root).as_posix() + "/"
    manifest_documents: list[dict[str, Any]] = []
    data_paths = [source["path"] for source in design["input_contract"]["sources"]]
    if len(data_paths) != len(set(data_paths)):
        raise GovernanceError(f"{directory}: duplicate data-manifest paths")
    for source in design["input_contract"]["sources"]:
        if verify_current_shared_inputs or source["path"].startswith(directory_prefix):
            manifest, manifest_hash = validate_development_data_manifest(
                root, source["path"]
            )
            manifest_documents.append(manifest)
            roles = sorted({entry["role"] for entry in manifest["entries"]})
            if manifest_hash != source["sha256"]:
                raise GovernanceError(
                    f"{directory}: input source hash mismatch: {source['path']}"
                )
            if (
                manifest["manifest_id"] != source["manifest_id"]
                or roles != source["development_roles"]
            ):
                raise GovernanceError(f"{directory}: data-manifest identity/roles mismatch")
    if manifest_documents:
        _validate_data_role_disjointness(
            manifest_documents, f"{directory}: development data manifests"
        )
    uses_data = design["input_contract"]["uses_data"]
    if uses_data and not design["input_contract"]["sources"]:
        raise GovernanceError(f"{directory}: uses_data=true requires at least one source")
    if not uses_data and design["input_contract"]["sources"]:
        raise GovernanceError(f"{directory}: uses_data=false cannot list sources")

    planned_paths = {
        group: [record["path"] for record in design["execution_plan"][group]]
        for group in ("source_files", "config_files")
    }
    for group, paths in planned_paths.items():
        if len(paths) != len(set(paths)):
            raise GovernanceError(f"{directory}: duplicate execution-plan {group} paths")
    overlap = set(planned_paths["source_files"]) & set(planned_paths["config_files"])
    if overlap:
        raise GovernanceError(
            f"{directory}: paths cannot be both source and config: {sorted(overlap)}"
        )
    for group in ("source_files", "config_files"):
        for record in design["execution_plan"][group]:
            if verify_current_shared_inputs or record["path"].startswith(directory_prefix):
                actual_hash = canonical_file_sha256(
                    root, record["path"], f"{directory}: execution plan {group}"
                )
                if actual_hash != record["sha256"]:
                    raise GovernanceError(
                        f"{directory}: execution plan hash mismatch: {record['path']}"
                    )
    local_source_files = {
        path.relative_to(root).as_posix()
        for path in (directory / "scripts").glob("*")
        if path.is_file()
    }
    local_config_files = {
        path.relative_to(root).as_posix()
        for path in (directory / "configs").glob("*")
        if path.is_file()
    }
    planned_source_files = {
        record["path"] for record in design["execution_plan"]["source_files"]
    }
    planned_config_files = {
        record["path"] for record in design["execution_plan"]["config_files"]
    }
    if not local_source_files.issubset(planned_source_files):
        raise GovernanceError(f"{directory}: local source file lacks frozen provenance")
    if not local_config_files.issubset(planned_config_files):
        raise GovernanceError(f"{directory}: local config file lacks frozen provenance")
    environment = design["execution_plan"]["environment"]
    environment_target = safe_repository_file(
        root, environment["path"], f"{directory}: environment"
    )
    environment_bytes = environment_target.read_bytes()
    _reject_cr_bytes(environment_target, environment_bytes)
    if sha256_bytes(environment_bytes) != environment["sha256"]:
        raise GovernanceError(f"{directory}: environment hash mismatch")

    baseline = design["baseline"]
    if design["experiment_kind"] == "comparison":
        if baseline is None:
            raise GovernanceError(f"{directory}: comparison requires baseline evidence")
        if verify_current_shared_inputs or baseline["evidence_path"].startswith(
            directory_prefix
        ):
            baseline_hash = canonical_file_sha256(
                root, baseline["evidence_path"], f"{directory}: baseline evidence"
            )
            if baseline_hash != baseline["sha256"]:
                raise GovernanceError(f"{directory}: baseline evidence hash mismatch")
        if not design["reproducibility"]["seeds"]:
            raise GovernanceError(f"{directory}: comparison requires at least one seed")
    elif baseline is not None:
        if verify_current_shared_inputs or baseline["evidence_path"].startswith(
            directory_prefix
        ):
            baseline_hash = canonical_file_sha256(
                root, baseline["evidence_path"], f"{directory}: baseline evidence"
            )
            if baseline_hash != baseline["sha256"]:
                raise GovernanceError(f"{directory}: baseline evidence hash mismatch")

    artifact_paths = [
        artifact["manifest_path"] for artifact in design["reused_learned_artifacts"]
    ]
    if len(artifact_paths) != len(set(artifact_paths)):
        raise GovernanceError(f"{directory}: duplicate learned-artifact manifests")
    for artifact in design["reused_learned_artifacts"]:
        if verify_current_shared_inputs or artifact["manifest_path"].startswith(
            directory_prefix
        ):
            manifest, manifest_hash = validate_learned_artifact_manifest(
                root, artifact["manifest_path"]
            )
            expected = {
                "id": manifest["artifact_id"],
                "manifest_path": artifact["manifest_path"],
                "manifest_sha256": manifest_hash,
                "content_sha256": manifest["content_sha256"],
                "locator": manifest["locator"],
                "origin": manifest["origin"],
                "availability_limits": manifest["availability_limits"],
                "fit_data_roles": manifest["fit_data_roles"],
                "candidate_or_locked_test_derived": False,
            }
            if artifact != expected:
                raise GovernanceError(f"{directory}: reused artifact lineage mismatch")

    table_specs = design["output_contract"].get("aggregate_tables", [])
    table_paths = [spec["path"] for spec in table_specs]
    if len(table_paths) != len(set(table_paths)):
        raise GovernanceError(f"{directory}: duplicate aggregate-table contracts")
    for spec in table_specs:
        forbidden = [
            column
            for column in spec["columns"]
            if FORBIDDEN_ROW_LEVEL_COLUMN_RE.search(column)
        ]
        if forbidden:
            raise GovernanceError(
                f"{directory}: aggregate-table contract contains row-level columns "
                f"{forbidden}"
            )
        if spec["max_rows"] > MAX_AGGREGATE_TABLE_ROWS:
            raise GovernanceError(
                f"{directory}: aggregate-table max_rows exceeds "
                f"{MAX_AGGREGATE_TABLE_ROWS}: {spec['path']}"
            )


def validate_design_directory(
    root: Path,
    directory: Path,
    *,
    verify_current_shared_inputs: bool = True,
) -> tuple[dict[str, Any], str]:
    design_path = safe_repository_file(
        root, directory.relative_to(root) / DESIGN_NAME, "frozen design"
    )
    sidecar_path = safe_repository_file(
        root, directory.relative_to(root) / DESIGN_HASH_NAME, "frozen design hash"
    )
    _reject_cr_bytes(design_path, design_path.read_bytes())
    _reject_cr_bytes(sidecar_path, sidecar_path.read_bytes())
    design = load_json(design_path)
    validate_with_schema(design, root / DESIGN_SCHEMA_PATH, str(design_path))
    _validate_design_invariants(
        root,
        directory,
        design,
        verify_current_shared_inputs=verify_current_shared_inputs,
    )
    expected_hash = _parse_hash_sidecar(sidecar_path)
    actual_hash = sha256_file(design_path)
    if actual_hash != expected_hash:
        raise GovernanceError(
            f"{design_path}: frozen design hash mismatch ({expected_hash} != {actual_hash})"
        )
    return design, actual_hash


def _validate_result_invariants(
    root: Path,
    directory: Path,
    design: dict[str, Any],
    design_hash: str,
    result: dict[str, Any],
    archive_files: Sequence[Path],
    *,
    verify_current_shared_inputs: bool,
) -> None:
    for field in (
        "work_id",
        "name",
        "owner",
        "track",
        "experiment_kind",
        "workflow_layer",
        "protocol",
        "task_definition",
        "output_policy",
    ):
        if result[field] != design[field]:
            raise GovernanceError(f"{directory}: result.{field} does not match frozen design")
    if result["design_sha256"] != design_hash:
        raise GovernanceError(f"{directory}: result.design_sha256 does not match frozen design")
    if result["work_kind"] != "experiment":
        raise GovernanceError(f"{directory}: E-series result must use work_kind 'experiment'")
    if result["reproducibility"] != {
        "seeds": design["reproducibility"]["seeds"],
        "folds": design["reproducibility"]["folds"],
        "repeat_count": design["reproducibility"]["repeat_count"],
    }:
        raise GovernanceError(f"{directory}: result reproducibility differs from frozen design")
    if result["safety_assertions"] != {
        key: design["safety_assertions"][key]
        for key in (
            "no_candidate_or_locked_test_feedback",
            "no_candidate_or_locked_test_derived_learned_state",
            "preprocessing_fit_scope",
            "shared_inputs_are_immutable_and_hashed",
        )
    }:
        raise GovernanceError(f"{directory}: result safety assertions differ from frozen design")

    validity = result["validity"]["status"]
    outcome = result["outcome"]
    execution = result["execution"]["status"]
    lifecycle_status = result["lifecycle_status"]
    action = result["decision"]["action"]
    if lifecycle_status == "superseded_before_execution":
        if (
            execution != "not_run"
            or validity != "not_assessed"
            or outcome != "not_applicable"
            or action != "supersede"
            or not isinstance(result["superseded_by"], str)
            or result["superseded_by"] == result["work_id"]
        ):
            raise GovernanceError(
                f"{directory}: superseded_before_execution requires not_run, "
                "not_assessed, not_applicable, supersede, and another E-series ID"
            )
        if result.get("metrics") or result.get("observations") or result["evidence"]:
            raise GovernanceError(
                f"{directory}: pre-execution supersession cannot claim metrics, "
                "observations, or evidence"
            )
    else:
        if result["superseded_by"] is not None:
            raise GovernanceError(
                f"{directory}: completed lifecycle requires superseded_by=null"
            )
        if not result["evidence"]:
            raise GovernanceError(f"{directory}: completed result requires evidence")
        if (validity == "invalid") != (outcome == "invalid"):
            raise GovernanceError(
                f"{directory}: validity=invalid and outcome=invalid must be used together"
            )
        if outcome in {"supported", "not_supported", "inconclusive"}:
            if execution != "succeeded" or validity != "valid":
                raise GovernanceError(
                    f"{directory}: non-invalid outcomes require succeeded execution "
                    "and valid result"
                )
        if execution != "succeeded" and outcome != "invalid":
            raise GovernanceError(
                f"{directory}: failed/not-run execution must have invalid outcome"
            )
        if outcome == "invalid":
            if action not in {"close-invalid", "repeat", "defer"}:
                raise GovernanceError(
                    f"{directory}: invalid outcome requires close-invalid, repeat, or defer"
                )
        elif action == "close-invalid":
            raise GovernanceError(
                f"{directory}: close-invalid is reserved for invalid outcomes"
            )
        if (
            design["experiment_kind"] == "comparison"
            and outcome in {"supported", "not_supported", "inconclusive"}
        ):
            metrics = result.get("metrics", [])
            if not metrics:
                raise GovernanceError(
                    f"{directory}: valid comparison outcome requires declared metrics"
                )
            primary_metric = design["method"]["primary_metric"]["name"]
            if primary_metric not in {metric["name"] for metric in metrics}:
                raise GovernanceError(
                    f"{directory}: comparison result omits frozen primary metric "
                    f"{primary_metric!r}"
                )
        if design["experiment_kind"] in {"diagnostic", "feasibility"}:
            if not result.get("observations"):
                raise GovernanceError(
                    f"{directory}: diagnostic/feasibility result requires observations"
                )

    provenance = result["provenance"]
    if provenance["base_git_commit"] != design["execution_plan"]["base_git_commit"]:
        raise GovernanceError(f"{directory}: result base commit differs from frozen design")
    if provenance["executed_source_files"] != design["execution_plan"]["source_files"]:
        raise GovernanceError(f"{directory}: executed source hashes differ from frozen plan")
    if provenance["config_files"] != design["execution_plan"]["config_files"]:
        raise GovernanceError(f"{directory}: config hashes differ from frozen plan")
    if provenance["environment"] != design["execution_plan"]["environment"]:
        raise GovernanceError(f"{directory}: environment hash differs from frozen plan")
    directory_prefix = directory.relative_to(root).as_posix() + "/"
    for group in (
        "executed_source_files",
        "config_files",
    ):
        for record in provenance[group]:
            if verify_current_shared_inputs or record["path"].startswith(directory_prefix):
                actual_hash = canonical_file_sha256(
                    root, record["path"], f"{directory}: provenance {group}"
                )
                if actual_hash != record["sha256"]:
                    raise GovernanceError(
                        f"{directory}: provenance hash mismatch: {record['path']}"
                    )
    environment = provenance["environment"]
    environment_hash = canonical_file_sha256(
        root, environment["path"], f"{directory}: result environment"
    )
    if environment_hash != environment["sha256"]:
        raise GovernanceError(f"{directory}: result environment hash mismatch")

    design_data = {
        (record["path"], record["sha256"])
        for record in design["input_contract"]["sources"]
        if record["role"] == "data_manifest"
    }
    result_data = {
        (record["path"], record["sha256"])
        for record in provenance["data_manifests"]
    }
    if result_data != design_data:
        raise GovernanceError(f"{directory}: result data-manifest lineage differs from design")
    if verify_current_shared_inputs:
        current_manifests: list[dict[str, Any]] = []
        for record in provenance["data_manifests"]:
            manifest, manifest_hash = validate_development_data_manifest(
                root, record["path"]
            )
            if manifest_hash != record["sha256"]:
                raise GovernanceError(
                    f"{directory}: current data-manifest hash mismatch"
                )
            current_manifests.append(manifest)
        if current_manifests:
            _validate_data_role_disjointness(
                current_manifests, f"{directory}: result data manifests"
            )
    if provenance["reused_learned_artifacts"] != design["reused_learned_artifacts"]:
        raise GovernanceError(f"{directory}: reused learned-artifact lineage differs from design")
    for record in provenance["reused_learned_artifacts"]:
        if verify_current_shared_inputs or record["manifest_path"].startswith(
            directory_prefix
        ):
            _, manifest_hash = validate_learned_artifact_manifest(
                root, record["manifest_path"]
            )
            if manifest_hash != record["manifest_sha256"]:
                raise GovernanceError(
                    f"{directory}: learned-artifact manifest hash mismatch"
                )

    declared: dict[str, dict[str, Any]] = {}
    for record in result["archive"]["files"]:
        relative_path = record["path"].replace("\\", "/")
        _validate_relative_path(relative_path, f"{directory}: archive file")
        if relative_path in {DESIGN_NAME, DESIGN_HASH_NAME, RESULT_NAME}:
            raise GovernanceError(f"{directory}: core manifest {relative_path} is implicit")
        if relative_path in declared:
            raise GovernanceError(f"{directory}: duplicate archive declaration {relative_path}")
        declared[relative_path] = record

        target = safe_repository_file(
            root,
            directory.relative_to(root).joinpath(*PurePosixPath(relative_path).parts),
            f"{directory}: declared archive file",
        )
        actual_hash = canonical_file_sha256(
            root, target.relative_to(root), f"{directory}: archive file"
        )
        if actual_hash != record["sha256"]:
            raise GovernanceError(f"{target}: result archive hash mismatch")
        _validate_archive_role(directory, PurePosixPath(relative_path), record["role"])
        if record["role"] == "aggregate_table":
            _validate_aggregate_table(target, design)

    for evidence in result["evidence"]:
        evidence_path = evidence["path"].replace("\\", "/")
        _validate_relative_path(evidence_path, f"{directory}: evidence path")
        declaration = declared.get(evidence_path)
        if declaration is None:
            raise GovernanceError(
                f"{directory}: evidence path is not present in archive.files: {evidence_path}"
            )
        if declaration["role"] not in {"narrative", "aggregate_table", "figure"}:
            raise GovernanceError(
                f"{directory}: evidence must reference narrative/table/figure: {evidence_path}"
            )

    actual = {
        path.relative_to(directory).as_posix()
        for path in archive_files
        if path.name not in {DESIGN_NAME, DESIGN_HASH_NAME, RESULT_NAME}
    }
    if actual != set(declared):
        missing = sorted(actual - set(declared))
        absent = sorted(set(declared) - actual)
        raise GovernanceError(
            f"{directory}: result archive inventory mismatch; "
            f"undeclared={missing}, missing={absent}"
        )


def _new_archive_files(
    root: Path,
    directory: Path,
    relative_files: Iterable[str] | None = None,
) -> list[Path]:
    if relative_files is None:
        prefix = directory.relative_to(root).as_posix() + "/"
        relative_files = [
            path.as_posix()[len(prefix) :]
            for path in trackable_paths(root)
            if path.as_posix().startswith(prefix)
        ]
    files: list[Path] = []
    for relative_text in relative_files:
        relative = PurePosixPath(relative_text)
        forbidden = MUTABLE_OUTPUT_SEGMENTS.intersection(relative.parts)
        if forbidden:
            raise GovernanceError(
                f"{directory}: trackable archive path uses mutable/output segment "
                f"{sorted(forbidden)}: {relative}"
            )
        target = safe_repository_file(
            root,
            directory.relative_to(root).joinpath(*relative.parts),
            f"archive path {relative}",
        )
        files.append(target)
    return sorted(files, key=lambda path: path.as_posix())


def _validate_archive_path(directory: Path, relative: PurePosixPath) -> None:
    if len(relative.parts) == 1:
        if relative.name not in ALLOWED_NEW_ARCHIVE_PATHS["."]:
            raise GovernanceError(f"{directory}: root archive file is not allowed: {relative}")
        return
    if len(relative.parts) != 2:
        raise GovernanceError(f"{directory}: archive paths may use only one approved subdirectory")
    section, filename = relative.parts
    allowed_suffixes = ALLOWED_NEW_ARCHIVE_PATHS.get(section)
    is_named_build_file = (
        section == "scripts" and filename in ALLOWED_SCRIPT_BUILD_FILES
    )
    if (
        allowed_suffixes is None
        or (
            Path(filename).suffix.lower() not in allowed_suffixes
            and not is_named_build_file
        )
    ):
        raise GovernanceError(f"{directory}: archive path is not allowed: {relative}")


def _validate_archive_role(directory: Path, relative: PurePosixPath, role: str) -> None:
    section = "." if len(relative.parts) == 1 else relative.parts[0]
    if section not in ROLE_DIRECTORIES[role]:
        raise GovernanceError(f"{directory}: role {role!r} is incompatible with {relative}")
    if role == "checksum" and not relative.name.endswith("SHA256SUMS.txt"):
        raise GovernanceError(f"{directory}: checksum role requires a SHA256SUMS.txt file")
    if role == "environment" and relative.name != "environment.txt":
        raise GovernanceError(f"{directory}: environment role requires environment.txt")
    if role == "command_log" and relative.name != "commands.log":
        raise GovernanceError(f"{directory}: command_log role requires commands.log")


def _validate_aggregate_table(path: Path, design: dict[str, Any] | None = None) -> None:
    if path.suffix.lower() != ".csv":
        raise GovernanceError(f"{path}: aggregate tables must be CSV")
    lowered_name = path.name.lower()
    relative_table = f"tables/{path.name}"
    declared_specs = {
        spec["path"]: spec
        for spec in (design or {}).get("output_contract", {}).get(
            "aggregate_tables", []
        )
    }
    declared = declared_specs.get(relative_table)
    if declared is not None:
        required = set(declared["columns"])
        allowed = required
        exact_columns = declared["columns"]
        row_limit = declared["max_rows"]
    elif design is not None:
        raise GovernanceError(
            f"{path}: aggregate table was not predeclared in the frozen design"
        )
    elif lowered_name in AGGREGATE_TABLE_CONTRACTS:
        required, allowed = AGGREGATE_TABLE_CONTRACTS[lowered_name]
        exact_columns = None
        row_limit = MAX_AGGREGATE_TABLE_ROWS
    elif lowered_name.endswith("_summary.csv"):
        required, allowed = GENERIC_SUMMARY_REQUIRED, GENERIC_SUMMARY_ALLOWED
        exact_columns = None
        row_limit = MAX_AGGREGATE_TABLE_ROWS
    else:
        raise GovernanceError(
            f"{path}: table name has no approved aggregate-column contract"
        )
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            normalised = [name.strip().lower() for name in header]
            normalised_header = set(normalised)
            if not header or "" in normalised_header:
                raise GovernanceError(f"{path}: aggregate table needs non-empty columns")
            if len(normalised) != len(normalised_header):
                raise GovernanceError(f"{path}: aggregate table has duplicate columns")
            forbidden_columns = [
                name
                for name in normalised
                if (
                    FORBIDDEN_ROW_LEVEL_COLUMN_RE.search(name)
                    and name not in SAFE_AGGREGATE_ROW_TOKEN_COLUMNS
                )
            ]
            if forbidden_columns:
                raise GovernanceError(
                    f"{path}: row-level/prediction columns are forbidden: "
                    f"{forbidden_columns}"
                )
            if exact_columns is not None and normalised != exact_columns:
                raise GovernanceError(
                    f"{path}: columns must exactly match frozen contract "
                    f"{exact_columns}, got {normalised}"
                )
            missing = sorted(required - normalised_header)
            unexpected = sorted(normalised_header - allowed)
            if missing or unexpected:
                raise GovernanceError(
                    f"{path}: aggregate column contract failed; "
                    f"missing={missing}, unexpected={unexpected}"
                )
            row_count = 0
            dimension_indexes = [
                index
                for index, name in enumerate(normalised)
                if name not in MEASURE_AGGREGATE_COLUMNS
            ]
            if not dimension_indexes:
                dimension_indexes = list(range(len(normalised)))
            seen_dimensions: set[tuple[str, ...]] = set()
            for row_number, row in enumerate(reader, start=2):
                row_count += 1
                if len(row) != len(header):
                    raise GovernanceError(
                        f"{path}:{row_number}: ragged row has {len(row)} cells; "
                        f"expected {len(header)}"
                    )
                stripped = [cell.strip() for cell in row]
                empty_columns = {
                    normalised[index]
                    for index, cell in enumerate(stripped)
                    if not cell
                }
                if empty_columns - OPTIONAL_AGGREGATE_MEASURE_COLUMNS:
                    raise GovernanceError(f"{path}:{row_number}: empty cells are forbidden")
                if any(len(cell) > MAX_AGGREGATE_CELL_LENGTH for cell in stripped):
                    raise GovernanceError(
                        f"{path}:{row_number}: aggregate cell exceeds "
                        f"{MAX_AGGREGATE_CELL_LENGTH} characters"
                    )
                for index, name in enumerate(normalised):
                    if name in NUMERIC_AGGREGATE_COLUMNS:
                        if not stripped[index]:
                            continue
                        try:
                            numeric = float(stripped[index])
                        except ValueError as exc:
                            raise GovernanceError(
                                f"{path}:{row_number}: {name} must be numeric"
                            ) from exc
                        if not math.isfinite(numeric):
                            raise GovernanceError(
                                f"{path}:{row_number}: {name} must be finite"
                            )
                    if (
                        name in BOOLEAN_AGGREGATE_COLUMNS
                        and stripped[index].lower() not in {"true", "false"}
                    ):
                        raise GovernanceError(
                            f"{path}:{row_number}: {name} must be Boolean"
                        )
                dimension_key = tuple(stripped[index] for index in dimension_indexes)
                if dimension_key in seen_dimensions:
                    raise GovernanceError(
                        f"{path}:{row_number}: duplicate aggregate dimension key "
                        f"{dimension_key}"
                    )
                seen_dimensions.add(dimension_key)
    except UnicodeDecodeError as exc:
        raise GovernanceError(f"{path}: aggregate table must be UTF-8") from exc
    if row_count < 1:
        raise GovernanceError(f"{path}: aggregate table must contain at least one data row")
    if row_count > row_limit:
        raise GovernanceError(
            f"{path}: {row_count} rows exceeds aggregate-table limit "
            f"{row_limit}"
        )


def _validate_new_archive(
    root: Path,
    directory: Path,
    relative_files: Iterable[str] | None = None,
) -> None:
    validate_tree_has_no_links(
        directory,
        MUTABLE_OUTPUT_SEGMENTS | IGNORED_LOCAL_ENVIRONMENT_SEGMENTS,
    )
    result_path = directory / RESULT_NAME
    has_result = result_path.is_file()
    expected_work_id = directory.name.split("-", 1)[0]
    active_records = [
        record
        for record in load_active_e_registry(root)
        if record.work_id == expected_work_id
    ]
    if len(active_records) > 1:
        raise GovernanceError(f"{directory}: duplicate active registry identity")
    verify_current_shared_inputs = not has_result or bool(active_records)
    design, design_hash = validate_design_directory(
        root,
        directory,
        verify_current_shared_inputs=verify_current_shared_inputs,
    )
    work_index_records = load_work_index_e_records(root)
    indexed = work_index_records.get(design["work_id"])
    if indexed is None or indexed[0] != design["name"]:
        raise GovernanceError(
            f"{directory}: WORK_INDEX.md lacks exact identity "
            f"{design['work_id']} — {design['name']}"
        )
    archive_files = _new_archive_files(root, directory, relative_files)
    for path in archive_files:
        if (
            not has_result
            and path.relative_to(directory).as_posix()
            in {"EXPERIMENT.md", "commands.log"}
        ):
            continue
        canonical_index_bytes(
            root, path.relative_to(root), f"{directory}: portable archive file"
        )
    for path in archive_files:
        relative = PurePosixPath(path.relative_to(directory).as_posix())
        _validate_archive_path(directory, relative)
        if not has_result and (
            relative.parts[0] in {"tables", "figures"}
            or relative.name in {"REPORT.md", "SHA256SUMS.txt", "SOURCE_FILE_SHA256SUMS.txt"}
        ):
            raise GovernanceError(
                f"{directory}: design-only archive cannot contain result evidence {relative}"
            )
        if relative.parts[0] == "tables":
            _validate_aggregate_table(path, design)

    if has_result:
        result = load_json(result_path)
        validate_with_schema(result, root / RESULT_SCHEMA_PATH, str(result_path))
        expected_index_status = (
            "Superseded"
            if result["lifecycle_status"] == "superseded_before_execution"
            else "Archived"
        )
        if indexed[1] != expected_index_status:
            raise GovernanceError(
                f"{directory}: WORK_INDEX status must be {expected_index_status!r}, "
                f"got {indexed[1]!r}"
            )
        outcome_cell = indexed[2]
        if result["outcome"] not in outcome_cell:
            raise GovernanceError(
                f"{directory}: WORK_INDEX outcome/evidence must name "
                f"result outcome {result['outcome']!r}"
            )
        evidence_links = {item["path"] for item in result["evidence"]} | {
            RESULT_NAME
        }
        if not any(path in outcome_cell for path in evidence_links):
            raise GovernanceError(
                f"{directory}: WORK_INDEX outcome/evidence must link result.json "
                "or a declared evidence file"
            )
        if not isinstance(result["design_commit"], str):
            raise GovernanceError(f"{directory}: E-series result requires design_commit")
        if active_records:
            active = active_records[0]
            if (
                active.status != "design_frozen"
                or active.design_sha256 != design_hash
                or active.design_commit != result["design_commit"]
            ):
                raise GovernanceError(f"{directory}: active and durable design anchors differ")
        validate_design_commit_anchor(
            root,
            directory,
            design_hash,
            result["design_commit"],
            verify_current_shared_inputs=verify_current_shared_inputs,
        )
        _validate_result_invariants(
            root,
            directory,
            design,
            design_hash,
            result,
            archive_files,
            verify_current_shared_inputs=verify_current_shared_inputs,
        )
        if result["lifecycle_status"] == "superseded_before_execution":
            superseded_by = result["superseded_by"]
            if superseded_by not in indexed[2]:
                raise GovernanceError(
                    f"{directory}: WORK_INDEX outcome/evidence must cross-link "
                    f"superseding work {superseded_by}"
                )
    else:
        if len(active_records) != 1 or active_records[0].status != "design_frozen":
            raise GovernanceError(
                f"{directory}: design-only archive requires active design_frozen registry anchor"
            )
        active = active_records[0]
        if active.design_sha256 != design_hash:
            raise GovernanceError(f"{directory}: active design hash does not match")
        validate_design_commit_anchor(
            root,
            directory,
            active.design_sha256,
            active.design_commit,
            verify_current_shared_inputs=True,
        )


def _validate_t_series_archive(
    root: Path,
    directory: Path,
    relative_files: Iterable[str] | None = None,
) -> None:
    """Validate a compact result archive governed by a frozen T-series manifest."""
    validate_tree_has_no_links(
        directory,
        MUTABLE_OUTPUT_SEGMENTS | IGNORED_LOCAL_ENVIRONMENT_SEGMENTS,
    )
    work_id = directory.name.split("-", 1)[0]
    manifest_relative = T_SERIES_ARCHIVE_CONFIGS.get(work_id)
    if manifest_relative is None:
        raise GovernanceError(f"{directory}: no T-series archive contract is registered")

    manifest_path = safe_repository_file(
        root, manifest_relative, f"{directory}: T-series manifest"
    )
    manifest = load_json(manifest_path)
    schema_relative = Path(manifest["$schema"])
    validate_with_schema(manifest, root / schema_relative, str(manifest_path))
    manifest_hash = canonical_file_sha256(
        root, manifest_relative, f"{directory}: T-series manifest"
    )
    sidecar_relative = manifest_relative.with_suffix(".sha256")
    expected_sidecar = (
        f"{manifest_hash}  {manifest_relative.as_posix()}\n".encode("ascii")
    )
    actual_sidecar = canonical_index_bytes(
        root, sidecar_relative, f"{directory}: T-series manifest sidecar"
    )
    if actual_sidecar != expected_sidecar:
        raise GovernanceError(f"{directory}: T-series manifest sidecar mismatch")
    if manifest["task"]["work_id"] != work_id:
        raise GovernanceError(f"{directory}: manifest work identity mismatch")
    expected_archive = directory.relative_to(root).as_posix()
    if manifest["output_contract"]["archive"] != expected_archive:
        raise GovernanceError(f"{directory}: manifest archive path mismatch")

    archive_files = _new_archive_files(root, directory, relative_files)
    actual_relative = {
        path.relative_to(directory).as_posix() for path in archive_files
    }
    required = {
        "BASELINE_REPORT.md",
        "result.json",
        "environment.txt",
        "commands.log",
        "model_artifacts.json",
        "CHECKSUMS.sha256",
        *{
            spec["path"]
            for spec in manifest["output_contract"]["aggregate_tables"]
        },
    }
    if not required.issubset(actual_relative):
        raise GovernanceError(
            f"{directory}: T-series archive lacks required files "
            f"{sorted(required - actual_relative)}"
        )
    for path in archive_files:
        canonical_index_bytes(
            root, path.relative_to(root), f"{directory}: portable archive file"
        )

    result_path = directory / RESULT_NAME
    result = load_json(result_path)
    validate_with_schema(result, root / RESULT_SCHEMA_PATH, str(result_path))
    if (
        result["work_id"] != work_id
        or result["name"] != manifest["task"]["direct_name"]
        or result["track"] != "T-series"
        or result["status"] != "complete"
    ):
        raise GovernanceError(f"{directory}: result identity or lifecycle mismatch")
    if result["design_sha256"] is not None or result["design_commit"] is not None:
        raise GovernanceError(f"{directory}: T-series result must not claim an E-series anchor")
    config_files = result["provenance"]["config_files"]
    if config_files != [
        {"path": manifest_relative.as_posix(), "sha256": manifest_hash}
    ]:
        raise GovernanceError(f"{directory}: result manifest provenance mismatch")

    base_commit = result["provenance"]["base_git_commit"]
    require_full_git_history(root)
    commit_object = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{base_commit}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    if commit_object.returncode:
        raise GovernanceError(f"{directory}: pre-run commit does not exist")
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", base_commit, "HEAD"],
        check=False,
        capture_output=True,
    )
    if ancestor.returncode:
        raise GovernanceError(f"{directory}: pre-run commit is not an ancestor of HEAD")
    committed_manifest = _git_output(
        root,
        ["show", f"{base_commit}:{manifest_relative.as_posix()}"],
        f"{directory}: committed T-series manifest",
    )
    committed_sidecar = _git_output(
        root,
        ["show", f"{base_commit}:{sidecar_relative.as_posix()}"],
        f"{directory}: committed T-series manifest sidecar",
    )
    if (
        sha256_bytes(committed_manifest) != manifest_hash
        or committed_sidecar != expected_sidecar
    ):
        raise GovernanceError(f"{directory}: pre-run manifest anchor mismatch")

    executed_sources = result["provenance"]["executed_source_files"]
    expected_sources = [
        {"path": record["path"], "sha256": record["sha256"]}
        for record in manifest["source_identity"]
    ]
    if executed_sources != expected_sources:
        raise GovernanceError(f"{directory}: executed source identity mismatch")
    for record in manifest["source_identity"]:
        committed_source = _git_output(
            root,
            ["show", f"{base_commit}:{record['path']}"],
            f"{directory}: committed source {record['path']}",
        )
        if sha256_bytes(committed_source) != record["sha256"]:
            raise GovernanceError(
                f"{directory}: pre-run source hash mismatch for {record['path']}"
            )

    declared: dict[str, dict[str, Any]] = {}
    for record in result["archive"]["files"]:
        relative_text = record["path"].replace("\\", "/")
        _validate_relative_path(relative_text, f"{directory}: archive file")
        if relative_text == RESULT_NAME or relative_text in declared:
            raise GovernanceError(
                f"{directory}: invalid or duplicate archive declaration {relative_text}"
            )
        relative = PurePosixPath(relative_text)
        target = safe_repository_file(
            root,
            directory.relative_to(root).joinpath(*relative.parts),
            f"{directory}: declared archive file",
        )
        if canonical_file_sha256(
            root, target.relative_to(root), f"{directory}: archive file"
        ) != record["sha256"]:
            raise GovernanceError(f"{target}: result archive hash mismatch")
        if record["contains_row_level_data"] or record["contains_sensitive_data"]:
            raise GovernanceError(f"{target}: compact T-series archive flags are unsafe")
        expected_role = None
        if relative_text == "model_artifacts.json":
            expected_role = "configuration"
        elif relative_text == "CHECKSUMS.sha256":
            expected_role = "checksum"
        elif relative.parts[0] == "tables":
            expected_role = "aggregate_table"
        else:
            expected_roles = {
                "BASELINE_REPORT.md": "narrative",
                "environment.txt": "environment",
                "commands.log": "command_log",
            }
            expected_role = expected_roles.get(relative_text)
        if record["role"] != expected_role:
            raise GovernanceError(
                f"{directory}: role {record['role']!r} is incompatible with {relative}"
            )
        if record["role"] == "aggregate_table":
            _validate_aggregate_table(target, manifest)
        declared[relative_text] = record

    actual_declared = actual_relative - {RESULT_NAME}
    if set(declared) != actual_declared:
        raise GovernanceError(
            f"{directory}: result archive inventory mismatch; "
            f"undeclared={sorted(actual_declared - set(declared))}, "
            f"missing={sorted(set(declared) - actual_declared)}"
        )
    for evidence in result["evidence"]:
        declaration = declared.get(evidence["path"])
        if declaration is None or declaration["role"] not in {
            "narrative",
            "aggregate_table",
        }:
            raise GovernanceError(
                f"{directory}: evidence path is not a declared report/table"
            )

    environment = result["provenance"]["environment"]
    expected_environment = (
        directory.relative_to(root).joinpath("environment.txt").as_posix()
    )
    if (
        environment["path"] != expected_environment
        or environment["sha256"] != declared["environment.txt"]["sha256"]
    ):
        raise GovernanceError(f"{directory}: environment provenance mismatch")

    checksum_lines = canonical_index_bytes(
        root,
        (directory / "CHECKSUMS.sha256").relative_to(root),
        f"{directory}: checksums",
    ).decode("ascii").splitlines()
    checksum_records: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match or match.group(2) in checksum_records:
            raise GovernanceError(f"{directory}: malformed or duplicate checksum line")
        checksum_records[match.group(2)] = match.group(1)
    expected_checksum_paths = set(declared) - {"CHECKSUMS.sha256"}
    if set(checksum_records) != expected_checksum_paths:
        raise GovernanceError(f"{directory}: checksum inventory mismatch")
    for relative_text, expected_hash in checksum_records.items():
        if expected_hash != declared[relative_text]["sha256"]:
            raise GovernanceError(
                f"{directory}: checksum differs from result for {relative_text}"
            )


def _validate_prototype_t_series_archive(
    root: Path,
    directory: Path,
    relative_files: Iterable[str],
) -> None:
    """Validate the deliberately compact T006 prototype result."""

    validate_tree_has_no_links(
        directory,
        MUTABLE_OUTPUT_SEGMENTS | IGNORED_LOCAL_ENVIRONMENT_SEGMENTS,
    )
    expected = PROTOTYPE_T_SERIES_ARCHIVES[directory.name]
    actual = set(relative_files)
    if actual != expected:
        raise GovernanceError(
            f"{directory}: prototype archive inventory mismatch; "
            f"expected={sorted(expected)}, actual={sorted(actual)}"
        )
    for relative_text in sorted(actual):
        path = directory / relative_text
        if path.suffix.lower() in GOVERNED_TEXT_SUFFIXES:
            canonical_index_bytes(
                root, path.relative_to(root), f"{directory}: portable prototype file"
            )

    result = load_json(directory / RESULT_NAME)
    if (
        result.get("work_id") != "T006"
        or result.get("name") != "Direct rTM NILM Prototype"
        or result.get("track") != "T-series"
        or result.get("status") != "complete"
    ):
        raise GovernanceError(f"{directory}: prototype result identity mismatch")
    protocol = result.get("protocol")
    if not isinstance(protocol, dict) or (
        protocol.get("fold") != "F1"
        or protocol.get("training_blocks") != ["B2", "B3", "B4"]
        or protocol.get("validation_block") != "B1"
        or protocol.get("locked_test_access") is not False
        or protocol.get("protocol_x_access") is not False
    ):
        raise GovernanceError(f"{directory}: prototype protocol boundary mismatch")
    data = result.get("data")
    if not isinstance(data, dict) or (
        data.get("appliance") != "fridge"
        or data.get("window_samples") != 32
        or data.get("output_delay_samples") != 0
    ):
        raise GovernanceError(f"{directory}: prototype data contract mismatch")
    interpretation = result.get("interpretation")
    if not isinstance(interpretation, dict) or interpretation.get("operational") is not True:
        raise GovernanceError(f"{directory}: prototype did not complete operationally")

    implementation_commit = result.get("implementation_commit")
    if not isinstance(implementation_commit, str) or not re.fullmatch(
        r"[0-9a-f]{40}", implementation_commit
    ):
        raise GovernanceError(f"{directory}: invalid prototype implementation commit")
    commit_object = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{implementation_commit}^{{commit}}"],
        check=False,
        capture_output=True,
    )
    if commit_object.returncode:
        raise GovernanceError(f"{directory}: prototype implementation commit is unavailable")
    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", implementation_commit, "HEAD"],
        check=False,
        capture_output=True,
    )
    if ancestor.returncode:
        raise GovernanceError(f"{directory}: prototype implementation commit is not an ancestor")


def validate_experiment_archives(root: Path, paths: Sequence[Path]) -> CheckResult:
    experiment_root = root / "experiments"
    if not experiment_root.is_dir():
        raise GovernanceError("experiments/: directory is missing")

    trackable = {
        path.relative_to("experiments").as_posix()
        for path in paths
        if path.parts and path.parts[0] == "experiments"
    }
    top_level_files = {".gitignore", "README.md"}
    unexpected_top = {
        path for path in trackable if "/" not in path and path not in top_level_files
    }
    if unexpected_top:
        raise GovernanceError(f"experiments/: unexpected top-level files {sorted(unexpected_top)}")

    directories = sorted(
        {
            relative.split("/", 1)[0]
            for relative in trackable
            if "/" in relative
        }
    )
    legacy_checksums = load_json(root / LEGACY_CHECKSUM_PATH)
    checksum_archives = legacy_checksums.get("archives", {})
    checked = 0
    for name in directories:
        if not EXPERIMENT_DIR_RE.fullmatch(name):
            raise GovernanceError(f"experiments/{name}: invalid named-work directory")
        directory = experiment_root / name
        relative_files = {
            relative.split("/", 1)[1]
            for relative in trackable
            if relative.startswith(f"{name}/")
        }
        work_id = name.split("-", 1)[0]
        if (directory / DESIGN_NAME).is_file():
            if not WORK_ID_RE.fullmatch(name.split("-", 1)[0]):
                raise GovernanceError(f"{directory}: design manifests are currently E-series only")
            _validate_new_archive(root, directory, relative_files)
        elif name in PROTOTYPE_T_SERIES_ARCHIVES:
            _validate_prototype_t_series_archive(root, directory, relative_files)
        elif T_WORK_ID_RE.fullmatch(work_id) and (directory / RESULT_NAME).is_file():
            _validate_t_series_archive(root, directory, relative_files)
        elif name in LEGACY_ARCHIVE_FILES:
            if relative_files != LEGACY_ARCHIVE_FILES[name]:
                raise GovernanceError(
                    f"{directory}: legacy archive changed outside its fixed allowlist; "
                    f"expected={sorted(LEGACY_ARCHIVE_FILES[name])}, "
                    f"actual={sorted(relative_files)}"
                )
            expected_hashes = checksum_archives.get(name, {}).get("files")
            if not isinstance(expected_hashes, dict):
                raise GovernanceError(f"{directory}: missing v2 legacy checksum record")
            if set(expected_hashes) != relative_files:
                raise GovernanceError(f"{directory}: v2 checksum inventory is incomplete")
            for relative_file, expected_hash in expected_hashes.items():
                if not SHA256_RE.fullmatch(expected_hash):
                    raise GovernanceError(f"{directory}: invalid v2 checksum value")
                relative_path = (directory / relative_file).relative_to(root)
                actual_hash = sha256_bytes(
                    index_file_bytes(root, relative_path, "legacy archive file")
                )
                if actual_hash != expected_hash:
                    raise GovernanceError(
                        f"{directory / relative_file}: v2 legacy checksum mismatch"
                    )
        else:
            raise GovernanceError(
                f"{directory}: archive needs a frozen design manifest or explicit legacy review"
            )
        checked += 1
    return CheckResult("Experiment archives", f"{checked} named archives validated")


def _load_scan_allowlist(root: Path) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    content = load_json(root / SCAN_ALLOWLIST_PATH)
    absolute = {
        (entry["path"], entry["line_sha256"])
        for entry in content.get("absolute_path_lines", [])
    }
    sensitive = {
        (entry["path"], entry["line_sha256"])
        for entry in content.get("sensitive_lines", [])
    }
    return absolute, sensitive


def _is_probably_text(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:8192]
    except OSError as exc:
        raise GovernanceError(f"{path}: cannot read file: {exc}") from exc
    return b"\0" not in sample


def validate_sensitive_content(root: Path, paths: Sequence[Path]) -> CheckResult:
    allowed_absolute, allowed_sensitive = _load_scan_allowlist(root)
    used_absolute: set[tuple[str, str]] = set()
    used_sensitive: set[tuple[str, str]] = set()
    errors: list[str] = []
    scanned = 0
    for relative in paths:
        posix = relative.as_posix()
        if relative == SCAN_ALLOWLIST_PATH:
            continue
        if SENSITIVE_FILE_RE.search(posix) and not posix.endswith((".env.example", ".env.template")):
            errors.append(f"{posix}: sensitive filename is trackable")
        path = root / relative
        if path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            continue
        if relative.suffix.lower() in GOVERNED_TEXT_SUFFIXES:
            raw = path.read_bytes()
            if b"\0" in raw:
                errors.append(f"{posix}: governed text contains NUL bytes")
                continue
        elif not _is_probably_text(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            if relative.suffix.lower() in GOVERNED_TEXT_SUFFIXES:
                errors.append(f"{posix}: governed text is not UTF-8")
            continue
        scanned += 1
        for line_number, line in enumerate(lines, start=1):
            line_hash = sha256_bytes(line.encode("utf-8"))
            scan_absolute_path = posix not in {".gitignore", "experiments/.gitignore"}
            if scan_absolute_path and ABSOLUTE_PATH_RE.search(line):
                occurrence = (posix, line_hash)
                if occurrence in allowed_absolute:
                    used_absolute.add(occurrence)
                else:
                    errors.append(f"{posix}:{line_number}: personal absolute path")
            sensitive_match = PRIVATE_KEY_RE.search(line)
            assignment_match = SECRET_ASSIGNMENT_RE.search(line)
            unsafe_assignment = bool(
                assignment_match and not SAFE_SECRET_VALUE_RE.search(assignment_match.group(2))
            )
            if sensitive_match or unsafe_assignment:
                occurrence = (posix, line_hash)
                if occurrence in allowed_sensitive:
                    used_sensitive.add(occurrence)
                else:
                    errors.append(f"{posix}:{line_number}: possible credential or secret")
    for path, _ in sorted(allowed_absolute - used_absolute):
        errors.append(f"{path}: stale absolute-path allowlist entry")
    for path, _ in sorted(allowed_sensitive - used_sensitive):
        errors.append(f"{path}: stale sensitive-content allowlist entry")
    if errors:
        raise GovernanceError(
            "sensitive/absolute-path scan failed:\n"
            + "\n".join(f"  - {item}" for item in errors)
        )
    return CheckResult("Sensitive content", f"{scanned} text files scanned")


def validate_file_sizes(root: Path, paths: Sequence[Path]) -> CheckResult:
    errors: list[str] = []
    largest = 0
    for relative in paths:
        size = (root / relative).stat().st_size
        largest = max(largest, size)
        if size > MAX_TRACKED_FILE_BYTES:
            errors.append(
                f"{relative.as_posix()}: {size} bytes exceeds {MAX_TRACKED_FILE_BYTES}"
            )
    if errors:
        raise GovernanceError("large-file scan failed:\n" + "\n".join(f"  - {item}" for item in errors))
    return CheckResult(
        "File sizes",
        f"{len(paths)} trackable files; largest {largest} bytes",
    )


def validate_text_hygiene(root: Path, paths: Sequence[Path]) -> CheckResult:
    errors: list[str] = []
    checked = 0
    for relative in paths:
        path = root / relative
        if path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            continue
        if relative.suffix.lower() in GOVERNED_TEXT_SUFFIXES:
            if b"\0" in path.read_bytes():
                errors.append(f"{relative.as_posix()}: governed text contains NUL bytes")
                continue
        elif not _is_probably_text(path):
            continue
        try:
            raw = path.read_bytes()
            _reject_cr_bytes(path, raw)
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            if relative.suffix.lower() in GOVERNED_TEXT_SUFFIXES:
                errors.append(f"{relative.as_posix()}: governed text is not UTF-8")
            continue
        checked += 1
        for line_number, line in enumerate(content.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                if relative.suffix.lower() == ".md" and line.endswith("  ") and not line.endswith("   "):
                    continue
                errors.append(f"{relative.as_posix()}:{line_number}: trailing whitespace")
        if content and not content.endswith("\n"):
            posix = relative.as_posix()
            expected_legacy_hash = LEGACY_MISSING_FINAL_NEWLINE_SHA256.get(posix)
            if expected_legacy_hash != sha256_bytes(raw):
                errors.append(f"{posix}: missing final newline")
    if errors:
        raise GovernanceError("text hygiene failed:\n" + "\n".join(f"  - {item}" for item in errors))
    return CheckResult("Text hygiene", f"{checked} text files checked")


def validate_git_diff(root: Path) -> CheckResult:
    commands = [
        ["git", "-C", str(root), "diff", "--check", "--"],
        ["git", "-C", str(root), "diff", "--cached", "--check", "--"],
    ]
    for command in commands:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode:
            message = (completed.stdout + completed.stderr).strip()
            raise GovernanceError(f"{' '.join(command[3:])} failed:\n{message}")
    return CheckResult("Git diff", "working-tree and staged diff checks passed")


def run_repository_checks(root: Path) -> list[CheckResult]:
    paths = trackable_paths(root)
    if not paths:
        raise GovernanceError("repository has no trackable files")
    return [
        validate_path_safety(root, paths),
        validate_schema_documents(root, paths),
        validate_contract_references(root, paths),
        validate_markdown_links(root, paths),
        validate_active_e_registry(root),
        validate_experiment_archives(root, paths),
        validate_sensitive_content(root, paths),
        validate_file_sizes(root, paths),
        validate_text_hygiene(root, paths),
        validate_git_diff(root),
    ]
