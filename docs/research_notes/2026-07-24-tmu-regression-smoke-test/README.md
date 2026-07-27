# TMU Regression Synthetic Smoke Test — Historical Archive

**Original work date:** 2026-07-24

**Archive date:** 2026-07-27

**Classification:** `inconclusive`

**Evidence scope:** Windows CPU environment and interface feasibility only

**Formal experiment:** no

**REDD accessed:** no

**Rerun during archival:** no

## Purpose and boundary

This directory preserves the recoverable materials from a project-external,
Windows-native TMU regression smoke-test environment. The intended check was
limited to importing `StandardBinarizer` and `TMRegressor`, fitting Boolean
thresholds on the training split only, transforming a held-out synthetic test
split, calling CPU `fit` and `predict` for vanilla and integer-weighted rTM, and
checking prediction shape and finiteness.

This was not a NILM experiment, did not use REDD, did not compare a formal
method, and cannot change Protocol R or any accepted project decision.

## Recoverable design and configuration

The preserved script deterministically constructs 160 synthetic samples with
three continuous inputs and a multi-level numerical target. It uses random seed
`20260724` for data generation, seed `311` for a fixed 120/40 train/test split,
and fits `StandardBinarizer(max_bits_per_feature=8)` on the 120 training samples
only. The two models differ only in `weighted_clauses=False` and
`weighted_clauses=True`.

Both use 64 clauses, `T=40`, `s=3.0`, CPU platform,
`max_included_literals=16`, seed `20260724`, and three explicit one-epoch
`fit` calls.

The isolated uv project pinned Python `3.11`, `numpy==1.26.4`, and
`tmu==0.8.3`. The complete resolved environment is preserved in `uv.lock`,
`pip-freeze.txt`, and `uv-tree.txt`. The lock identifies the public PyPI
registry as the package source. The virtual environment itself is intentionally
not archived.

## Evidence assessment

The script, dependency declaration, lock, Python pin, dependency tree, and
freeze were recovered byte-for-byte from the external bootstrap project. No
captured stdout, structured result file, or raw prediction array was found.

A prior operator/session summary reported that both variants imported, fitted,
predicted, returned the expected shape, and produced finite values. Under the
current evidence standard, that summary is not authoritative local execution
evidence. Exact prediction ranges, unique counts, MAE values, runtime, and the
final process exit code are therefore `not recoverable`.

Accordingly, this archive is `inconclusive`: it preserves a reproducible
historical configuration and the exact smoke-test source, but it does not
promote the reported pass to a formal supported result. No experiment was rerun
merely to improve the archive.

## Preserved files

- `.python-version`: original uv Python pin;
- `pyproject.toml`: original direct dependency declaration;
- `uv.lock`: original complete uv lock;
- `smoke_tmu_regression.py`: exact synthetic smoke-test source;
- `pip-freeze.txt`: resolved installed distributions;
- `uv-tree.txt`: dependency tree; and
- `SOURCE_FILE_SHA256SUMS.txt`: hashes of the external source files before copy.

The machine-readable archival assessment is
[`artifacts/manifests/tmu-regression-smoke-test-archive.json`](../../../artifacts/manifests/tmu-regression-smoke-test-archive.json).

## Historical reproduction commands

These commands describe how the preserved project was intended to be invoked.
They were not run during this archival task:

```powershell
Set-Location <path-to-this-archive-directory>
uv sync --locked
uv run --locked python smoke_tmu_regression.py
```

Running them later would create new execution evidence and must be authorised
and recorded separately.
