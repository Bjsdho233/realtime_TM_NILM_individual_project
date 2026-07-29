"""Small deterministic processes used only to test the bounded supervisor."""

from __future__ import annotations

import argparse
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
        choices=("quick", "hang", "crash", "spawn_child", "child_hang"),
        required=True,
    )
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--step-dir", type=Path, required=True)
    return parser.parse_args()


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
