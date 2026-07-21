# Current State

**Status:** Current governance snapshot\
**Last updated:** 2026-07-21\
**Current phase:** Paused pending explicit authorisation and phase transition\
**Active execution task:** None\
**Local verification:** T001 Gate B reconciliation and Gate C local Git bootstrap completed on 2026-07-21.

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
| T002 | Not started — Blocked. T001 completion: Satisfied. Explicit T002 authorisation and phase transition: Not satisfied. Exact local REDD root path: Not provided. |
| T003 | Not started. No Han reference revision or reusable component has been approved. |
| T004–T013 | Not started. |

T002 and T003 must not begin automatically. Tianhang must explicitly authorise the next task and phase transition.

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

There is no active execution task. The project is paused pending Tianhang's next explicit authorisation and phase transition.

T002, T003, and all other later tasks remain unauthorised. Do not create a remote, push, access GitHub, access REDD or external repositories, create or migrate algorithms, run training or experiments, or perform firmware, Pico, or hardware work.

## 8. T001 Completion

T001 Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record are complete. The closure commit identifier is reported in the Gate C execution report because a commit cannot record its own final hash.

## 9. Immediate Next Action

Wait for Tianhang's next explicit task authorisation and phase transition. No later project phase or task is currently authorised.
