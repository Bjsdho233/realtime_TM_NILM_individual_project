# Current State

**Status:** Current governance snapshot\
**Last updated:** 2026-07-21\
**Current phase:** T003 static source audit complete; T003 remains In progress pending review\
**Active execution task:** None; executable reproduction has not started\
**Local verification:** T001 and T002 completed on 2026-07-21. T003 has recorded a static audit of the fixed Han snapshot without executing upstream code.

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
| `docs/decisions/D004-protocol-r-class-fallback.md` | Accepted by Tianhang on 2026-07-21. |
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
| T002 | Complete — 2026-07-21. The original class set failed because `electric furnace` had only 1 candidate complete cycle. Tianhang approved the predeclared `washer dryer` fallback, and the successor manifest was verified. |
| T003 | In progress. Static source audit completed on 2026-07-21 at Han commit `8c5e90df34236ba0afcc4ec46ac083d829de4d51`; review, reusable-component approval, and the minimum reproduction contract remain Pending. |
| T004–T013 | Not started. |

No executable reproduction task is active. T003 remains the current governance task; T004 and all later tasks remain unauthorised.

## 5. Verified Project Evidence

T001 Gate B inspected `D:\projects\tm-nilm-pico-research` on 2026-07-21. At inspection time, the project contained 5 directories and 11 ordinary files totalling approximately 88,542 bytes.

The inspection found no algorithm code, REDD data, generated results, models, firmware, compilation outputs, credentials, large binary files, or machine-specific state. It found no `.git` directory and no enclosing parent Git repository.

Gate B identified three short filenames that differed from the canonical long filenames referenced by the governance documents. Tianhang selected the long filenames, and the files were renamed and reconciled under explicit authorisation without rewriting the body of the initial progress record.

The local Git repository uses branch `main`. The initial governance baseline commit is `df8451b4eea59e1b9a3af78fa7aac72f614de8b7` and contains the approved 12 governance files. The T001 closure record has been created.

T002 admitted task-bounded standard-library inventory, support-audit, and manifest-finalizer utilities plus their evidence outputs. No research algorithm, dataset copy, experiment, model, firmware, or hardware result has been admitted. No remote, tag, push, or GitHub operation occurred for this project.

The following evidence is therefore not currently available:

- an approved Han reusable-component set and minimum reproduction contract;
- migrated or newly implemented algorithm code;
- a locally trained TM model;
- a model bundle or parity fixture;
- host-native inference results;
- Pico compilation, flashing, or runtime results;
- formal experiment results;
- a remote or GitHub repository.

The T002 inventory and approved split evidence are recorded in Section 9. The remaining list identifies evidence not yet produced.

## 6. Pending Decisions

The following items remain `Pending`:

- original calendar timestamps, gaps, and per-file channel provenance;
- actual detector, pairer, window, event, and feature dependency horizons;
- cross-house scoring, missing-label eligibility, and macro aggregation for the first model evaluation;
- approved reusable Han components and minimum Protocol H reproduction contract;
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

T003 static source inspection is complete. No executable reproduction phase is authorised; T004 and all later work remain unauthorised.

Do not install dependencies, run edge detection, event pairing, feature extraction, training, inference, or model scoring; modify the upstream clone; copy upstream code or CSV files; begin executable reproduction or T004; create a project remote, tag, branch, or push; access other sources; or perform firmware, Pico, or hardware work.

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
- Fifteen standard-library unit tests passed in final verification.
- Fridge, microwave, and dish washer meet every frozen base-class minimum.
- Electric furnace has 38 train/validation complete cycles and fold counts 10, 15, and 13, but only 1 complete cycle in the sealed candidate test; its candidate active duration is 824,943 nominal seconds.
- Washer dryer was audited as the predeclared optional class and meets the same frozen standard.
- The candidate manifest canonical SHA-256 is `480a738ad799860f6cdecbba9affb1d76c365a71468b276b8b0669ea55bba11a`.
- D004 fallback decision commit: `c6ceb9a81da1fe24d79c935a0e9ffea3022fa0c2`.
- Approved split commit: `3669e900cb5fa9c4c1890413c238ef693a163ada`.
- Approved classes: fridge, microwave, dish washer, and washer dryer. All four pass the original frozen standard.
- Approved successor manifest: `artifacts/manifests/protocol_r_approved_split.json` with canonical SHA-256 `b4509778dc15ccdf7a6ab48357cfcef90a28b58a5b12bbe57dfef0a590e24eb4`.
- Candidate-test support labels were inspected during preflight. No model predictions or metrics were generated or viewed, and H2/H4 remain sealed for model development.
- Missing-label eligibility, cross-house scoring, and macro aggregation must be frozen before the first model evaluation.

The external absolute snapshot path remains machine-specific and is not stored in tracked evidence.

## 10. T003 Static Source Audit

- Fixed Han snapshot: `main` commit `8c5e90df34236ba0afcc4ec46ac083d829de4d51`, source tree `5254fc117d8c6f392d6eee1ea7bacc41d2b2039c`.
- Fixed REDD gitlink: `a621bbd6399e49c6798550618fe43b113149455b`.
- The audit found multiple entry candidates but no uniquely provable canonical workflow.
- The staged preparation route is label-assisted; the integrated Python routes reimplement it rather than calling the staged scripts.
- The observed TM input has 23 ordered numeric slots, 22 unique feature names, and 184 Boolean inputs at 8 bits. Each clause can address positive and negated forms of those 184 inputs.
- The current trainer defaults to two classes, while the committed embedded header declares four classes. Exact model provenance is unresolved.
- The integrated firmware replays native float samples from SD, uses a different FIFO pairer and Boolean quantiser, and reads post-event samples from the file. It is not evidence of live causal NILM.
- Missing generated headers/assets and the absent parity fixtures prevent a self-contained, proven Python-to-C-to-firmware chain at this snapshot.
- Detailed findings: [`HAN_PIPELINE_SOURCE_AUDIT.md`](reproduction/HAN_PIPELINE_SOURCE_AUDIT.md).
- Machine-readable inventory: [`han_pipeline_source_inventory.json`](../artifacts/manifests/han_pipeline_source_inventory.json).
- No Han program, notebook, training, inference, build, benchmark, firmware, or hardware work was executed.
- No reusable component or minimum reproduction contract has been approved.

## 11. Immediate Next Action

Tianhang and ChatGPT review the T003 static audit and decide the minimum Protocol H reproduction contract, reusable components, compatibility deviations, and PC/host/Pico boundary. T003 remains In progress; no executable reproduction or later task begins automatically.
