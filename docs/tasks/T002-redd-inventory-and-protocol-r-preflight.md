# T002 — REDD Inventory and Protocol R Preflight

> **Historical closed-task record.** The authorised Phase B scope below records
> what T002 was allowed to do in 2026-07-21; it is not current authority. Live
> authority is only in [`docs/CURRENT_STATE.md`](../CURRENT_STATE.md).

**Status:** Complete — 2026-07-21\
**Owner:** Tianhang Tan\
**Created:** 2026-07-21\
**Last updated:** 2026-07-21\
**Task type:** Data inventory and evaluation preflight\
**Dependencies:** T001 completion, explicit revised T002 authorisation, an absent external clone target, and successful recursive acquisition of the authorised upstream snapshot\
**Historical authorised scope:** Phase B sequence-time contract, label-assisted support audit, and Protocol R candidate manifest\
**Dependency state:** T001 completion: Satisfied. Revised T002 authorisation: Satisfied. External clone target absence: Verified before acquisition. Recursive upstream acquisition: Satisfied.

## Phase B Revision — 2026-07-21

Tianhang accepted the upstream inventory and authorised Phase B. This revision supersedes requirements that depend on unavailable original timestamps for the pinned preprocessed CSVs.

The binding sequence, house, class, fold, boundary, and support decisions are in [`D003`](../decisions/D003-redd-sequence-time-contract.md). In summary:

- every chunk is an independent Protocol R segment with a nominal 3-second cadence;
- row identity is `segment_id`, `sample_index`, and `nominal_offset_seconds`, never an asserted original timestamp;
- H1, H3, H5, and H6 are the train/validation pool; H2 and H4 are the sealed candidate test;
- D003's original base classes are fridge, microwave, dish washer, and electric furnace; washer dryer was predeclared as optional and exploratory;
- each pool segment is divided independently into three contiguous row-position blocks;
- full dependency containment and state reset apply at every segment and block boundary;
- label-assisted support uses the fixed 15 W, two-sample, complete-cycle rule and fixed minima in D003.

Phase B may create `tools/data/audit_redd_support.py`, `tests/data/test_audit_redd_support.py`, the named support evidence, and the authorised commits. It must not execute the NILM pipeline or inspect model results.

## Class Fallback and Completion Revision — 2026-07-21

The original D003 four-class set failed because `electric furnace` had 1 sealed-candidate-test complete cycle against a minimum of 10. Tianhang explicitly approved the predeclared fallback before any model prediction or metric was viewed. D004 replaces `electric furnace` with `washer dryer` and leaves every house, file, row range, fold, threshold, boundary, and processing rule unchanged.

The approved classes are `fridge`, `microwave`, `dish washer`, and `washer dryer`. All four pass the original frozen support standard. The approved successor manifest is `artifacts/manifests/protocol_r_approved_split.json` with canonical SHA-256 `b4509778dc15ccdf7a6ab48357cfcef90a28b58a5b12bbe57dfef0a590e24eb4`.

Candidate-test support labels were inspected for feasibility. No model output or metric was generated or viewed, and H2/H4 remain sealed for model development. Missing-label eligibility, cross-house scoring, and macro aggregation remain unresolved and must be frozen before first model evaluation.

## Active Revision — 2026-07-21

This revision replaces the earlier requirement for Tianhang to provide an existing local REDD root.

The authorised input acquisition is:

- clone the current `main` branch from `https://github.com/wuhanstudio/nilm.git`;
- fetch its `redd` submodule recursively;
- record the full main-repository and submodule commit identifiers;
- keep the clone external to this project and treat it as read-only evidence.

For Han upstream reproduction, the `redd` submodule is the input source. `docs/redd` is classified as a web-distribution or scoring derivative and is not an independent dataset.

The active inventory must report:

- upstream branch, HEAD, remote, and clean status;
- `redd` submodule URL, commit, and clean status;
- per-house file counts, rows, columns, missing values, data types, and appliance coverage under `redd/`;
- the same statistics for the six combined CSV files under `docs/redd/`;
- correspondence under lexicographic and natural numeric ordering, including the House 1 `_10.csv` ordering issue;
- all actual Python and JavaScript data-reading paths;
- only source-chain links supported by local evidence, with every unproved link marked `Unresolved`.

This revision does not authorise dependency installation, NILM pipeline execution, modification of the upstream clone, repair of data, copying upstream code or CSV files into this project, T003, firmware, Pico, or hardware work.

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

Protocol R requires each available sequence segment to be split by the D003 row-position contract before event detection, pairing, feature extraction, Booleanisation, or model training. The current CSVs do not support invented calendar timestamps or cross-segment chronology.

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

- T001 is complete;
- Tianhang has explicitly authorised the revised T002 and its single upstream source;
- the external clone target is confirmed absent before acquisition;
- the project phase lock permits the revised T002;
- Git is available for the recursive clone;
- no dependency installation or environment change is required.

The external absolute clone path is machine-specific information. It must not be committed to the repository. Tracked evidence must use the upstream URL, immutable revisions, repository-relative paths, or a documented runtime placeholder.

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
- Acquire the single authorised recursive Han upstream snapshot.
- Inventory the submodule and combined CSV evidence without modifying it.
- Inspect actual Python and JavaScript data-reading paths.
- Record locally supported source-chain links and mark unsupported links `Unresolved`.

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
- Installing dependencies or running `uv sync`.
- Modifying the external upstream clone or repairing its data.
- Copying upstream code or CSV files into this project.

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

- define row-position blocks separately for every eligible segment;
- avoid concatenating houses into an artificial time series;
- use explicit half-open row-range conventions and nominal offsets;
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

The authorised output locations are:

- `docs/data/REDD_INVENTORY.md`;
- `docs/data/PROTOCOL_R_PREFLIGHT.md`;
- `artifacts/manifests/redd_inventory.json`;
- `artifacts/manifests/protocol_r_candidate_split.json`;
- `artifacts/manifests/protocol_r_preflight_access.json`;
- `tools/data/audit_redd_support.py` for the approved repeatable audit utility;
- `tests/data/test_audit_redd_support.py` for synthetic unit tests;
- `artifacts/tables/redd_support_audit.csv` and `artifacts/manifests/redd_support_audit.json` for support evidence.

The Phase B authorisation explicitly authorises the named Phase B files.

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

- [x] T001 and the T002 phase transition were explicitly approved.
- [x] The revised external snapshot root was acquired and verified without tracking its machine-specific absolute path.
- [x] The inspected copy was identified as a pinned preprocessed synchronized output and accepted under D003 without being misrepresented as raw REDD.
- [x] No upstream dataset file was modified.
- [x] The dataset format and fingerprint method were recorded.
- [x] All available houses and relevant CSV files were inventoried.
- [x] Mains and appliance columns were mapped.
- [x] Nominal sampling behaviour and the inability to recover calendar coverage or original gaps were recorded.
- [x] A house/chunk/appliance support table was produced.
- [x] All label-derived statistics were marked as label-assisted or oracle evidence.
- [x] The support rule was declared before audit and used only for feasibility.
- [x] A per-segment row-position candidate split was proposed under D003.
- [x] Houses and segments were not concatenated into one Protocol R signal.
- [x] Boundary, state-reset, and dependency-aware purge handling were stated explicitly.
- [x] Candidate-test label support was accessed only for the authorised preflight fields and fully recorded.
- [x] The preflight-access record contains every inspected field category.
- [x] No event-detector, pairer, feature, Booleanisation, or classifier score was used.
- [x] No class or boundary was changed silently.
- [x] Human-readable inventory and preflight-status reports were produced.
- [x] Machine-readable inventory and candidate split manifests were produced.
- [x] Manifest identities or hashes were verified.
- [x] No raw data, absolute local path, credentials, or unapproved large outputs entered version control.
- [x] `docs/CURRENT_STATE.md` and the progress record were updated accurately.
- [x] No split was proposed or frozen.
- [x] T004 or any later task did not begin automatically.

The original four-class support gate failed because `electric furnace` had 1 complete cycle in the sealed candidate test, below the minimum of 10. D004 preserves that failure evidence and approves the predeclared `washer dryer` fallback. The approved four classes all meet the unchanged standard, the successor manifest and hash were verified, and T002 is complete.

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
