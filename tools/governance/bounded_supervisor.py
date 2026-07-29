"""Run frozen experiment steps inside hard time and memory boundaries."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXECUTION_STATUSES = {
    "COMPLETED",
    "TIMED_OUT",
    "MEMORY_STOPPED",
    "INTERRUPTED",
    "INFRASTRUCTURE_FAILED",
    "PROTOCOL_INVALID",
}
EXECUTION_TYPES = {"smoke", "cost_probe", "capability", "full"}
REQUIRED_FIELDS = {
    "experiment_id",
    "research_question",
    "execution_type",
    "execution_authority",
    "implementation_commit",
    "data_allowlist",
    "data_denylist",
    "candidates",
    "row_schedule",
    "epochs",
    "seed",
    "max_workers",
    "per_step_timeout_s",
    "total_run_timeout_s",
    "minimum_available_ram",
    "checkpoint_interval_s",
    "allowed_outputs",
    "forbidden_actions",
    "stop_conditions",
    "next_step_safety_factor",
    "step_command",
}
REQUIRED_OUTPUTS = {
    "supervisor_events",
    "run_state",
    "step_stdout",
    "step_stderr",
}
REQUIRED_FORBIDDEN_ACTIONS = {
    "automatic_retry",
    "unapproved_configuration_change",
}
REQUIRED_STOP_CONDITIONS = {
    "per_step_timeout",
    "total_run_timeout",
    "minimum_available_ram",
}
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


class RunSpecError(ValueError):
    """The run must not start because its execution contract is invalid."""


class StepResultError(ValueError):
    """A completed child did not produce its declared atomic result."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reject_constant(value: str) -> None:
    raise RunSpecError(f"non-finite JSON constant is forbidden: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RunSpecError(f"duplicate RunSpec key: {key}")
        result[key] = value
    return result


def load_run_spec(path: Path) -> tuple[dict[str, Any], str, bytes]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunSpecError(f"RunSpec must be UTF-8 JSON-compatible YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise RunSpecError("RunSpec root must be an object")
    validate_run_spec(payload)
    return payload, digest, raw


def _positive_number(spec: dict[str, Any], field: str) -> float:
    value = spec[field]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RunSpecError(f"{field} must be a positive number")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise RunSpecError(f"{field} must be a positive finite number")
    return parsed


def _string_list(spec: dict[str, Any], field: str, *, nonempty: bool = True) -> list[str]:
    value = spec[field]
    if not isinstance(value, list) or (nonempty and not value):
        raise RunSpecError(f"{field} must be a{' non-empty' if nonempty else ''} list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RunSpecError(f"{field} must contain only non-empty strings")
    if len(value) != len(set(value)):
        raise RunSpecError(f"{field} must not contain duplicates")
    return value


def validate_run_spec(spec: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_FIELDS - spec.keys())
    if missing:
        raise RunSpecError(f"missing required RunSpec fields: {', '.join(missing)}")
    for field in ("experiment_id", "research_question", "execution_authority"):
        if not isinstance(spec[field], str) or not spec[field].strip():
            raise RunSpecError(f"{field} must be a non-empty string")
    if spec["execution_type"] not in EXECUTION_TYPES:
        raise RunSpecError(f"execution_type must be one of {sorted(EXECUTION_TYPES)}")
    if not isinstance(spec["implementation_commit"], str) or not HEX_40.fullmatch(
        spec["implementation_commit"]
    ):
        raise RunSpecError("implementation_commit must be lowercase 40-hex")

    allowlist = _string_list(spec, "data_allowlist")
    denylist = _string_list(spec, "data_denylist")
    overlap = sorted(set(allowlist) & set(denylist))
    if overlap:
        raise RunSpecError(f"data allow/deny lists overlap: {overlap}")
    _string_list(spec, "candidates")
    outputs = set(_string_list(spec, "allowed_outputs"))
    if not REQUIRED_OUTPUTS <= outputs:
        raise RunSpecError(
            f"allowed_outputs must include {sorted(REQUIRED_OUTPUTS)}"
        )
    forbidden = set(_string_list(spec, "forbidden_actions"))
    if not REQUIRED_FORBIDDEN_ACTIONS <= forbidden:
        raise RunSpecError(
            f"forbidden_actions must include {sorted(REQUIRED_FORBIDDEN_ACTIONS)}"
        )
    stops = set(_string_list(spec, "stop_conditions"))
    if not REQUIRED_STOP_CONDITIONS <= stops:
        raise RunSpecError(
            f"stop_conditions must include {sorted(REQUIRED_STOP_CONDITIONS)}"
        )

    rows = spec["row_schedule"]
    if (
        not isinstance(rows, list)
        or not rows
        or any(isinstance(row, bool) or not isinstance(row, int) or row <= 0 for row in rows)
    ):
        raise RunSpecError("row_schedule must contain positive integers")
    if rows != sorted(set(rows)):
        raise RunSpecError("row_schedule must be strictly increasing")
    for field in ("epochs", "max_workers"):
        value = spec[field]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise RunSpecError(f"{field} must be a positive integer")
    if isinstance(spec["seed"], bool) or not isinstance(spec["seed"], int):
        raise RunSpecError("seed must be an integer")
    if spec["max_workers"] != 1:
        raise RunSpecError("this supervisor supports max_workers=1 only")

    per_step = _positive_number(spec, "per_step_timeout_s")
    total = _positive_number(spec, "total_run_timeout_s")
    minimum_ram = spec["minimum_available_ram"]
    if (
        isinstance(minimum_ram, bool)
        or not isinstance(minimum_ram, int)
        or minimum_ram <= 0
    ):
        raise RunSpecError("minimum_available_ram must be a positive byte count")
    checkpoint = _positive_number(spec, "checkpoint_interval_s")
    safety = _positive_number(spec, "next_step_safety_factor")
    if total < per_step:
        raise RunSpecError("total_run_timeout_s must be >= per_step_timeout_s")
    if checkpoint > per_step:
        raise RunSpecError("checkpoint_interval_s must not exceed per_step_timeout_s")
    if safety < 2.0:
        raise RunSpecError("next_step_safety_factor must be >= 2.0")

    command = spec["step_command"]
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(item, str) or not item for item in command)
    ):
        raise RunSpecError("step_command must be a non-empty string argument array")
    joined = "\0".join(command)
    for placeholder in ("{candidate}", "{rows}"):
        if placeholder not in joined:
            raise RunSpecError(f"step_command must contain {placeholder}")

    parent_forbidden = spec.get("parent_forbidden_imports", [])
    if not isinstance(parent_forbidden, list) or any(
        not isinstance(name, str) or not name for name in parent_forbidden
    ):
        raise RunSpecError("parent_forbidden_imports must be a string list")

    result_contract = spec.get("step_result_contract")
    if result_contract is not None:
        if not isinstance(result_contract, dict):
            raise RunSpecError("step_result_contract must be an object")
        required_contract = {
            "filename",
            "probe_spec_sha256",
            "input_bits_by_candidate",
            "required_tmu_version",
        }
        missing_contract = sorted(required_contract - result_contract.keys())
        if missing_contract:
            raise RunSpecError(
                "step_result_contract missing fields: "
                + ", ".join(missing_contract)
            )
        filename = result_contract["filename"]
        if (
            not isinstance(filename, str)
            or not filename
            or Path(filename).name != filename
        ):
            raise RunSpecError("step result filename must be one safe basename")
        if not isinstance(result_contract["probe_spec_sha256"], str) or not HEX_64.fullmatch(
            result_contract["probe_spec_sha256"]
        ):
            raise RunSpecError("probe_spec_sha256 must be lowercase 64-hex")
        input_bits = result_contract["input_bits_by_candidate"]
        if not isinstance(input_bits, dict) or set(input_bits) != set(spec["candidates"]):
            raise RunSpecError(
                "input_bits_by_candidate must exactly cover declared candidates"
            )
        if any(
            isinstance(bits, bool) or not isinstance(bits, int) or bits <= 0
            for bits in input_bits.values()
        ):
            raise RunSpecError("input bit counts must be positive integers")
        if (
            not isinstance(result_contract["required_tmu_version"], str)
            or not result_contract["required_tmu_version"]
        ):
            raise RunSpecError("required_tmu_version must be a non-empty string")

    ordinary_limit = (120.0, 600.0)
    cost_limit = (300.0, 1200.0)
    limits = cost_limit if spec["execution_type"] == "cost_probe" else ordinary_limit
    if (per_step > limits[0] or total > limits[1]) and not (
        isinstance(spec.get("budget_exception_authority"), str)
        and spec["budget_exception_authority"].strip()
    ):
        raise RunSpecError(
            "budget exceeds the default; budget_exception_authority is required"
        )


def verify_repository_binding(repository_root: Path, implementation_commit: str) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if head != implementation_commit:
        raise RunSpecError(
            f"implementation commit mismatch: expected {implementation_commit}, got {head}"
        )
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if status:
        raise RunSpecError("implementation worktree must be clean")


def available_ram_bytes() -> int:
    if os.name == "nt":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise ctypes.WinError()
        return int(status.ullAvailPhys)
    page_size = os.sysconf("SC_PAGE_SIZE")
    available_pages = os.sysconf("SC_AVPHYS_PAGES")
    return int(page_size * available_pages)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


class EvidenceStore:
    def __init__(
        self,
        output_dir: Path,
        spec_bytes: bytes,
        spec_hash: str,
    ) -> None:
        if output_dir.exists() and any(output_dir.iterdir()):
            raise RunSpecError("output directory already contains evidence; retry is forbidden")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        self.events_dir = output_dir / "events"
        self.events_dir.mkdir()
        self.sequence = 0
        atomic_bytes(output_dir / "frozen_run_spec.yaml", spec_bytes)
        atomic_text(output_dir / "frozen_run_spec.sha256", f"{spec_hash}\n")

    def event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.sequence += 1
        event = {
            "sequence": self.sequence,
            "timestamp_utc": utc_now(),
            "event_type": event_type,
            **payload,
        }
        atomic_json(
            self.events_dir / f"{self.sequence:06d}-{event_type}.json",
            event,
        )
        return event

    def state(self, payload: dict[str, Any]) -> None:
        atomic_json(self.output_dir / "run_state.json", payload)


if os.name == "nt":
    from ctypes import wintypes

    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
    JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS = 1
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class _IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class _BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BasicLimitInformation),
            ("IoInfo", _IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class _BasicAccountingInformation(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_longlong),
            ("TotalKernelTime", ctypes.c_longlong),
            ("ThisPeriodTotalUserTime", ctypes.c_longlong),
            ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
            ("TotalPageFaultCount", wintypes.DWORD),
            ("TotalProcesses", wintypes.DWORD),
            ("ActiveProcesses", wintypes.DWORD),
            ("TotalTerminatedProcesses", wintypes.DWORD),
        ]

    _kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    _kernel32.SetInformationJobObject.restype = wintypes.BOOL
    _kernel32.AssignProcessToJobObject.argtypes = [
        wintypes.HANDLE,
        wintypes.HANDLE,
    ]
    _kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    _kernel32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.c_void_p,
    ]
    _kernel32.QueryInformationJobObject.restype = wintypes.BOOL
    _kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    _kernel32.TerminateJobObject.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL


class ProcessTree:
    """Bind one bootstrap and every descendant to one killable boundary."""

    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.handle: int | None = None
        if os.name == "nt":
            raw_handle = _kernel32.CreateJobObjectW(None, None)
            if not raw_handle:
                raise ctypes.WinError(ctypes.get_last_error())
            self.handle = int(raw_handle)
            limits = _ExtendedLimitInformation()
            limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            ok = _kernel32.SetInformationJobObject(
                self.handle,
                JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                ctypes.byref(limits),
                ctypes.sizeof(limits),
            )
            if not ok:
                _kernel32.CloseHandle(self.handle)
                raise ctypes.WinError(ctypes.get_last_error())

    def bind(self, process: subprocess.Popen[str]) -> None:
        self.process = process
        if os.name == "nt":
            assert self.handle is not None
            ok = _kernel32.AssignProcessToJobObject(
                self.handle,
                int(process._handle),  # type: ignore[attr-defined]
            )
            if not ok:
                process.kill()
                process.wait()
                raise ctypes.WinError(ctypes.get_last_error())

    def metrics(self) -> dict[str, int | None]:
        if os.name == "nt":
            assert self.handle is not None
            limits = _ExtendedLimitInformation()
            accounting = _BasicAccountingInformation()
            ok_limits = _kernel32.QueryInformationJobObject(
                self.handle,
                JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                ctypes.byref(limits),
                ctypes.sizeof(limits),
                None,
            )
            ok_accounting = _kernel32.QueryInformationJobObject(
                self.handle,
                JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS,
                ctypes.byref(accounting),
                ctypes.sizeof(accounting),
                None,
            )
            if not ok_limits or not ok_accounting:
                raise ctypes.WinError(ctypes.get_last_error())
            return {
                "peak_job_memory_bytes": int(limits.PeakJobMemoryUsed),
                "peak_process_memory_bytes": int(limits.PeakProcessMemoryUsed),
                "active_processes": int(accounting.ActiveProcesses),
                "job_cpu_time_s": (
                    int(accounting.TotalUserTime) + int(accounting.TotalKernelTime)
                )
                / 10_000_000,
            }
        active = int(self.process is not None and self.process.poll() is None)
        return {
            "peak_job_memory_bytes": None,
            "peak_process_memory_bytes": None,
            "active_processes": active,
            "job_cpu_time_s": None,
        }

    def terminate(self) -> None:
        if os.name == "nt":
            assert self.handle is not None
            if not _kernel32.TerminateJobObject(self.handle, 143):
                raise ctypes.WinError(ctypes.get_last_error())
        elif self.process is not None and self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGTERM)

    def close(self) -> None:
        if os.name == "nt" and self.handle is not None:
            _kernel32.CloseHandle(self.handle)
            self.handle = None


def expand_step_command(
    command: list[str],
    *,
    candidate: str,
    rows: int,
    epochs: int,
    seed: int,
    step_dir: Path,
    step_id: str,
    run_id: str,
    run_spec_path: Path,
    run_spec_sha256: str,
    implementation_commit: str,
    step_authority_path: Path,
    step_result_path: Path,
    probe_spec_sha256: str | None,
) -> list[str]:
    values = {
        "{python}": sys.executable,
        "{candidate}": candidate,
        "{rows}": str(rows),
        "{epochs}": str(epochs),
        "{seed}": str(seed),
        "{step_dir}": str(step_dir),
        "{step_id}": step_id,
        "{run_id}": run_id,
        "{run_spec_path}": str(run_spec_path),
        "{run_spec_sha256}": run_spec_sha256,
        "{implementation_commit}": implementation_commit,
        "{step_authority_path}": str(step_authority_path),
        "{step_result_path}": str(step_result_path),
        "{probe_spec_sha256}": probe_spec_sha256 or "",
    }
    expanded = []
    for argument in command:
        for placeholder, value in values.items():
            argument = argument.replace(placeholder, value)
        expanded.append(argument)
    return expanded


def _bootstrap(command_file: Path, go_file: Path) -> int:
    deadline = time.monotonic() + 30.0
    while not go_file.exists():
        if time.monotonic() >= deadline:
            return 125
        time.sleep(0.01)
    payload = json.loads(command_file.read_text(encoding="utf-8"))
    command = payload["command"]
    task = subprocess.Popen(command, shell=False)
    atomic_json(
        Path(payload["task_pid_file"]),
        {"task_pid": task.pid, "timestamp_utc": utc_now()},
    )
    return task.wait()


@dataclass
class StepResult:
    status: str
    reason: str
    wall_seconds: float
    returncode: int | None
    peak_job_memory_bytes: int | None
    task_pid: int | None
    child_result_sha256: str | None


def _read_task_pid(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        return int(json.loads(path.read_text(encoding="utf-8"))["task_pid"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StepResultError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise StepResultError(f"{label} root must be an object")
    return payload


def verify_step_result(
    *,
    spec: dict[str, Any],
    spec_hash: str,
    step_id: str,
    candidate: str,
    rows: int,
    task_pid: int | None,
    step_result_path: Path,
    authority_sha256: str,
) -> str | None:
    contract = spec.get("step_result_contract")
    if contract is None:
        return None
    if not step_result_path.is_file():
        raise StepResultError("declared child result is missing")
    first = step_result_path.read_bytes()
    time.sleep(0.01)
    second = step_result_path.read_bytes()
    if first != second:
        raise StepResultError("child result changed during supervisor verification")
    payload = _strict_json_bytes(first, "child result")
    expected = {
        "result_schema_version": "1.0",
        "run_id": spec["experiment_id"],
        "step_id": step_id,
        "candidate": candidate,
        "rows": rows,
        "input_shape": [
            rows,
            contract["input_bits_by_candidate"][candidate],
        ],
        "implementation_commit": spec["implementation_commit"],
        "run_spec_sha256": spec_hash,
        "probe_spec_sha256": contract["probe_spec_sha256"],
        "seed": spec["seed"],
        "epochs": spec["epochs"],
        "process_pid": task_pid,
        "terminal_status": "COMPLETED",
        "step_authority_sha256": authority_sha256,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise StepResultError(
                f"child result {key} mismatch: expected {value!r}, got {payload.get(key)!r}"
            )
    versions = payload.get("versions")
    if not isinstance(versions, dict):
        raise StepResultError("child result versions must be an object")
    for key in ("python", "numpy", "tmu"):
        if not isinstance(versions.get(key), str) or not versions[key]:
            raise StepResultError(f"child result is missing {key} version")
    if versions["tmu"] != contract["required_tmu_version"]:
        raise StepResultError(
            f"TMU version mismatch: expected {contract['required_tmu_version']}, "
            f"got {versions['tmu']}"
        )
    if payload.get("scientific_conclusion") is not None:
        raise StepResultError("child result must not contain a scientific conclusion")
    if payload.get("predictive_metrics_computed") is not False:
        raise StepResultError("child result must declare no predictive metrics")
    if payload.get("saved_model") is not False:
        raise StepResultError("child result must declare no saved model")
    temporary_files = list(step_result_path.parent.glob(f".{step_result_path.name}.*.tmp"))
    if temporary_files:
        raise StepResultError("atomic child result left temporary files behind")
    return hashlib.sha256(first).hexdigest()


def run_step(
    *,
    store: EvidenceStore,
    spec: dict[str, Any],
    spec_hash: str,
    candidate: str,
    rows: int,
    step_index: int,
    total_steps: int,
    run_deadline: float,
    repository_root: Path,
    interrupt_event: threading.Event | None,
) -> StepResult:
    step_id = f"{step_index:03d}-{candidate}-{rows}"
    step_dir = store.output_dir / "steps" / step_id
    step_dir.mkdir(parents=True)
    step_authority_path = step_dir / "step_authority.json"
    result_contract = spec.get("step_result_contract")
    result_filename = (
        result_contract["filename"]
        if isinstance(result_contract, dict)
        else "worker_result.json"
    )
    step_result_path = step_dir / result_filename
    command = expand_step_command(
        spec["step_command"],
        candidate=candidate,
        rows=rows,
        epochs=spec["epochs"],
        seed=spec["seed"],
        step_dir=step_dir,
        step_id=step_id,
        run_id=spec["experiment_id"],
        run_spec_path=store.output_dir / "frozen_run_spec.yaml",
        run_spec_sha256=spec_hash,
        implementation_commit=spec["implementation_commit"],
        step_authority_path=step_authority_path,
        step_result_path=step_result_path,
        probe_spec_sha256=(
            result_contract.get("probe_spec_sha256")
            if isinstance(result_contract, dict)
            else None
        ),
    )
    command_file = step_dir / "command.json"
    go_file = step_dir / "go.signal"
    task_pid_file = step_dir / "task_process.json"
    atomic_json(
        command_file,
        {"command": command, "task_pid_file": str(task_pid_file)},
    )

    stdout_path = step_dir / "stdout.log"
    stderr_path = step_dir / "stderr.log"
    tree = ProcessTree()
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    with stdout_path.open("w", encoding="utf-8", newline="\n") as stdout, stderr_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as stderr:
        bootstrap = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--_bootstrap-command-file",
                str(command_file),
                "--_go-file",
                str(go_file),
            ],
            cwd=repository_root,
            stdout=stdout,
            stderr=stderr,
            text=True,
            shell=False,
            creationflags=creationflags,
            start_new_session=os.name != "nt",
        )
        try:
            tree.bind(bootstrap)
            started = time.monotonic()
            step_deadline = started + float(spec["per_step_timeout_s"])
            authority = {
                "run_id": spec["experiment_id"],
                "step_id": step_id,
                "candidate": candidate,
                "rows": rows,
                "run_spec_sha256": spec_hash,
                "implementation_commit": spec["implementation_commit"],
                "supervisor_pid": os.getpid(),
                "bootstrap_pid": bootstrap.pid,
                "nonce": secrets.token_hex(32),
            }
            atomic_json(step_authority_path, authority)
            authority_sha256 = hashlib.sha256(
                step_authority_path.read_bytes()
            ).hexdigest()
            store.event(
                "step_started",
                {
                    "step_id": step_id,
                    "step_index": step_index,
                    "total_steps": total_steps,
                    "candidate": candidate,
                    "rows": rows,
                    "supervisor_pid": os.getpid(),
                    "bootstrap_pid": bootstrap.pid,
                    "spec_sha256": spec_hash,
                    "implementation_commit": spec["implementation_commit"],
                    "step_authority_sha256": authority_sha256,
                },
            )
            atomic_text(go_file, "go\n")

            pid_deadline = time.monotonic() + 2.0
            task_pid = _read_task_pid(task_pid_file)
            while task_pid is None and bootstrap.poll() is None and time.monotonic() < pid_deadline:
                time.sleep(0.01)
                task_pid = _read_task_pid(task_pid_file)
            print(
                f"step {step_index}/{total_steps}: candidate={candidate} rows={rows} "
                f"supervisor_pid={os.getpid()} bootstrap_pid={bootstrap.pid} "
                f"task_pid={task_pid}"
            )

            status = "INFRASTRUCTURE_FAILED"
            reason = "supervisor monitor did not establish a terminal state"
            returncode: int | None = None
            initial_available = available_ram_bytes()
            last_metrics = tree.metrics()
            store.event(
                "heartbeat",
                {
                    "step_id": step_id,
                    "candidate": candidate,
                    "rows": rows,
                    "elapsed_wall_seconds": time.monotonic() - started,
                    "available_ram_bytes": initial_available,
                    "task_pid": _read_task_pid(task_pid_file),
                    **last_metrics,
                },
            )
            heartbeat_due = started + float(spec["checkpoint_interval_s"])
            try:
                while True:
                    now = time.monotonic()
                    returncode = bootstrap.poll()
                    if returncode is not None:
                        if returncode == 0:
                            status = "COMPLETED"
                            reason = "step process exited successfully"
                        else:
                            status = "INFRASTRUCTURE_FAILED"
                            reason = f"step process exited with code {returncode}"
                        break
                    if interrupt_event is not None and interrupt_event.is_set():
                        status = "INTERRUPTED"
                        reason = "manual interrupt event"
                        tree.terminate()
                        break
                    available = available_ram_bytes()
                    if available < int(spec["minimum_available_ram"]):
                        status = "MEMORY_STOPPED"
                        reason = "available RAM fell below RunSpec minimum"
                        tree.terminate()
                        break
                    if now >= min(step_deadline, run_deadline):
                        status = "TIMED_OUT"
                        reason = (
                            "total run wall timeout"
                            if run_deadline <= step_deadline
                            else "per-step wall timeout"
                        )
                        tree.terminate()
                        break
                    if now >= heartbeat_due:
                        last_metrics = tree.metrics()
                        store.event(
                            "heartbeat",
                            {
                                "step_id": step_id,
                                "candidate": candidate,
                                "rows": rows,
                                "elapsed_wall_seconds": now - started,
                                "available_ram_bytes": available,
                                "task_pid": _read_task_pid(task_pid_file),
                                **last_metrics,
                            },
                        )
                        heartbeat_due = now + float(spec["checkpoint_interval_s"])
                    time.sleep(0.02)
            except KeyboardInterrupt:
                status = "INTERRUPTED"
                reason = "keyboard interrupt"
                tree.terminate()

            if bootstrap.poll() is None:
                try:
                    bootstrap.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    tree.terminate()
                    bootstrap.wait(timeout=5)
            returncode = bootstrap.returncode
            child_result_sha256 = None
            if status == "COMPLETED":
                try:
                    child_result_sha256 = verify_step_result(
                        spec=spec,
                        spec_hash=spec_hash,
                        step_id=step_id,
                        candidate=candidate,
                        rows=rows,
                        task_pid=_read_task_pid(task_pid_file),
                        step_result_path=step_result_path,
                        authority_sha256=authority_sha256,
                    )
                except StepResultError as exc:
                    status = "INFRASTRUCTURE_FAILED"
                    reason = f"child result verification failed: {exc}"
            try:
                last_metrics = tree.metrics()
            except OSError:
                pass
            wall_seconds = time.monotonic() - started
            result = StepResult(
                status=status,
                reason=reason,
                wall_seconds=wall_seconds,
                returncode=returncode,
                peak_job_memory_bytes=(
                    int(last_metrics["peak_job_memory_bytes"])
                    if last_metrics.get("peak_job_memory_bytes") is not None
                    else None
                ),
                task_pid=_read_task_pid(task_pid_file),
                child_result_sha256=child_result_sha256,
            )
            store.event(
                "step_terminal",
                {
                    "step_id": step_id,
                    "candidate": candidate,
                    "rows": rows,
                    "execution_status": result.status,
                    "reason": result.reason,
                    "wall_seconds": result.wall_seconds,
                    "returncode": result.returncode,
                    "peak_job_memory_bytes": result.peak_job_memory_bytes,
                    "task_pid": result.task_pid,
                    "child_result_sha256": result.child_result_sha256,
                    "child_result_file": (
                        result_filename
                        if result.child_result_sha256 is not None
                        else None
                    ),
                },
            )
            return result
        finally:
            if bootstrap.poll() is None:
                tree.terminate()
                try:
                    bootstrap.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    bootstrap.kill()
                    bootstrap.wait()
            tree.close()


def _run_state(
    *,
    spec: dict[str, Any],
    spec_hash: str,
    phase: str,
    execution_status: str | None,
    completed_steps: int,
    total_steps: int,
    reason: str | None,
) -> dict[str, Any]:
    return {
        "experiment_id": spec["experiment_id"],
        "phase": phase,
        "execution_status": execution_status,
        "scientific_conclusion": None,
        "completed_steps": completed_steps,
        "total_steps": total_steps,
        "reason": reason,
        "spec_sha256": spec_hash,
        "implementation_commit": spec["implementation_commit"],
        "updated_at_utc": utc_now(),
    }


def run_supervised(
    *,
    spec_path: Path,
    expected_spec_sha256: str,
    output_dir: Path,
    repository_root: Path,
    interrupt_event: threading.Event | None = None,
) -> dict[str, Any]:
    spec, spec_hash, spec_bytes = load_run_spec(spec_path)
    if spec_hash != expected_spec_sha256:
        raise RunSpecError(
            f"RunSpec hash mismatch: expected {expected_spec_sha256}, got {spec_hash}"
        )
    verify_repository_binding(repository_root, spec["implementation_commit"])
    forbidden_parent_imports = spec.get("parent_forbidden_imports", [])
    imported_forbidden = sorted(
        name
        for name in forbidden_parent_imports
        if name in sys.modules
        or any(module.startswith(f"{name}.") for module in sys.modules)
    )
    if imported_forbidden:
        raise RunSpecError(
            "forbidden modules are already imported in supervisor: "
            + ", ".join(imported_forbidden)
        )

    store = EvidenceStore(output_dir, spec_bytes, spec_hash)
    steps = [
        (candidate, rows)
        for candidate in spec["candidates"]
        for rows in spec["row_schedule"]
    ]
    total_steps = len(steps)
    run_started = time.monotonic()
    run_deadline = run_started + float(spec["total_run_timeout_s"])
    print(
        f"run budget: max_wall={spec['total_run_timeout_s']}s "
        f"max_steps={total_steps} max_workers={spec['max_workers']}"
    )
    print(
        f"spec_sha256={spec_hash} implementation_commit={spec['implementation_commit']} "
        f"supervisor_pid={os.getpid()}"
    )
    print(
        "next-step condition: safety-adjusted projection must fit both the "
        "per-step and remaining total budgets"
    )
    store.event(
        "run_started",
        {
            "experiment_id": spec["experiment_id"],
            "execution_type": spec["execution_type"],
            "maximum_wall_seconds": spec["total_run_timeout_s"],
            "maximum_steps": total_steps,
            "max_workers": spec["max_workers"],
            "supervisor_pid": os.getpid(),
            "spec_sha256": spec_hash,
            "implementation_commit": spec["implementation_commit"],
            "forbidden_parent_imports": forbidden_parent_imports,
            "forbidden_parent_imports_present": [],
        },
    )
    store.state(
        _run_state(
            spec=spec,
            spec_hash=spec_hash,
            phase="RUNNING",
            execution_status=None,
            completed_steps=0,
            total_steps=total_steps,
            reason=None,
        )
    )

    completed_steps = 0
    previous: tuple[str, int, float] | None = None
    final_status = "COMPLETED"
    final_reason = "all declared steps completed"
    for step_index, (candidate, rows) in enumerate(steps, start=1):
        now = time.monotonic()
        remaining = run_deadline - now
        if remaining <= 0:
            final_status = "TIMED_OUT"
            final_reason = "total run budget exhausted before next step"
            break
        if available_ram_bytes() < int(spec["minimum_available_ram"]):
            final_status = "MEMORY_STOPPED"
            final_reason = "available RAM below minimum before next step"
            break
        if previous is not None:
            previous_candidate, previous_rows, previous_wall = previous
            row_ratio = max(1.0, rows / previous_rows)
            projected = (
                previous_wall
                * row_ratio
                * float(spec["next_step_safety_factor"])
            )
            store.event(
                "next_step_projection",
                {
                    "candidate": candidate,
                    "rows": rows,
                    "basis_candidate": previous_candidate,
                    "basis_rows": previous_rows,
                    "basis_wall_seconds": previous_wall,
                    "safety_factor": spec["next_step_safety_factor"],
                    "projected_wall_seconds": projected,
                    "remaining_total_wall_seconds": remaining,
                },
            )
            if projected > float(spec["per_step_timeout_s"]) or projected > remaining:
                final_status = "TIMED_OUT"
                final_reason = "adaptive next-step projection exceeds remaining budget"
                store.event(
                    "adaptive_stop",
                    {
                        "candidate": candidate,
                        "rows": rows,
                        "projected_wall_seconds": projected,
                        "per_step_timeout_s": spec["per_step_timeout_s"],
                        "remaining_total_wall_seconds": remaining,
                    },
                )
                break

        try:
            result = run_step(
                store=store,
                spec=spec,
                spec_hash=spec_hash,
                candidate=candidate,
                rows=rows,
                step_index=step_index,
                total_steps=total_steps,
                run_deadline=run_deadline,
                repository_root=repository_root,
                interrupt_event=interrupt_event,
            )
        except Exception as exc:
            final_status = "INFRASTRUCTURE_FAILED"
            final_reason = f"supervisor step failure: {type(exc).__name__}: {exc}"
            store.event(
                "infrastructure_exception",
                {
                    "candidate": candidate,
                    "rows": rows,
                    "reason": final_reason,
                },
            )
            break
        if result.status != "COMPLETED":
            final_status = result.status
            final_reason = result.reason
            break
        completed_steps += 1
        previous = (candidate, rows, result.wall_seconds)
        store.state(
            _run_state(
                spec=spec,
                spec_hash=spec_hash,
                phase="RUNNING",
                execution_status=None,
                completed_steps=completed_steps,
                total_steps=total_steps,
                reason=None,
            )
        )

    if final_status not in EXECUTION_STATUSES:
        raise RuntimeError(f"invalid supervisor status: {final_status}")
    terminal = _run_state(
        spec=spec,
        spec_hash=spec_hash,
        phase="TERMINAL",
        execution_status=final_status,
        completed_steps=completed_steps,
        total_steps=total_steps,
        reason=final_reason,
    )
    terminal["total_wall_seconds"] = time.monotonic() - run_started
    store.event("run_terminal", terminal)
    store.state(terminal)
    print(
        f"run terminal: status={final_status} completed_steps={completed_steps}/"
        f"{total_steps} reason={final_reason}"
    )
    return terminal


def write_protocol_invalid(output_dir: Path, reason: str) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(
        output_dir / "run_state.json",
        {
            "phase": "TERMINAL",
            "execution_status": "PROTOCOL_INVALID",
            "scientific_conclusion": None,
            "reason": reason,
            "updated_at_utc": utc_now(),
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-spec", type=Path)
    parser.add_argument("--expected-spec-sha256")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--_bootstrap-command-file", type=Path)
    parser.add_argument("--_go-file", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args._bootstrap_command_file is not None:
        if args._go_file is None:
            return 125
        return _bootstrap(args._bootstrap_command_file, args._go_file)
    if (
        args.run_spec is None
        or args.expected_spec_sha256 is None
        or args.output_dir is None
    ):
        raise SystemExit(
            "--run-spec, --expected-spec-sha256 and --output-dir are required"
        )
    try:
        run_supervised(
            spec_path=args.run_spec.resolve(),
            expected_spec_sha256=args.expected_spec_sha256,
            output_dir=args.output_dir.resolve(),
            repository_root=args.repository_root.resolve(),
        )
    except RunSpecError as exc:
        write_protocol_invalid(args.output_dir.resolve(), str(exc))
        print(f"PROTOCOL_INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
