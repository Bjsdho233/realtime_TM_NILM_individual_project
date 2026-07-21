# Current State

**Status:** Current governance snapshot\
**Last updated:** 2026-07-21\
**Current phase:** T002 Han upstream snapshot acquisition and REDD inventory\
**Active execution task:** T002 — REDD Inventory and Protocol R Preflight\
**Local verification:** T001 completed. The authorised T002 upstream snapshot and read-only inventory were verified on 2026-07-21.

## 1. Purpose

This file records the project's current verified state. It is an operational snapshot, not a research plan or detailed progress log.

Only locally verified facts may be recorded as completed work. Planned work, historical results, conversation summaries, and unverified files must not be presented as current project evidence.

If this file conflicts with the actual worktree or locally generated outputs, the worktree must be inspected and this file corrected.

## 2. Governance Files

| File | Current state |
|---|---|
| `AGENTS.md` | Reviewed and manually saved. Its current phase lock remains active. |
| `PROJECT_PLAN.md` | Accepted by Tianhang on 2026-07-21. |
| `docs/decisions/D001-clean-repository.md` | Accepted and manually saved. |
| `docs/decisions/D002-primary-evaluation-protocol.md` | Accepted and manually saved. |
| `docs/CURRENT_STATE.md` | Current review item. |
| T001, T002, and progress records | Reconciled to the canonical long filenames selected by Tianhang. |

## 3. Decisions in Force

### D001 — Clean repository

- The project will use a new independent repository and clean history.
- The previous project remains read-only historical evidence.
- Han's repository is an external reference implementation.
- Neither repository will be copied or merged wholesale.
- Code may be migrated only through a named task with recorded provenance and local verification.

### D002 — Primary evaluation protocol

- Protocol H is used for Han-compatible engineering reproduction.
- Protocol R is the primary research evaluation.
- Protocol X is an optional held-out-house stress test.
- Protocol D is used for final deployment-model training after method freeze.
- Protocol R must split each house in raw time before event generation.
- Training, validation, and candidate test processing must remain separate.
- The candidate test becomes the locked test only after explicit approval of the split manifest and its identity or hash.
- Compatibility, research, stress-test, and deployment results must retain separate evidential status.

## 4. Current Task State

| Task | State |
|---|---|
| T001 | Complete — 2026-07-21. Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record are complete. |
| T002 | In progress. Upstream acquisition and inventory are complete. Timestamp, original-source provenance, active-support, candidate split, boundary, purge, and candidate-manifest requirements remain unresolved. |
| T003 | Not started. No Han reference revision or reusable component has been approved. |
| T004–T013 | Not started. |

T002 is active only within its recorded limited authorisation. T003 and all later tasks remain unauthorised.

## 5. Verified Project Evidence

T001 Gate B inspected `D:\projects\tm-nilm-pico-research` on 2026-07-21. At inspection time, the project contained 5 directories and 11 ordinary files totalling approximately 88,542 bytes.

The inspection found no algorithm code, REDD data, generated results, models, firmware, compilation outputs, credentials, large binary files, or machine-specific state. It found no `.git` directory and no enclosing parent Git repository.

Gate B identified three short filenames that differed from the canonical long filenames referenced by the governance documents. Tianhang selected the long filenames, and the files were renamed and reconciled under explicit authorisation without rewriting the body of the initial progress record.

The local Git repository uses branch `main`. The initial governance baseline commit is `df8451b4eea59e1b9a3af78fa7aac72f614de8b7` and contains the approved 12 governance files. The T001 closure record has been created.

No implementation, dataset, experiment, model, firmware, or hardware operation has yet been admitted as verified evidence in the new project. No remote, tag, push, or GitHub operation occurred.

The following evidence is therefore not currently available:

- a verified REDD inventory;
- an approved Protocol R split manifest;
- a pinned Han reference audit;
- migrated or newly implemented algorithm code;
- a locally trained TM model;
- a model bundle or parity fixture;
- host-native inference results;
- Pico compilation, flashing, or runtime results;
- formal experiment results;
- a remote or GitHub repository.

This section records the absence of accepted technical evidence and the verified Gate B governance state.

## 6. Pending Decisions

The following items remain `Pending`:

- exact local REDD path;
- available houses, channels, timestamps, and gaps;
- appliance class set;
- split proportions, raw-time boundaries, and purge;
- pinned Han repository revision;
- Protocol H data and configuration;
- approved reusable components;
- detector, pairer, feature, Booleanisation, and TM design;
- multiclass versus multiple binary TMs;
- TM parameters and repeated-run policy;
- exact Pico board variant, Arduino core, compiler, and serial protocol;
- feature schema and numeric representation;
- embedded resource and latency targets;
- real-time input boundary and deadline;
- whether Protocol X will be executed.

No task may silently infer these decisions from historical experiments or conversation summaries.

## 7. Current Authorisation and Restrictions

T002 is the active execution task. Its authorisation is limited to one recursive clone of Han's upstream repository to the external target supplied by Tianhang, read-only REDD inventory, source-chain inspection, governance evidence, and the associated local commits.

Do not install dependencies, run the NILM pipeline, modify the upstream clone, copy upstream code or CSV files into this project, begin T003, create a project remote, push, access other external repositories, create or migrate algorithms, run training or inference, or perform firmware, Pico, or hardware work.

## 8. T001 Completion

T001 Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record are complete. The closure commit identifier is reported in the Gate C execution report because a commit cannot record its own final hash.

## 9. T002 Verified Evidence

- Han upstream snapshot commit: `8c5e90df34236ba0afcc4ec46ac083d829de4d51` on `main`.
- `redd` submodule commit: `a621bbd6399e49c6798550618fe43b113149455b`.
- Both the upstream worktree and submodule were clean after inventory.
- The submodule contains 35 pre-processed CSV chunks for six houses and 1,508,578 data rows.
- The main repository contains six `docs/redd` combined CSV files with the same per-house row totals.
- The verified CSV content-tree fingerprint is `5e1ee53cdce2a5ad2d5007a08527bd1fc9486130d56dc008cf8c8ba8e336e73d`.
- `docs/redd` matches lexicographic chunk concatenation followed by backward fill. For House 1, lexicographic order places `_10.csv` between `_1.csv` and `_2.csv`; natural numeric order does not match the combined file.
- The submodule README describes the files as a pre-processed, synchronized REDD dataset. The chain to original raw REDD, timestamp semantics, preprocessing procedure, and original channel provenance remains `Unresolved`.

The external absolute snapshot path remains machine-specific and is not stored in tracked evidence.

## 10. Immediate Next Action

Review the T002 inventory and unresolved completion criteria. T002 remains active but incomplete. T003 and all other later tasks remain unauthorised.
