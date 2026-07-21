# T002 — REDD Inventory and Protocol R Preflight

**Status:** Not started — Blocked\
**Owner:** Tianhang Tan\
**Created:** 2026-07-21\
**Last updated:** 2026-07-21\
**Task type:** Data inventory and evaluation preflight\
**Dependencies:** T001 completion, explicit T002 authorisation and phase transition, and the exact local REDD root path\
**Current authorisation:** None; execution remains unauthorised\
**Dependency state:** T001 completion: Satisfied. Explicit T002 authorisation and phase transition: Not satisfied. Exact local REDD root path: Not provided.

## 1. Objective

Inspect the local REDD dataset without modifying it and produce:

- a reproducible inventory of the available data;
- a house-by-appliance support summary;
- a reviewable Protocol R candidate split proposal;
- a machine-readable candidate split manifest;
- a record of all candidate-test information inspected during preflight.

This task establishes whether the available REDD data can support the intended research evaluation. It does not freeze the split, generate the research event dataset, train a model, or evaluate classification performance.

The proposed future-test region must remain named the `candidate test block` throughout T002.

## 2. Context

Protocol R requires each house to be split in raw time before event detection, pairing, feature extraction, Booleanisation, or model training.

Before those boundaries can be approved, the actual local REDD copy must be inspected. The project currently does not have verified information about:

- available houses;
- mains and appliance channels;
- appliance label mappings;
- timestamp coverage;
- sampling intervals;
- recording gaps;
- duplicate or invalid samples;
- appliance support within possible train, validation, and candidate test regions.

D002 permits limited label-assisted inspection during preflight to determine whether a proposed class set and split are technically evaluable. It does not permit model scoring, feature analysis, or test-guided method selection.

Historical REDD summaries and previous project outputs may provide background, but they cannot replace inspection of the local dataset used by this project.

## 3. Preconditions

T002 may begin only when:

- T001 has been completed or explicitly closed with any remaining limitation recorded;
- Tianhang has provided the exact local REDD root path;
- Tianhang has explicitly authorised access to that path for T002;
- the intended REDD copy has been distinguished from historical processed data and experiment outputs;
- the project phase lock has been updated to permit this task;
- any required dependency installation or environment change has been separately approved.

The local absolute REDD path is machine-specific information. It must not be committed to the repository. Tracked files must use a dataset identifier, relative paths, or a documented runtime placeholder.

## 4. Scope

### 4.1 In scope

- Verify that the supplied path is the intended REDD dataset root.
- Identify the REDD format and directory structure.
- Inventory houses, files, channels, labels, and available measurements.
- Distinguish aggregate mains channels from appliance submeters.
- Record file sizes and a documented dataset-fingerprint method.
- Inspect timestamps, sampling intervals, duplicates, invalid values, and recording gaps.
- Produce a house-by-appliance availability table.
- Produce limited label-assisted support statistics for split feasibility.
- Identify data regions that cannot be used safely.
- Propose eligible appliance-class options.
- Propose per-house raw-time train, validation, and candidate test blocks.
- Propose boundary and purge handling for later approval.
- Record every item inspected from a candidate test block.
- Create narrowly scoped, repeatable inventory and preflight tooling where required.
- Generate human-readable and machine-readable preflight evidence.
- Prepare the proposed split and manifest for review under T004.

### 4.2 Out of scope

- Modifying, renaming, moving, extracting, or deleting raw REDD files.
- Copying raw REDD data into the project repository.
- Treating historical processed CSV files as the new raw-data source.
- Running the project event detector or pairer.
- Generating the formal Protocol R event dataset.
- Extracting research features or assessing feature quality.
- Fitting normalisation or Booleanisation parameters.
- Training, tuning, exporting, or evaluating a TM.
- Running another learned classifier for comparison or data selection.
- Measuring aggregate-mains-only event or classification performance.
- Choosing boundaries based on model scores or prediction errors.
- Calling the candidate test block the locked test.
- Approving or freezing the split.
- Beginning T003, T004, or any implementation task automatically.
- Committing, pushing, or publishing files without separate Git authorisation.

Inventory utilities created under this task must remain limited to data identification, integrity checks, support analysis, and split-manifest preparation. They must not silently become part of the NILM training pipeline.

## 5. Permitted Preflight Inspection

The following candidate-test information may be inspected:

| Information | Permitted purpose |
|---|---|
| House, file, and channel availability | Confirm that the data exist and can be parsed. |
| Timestamp range and valid sample coverage | Confirm that a block is technically evaluable. |
| Sampling interval, duplicates, and recording gaps | Define safe continuous regions and boundary handling. |
| Appliance label and submeter availability | Determine whether a class is represented. |
| Label-derived active duration or approximate activation count | Check whether there is sufficient ground-truth support. |
| Missing or invalid label coverage | Prevent unsupported evaluation blocks. |

Any label-derived activation statistic must:

- use a declared, reproducible feasibility-only rule;
- be marked as label-assisted or oracle support evidence;
- be used only to assess class support;
- remain separate from the later aggregate-mains event pipeline;
- not be presented as detector, pairer, or classifier performance;
- not automatically become a research threshold or model parameter.

The following candidate-test inspection is prohibited:

- event-detector or pairing performance;
- extracted feature distributions;
- class separability;
- Boolean representation quality;
- classifier metrics;
- model errors or confusion matrices;
- hyperparameter comparisons;
- selection between research methods;
- movement of a boundary to improve a model result.

## 6. Required Inventory

### 6.1 Dataset identity

Record:

- dataset name and local format;
- supplied root-path verification result;
- inventory date;
- inventory tool and revision;
- fingerprint method;
- relative file list;
- file size;
- file checksum where practical;
- any file excluded from the fingerprint and the reason.

A fingerprint based only on names, sizes, or timestamps must be identified as a metadata fingerprint. It must not be described as a content hash.

Absolute local paths must remain outside tracked evidence.

### 6.2 House and channel inventory

For every available house, record:

- house identifier;
- recording start and end;
- usable time coverage;
- mains channels;
- submeter channels;
- channel-to-appliance label mapping;
- units and known sampling intervals;
- file and channel parse status;
- missing or unavailable channels;
- ambiguous or duplicate appliance labels;
- known recording anomalies.

Where several channels represent the same appliance or circuit, the inventory must record the raw mapping without silently merging them.

### 6.3 Timestamp and continuity checks

For every relevant channel, inspect:

- timestamp ordering;
- duplicate timestamps;
- non-positive timestamp steps;
- expected and observed sampling intervals;
- large gaps;
- invalid or non-finite values;
- empty files or ranges;
- mismatch between mains and label coverage.

The gap definition used by the inventory must be recorded. A gap threshold must not be inferred silently.

### 6.4 Appliance support

Produce a house-by-appliance table containing, where available:

- channel presence;
- valid label duration;
- label-assisted active duration;
- approximate activation count under the declared support rule;
- support within each proposed train block;
- support within each proposed validation block;
- support within each proposed candidate test block;
- any reason the appliance or block may be unsuitable.

These values are feasibility evidence only.

If an intended appliance lacks sufficient support, report the limitation. Do not silently remove the class, change the boundary, or replace it with another appliance.

## 7. Candidate Protocol R Split

### 7.1 Split principles

The candidate split proposal must:

- define raw-time blocks separately for every eligible house;
- avoid concatenating houses into an artificial time series;
- use explicit inclusive or exclusive timestamp conventions;
- identify train, validation, and candidate test blocks;
- account for recording gaps and unusable regions;
- record the rationale for each proposed boundary;
- preserve independent state reset at every house and split boundary;
- retain traceability from every future processed event to its source range;
- avoid model or feature evidence when selecting boundaries.

Processed events may later be pooled across houses only after each house and split have been processed independently.

### 7.2 Purge and boundary policy

T002 must propose a boundary-safety rule.

The default proposal should require that every accepted event and feature instance have its complete raw-data dependency interval inside one split. Any instance whose detector, pairing, duration, pre-window, post-window, or feature dependency crosses a split boundary must be excluded.

If the exact dependency horizon is not yet known, the manifest must record it as an unresolved freeze input. T004 must not approve the final split until the relevant horizon or containment rule is sufficiently defined.

A numerical purge duration must not be invented from historical experiments.

### 7.3 Candidate revisions

If several candidate layouts are considered, record:

- the candidate identifier;
- the boundaries;
- the allowed preflight evidence inspected;
- the reason it was retained, revised, or rejected.

The final T002 output should identify one recommended candidate where the evidence permits. Alternatives may remain documented, but none is frozen during this task.

## 8. Required Outputs

The expected outputs are:

- a human-readable REDD inventory report;
- a human-readable Protocol R preflight report;
- a machine-readable REDD inventory manifest;
- a machine-readable candidate split manifest;
- a preflight-access record;
- any narrowly scoped script or configuration required to reproduce the inventory;
- a dated progress record.

The exact repository paths must be reconciled with the reviewed `README.md` before T002 execution. The recommended locations are:

- `docs/data/REDD_INVENTORY.md`;
- `docs/data/PROTOCOL_R_PREFLIGHT.md`;
- `artifacts/manifests/redd_inventory.json`;
- `artifacts/manifests/protocol_r_candidate_split.json`;
- `artifacts/manifests/protocol_r_preflight_access.json`;
- `scripts/` for approved repeatable inventory utilities.

Creating this task specification does not create or authorise those files.

## 9. Manifest Requirements

### 9.1 Inventory manifest

The machine-readable inventory should contain or identify:

- schema version;
- dataset identifier;
- inventory identifier;
- fingerprint method and value;
- houses;
- relative source files;
- channels and appliance labels;
- time coverage;
- sampling information;
- gap and validity summaries;
- support-statistics rule;
- generating tool and configuration;
- generation timestamp.

### 9.2 Candidate split manifest

The candidate split manifest should contain or identify:

- schema version;
- protocol name;
- candidate identifier;
- referenced inventory identifier and hash;
- proposed appliance class set or class-set status;
- per-house train ranges;
- per-house validation ranges;
- per-house candidate test ranges;
- timestamp boundary convention;
- excluded ranges;
- gap-handling rule;
- state-reset rule;
- proposed purge or full-dependency-containment rule;
- label-assisted support-summary reference;
- unresolved freeze inputs;
- generating tool and configuration;
- manifest identity or hash.

The manifest must not contain model scores, selected model parameters, or absolute machine-specific paths.

## 10. Procedure

### Step 1 — Confirm authorisation and path

Before reading the data:

1. confirm that T001 is complete;
2. record the exact path supplied by Tianhang;
3. verify that the path exists;
4. confirm that it is the intended raw REDD copy;
5. check whether it is inside the project repository;
6. check whether an operation would modify or extract the dataset;
7. report any unexpected condition before continuing.

Do not search broadly across the user's drives for alternative REDD copies.

### Step 2 — Identify the dataset structure

Inspect the minimum files required to determine:

- REDD format;
- available houses;
- channel metadata;
- mains and submeter organisation;
- timestamp representation;
- appliance labels.

Document any departure from the expected REDD structure.

### Step 3 — Generate the reproducible inventory

Run or create a task-bounded inventory utility.

The utility must:

- use read-only access to raw data;
- work from a supplied root path;
- emit relative source paths;
- make gap and support rules explicit;
- produce deterministic ordering;
- report parse failures rather than skipping them silently.

### Step 4 — Review continuity and support

Produce:

- house coverage summaries;
- channel and appliance tables;
- gap and anomaly summaries;
- label-assisted class-support tables.

Separate confirmed dataset facts from interpretation and recommendations.

### Step 5 — Prepare candidate split options

Using only permitted preflight evidence:

1. identify technically usable continuous regions;
2. propose per-house train, validation, and candidate test blocks;
3. evaluate label-derived support for those blocks;
4. record any revisions and their reasons;
5. identify one recommended candidate if possible;
6. keep unresolved class, ratio, boundary, or purge choices explicit.

Do not run the research event or classification pipeline.

### Step 6 — Validate outputs

Check that:

- every manifest source is traceable to the inventory;
- houses remain independent;
- ranges do not overlap unintentionally;
- boundary conventions are explicit;
- candidate-test inspection is fully logged;
- no absolute data path is tracked;
- no raw data have entered the repository;
- no model or feature results are present;
- the candidate manifest hash can be reproduced.

### Step 7 — Report and stop

Present:

- verified dataset summary;
- anomalies and limitations;
- house-by-appliance support;
- proposed class-set options;
- recommended candidate split;
- unresolved freeze inputs;
- generated evidence files;
- confirmation that no model scoring occurred.

Wait for a separate decision before T004 or any data-processing implementation begins.

## 11. Acceptance Criteria

T002 is complete only when:

- [ ] T001 and the T002 phase transition were explicitly approved.
- [ ] The exact local REDD path was supplied and verified.
- [ ] The inspected copy was identified as raw REDD rather than a historical processed output.
- [ ] No raw dataset file was modified.
- [ ] The dataset format and fingerprint method were recorded.
- [ ] All available houses and relevant files were inventoried.
- [ ] Mains and appliance channels were mapped.
- [ ] Timestamp coverage, sampling behaviour, gaps, and major anomalies were recorded.
- [ ] A house-by-appliance support table was produced.
- [ ] All label-derived statistics were marked as label-assisted or oracle evidence.
- [ ] The support rule was declared and used only for feasibility.
- [ ] A per-house raw-time candidate split was proposed.
- [ ] Houses were not concatenated into one signal.
- [ ] Boundary, state-reset, and purge handling were stated explicitly.
- [ ] Candidate-test access was limited to the permitted preflight fields.
- [ ] Every inspected candidate-test field was recorded.
- [ ] No event-detector, pairer, feature, Booleanisation, or classifier score was used.
- [ ] No class or boundary was changed silently.
- [ ] Human-readable reports were produced.
- [ ] Machine-readable inventory and candidate split manifests were produced.
- [ ] Manifest identities or hashes were verified.
- [ ] No raw data, absolute local path, credentials, or unapproved large outputs entered version control.
- [ ] `docs/CURRENT_STATE.md` and the progress record were updated accurately.
- [ ] The proposed split was still described as a candidate and was not frozen.
- [ ] T004 or any later task did not begin automatically.

## 12. Stop Conditions

Stop and report instead of continuing if:

- the supplied path is missing, ambiguous, or not the intended dataset;
- more than one plausible REDD copy is found and their identity cannot be resolved;
- the data require extraction, conversion, repair, or modification;
- the dataset format differs materially from the expected format;
- key metadata or appliance labels are missing;
- timestamps cannot be interpreted reliably;
- files are corrupt, empty, or unreadable;
- the dataset is inside the repository in a way that risks accidental tracking;
- the available houses cannot support a meaningful candidate split;
- the intended appliance classes lack candidate-test support;
- a proposed boundary can be justified only through model or feature performance;
- a required package or environment change has not been approved;
- the task would expose an absolute private path or secret;
- completing the task would require deleting or overwriting user work.

Insufficient class support is a result of preflight, not permission to reduce the class set automatically.

## 13. Evidence

The T002 completion report must include:

- inspected dataset identifier;
- local path verification result without committing the absolute path;
- inventory and fingerprint method;
- available houses and channels;
- timestamp and gap summary;
- house-by-appliance support table;
- declared label-assisted support rule;
- candidate split summary;
- candidate manifest identifier or hash;
- candidate-test access record;
- anomalies and excluded regions;
- unresolved decisions;
- confirmation that no model scoring or formal event generation occurred;
- exact files created or changed;
- final project and Git status, if Git inspection is authorised.

## 14. Exit and Handoff

T002 ends with a reviewable inventory and candidate split proposal.

It does not convert the candidate test block into a locked test.

The natural later handoff is:

- **T003**, if the Han reference audit is still required before resolving technical boundary assumptions; or
- **T004**, when the class set, boundaries, split proportions, purge rule, and manifest are ready for Tianhang's explicit review and freeze decision.

Neither task begins automatically.
