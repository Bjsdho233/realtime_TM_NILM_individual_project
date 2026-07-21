# Current State

**Status:** Current governance snapshot\
**Last updated:** 2026-07-21\
**Current phase:** T001 Gate C local Git bootstrap and closure\
**Active task:** T001 — Governance Review and Repository Bootstrap\
**Local verification:** T001 Gate B consolidated read-only inspection and reconciliation completed; Tianhang explicitly authorised Gate C on 2026-07-21.

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
| T001 | In progress. Gate B is complete. Gate C is explicitly authorised; both commits and final verification remain pending. |
| T002 | Not started — Blocked by T001 completion, explicit T002 authorisation and phase transition, and the exact local REDD root path. |
| T003 | Not started. No Han reference revision or reusable component has been approved. |
| T004–T013 | Not started. |

T002 and T003 must not begin automatically after document review. The current phase lock must first be explicitly changed.

## 5. Verified Project Evidence

T001 Gate B inspected `D:\projects\tm-nilm-pico-research` on 2026-07-21. At inspection time, the project contained 5 directories and 11 ordinary files totalling approximately 88,542 bytes.

The inspection found no algorithm code, REDD data, generated results, models, firmware, compilation outputs, credentials, large binary files, or machine-specific state. It found no `.git` directory and no enclosing parent Git repository.

Gate B identified three short filenames that differed from the canonical long filenames referenced by the governance documents. Tianhang selected the long filenames, and the files were renamed and reconciled under explicit authorisation without rewriting the body of the initial progress record.

No implementation, dataset, experiment, model, firmware, hardware, or Git operation has yet been admitted as verified evidence in the new project.

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
- a verified Git repository, commit, remote, or GitHub state.

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

Tianhang authorised only the following T001 Gate C work on 2026-07-21:

- local Git initialisation at the verified project root with initial branch `main`;
- staging and checking the specified allowlists;
- the specified initial governance baseline commit;
- T001 closure governance updates;
- the specified T001 closure commit;
- final Gate C verification.

T001 remains `In progress` until both commits and final verification succeed.

T002, T003, and all other later tasks remain unauthorised. Do not create a remote, push, access GitHub, access REDD or external repositories, create or migrate algorithms, run training or experiments, or perform firmware, Pico, or hardware work.

## 8. Remaining T001 Work

Before T001 can be completed:

- execute the authorised Gate C Git bootstrap and initial governance baseline commit;
- complete and commit the T001 closure governance update;
- perform final Gate C verification and record the resulting commit identifiers.

T002, T003, and all other later tasks remain unauthorised for execution.

## 9. Immediate Next Action

Execute the explicitly authorised T001 Gate C local Git bootstrap, both specified commits, and final verification.

No later project phase or task is authorised.
