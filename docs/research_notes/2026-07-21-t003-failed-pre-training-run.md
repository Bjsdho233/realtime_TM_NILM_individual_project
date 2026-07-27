# T003 First Local Attempt — Invalid Pre-Training Run

**Run date:** 2026-07-21 to 2026-07-22 local time

**Archive date:** 2026-07-27

**Classification:** `invalid` / debugging record

**Formal research conclusion:** none

**Superseded by:** the completed T003 local reproduction archive

## What happened

The first isolated T003 local attempt completed environment setup, source
contract inspection, edge detection, edge matching, and event pairing. It then
stopped at the start of the run-1 diagnostic harness, before runtime
Booleanisation, model initialisation, or training.

The immediate error was `FileNotFoundError` for a missing staged
house/class matched-transition file. Han's original trainer skips missing files,
but the independent diagnostic harness did not mirror that skip behaviour at
this point. The stop was therefore caused by a harness compatibility bug, not
by a measured TM or NILM result.

## Validity boundary

This run is `invalid` for research conclusions:

- no Booleanisation result was produced;
- no model was initialised or trained;
- no prediction or metric was produced;
- no save/reload or export evidence was produced; and
- run 2 was not started.

It must not be cited as positive, negative, or inconclusive model-performance
evidence. Its only durable value is debugging provenance: a diagnostic harness
for Han-compatible staged data must mirror the upstream missing-file skip
behaviour.

## Relationship to the completed T003 evidence

A later, separately recorded attempt used the narrowly corrected harness
behaviour and completed two matching runs. That authoritative evidence is
already archived at
[`experiments/T003-local-reproduction/`](../../experiments/T003-local-reproduction/).
This debugging record does not change that archive, its metrics, or its accepted
scope.

## What was preserved and what remains local

The repository stores this normalised debugging record and the machine-readable
manifest at
[`artifacts/manifests/t003-failed-pre-training-run.json`](../../artifacts/manifests/t003-failed-pre-training-run.json).

The original failure report, manifest, command log, environment file, runner,
requirements, staged outputs, embedded Python environment, and checksum list
remain in the external local run directory. They were not copied because the
command log contains machine-specific absolute paths, the run directory
contains REDD-derived staged data and other excluded generated files, and the
complete later T003 result is already archived.

Original source-file SHA-256 values:

| File | SHA-256 |
|---|---|
| `LOCAL_REPRODUCTION_REPORT.md` | `f3ae16df0e684e40cb922444ca9129af467dc5da79c0d43810485145037a9d2c` |
| `local_reproduction_manifest.json` | `6ee32a235703a3d4dcd48abbfe07bb20867bf339028a4124766d2477cb6126eb` |
| `commands.log` | `8c276271e0d56e54dca13704d32f314913b739a3ab148d95446413872c2dcfdc` |
| `environment.txt` | `224cbeb6db555f56b36d1040c79d208eac91c00f3b3d218235dfd2800100a3ba` |
| `local_reproduction_runner.py` | `cc1557a4f7fc33c2856e3f4d885620d15dddb832cfbd89b18aa2f91b5019b8c4` |
| `requirements.txt` | `8246dd363df16a2285ab54e456a018b57b2d98906deeb2c47ce80a2a0bdbebd1` |
| `SHA256SUMS.txt` | `a5e636d4ea0f642575af3789ab1bf191fbc0c9f3a755fb0847a8037e6005cdf8` |

No experiment was rerun for this archival record.
