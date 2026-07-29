# Real-Time rTM NILM System

This directory is the public-facing implementation workspace for the MSc
prototype. Its contents are intended to become the code presented or released
as the runnable system.

The implementation has not yet been assembled here. Files will be added as the
minimum end-to-end workflow is built, using clear functional responsibilities
such as data supply, feature and Boolean input construction, model definition,
training, evaluation and chronological replay. The final structure will follow
actual code needs rather than a pre-generated framework.

The selected model family is TMU 0.8.3 `TMRegressor` with integer-weighted
clauses. Exact features, Booleanisation, target transformation and training
configuration are intentionally not implied by that model choice.

This workspace may contain:

- runnable source code and thin command-line entry points;
- required public configuration;
- focused tests for the runnable path and material failure modes;
- concise installation, usage and example documentation.

The reviewed preprocessed REDD copy and deterministic split tables under
`data/` are included so the public prototype can be run without reconstructing
the local research workspace. Their upstream commit and per-file hashes are
recorded by the split manifest.

The tracked public workspace does not contain:

- original raw REDD recordings;
- agent instructions or repository governance;
- internal task, review or experiment records;
- private reference files, temporary runs, caches or trained artefacts.

During development `system/` remains part of the surrounding research
repository; it is not a nested Git repository. Public code should remain usable
without runtime imports from the surrounding internal documentation and
governance files.

## REDD block preparation

`split_redd_blocks.py` treats every source CSV as an independent acquisition
segment. It does not assume that two files from the same house are temporally
continuous.

For Protocol R houses H1, H3, H5 and H6, every segment is independently divided
by row position into B1–B5 using the frozen `floor(n*k/5)` boundaries. Portions
with the same block name are then combined within each house. Protocol X houses
H2 and H4 take a physically separate output path and remain complete held-out
segments labelled `PX`.

Create the locked environment and run from this directory:

```bash
uv sync --locked
uv run --locked python split_redd_blocks.py
```

Outputs are written to `data/protocol_r/`, `data/protocol_x/` and
`data/split_manifest.json`. Re-running the command overwrites the same outputs;
it never appends rows.

Missing `main` values already present in the source are preserved and reported;
downstream causal windows must treat them as continuity breaks.

## Python environment

`system/` has its own small `uv` environment. Python 3.11, NumPy 1.26.4 and
TMU 0.8.3 follow the Windows CPU combination already verified by this project;
Pandas 2.2.3 supplies the tabular REDD data path.

Restore the exact environment with `uv sync --locked`. For VS Code, select
`system/.venv/Scripts/python.exe` as the Python interpreter. The local `.venv/`
is ignored by Git; `pyproject.toml`, `uv.lock` and `.python-version` are the
reproducible environment definition.

## Development style

This is a supervisor-reviewed MSc prototype. It is developed in small,
reviewable increments so that its control flow, definitions and outputs can be
explained directly in VS Code and demonstrated from a simple command.

Code favours concrete names, clear functional modules and visible data flow.
Comments briefly explain definitions, units, causality or boundary rules,
assumptions and design intent where they are not obvious. They do not repeat
routine syntax or provide defensive explanations for hypothetical behaviour.
