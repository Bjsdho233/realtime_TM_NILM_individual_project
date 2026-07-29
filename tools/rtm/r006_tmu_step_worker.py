"""Execute exactly one supervised synthetic R006 TMU integration step."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from tools.governance.bounded_supervisor import atomic_json, load_run_spec


EXPECTED_PROBE_SHA256 = (
    "43636376d2f598052c1fbbdc2b1cd4b1381bd60ca8a392df4603c700eb7dfc89"
)
EXPECTED_TMU_VERSION = "0.8.3"
EXPECTED_INPUT_BITS = {"C8": 56, "C11": 74}
EXPECTED_MODEL = {
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


class WorkerContractError(ValueError):
    """The worker was not launched under its exact supervised contract."""


class SingleValue(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be supplied exactly once")
        setattr(namespace, self.dest, values)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-spec", type=Path, required=True, action=SingleValue)
    parser.add_argument(
        "--run-spec-sha256", required=True, action=SingleValue
    )
    parser.add_argument("--probe-spec", type=Path, required=True, action=SingleValue)
    parser.add_argument(
        "--probe-spec-sha256", required=True, action=SingleValue
    )
    parser.add_argument(
        "--implementation-commit", required=True, action=SingleValue
    )
    parser.add_argument("--run-id", required=True, action=SingleValue)
    parser.add_argument("--step-id", required=True, action=SingleValue)
    parser.add_argument(
        "--candidate",
        choices=tuple(EXPECTED_INPUT_BITS),
        required=True,
        action=SingleValue,
    )
    parser.add_argument("--rows", type=int, required=True, action=SingleValue)
    parser.add_argument("--seed", type=int, required=True, action=SingleValue)
    parser.add_argument(
        "--data-mode",
        choices=("synthetic",),
        required=True,
        action=SingleValue,
    )
    parser.add_argument(
        "--step-authority", type=Path, required=True, action=SingleValue
    )
    parser.add_argument("--output", type=Path, required=True, action=SingleValue)
    return parser.parse_args(argv)


def read_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkerContractError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkerContractError(f"{label} root must be an object")
    return payload, raw


def verify_probe_spec(path: Path, expected_hash: str) -> dict[str, Any]:
    if expected_hash != EXPECTED_PROBE_SHA256:
        raise WorkerContractError("probe-spec hash is not the frozen R006 hash")
    if sha256_file(path) != expected_hash:
        raise WorkerContractError("probe-spec bytes do not match the frozen hash")
    probe, _ = read_object(path, "probe spec")
    for candidate, bits in EXPECTED_INPUT_BITS.items():
        actual = probe.get("candidates", {}).get(candidate, {}).get("boolean_bit_count")
        if actual != bits:
            raise WorkerContractError(
                f"{candidate} Boolean input count mismatch: {actual}"
            )
    model = probe.get("model")
    if not isinstance(model, dict):
        raise WorkerContractError("probe spec model is missing")
    for key, value in EXPECTED_MODEL.items():
        if model.get(key) != value:
            raise WorkerContractError(
                f"probe model {key} mismatch: expected {value!r}, got {model.get(key)!r}"
            )
    if model.get("epochs_per_fresh_model") != 1 or model.get("shuffle") is not True:
        raise WorkerContractError("probe model must use one shuffled epoch")
    return probe


def verify_worker_contract(
    args: argparse.Namespace,
    repository_root: Path,
) -> tuple[dict[str, Any], str]:
    spec, spec_hash, _ = load_run_spec(args.run_spec)
    if spec_hash != args.run_spec_sha256:
        raise WorkerContractError("RunSpec hash mismatch")
    if spec["implementation_commit"] != args.implementation_commit:
        raise WorkerContractError("RunSpec implementation commit mismatch")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if head != args.implementation_commit:
        raise WorkerContractError("worker HEAD does not match implementation commit")
    if spec["experiment_id"] != args.run_id:
        raise WorkerContractError("run ID mismatch")
    if args.candidate not in spec["candidates"]:
        raise WorkerContractError("candidate is not declared by RunSpec")
    if args.rows not in spec["row_schedule"]:
        raise WorkerContractError("row count is not declared by RunSpec")
    if spec["epochs"] != 1 or spec["seed"] != args.seed or args.seed != 0:
        raise WorkerContractError("synthetic integration requires one epoch and seed 0")
    if spec["max_workers"] != 1 or spec["execution_type"] != "smoke":
        raise WorkerContractError("synthetic integration requires serial smoke execution")
    if "deterministic generated Boolean matrix only" not in spec["data_allowlist"]:
        raise WorkerContractError("synthetic data allowlist is missing")
    if "REDD" not in spec["data_denylist"]:
        raise WorkerContractError("REDD must be explicitly denied")
    if "tmu" not in spec.get("parent_forbidden_imports", []):
        raise WorkerContractError("RunSpec must forbid TMU import in the parent")
    contract = spec.get("step_result_contract")
    if not isinstance(contract, dict):
        raise WorkerContractError("step result contract is missing")
    if contract.get("probe_spec_sha256") != args.probe_spec_sha256:
        raise WorkerContractError("result contract probe hash mismatch")
    if contract.get("input_bits_by_candidate", {}).get(args.candidate) != (
        EXPECTED_INPUT_BITS[args.candidate]
    ):
        raise WorkerContractError("result contract input shape mismatch")
    if contract.get("required_tmu_version") != EXPECTED_TMU_VERSION:
        raise WorkerContractError("result contract TMU version mismatch")
    if args.output.parent != args.step_authority.parent:
        raise WorkerContractError("output and step authority must share one step directory")
    if args.output.name != contract.get("filename"):
        raise WorkerContractError("output filename does not match result contract")

    authority, authority_raw = read_object(args.step_authority, "step authority")
    expected_authority = {
        "run_id": args.run_id,
        "step_id": args.step_id,
        "candidate": args.candidate,
        "rows": args.rows,
        "run_spec_sha256": args.run_spec_sha256,
        "implementation_commit": args.implementation_commit,
        "bootstrap_pid": os.getppid(),
    }
    for key, value in expected_authority.items():
        if authority.get(key) != value:
            raise WorkerContractError(
                f"step authority {key} mismatch: expected {value!r}, "
                f"got {authority.get(key)!r}"
            )
    nonce = authority.get("nonce")
    if not isinstance(nonce, str) or len(nonce) != 64:
        raise WorkerContractError("step authority nonce is invalid")
    verify_probe_spec(args.probe_spec, args.probe_spec_sha256)
    return spec, hashlib.sha256(authority_raw).hexdigest()


def deterministic_synthetic_data(
    candidate: str,
    rows: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, str]:
    bits = EXPECTED_INPUT_BITS[candidate]
    candidate_offset = 8 if candidate == "C8" else 11
    rng = np.random.RandomState(seed + candidate_offset)
    inputs = rng.randint(0, 2, size=(rows, bits)).astype(np.uint32)
    weights = (np.arange(bits, dtype=np.float64) % 7.0) + 1.0
    targets = inputs.astype(np.float64) @ weights
    targets = targets / weights.sum() * 100.0
    if not np.isfinite(inputs).all() or not np.isfinite(targets).all():
        raise WorkerContractError("synthetic data must be finite")
    if float(targets.min()) == float(targets.max()):
        raise WorkerContractError("synthetic targets must have a non-zero range")
    digest = hashlib.sha256()
    digest.update(inputs.tobytes(order="C"))
    digest.update(targets.tobytes(order="C"))
    return inputs, targets, digest.hexdigest()


def execute_tmu_step(inputs: np.ndarray, targets: np.ndarray) -> float:
    from tmu.models.regression.vanilla_regressor import TMRegressor

    if importlib.metadata.version("tmu") != EXPECTED_TMU_VERSION:
        raise WorkerContractError(
            f"TMU {EXPECTED_TMU_VERSION} is required for the integration smoke"
        )
    model = TMRegressor(**EXPECTED_MODEL)
    started = time.perf_counter()
    model.fit(inputs, targets, shuffle=True)
    fit_wall_seconds = time.perf_counter() - started
    del model
    return fit_wall_seconds


def run_worker(args: argparse.Namespace, repository_root: Path) -> dict[str, Any]:
    _, authority_sha256 = verify_worker_contract(args, repository_root)
    inputs, targets, data_sha256 = deterministic_synthetic_data(
        args.candidate, args.rows, args.seed
    )
    fit_wall_seconds = execute_tmu_step(inputs, targets)
    versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "tmu": importlib.metadata.version("tmu"),
    }
    result: dict[str, Any] = {
        "result_schema_version": "1.0",
        "run_id": args.run_id,
        "step_id": args.step_id,
        "candidate": args.candidate,
        "rows": args.rows,
        "input_shape": [args.rows, EXPECTED_INPUT_BITS[args.candidate]],
        "implementation_commit": args.implementation_commit,
        "run_spec_sha256": args.run_spec_sha256,
        "probe_spec_sha256": args.probe_spec_sha256,
        "seed": args.seed,
        "epochs": 1,
        "process_pid": os.getpid(),
        "supervised_parent_pid": os.getppid(),
        "terminal_status": "COMPLETED",
        "step_authority_sha256": authority_sha256,
        "versions": versions,
        "model": {
            **EXPECTED_MODEL,
            "implementation": "TMRegressor",
            "tmu_version": EXPECTED_TMU_VERSION,
            "epochs": 1,
            "weighted": False,
        },
        "synthetic_data_sha256": data_sha256,
        "fit_wall_seconds": fit_wall_seconds,
        "evidence_scope": "synthetic bounded-supervisor integration only",
        "scientific_conclusion": None,
        "predictive_metrics_computed": False,
        "saved_model": False,
    }
    atomic_json(args.output, result)
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        repository_root = Path.cwd().resolve()
        run_worker(args, repository_root)
    except (WorkerContractError, OSError, subprocess.SubprocessError) as exc:
        print(f"WORKER_CONTRACT_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
