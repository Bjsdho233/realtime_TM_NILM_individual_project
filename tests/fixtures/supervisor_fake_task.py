"""Small deterministic processes used only to test the bounded supervisor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=(
            "quick",
            "hang",
            "crash",
            "spawn_child",
            "child_hang",
            "contract_complete",
            "missing_result",
            "malformed_result",
        ),
        required=True,
    )
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--step-dir", type=Path, required=True)
    parser.add_argument("--result-path", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--step-id")
    parser.add_argument("--candidate")
    parser.add_argument("--implementation-commit")
    parser.add_argument("--run-spec-sha256")
    parser.add_argument("--probe-spec-sha256")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--input-bits", type=int)
    parser.add_argument("--step-authority", type=Path)
    return parser.parse_args()


def atomic_result(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def main() -> int:
    args = parse_args()
    args.step_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "quick":
        (args.step_dir / "fake_result.json").write_text(
            json.dumps({"rows": args.rows, "pid": os.getpid()}) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return 0
    if args.mode == "crash":
        return 7
    if args.mode in {"contract_complete", "missing_result", "malformed_result"}:
        if args.mode == "missing_result":
            return 0
        assert args.result_path is not None
        if args.mode == "malformed_result":
            args.result_path.write_text("{broken", encoding="utf-8")
            return 0
        assert args.step_authority is not None
        atomic_result(
            args.result_path,
            {
                "result_schema_version": "1.0",
                "run_id": args.run_id,
                "step_id": args.step_id,
                "candidate": args.candidate,
                "rows": args.rows,
                "input_shape": [args.rows, args.input_bits],
                "implementation_commit": args.implementation_commit,
                "run_spec_sha256": args.run_spec_sha256,
                "probe_spec_sha256": args.probe_spec_sha256,
                "seed": args.seed,
                "epochs": args.epochs,
                "process_pid": os.getpid(),
                "terminal_status": "COMPLETED",
                "step_authority_sha256": hashlib.sha256(
                    args.step_authority.read_bytes()
                ).hexdigest(),
                "versions": {
                    "python": "fake",
                    "numpy": "fake",
                    "tmu": "0.8.3",
                },
                "scientific_conclusion": None,
                "predictive_metrics_computed": False,
                "saved_model": False,
            },
        )
        return 0
    if args.mode == "spawn_child":
        time.sleep(0.1)
        child = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--mode",
                "child_hang",
                "--rows",
                str(args.rows),
                "--step-dir",
                str(args.step_dir),
            ]
        )
        (args.step_dir / "descendant_pid.json").write_text(
            json.dumps({"pid": child.pid}) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    while True:
        time.sleep(0.05)


if __name__ == "__main__":
    raise SystemExit(main())
