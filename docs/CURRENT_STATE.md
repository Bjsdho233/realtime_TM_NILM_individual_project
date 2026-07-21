# Current State

**Status:** Current governance snapshot\
**Last updated:** 2026-07-21\
**Current phase:** T002 Phase B — Protocol R preflight audited; closure blocked\
**Active execution task:** T002 — REDD Inventory and Protocol R Preflight\
**Local verification:** T001 completed. T002 snapshot, inventory, sequence contract, support audit, and candidate manifest were verified on 2026-07-21.

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
| `docs/decisions/D003-redd-sequence-time-contract.md` | Accepted by Tianhang on 2026-07-21. |
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

### D003 — REDD sequence-time contract

- The pinned `redd` submodule is the canonical reproduction input.
- Han reproduction retains the observed upstream glob, concatenation, and backward-fill behaviour.
- Protocol R treats every chunk as an independent segment at a nominal 3-second cadence and does not use `docs/redd` combined files.
- H1, H3, H5, and H6 form the train/validation pool; H2 and H4 form the sealed candidate test.
- The four base classes and frozen support standard are recorded in D003.
- Full dependency containment, with state reset and discarded boundary-crossing items, is the purge policy.

## 4. Current Task State

| Task | State |
|---|---|
| T001 | Complete — 2026-07-21. Gate B reconciliation, local Git bootstrap, the initial governance baseline commit, and the T001 closure record are complete. |
| T002 | In progress. The support audit and candidate manifest are complete, but `electric furnace` fails the sealed-candidate-test minimum of 10 complete cycles: H2 has no `electric furnace` column and H4 has 1 complete cycle. |
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

- original calendar timestamps, gaps, and per-file channel provenance;
- actual detector, pairer, window, event, and feature dependency horizons;
- pinned Han reference revision for the later T003 reference audit;
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

T002 Phase B remains the active task. Its authorised evidence has been generated. Because the frozen four-class closure gate failed, no fallback, threshold change, alternate house allocation, T003, or later implementation is authorised.

Do not install dependencies, run edge detection, event pairing, feature extraction, training, inference, or model scoring; modify the upstream clone; copy upstream code or CSV files; begin T003; create a project remote, tag, branch, or push; access other sources; or perform firmware, Pico, or hardware work.

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
- The limited source check supports a nominal 3-second appliance cadence, 15 W on/off threshold provenance, missing-data subsequence splitting, same-subsequence backward fill, and treatment of preprocessed CSVs as independent non-continuous long windows.
- The source implementation can retain one short subsequence when no large split is found; this is implementation evidence only and does not prove the House 5 generation chain.
- D003 is recorded in sequence-contract commit `5fb7f0e38c8e983969976dc4214038c77b5cafd9`.
- Ten synthetic unit tests passed.
- Fridge, microwave, and dish washer meet every frozen base-class minimum.
- Electric furnace has 38 train/validation complete cycles and fold counts 10, 15, and 13, but only 1 complete cycle in the sealed candidate test; its candidate active duration is 824,943 nominal seconds.
- Washer dryer meets the same standard as an optional exploratory class.
- The candidate manifest canonical SHA-256 is `480a738ad799860f6cdecbba9affb1d76c365a71468b276b8b0669ea55bba11a`.

The external absolute snapshot path remains machine-specific and is not stored in tracked evidence.

## 10. Immediate Next Action

Create the authorised support-evidence commit, keep T002 `In progress`, and stop for Tianhang's decision. No fallback or later task begins automatically.
