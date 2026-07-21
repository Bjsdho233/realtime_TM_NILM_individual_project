# Progress Record — 2026-07-21

**Task:** T001 — Governance Review and Repository Bootstrap\
**Status at end of record:** In progress\
**Record type:** Initial governance review\
**Author:** Tianhang Tan\
**Evidence basis:** Manual review and save confirmations; consolidated local inspection not yet performed

## 1. Summary

The initial governance structure for the new TM NILM project was reviewed and manually saved.

The work established:

- the purpose and boundaries of the new repository;
- the distinction between historical evidence, external references, and new project evidence;
- the primary evaluation framework;
- the current task and phase restrictions;
- the requirements for later REDD inspection and Git bootstrap.

This record does not claim that the complete local worktree has been inspected or that the repository has been initialised.

## 2. Files Reviewed

The following files were reviewed and manually saved:

- `AGENTS.md`;
- `PROJECT_PLAN.md`;
- `README.md`;
- `.gitignore`;
- `.codex/config.toml`;
- `docs/CURRENT_STATE.md`;
- `docs/decisions/D001-clean-repository.md`;
- `docs/decisions/D002-primary-evaluation-protocol.md`;
- `docs/tasks/T001-governance-review-and-repository-bootstrap.md`;
- `docs/tasks/T002-redd-inventory-and-protocol-r-preflight.md`;
- this initial progress record.

Manual save confirmation does not replace local validation of file contents, paths, links, or repository state.

## 3. Decisions Accepted

The following decisions were accepted:

### D001 — Clean repository

- The new project will use an independent repository and clean history.
- The previous experimental repository remains read-only historical evidence.
- Han's repository remains an external reference implementation.
- Neither repository will be copied or merged wholesale.
- Any reused code must enter through a named migration task with recorded provenance and local verification.

### D002 — Primary evaluation protocol

- Protocol H is reserved for Han-compatible engineering reproduction.
- Protocol R is the primary research evaluation.
- Protocol X is an optional held-out-house stress test.
- Protocol D is reserved for final deployment-model training after method freeze.
- Protocol R will split each house in raw time before event generation.
- Candidate test data will not become the locked test until the split manifest is explicitly approved and identified by a stable identity or hash.

## 4. Task State

- **T001:** In progress.
- **T002:** Blocked pending T001 completion, an approved phase transition, and the exact local REDD path.
- **T003:** Not started and not authorised.
- **T004–T013:** Not started.

Reviewing their specifications does not authorise execution of those tasks.

## 5. Evidence Status

No implementation, dataset, experiment, model, firmware, hardware, or Git result has been accepted as verified evidence in the new project.

In particular, this record does not establish:

- the contents of the complete local project tree;
- the presence or absence of unexpected code, data, outputs, or credentials;
- the validity of every internal Markdown link;
- the effective behaviour of `.gitignore` or `.codex/config.toml`;
- whether the project directory already has Git state;
- an initial branch, commit, remote, or GitHub repository;
- a verified REDD inventory or split manifest;
- a pinned Han reference revision;
- a working host or Pico implementation.

These items require direct local inspection or later approved tasks.

## 6. Work Not Performed

No action was taken to:

- access or process REDD;
- inspect or import Han's code;
- migrate historical project code;
- create algorithm or firmware files;
- install dependencies;
- run training or experiments;
- compile or flash the Pico;
- run `git init`;
- stage or commit files;
- configure a remote;
- push or publish project content.

## 7. Remaining T001 Work

The following work remains:

- perform one consolidated read-only inspection of the actual project root;
- confirm the complete file and directory tree;
- identify unexpected or unclassified files;
- check for code, datasets, generated outputs, credentials, and machine-specific artefacts;
- determine the actual Git state;
- validate internal filenames and Markdown links;
- validate `.gitignore` coverage and the project-level Codex configuration;
- reconcile `docs/CURRENT_STATE.md` with the inspection findings;
- confirm whether `PROJECT_PLAN.md` should move from `Draft for review` to an accepted state;
- prepare an exact initial Git-bootstrap proposal;
- obtain separate explicit authorisation before changing Git state.

## 8. Next Action

Perform the T001 Gate B consolidated read-only local inspection.

The inspection should report its findings before making any change. If the worktree is coherent, the next report should include a proposed initial branch, exact commit contents, exclusions, commit message, and required governance updates.

Git bootstrap and the transition to T002 or T003 remain separately authorised actions.

## 9. Record Policy

This is an append-only progress record once accepted into project history.

If later inspection reveals that any statement is incomplete or inaccurate, record the correction in a new dated progress entry and update `docs/CURRENT_STATE.md`. Do not silently rewrite historical evidence.
