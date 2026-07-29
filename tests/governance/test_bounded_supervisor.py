from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from tools.governance.bounded_supervisor import (
    REQUIRED_FIELDS,
    RunSpecError,
    load_run_spec,
    run_supervised,
)


ROOT = Path(__file__).resolve().parents[2]
FAKE_TASK = ROOT / "tests" / "fixtures" / "supervisor_fake_task.py"
RUN_SPEC_TEMPLATE = ROOT / "docs" / "templates" / "EXPERIMENT_RUN_SPEC.yaml"


def process_is_active(pid: int) -> bool:
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True
    synchronize = 0x00100000
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel32.WaitForSingleObject.restype = ctypes.c_ulong
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel32.OpenProcess(synchronize, False, pid)
    if not handle:
        return False
    try:
        return kernel32.WaitForSingleObject(handle, 0) == 0x00000102
    finally:
        kernel32.CloseHandle(handle)


class BoundedSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repo"
        self.repository.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repository, check=True)
        subprocess.run(
            ["git", "config", "core.autocrlf", "false"],
            cwd=self.repository,
            check=True,
        )
        (self.repository / "anchor.txt").write_text(
            "supervisor test anchor\n", encoding="utf-8", newline="\n"
        )
        subprocess.run(["git", "add", "anchor.txt"], cwd=self.repository, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Supervisor Test",
                "-c",
                "user.email=supervisor@example.invalid",
                "commit",
                "-q",
                "-m",
                "test anchor",
            ],
            cwd=self.repository,
            check=True,
        )
        self.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_spec(
        self,
        mode: str,
        *,
        per_step_timeout: float = 1.0,
        total_timeout: float = 3.0,
    ) -> tuple[Path, str]:
        spec = {
            "experiment_id": f"TEST — {mode}",
            "research_question": "Does the supervisor preserve the declared boundary?",
            "execution_type": "smoke",
            "execution_authority": "unit-test fake task only",
            "implementation_commit": self.commit,
            "data_allowlist": ["synthetic fake task"],
            "data_denylist": ["REDD", "TMU"],
            "candidates": [mode],
            "row_schedule": [1],
            "epochs": 1,
            "seed": 0,
            "max_workers": 1,
            "per_step_timeout_s": per_step_timeout,
            "total_run_timeout_s": total_timeout,
            "minimum_available_ram": 1,
            "checkpoint_interval_s": 0.05,
            "allowed_outputs": [
                "supervisor_events",
                "run_state",
                "step_stdout",
                "step_stderr",
                "declared_step_outputs",
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
            "step_command": [
                "{python}",
                str(FAKE_TASK),
                "--mode",
                "{candidate}",
                "--rows",
                "{rows}",
                "--step-dir",
                "{step_dir}",
            ],
        }
        path = self.root / f"{mode}.yaml"
        raw = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
        path.write_bytes(raw)
        return path, hashlib.sha256(raw).hexdigest()

    def run_mode(
        self,
        mode: str,
        *,
        interrupt_event: threading.Event | None = None,
    ) -> tuple[dict[str, object], Path]:
        spec_path, digest = self.make_spec(mode)
        output = self.root / f"output-{mode}"
        terminal = run_supervised(
            spec_path=spec_path,
            expected_spec_sha256=digest,
            output_dir=output,
            repository_root=self.repository,
            interrupt_event=interrupt_event,
        )
        return terminal, output

    def test_repository_template_is_machine_readable_and_complete(self) -> None:
        template = json.loads(RUN_SPEC_TEMPLATE.read_text(encoding="utf-8"))
        self.assertTrue(REQUIRED_FIELDS <= template.keys())
        self.assertEqual(template["max_workers"], 1)
        self.assertGreaterEqual(template["next_step_safety_factor"], 2.0)

    def test_quick_task_completes_with_incremental_evidence(self) -> None:
        terminal, output = self.run_mode("quick")
        self.assertEqual(terminal["execution_status"], "COMPLETED")
        self.assertEqual(terminal["scientific_conclusion"], None)
        events = sorted((output / "events").glob("*.json"))
        names = [path.name for path in events]
        self.assertTrue(any("step_started" in name for name in names))
        self.assertTrue(any("heartbeat" in name for name in names))
        self.assertTrue(any("step_terminal" in name for name in names))
        self.assertTrue(any("run_terminal" in name for name in names))
        frozen = output / "frozen_run_spec.yaml"
        self.assertEqual(
            hashlib.sha256(frozen.read_bytes()).hexdigest(),
            (output / "frozen_run_spec.sha256").read_text(encoding="utf-8").strip(),
        )

    def test_hanging_task_hits_hard_timeout(self) -> None:
        terminal, output = self.run_mode("hang")
        self.assertEqual(terminal["execution_status"], "TIMED_OUT")
        self.assertLess(float(terminal["total_wall_seconds"]), 2.5)
        step_terminal = next((output / "events").glob("*-step_terminal.json"))
        step = json.loads(step_terminal.read_text(encoding="utf-8"))
        self.assertEqual(step["reason"], "per-step wall timeout")

    def test_crash_is_infrastructure_failed_not_scientific_result(self) -> None:
        terminal, _ = self.run_mode("crash")
        self.assertEqual(terminal["execution_status"], "INFRASTRUCTURE_FAILED")
        self.assertIsNone(terminal["scientific_conclusion"])

    def test_descendant_process_is_killed_with_timed_out_tree(self) -> None:
        terminal, output = self.run_mode("spawn_child")
        self.assertEqual(terminal["execution_status"], "TIMED_OUT")
        descendant_record = next(
            (output / "steps").glob("*/descendant_pid.json")
        )
        descendant_pid = int(
            json.loads(descendant_record.read_text(encoding="utf-8"))["pid"]
        )
        time.sleep(0.1)
        self.assertFalse(process_is_active(descendant_pid))

    def test_manual_interrupt_preserves_terminal_evidence(self) -> None:
        interrupt_event = threading.Event()
        timer = threading.Timer(0.15, interrupt_event.set)
        timer.start()
        try:
            terminal, output = self.run_mode(
                "hang", interrupt_event=interrupt_event
            )
        finally:
            timer.cancel()
        self.assertEqual(terminal["execution_status"], "INTERRUPTED")
        self.assertTrue(any((output / "events").glob("*-step_terminal.json")))
        self.assertTrue(any((output / "events").glob("*-run_terminal.json")))

    def test_adaptive_gate_refuses_next_step_without_retry(self) -> None:
        spec_path, _ = self.make_spec("quick")
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        payload["row_schedule"] = [1, 2]
        payload["next_step_safety_factor"] = 100.0
        raw = (json.dumps(payload) + "\n").encode("utf-8")
        spec_path.write_bytes(raw)
        output = self.root / "adaptive-output"
        terminal = run_supervised(
            spec_path=spec_path,
            expected_spec_sha256=hashlib.sha256(raw).hexdigest(),
            output_dir=output,
            repository_root=self.repository,
        )
        self.assertEqual(terminal["execution_status"], "TIMED_OUT")
        self.assertEqual(terminal["completed_steps"], 1)
        self.assertEqual(len(list((output / "steps").iterdir())), 1)
        self.assertTrue(any((output / "events").glob("*-adaptive_stop.json")))

    def test_memory_gate_stops_before_child_launch(self) -> None:
        spec_path, _ = self.make_spec("quick")
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        payload["minimum_available_ram"] = (1 << 63) - 1
        raw = (json.dumps(payload) + "\n").encode("utf-8")
        spec_path.write_bytes(raw)
        output = self.root / "memory-output"
        terminal = run_supervised(
            spec_path=spec_path,
            expected_spec_sha256=hashlib.sha256(raw).hexdigest(),
            output_dir=output,
            repository_root=self.repository,
        )
        self.assertEqual(terminal["execution_status"], "MEMORY_STOPPED")
        self.assertEqual(terminal["completed_steps"], 0)
        self.assertFalse((output / "steps").exists())

    def test_missing_field_is_protocol_invalid_before_launch(self) -> None:
        spec_path, _ = self.make_spec("quick")
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        del payload["per_step_timeout_s"]
        spec_path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
        with self.assertRaises(RunSpecError):
            load_run_spec(spec_path)

    def test_commit_mismatch_refuses_before_output_or_child(self) -> None:
        spec_path, _ = self.make_spec("quick")
        payload = json.loads(spec_path.read_text(encoding="utf-8"))
        payload["implementation_commit"] = "0" * 40
        raw = (json.dumps(payload) + "\n").encode("utf-8")
        spec_path.write_bytes(raw)
        output = self.root / "mismatch-output"
        with self.assertRaises(RunSpecError):
            run_supervised(
                spec_path=spec_path,
                expected_spec_sha256=hashlib.sha256(raw).hexdigest(),
                output_dir=output,
                repository_root=self.repository,
            )
        self.assertFalse(output.exists())

    def test_hash_mismatch_refuses_before_output_or_child(self) -> None:
        spec_path, _ = self.make_spec("quick")
        output = self.root / "hash-mismatch-output"
        with self.assertRaises(RunSpecError):
            run_supervised(
                spec_path=spec_path,
                expected_spec_sha256="0" * 64,
                output_dir=output,
                repository_root=self.repository,
            )
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
