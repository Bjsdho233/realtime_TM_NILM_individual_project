#!/usr/bin/env python3
"""Run the repository's complete local governance check."""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

from repo_governance import GovernanceError, repository_root, run_repository_checks


def discover_tests(root: Path) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    return loader.discover(
        start_dir=str(root / "tests"),
        pattern="test_*.py",
        top_level_dir=str(root),
    )


def run_tests(root: Path, verbosity: int) -> bool:
    suite = discover_tests(root)
    count = suite.countTestCases()
    if count == 0:
        raise GovernanceError("test discovery returned zero tests")
    print(f"[RUN] Unit tests ({count} discovered)")
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(suite)
    return result.wasSuccessful()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet-tests",
        action="store_true",
        help="show one character per test instead of individual test names",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = repository_root()
        checks = run_repository_checks(root)
        for check in checks:
            print(f"[PASS] {check.name}: {check.details}")
        if not run_tests(root, 1 if args.quiet_tests else 2):
            return 1
    except GovernanceError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    print("[PASS] Repository check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
