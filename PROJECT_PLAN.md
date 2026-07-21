# Project Plan

**Status:** Accepted\
**Owner:** Tianhang Tan\
**Last updated:** 2026-07-21

## 1. Purpose and Current Priority

This project develops a traceable workflow for causal, event-level, multi-appliance non-intrusive load monitoring using Tsetlin Machines.

The first engineering milestone is a minimum Han-compatible closed loop:

1. train a Tsetlin Machine locally;
2. save and reload the inference model;
3. export the trained model into a versioned embedded representation;
4. verify the same model through Python and host-native inference;
5. deploy it to the Pico;
6. confirm parity using fixed validation fixtures.

This milestone does not require a complete clone of Han's repository, reproduction of every historical score, or immediate deployment of event detection, event pairing, feature extraction, display logic, SD-card replay, or live-meter input.

After the engineering path is stable, the project will establish a leakage-controlled Protocol R research baseline and begin controlled experiments to improve appliance coverage, classification performance, causal streaming behaviour, and embedded suitability.

The aspirational research target is a macro F1 score of at least 0.80 over a frozen Protocol R task containing at least three appliance classes. This is a research target, not a guaranteed result or a condition for honest project completion.

## 2. Target Outcomes

### 2.1 Research outcome

- A leakage-controlled Protocol R baseline.
- Controlled experiments in which one main scientific variable is changed at a time.
- Evidence showing which changes improve or fail to improve event-level NILM.
- Per-class analysis of remaining failure modes.
- A final method evaluated once on the locked Protocol R test.

The project does not assume that the main contribution must come from event pairing, feature design, Booleanisation, TM structure, or any other specific component.

### 2.2 Engineering outcome

- A repeatable path from local TM training to Pico inference.
- A versioned feature schema and model bundle.
- Generated embedded model artefacts rather than manually copied model values.
- Python, host-native, and Pico parity fixtures.
- Recorded model size, firmware size, memory use, and inference latency.
- A causal replay path suitable for demonstration and later extension.

### 2.3 Dissertation and demo outcome

- A clear distinction between compatibility reproduction, formal research results, and deployment-only results.
- An evidence-backed explanation of the complete workflow.
- A demonstrable Pico inference path using a locally trained model.
- Reproducible figures, tables, manifests, configurations, and result summaries.
- Honest reporting of limitations, negative results, and incomplete deployment stages.

## 3. Working Strategy

### 3.1 Han-compatible engineering path

The current Han repository is a reference implementation, not a specification to copy file by file.

A named audit task must first pin the reference revision and record:

- relevant source files;
- input and output formats;
- processing stages;
- model serialisation and export path;
- embedded dependencies;
- known inconsistencies;
- locally verified reusable components;
- deviations required for Pico deployment.

The initial Pico boundary will be an ordered numeric event-feature vector:

- Python performs event detection, event pairing, and feature extraction.
- Host-native code and the Pico receive the same ordered feature vector.
- Host-native code and the Pico perform Booleanisation and TM inference.
- Both expose the resulting Boolean bits, signed class votes, and prediction for validation.

A pre-Booleanised Pico input may be used as an earlier smoke step, but it does not complete the intended feature-to-inference parity path.

This engineering path is evaluated under Protocol H. It proves execution and compatibility only. It is not the formal research result.

### 3.2 Protocol R research baseline

The Protocol R implementation will be developed cleanly in this repository. Historical code may be migrated only through a named review task.

The research baseline must:

- split continuous raw time before event generation;
- process each REDD house independently;
- reset detector and pairer state at every house and split boundary;
- fit all learned preprocessing on training data only;
- use validation data for development and method selection;
- keep the locked test inaccessible until final evaluation;
- distinguish aggregate-mains-only inference from label-assisted or oracle analysis.

The term `Protocol R research baseline` refers to the controlled evaluation procedure. It does not imply that all choices in Han's workflow are incorrect.

### 3.3 Controlled research development

Once the training-to-Pico path and Protocol R baseline are stable, new experiments may investigate:

- event detection;
- event pairing;
- causal feature extraction;
- Booleanisation;
- multiclass versus per-appliance TM structures;
- class balance and sampling;
- TM training parameters;
- model size and embedded cost;
- causal streaming and bounded-delay inference.

The TM remains the primary learned classifier. Deterministic detection, pairing, filtering, and state logic may remain outside the TM where appropriate.

Other learned models are not part of the primary system. A conventional model may be added later only as a separately approved comparison baseline.

## 4. Scope

### 4.1 In scope

- Inspection of Han's current public workflow.
- REDD inventory and split preflight.
- Aggregate-main event detection and event pairing.
- Event-level feature extraction and Booleanisation.
- TM training, validation, model export, and inference.
- Host-native inference.
- Pico compilation, flashing, parity testing, and measurement.
- Controlled experiments for performance and class expansion.
- Causal replay from recorded REDD data.
- Dissertation and demonstration evidence.

### 4.2 Deferred from the first engineering loop

The following work is deferred unless approved by a later named task:

- exact reproduction of Han's complete environment or historical scores;
- direct reuse of the full ESP32 sketch;
- LVGL, TFT, dashboard, or display work;
- SD-card support;
- live electrical meter integration;
- on-device event detection, pairing, or feature extraction;
- end-to-end real-time claims;
- hyperparameter optimisation;
- cross-dataset evaluation;
- Protocol X;
- production deployment and long-duration reliability testing.

Deferred work is not permanently excluded.

### 4.3 Out of scope

- Copying the old project or Han's repository wholesale.
- Treating prototype code as verified production code.
- Using the frozen test for tuning or method selection.
- Reporting label-assisted event construction as aggregate-mains-only inference.
- Replacing the primary TM system with another learned classifier.
- Claiming hardware behaviour from compilation evidence alone.

## 5. Confirmed and Pending Decisions

### 5.1 Confirmed

| Item | Decision |
|---|---|
| Repository | Use a new clean repository and history. |
| Legacy project | Retain it unchanged as read-only evidence. |
| Code migration | Migrate only through named review tasks. |
| First milestone | Establish a minimum local-training-to-Pico closed loop. |
| Reproduction scope | Han-compatible behaviour, not file-for-file reproduction. |
| Primary model | Tsetlin Machine. |
| Main research protocol | Protocol R. |
| Compatibility protocol | Protocol H. |
| Stress test | Protocol X is optional. |
| Deployment model | Protocol D is deployment-only. |
| Main split principle | Per-house raw-time blocked splitting. |
| T002 canonical input | Pinned `redd` submodule commit `a621bbd6399e49c6798550618fe43b113149455b`. |
| Protocol R sequence contract | Each chunk is an independent segment at a nominal 3-second cadence; no cross-segment time order or dependencies. |
| Protocol R candidate houses | Train/validation pool H1, H3, H5, H6; sealed candidate test H2 and H4. |
| Protocol R candidate classes | Base: fridge, microwave, dish washer, electric furnace. Optional exploratory fifth: washer dryer. |
| Protocol R validation | Each train/validation segment is independently divided by row position into three contiguous blocks. |
| Protocol R purge | Full dependency containment within one segment/block; no invented fixed numerical purge. |
| Formal run summary | One canonical `result.json` per formal run. |
| Experiment identity | Use task, experiment, configuration, and run artefacts; do not rely on one Git branch per experiment. |

### 5.2 Pending

- Original REDD calendar timestamps, gaps, and per-file channel provenance.
- Actual detector, pairer, window, event, and feature dependency horizons.
- Pinned Han repository revision and approved reusable files.
- Multiclass TM versus multiple binary TMs.
- Detector, pairer, feature, Booleanisation, and TM parameters.
- Exact Pico board variant, Arduino core, compiler, and serial protocol.
- Final feature schema and numeric representation.
- Real-time input boundary and deadline.
- Flash, RAM, model-size, latency, and throughput targets.
- Number of repeated training runs and seeds.
- Whether Protocol X will be executed.

Pending items must be resolved by their named tasks. They must not be inferred from historical experiments.

## 6. Research Questions

### RQ1 — Engineering reproduction

Can a locally trained TM be exported, verified through Python and host-native inference, and deployed to the Pico with matching Boolean bits, class votes, and predictions?

### RQ2 — Protocol R baseline

What event-level appliance classification performance is achieved under a leakage-controlled, mixed-house raw-time blocked protocol?

### RQ3 — Controlled improvements

Which controlled changes improve macro F1, class coverage, or failure behaviour without using future samples or locked-test feedback?

### RQ4 — Embedded trade-offs

How do feature count, Boolean representation, TM structure, and model parameters affect prediction quality, model size, memory use, and inference latency on the Pico?

## 7. Evaluation Protocols

| Protocol | Purpose | Result status |
|---|---|---|
| Protocol H | Reproduce the minimum Han-compatible workflow and engineering path. | Compatibility and execution evidence only. |
| Protocol R | Main mixed-house, raw-time blocked research evaluation. | Primary dissertation result. |
| Protocol X | Optional held-out-house stress test. | Additional generalisation evidence only. |
| Protocol D | Train the final deployment model after method freeze. | Deployment evidence, not an unbiased test result. |

### 7.1 Protocol H

Protocol H may follow a pinned Han revision closely enough to verify:

- local training;
- model save and reload;
- embedded model export;
- host-native inference;
- Pico inference.

Any difference in data preparation, feature order, class set, preprocessing, model parameters, or embedded behaviour must be recorded.

Protocol H must not use the Protocol R candidate test block for training, model selection, or compatibility scoring.

### 7.2 Protocol R

Protocol R combines eligible development blocks from multiple houses only after each house has been split and processed independently. Signals from different houses must never be concatenated into one artificial time series.

For the pinned T002 preflight, each chunk is an independent segment with a nominal 3-second cadence. The train/validation pool is H1, H3, H5, and H6; H2 and H4 form the sealed candidate test. Each pool segment is split independently by row position into three contiguous validation blocks. The base classes are fridge, microwave, dish washer, and electric furnace; washer dryer is optional and exploratory. These decisions are defined in [`D003`](docs/decisions/D003-redd-sequence-time-contract.md).

The following rules apply:

- split raw time before event generation;
- reset state at every house and split boundary;
- fit normalisation, Booleanisation, duration limits, and learned preprocessing on training data only;
- use validation data for development and selection;
- do not use the frozen test for tuning or method selection;
- run aggregate-mains-only and label-assisted routes separately.
- never use `docs/redd` combined files as Protocol R input;
- reset state and require full dependency containment at every segment and block boundary.

### 7.3 Protocol R test lifecycle

1. **Preflight**\
   Candidate future-test blocks may be inspected only for time coverage, gaps, and label-derived class support. All inspected information must be recorded. Model scores and feature quality must not be used to choose the boundary.

2. **Freeze**\
   Tianhang approves the split manifest and its identity or hash. Only then does the candidate test block become the locked test.

3. **Model development**\
   Training, tuning, error analysis, and method-selection code cannot access the locked test until the final evaluation task.

Before freeze, the block must be called the `candidate test block`, not the locked test.

The final evaluation may run only models, configurations, and metrics listed in the approved evaluation manifest. Test results cannot be used to select between them or trigger further tuning.

### 7.4 Protocol X

Protocol X holds out one or more complete houses. It is optional and will be attempted only after the primary method and Protocol R evaluation are complete.

### 7.5 Protocol D

Protocol D is created only after the research method has been frozen and formally evaluated. It may use a broader approved training set to produce the final Pico model.

Protocol D metrics must not be presented as unbiased Protocol R test results.

## 8. System Contracts

The planned research path is:

`per-house raw mains -> raw-time split -> event detection -> event pairing -> feature extraction -> Booleanisation -> TM -> event prediction`

The planned engineering path is:

`local training -> model bundle -> Python reference -> host-native reference -> Pico`

### 8.1 Data and split contract

Every processed row or event must be traceable to:

- source house;
- source file or recording;
- original time or sample range;
- split identity;
- processing configuration;
- schema version.

Raw REDD data must remain outside version control.

### 8.2 Feature schema

The feature schema must define:

- ordered feature names;
- meaning and units;
- numeric type;
- causal availability time;
- window and boundary conventions;
- missing-value handling;
- schema version and hash.

Feature order must not be inferred from DataFrame or dictionary behaviour.

### 8.3 Booleanisation

The Booleanisation contract must define:

- normalisation statistics or thresholds;
- fitting source;
- comparison rule;
- quantisation and rounding rule;
- number of bits;
- bit order;
- handling of values outside the fitted range.

All fitted values must come from training data only.

### 8.4 Model bundle

The model bundle must be the shared source of truth for Python, host-native code, and Pico firmware.

It must contain or identify:

- bundle version;
- feature-schema version and hash;
- ordered class labels;
- Booleanisation configuration;
- TM type and dimensions;
- model payload;
- vote and tie-breaking conventions;
- training and exporter metadata;
- model payload hash.

Embedded headers or binaries must be generated from the bundle. Model values and preprocessing constants must not be copied manually into firmware.

### 8.5 Parity fixtures

Each fixture must record:

- fixture ID;
- non-test provenance;
- input at the declared deployment boundary;
- expected feature representation;
- expected Boolean bits;
- expected signed class votes;
- expected prediction.

Parity requirements are:

- numeric features: exact where represented as integers or fixed point; otherwise within an approved per-feature tolerance;
- Boolean bits: exact bit-for-bit equality;
- class votes: exact signed integer equality for every class;
- predictions: exact equality, including tie behaviour.

Prediction agreement alone is insufficient if bits or votes differ.

The first Pico loop does not require on-device feature extraction. Feature-extraction parity becomes mandatory if that stage is later implemented on more than one target.

## 9. Metrics and Evidence

### 9.1 Event metrics

Where an appropriate reference is available:

- event detection precision, recall, and F1;
- event timing error;
- event coverage;
- pairing precision, recall, and F1;
- duration error;
- paired power-mismatch distribution;
- unmatched and rejected-event counts.

Metrics derived from appliance labels must be marked as label-assisted or oracle evidence.

### 9.2 Classification metrics

Formal classification reports must include:

- per-class precision, recall, F1, and support;
- macro precision, recall, and F1;
- accuracy;
- confusion matrix;
- number of houses, time coverage, and event count;
- explicit input and ground-truth definitions.

The primary target is macro F1 over the frozen Protocol R class set.

### 9.3 Embedded metrics

Embedded reports must distinguish:

- serialised model payload size;
- generated model artefact size;
- total firmware flash use;
- static RAM use;
- stack and heap evidence where measurable;
- Booleanisation latency;
- TM inference latency;
- combined compute latency;
- parity pass count;
- reset, timeout, and dropped-input count.

Latency should report median, p95, and maximum over a documented repetition count. Serial transfer and logging time must be kept separate from compute latency.

Exact acceptance thresholds remain `Pending`.

### 9.4 Formal run evidence

Each formal run must have a unique immutable run directory.

`result.json` is the canonical run summary. Supporting evidence may include:

- configuration;
- data and split manifests;
- environment manifest;
- predictions;
- confusion matrices;
- per-class metrics;
- parity traces;
- raw timing samples;
- build logs;
- linker maps;
- plots and tables.

A smoke run proves execution only. It is not a formal scientific result.

Published results must never be overwritten.

## 10. Experiment Discipline

- Use training and validation data only during development.
- Change one main scientific variable per controlled experiment.
- If several implementation changes are technically inseparable, declare them as one combined intervention before running the experiment.
- Do not attribute a combined result to one internal sub-change without an ablation.
- Record the hypothesis, baseline, changed variable, configuration, seed, environment, and acceptance rule before execution.
- Record failed and negative experiments when they affect later decisions.
- Keep aggregate-mains-only and oracle results separate.
- Do not select configurations from the locked test.
- Do not claim reproducibility from a seed alone if the implementation is not deterministic.
- Use experiment and run identifiers rather than creating a new long-lived branch for every run.

## 11. Task Roadmap

Detailed specifications belong in `docs/tasks/`. This table records only task purpose and exit conditions.

| ID | Task | Exit condition | Status |
|---|---|---|---|
| T001 | Governance review and repository bootstrap | Governance files approved and validated; Git actions performed only after explicit authorisation. | Complete — 2026-07-21. |
| T002 | Han upstream snapshot acquisition, REDD inventory, and Protocol R preflight | Acquire the authorised recursive upstream snapshot, record immutable revisions, inventory REDD evidence, and assess the remaining preflight criteria without training or model scoring. | In progress — audit and candidate manifest complete; four-class closure blocked by insufficient sealed-candidate-test `electric furnace` complete cycles. |
| T003 | Han reference audit and minimum reproduction contract | Reference revision, workflow stages, reusable components, deviations, and deployment boundary approved. | Pending |
| T004 | Protocol R split approval and freeze | Tianhang approves the split manifest and hash; candidate test becomes locked test. | Pending |
| T005 | Han-compatible local training and export | A locally trained smoke model is saved, reloaded, exported, and accompanied by fixed fixtures. | Pending |
| T006 | Host-native parity | Host-native Boolean bits, votes, and predictions match the Python reference. | Pending |
| T007 | Pico closed-loop deployment | Firmware is compiled, flashed, and run on the verified board; parity and initial resource evidence are recorded. | Pending |
| T008 | Protocol R research baseline | A train/validation baseline is produced under the frozen protocol without accessing the locked test. | Pending |
| T009 | Controlled experiment cycle | Each approved experiment has a hypothesis, one main variable, immutable evidence, and a decision. | Pending |
| T010 | Method selection and final freeze | Final method, code revision, configuration, metrics, and evaluation manifest are approved. | Pending |
| T011 | Final Protocol R evaluation | Predeclared frozen models are evaluated once on the locked test with no further selection or tuning. | Pending |
| T012 | Protocol D model and final Pico deployment | Final deployment model is exported and Pico parity and resource measurements are repeated. | Pending |
| T013 | Optional Protocol X and evidence pack | Optional stress test and final dissertation/demo evidence are completed. | Pending |

T002 and T003 may be prepared independently after T001. Neither task may continue automatically into implementation.

## 12. Claim Boundaries

The following terms must be used carefully:

- **Causal replay:** recorded samples are processed sequentially without access to samples beyond the declared prediction time.
- **Real-time capable:** the complete declared processing boundary meets an approved deadline without an accumulating backlog.
- **Live-meter operation:** data are acquired from a real measurement source during execution.
- **On-device inference:** the board runs Booleanisation and/or TM inference at the declared boundary.
- **On-device end-to-end NILM:** the board performs acquisition, detection, pairing, feature extraction, Booleanisation, and prediction.

A Pico running only TM inference must not be described as end-to-end on-device NILM.

## 13. Risks and Honest Fallbacks

| Risk | Response or fallback |
|---|---|
| Han's current workflow cannot be reproduced exactly | Deliver a pinned, repeatable compatibility path and document every material deviation. |
| Han's Python and embedded stages are inconsistent | Treat the model bundle and parity fixtures as the new explicit contract. |
| Candidate blocks have insufficient class support | Keep T002 in progress, preserve the frozen support standard, and await Tianhang's decision on a predefined fallback. |
| The macro F1 target is not achieved | Report the best frozen-protocol result, per-class failures, negative experiments, and likely causes. |
| Three classes cannot be supported reliably | A smaller class set may be used as a supplementary demo, but it does not satisfy the stated research target. |
| Full preprocessing is too large for the Pico | Retain PC preprocessing with Pico Booleanisation and TM inference, and report the deployment boundary clearly. |
| Real-time end-to-end processing is not completed | Demonstrate causal replay and measured inference timing without claiming live real-time NILM. |
| Pico testing is incomplete | Report only the highest verified stage, such as host parity or compilation; do not claim board-tested behaviour. |
| Schedule becomes constrained | Preserve the minimum training-to-Pico loop, Protocol R baseline, and the highest-value controlled experiments. |

Failure to meet the target metric does not invalidate the project. A leakage-controlled baseline, a verified embedded path, and a well-supported analysis of limitations remain valid research and engineering outcomes.

## 14. Progress

The authoritative local state is recorded in [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

Dated work records are stored in [`docs/progress/`](docs/progress/). The plan should not duplicate the detailed progress log.

Current reported state:

- the governance skeleton has been created;
- `AGENTS.md` has received its first review;
- this project plan has been accepted by Tianhang;
- no algorithm code or REDD data has been imported;
- no model has been trained;
- no firmware has been compiled or tested;
- Gate B reconciliation and local Git bootstrap are complete;
- the initial governance baseline commit is `df8451b4eea59e1b9a3af78fa7aac72f614de8b7`;
- the T001 closure record has been created;
- T001 is complete;
- no remote, tag, push, or GitHub operation occurred;
- T002 upstream acquisition and inventory are complete;
- Tianhang accepted the D003 sequence-time contract and frozen support standard;
- the Phase B audit and candidate manifest were generated without model scoring;
- `electric furnace` failed the sealed-candidate-test complete-cycle minimum, so T002 remains in progress.

T002 remains the active task. The authorised evidence commit records the failed closure gate; no fallback or further execution is authorised. T003 and all other tasks remain unauthorised.
