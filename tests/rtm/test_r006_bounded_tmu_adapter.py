from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.governance import bounded_supervisor
from tools.rtm import r006_tmu_step_worker as worker
from tools.rtm import run_r006_cost_probe as legacy_probe


ROOT = Path(__file__).resolve().parents[2]
PROBE_SPEC = ROOT / "docs" / "reviews" / "R006-probe-spec.json"


class R006BoundedAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def valid_worker_args(self) -> tuple[object, Path]:
        spec = {
            "experiment_id": "R006 synthetic adapter unit contract",
            "research_question": "Can one synthetic C8 step validate its contract?",
            "execution_type": "smoke",
            "execution_authority": "focused unit test only",
            "implementation_commit": self.commit,
            "data_allowlist": ["deterministic generated Boolean matrix only"],
            "data_denylist": ["REDD"],
            "candidates": ["C8"],
            "row_schedule": [256],
            "epochs": 1,
            "seed": 0,
            "max_workers": 1,
            "per_step_timeout_s": 120,
            "total_run_timeout_s": 300,
            "minimum_available_ram": 1,
            "checkpoint_interval_s": 10,
            "allowed_outputs": [
                "supervisor_events",
                "run_state",
                "step_stdout",
                "step_stderr",
            ],
            "forbidden_actions": [
                "automatic_retry",
                "unapproved_configuration_change",
            ],
            "stop_conditions": [
                "per_step_timeout",
                "total_run_timeout",
                "minimum_available_ram",
            ],
            "next_step_safety_factor": 2.0,
            "parent_forbidden_imports": ["tmu"],
            "step_result_contract": {
                "filename": "worker_result.json",
                "probe_spec_sha256": worker.EXPECTED_PROBE_SHA256,
                "input_bits_by_candidate": {"C8": 56},
                "required_tmu_version": "0.8.3",
            },
            "step_command": ["{python}", "worker", "{candidate}", "{rows}"],
        }
        spec_path = self.root / "run_spec.yaml"
        raw = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
        spec_path.write_bytes(raw)
        spec_hash = hashlib.sha256(raw).hexdigest()
        step_dir = self.root / "step"
        step_dir.mkdir(exist_ok=True)
        authority_path = step_dir / "step_authority.json"
        authority_path.write_text(
            json.dumps(
                {
                    "run_id": spec["experiment_id"],
                    "step_id": "001-C8-256",
                    "candidate": "C8",
                    "rows": 256,
                    "run_spec_sha256": spec_hash,
                    "implementation_commit": self.commit,
                    "supervisor_pid": 1,
                    "bootstrap_pid": os.getppid(),
                    "nonce": "a" * 64,
                }
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        args = worker.parse_args(
            [
                "--run-spec",
                str(spec_path),
                "--run-spec-sha256",
                spec_hash,
                "--probe-spec",
                str(PROBE_SPEC),
                "--probe-spec-sha256",
                worker.EXPECTED_PROBE_SHA256,
                "--implementation-commit",
                self.commit,
                "--run-id",
                spec["experiment_id"],
                "--step-id",
                "001-C8-256",
                "--candidate",
                "C8",
                "--rows",
                "256",
                "--seed",
                "0",
                "--data-mode",
                "synthetic",
                "--step-authority",
                str(authority_path),
                "--output",
                str(step_dir / "worker_result.json"),
            ]
        )
        return args, step_dir

    def test_parent_and_importable_worker_do_not_import_tmu(self) -> None:
        self.assertNotIn("tmu", bounded_supervisor.sys.modules)
        self.assertFalse(
            any(name == "tmu" or name.startswith("tmu.") for name in sys.modules)
        )

    def test_worker_requires_a_valid_runspec_before_tmu(self) -> None:
        args, step_dir = self.valid_worker_args()
        args.run_spec = self.root / "missing.yaml"
        with mock.patch.object(worker, "execute_tmu_step") as execute:
            with self.assertRaises(OSError):
                worker.run_worker(args, ROOT)
        execute.assert_not_called()
        self.assertFalse((step_dir / "worker_result.json").exists())

    def test_worker_rejects_repeated_candidate_or_rows_arguments(self) -> None:
        args, _ = self.valid_worker_args()
        base = [
            "--run-spec",
            str(args.run_spec),
            "--run-spec-sha256",
            args.run_spec_sha256,
            "--probe-spec",
            str(args.probe_spec),
            "--probe-spec-sha256",
            args.probe_spec_sha256,
            "--implementation-commit",
            args.implementation_commit,
            "--run-id",
            args.run_id,
            "--step-id",
            args.step_id,
            "--candidate",
            "C8",
            "--rows",
            "256",
            "--seed",
            "0",
            "--data-mode",
            "synthetic",
            "--step-authority",
            str(args.step_authority),
            "--output",
            str(args.output),
        ]
        for duplicate in (["--candidate", "C11"], ["--rows", "512"]):
            with self.subTest(duplicate=duplicate), self.assertRaises(SystemExit):
                worker.parse_args(base + duplicate)

    def test_worker_rejects_hash_and_commit_mismatch(self) -> None:
        for field, value in (
            ("run_spec_sha256", "0" * 64),
            ("probe_spec_sha256", "0" * 64),
            ("implementation_commit", "0" * 40),
        ):
            args, _ = self.valid_worker_args()
            setattr(args, field, value)
            with self.subTest(field=field), self.assertRaises(
                worker.WorkerContractError
            ):
                worker.verify_worker_contract(args, ROOT)

    def test_one_worker_call_has_one_shape_and_atomic_result(self) -> None:
        args, step_dir = self.valid_worker_args()
        with mock.patch.object(worker, "execute_tmu_step", return_value=0.01):
            with mock.patch.object(
                worker.importlib.metadata, "version", return_value="0.8.3"
            ):
                result = worker.run_worker(args, ROOT)
        self.assertEqual(result["input_shape"], [256, 56])
        self.assertEqual(result["terminal_status"], "COMPLETED")
        self.assertIsNone(result["scientific_conclusion"])
        self.assertFalse(result["predictive_metrics_computed"])
        self.assertTrue((step_dir / "worker_result.json").is_file())
        self.assertFalse(list(step_dir.glob(".worker_result.json.*.tmp")))

    def test_legacy_multistep_cli_fails_closed(self) -> None:
        with self.assertRaises(legacy_probe.UnsupervisedExecutionDenied):
            legacy_probe.main()
        with self.assertRaises(legacy_probe.UnsupervisedExecutionDenied):
            legacy_probe.model_factory()

    def test_frozen_shapes_and_model_configuration_are_unchanged(self) -> None:
        self.assertEqual(worker.EXPECTED_INPUT_BITS, {"C8": 56, "C11": 74})
        self.assertEqual(worker.EXPECTED_MODEL["number_of_clauses"], 200)
        self.assertEqual(worker.EXPECTED_MODEL["T"], 200)
        self.assertEqual(worker.EXPECTED_MODEL["s"], 3.0)
        self.assertEqual(worker.EXPECTED_MODEL["platform"], "CPU")
        self.assertFalse(worker.EXPECTED_MODEL["weighted_clauses"])
        self.assertEqual(worker.EXPECTED_MODEL["seed"], 0)


if __name__ == "__main__":
    unittest.main()
