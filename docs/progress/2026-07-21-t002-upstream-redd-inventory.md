# T002 Upstream REDD Inventory — 2026-07-21

> **Historical mid-task snapshot.** The `In progress` state below describes this
> dated checkpoint and was superseded by completed T002. Live status and
> authority are only in [`docs/CURRENT_STATE.md`](../CURRENT_STATE.md).

**Task:** T002 — REDD Inventory and Protocol R Preflight\
**Status:** In progress; inventory complete, preflight incomplete

## Completed

- Recorded Tianhang's revised T002 authorisation before network access.
- Created authorisation commit `3f7e9aa17e9ede506d8a3ab31a63a7d124b389a8` with message `docs: authorise T002 upstream REDD acquisition`.
- Recursively cloned the single authorised Han upstream repository to the external target supplied by Tianhang.
- Verified upstream `main` at `8c5e90df34236ba0afcc4ec46ac083d829de4d51`.
- Verified the `redd` submodule at `a621bbd6399e49c6798550618fe43b113149455b`.
- Inventoried 35 submodule chunk CSVs and six `docs/redd` combined CSVs read-only.
- Recorded house rows, columns, missing fields, data types, appliance presence, file fingerprints, ordering correspondence, static data-reading paths, and source-chain limits.
- Confirmed that the upstream and submodule worktrees remained clean.

## Source Classification

- The pinned `redd` submodule is the input source for Han upstream reproduction.
- `docs/redd` is a web-distribution and scoring derivative, not an independent dataset.
- Provenance from original raw REDD to the pre-processed synchronized submodule remains `Unresolved`.

## T002 Status

T002 is not complete. The inspected CSVs do not provide proven timestamps or original raw-data provenance, so timestamp coverage, gaps, active-support evidence, candidate raw-time splits, purge, and the candidate split manifest remain unresolved.

No closure commit was created with the reserved message `docs: complete T002 REDD inventory`.

## Work Not Performed

- No dependency installation or `uv sync`.
- No edge detection, event pairing, feature analysis, TM training, or inference.
- No upstream file modification or data repair.
- No code or CSV copy into the project.
- No T003, firmware, Pico, or hardware work.
- No project remote, push, or access to any other external repository.
