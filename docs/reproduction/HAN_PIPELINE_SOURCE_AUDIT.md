# Han Pipeline Source Audit

**Status:** T003 static source audit complete; T003 remains In progress\
**Audit date:** 2026-07-21\
**Evidence boundary:** Static inspection only. No upstream program, notebook, build, training, inference, test, or benchmark was executed.

## 1. Fixed Snapshot

| Item | Fixed value |
|---|---|
| Upstream | `https://github.com/wuhanstudio/nilm` |
| Branch | `main` |
| Commit | `8c5e90df34236ba0afcc4ec46ac083d829de4d51` |
| Source tree | `5254fc117d8c6f392d6eee1ea7bacc41d2b2039c` |
| `origin/main` at audit | Same as the fixed commit |
| REDD gitlink | `a621bbd6399e49c6798550618fe43b113149455b` |
| Worktrees at audit | Upstream and REDD submodule clean |

The evidence labels used below are:

- **Wired/reachable:** called by an actual entry point in the fixed tree.
- **Implemented but not shown reachable:** implementation exists, but no current entry point was found calling it.
- **Documented only:** stated by README, comments, metadata, or prose without matching reachable code evidence.
- **Not found/unresolved:** the fixed snapshot does not establish the claim.

All code citations use `relative/path : symbol : line range : Git blob ID`.

## 2. Repository Map

| Area | Static responsibility | Finding |
|---|---|---|
| Root Python scripts | REDD preparation, training, integrated replay, and Iris example | Multiple independent entry points; no dispatcher or shared pipeline configuration |
| `tsetlin/` | Python TM, Booleanisation, protobuf save/load, and C-header compiler | Used by REDD training and integrated Python inference |
| `protobuf/` | Model wire schema | Defines training and compressed-inference representations |
| `arduino/lime-tm/` | Arduino library, inference runtime, REDD test sketch, integrated NILM sketch | Two conflicting examples; neither is self-contained in the fixed checkout |
| `posix/` | Host C detector, feature path, and TM inference prototype | Build target exists but required model/input files are absent |
| `redd/` | Pinned pre-processed REDD submodule | Data source used by root Python scripts; content was not reprocessed in T003 |
| `docs/redd/` and `docs/js/` | Website distribution and browser scoring path | Separate derivative path, not a Protocol R input |
| `notebooks/` | UK-DALE exploration | Separate empty-README workspace and notebook; not linked to the REDD entry points |
| `tests/` | REDD pruning utility | Standalone utility, not invoked by the documented root workflow |

Python requires 3.12. Root dependencies are lower-bounded in `pyproject.toml`, while `uv.lock` fixes a concrete resolution. The notebook workspace separately requires Python 3.11 or later and includes a Git dependency on NILMTK. The Arduino metadata names the Arduino framework and `ststm32`, while the integrated sketch contains ESP32-specific SD/display setup. The exact board, core, compiler, LVGL, and TFT_eSPI versions are unresolved.

## 3. Canonical Entry Candidates

No unique canonical entry point can be proved.

| Candidate | Evidence | Status | Difference |
|---|---|---|---|
| `redd_edge_detect.py` → `redd_edge_match.py` → `redd_event_pair.py` → `redd_tm_training.py` | README lists these four commands in order; each script has its own `__main__` body | Wired/reachable within each script; cross-script order is documented only | Label-assisted preparation chain; training currently defaults to two classes |
| `main.py` | README command and integrated `__main__` | Wired/reachable | Offline whole-building replay; aggregate-main detection/pairing, optional TM inference, appliance channels used for a ground-truth proxy |
| `main_real_time.py` | README command and `process_real_time()` entry | Wired/reachable | Preloads and backward-fills the complete building, then sequentially replays rows with idle-triggered inference |
| `arduino/.../nilm_inference.ino` | Arduino `setup()`/`loop()` | Wired/reachable in source | SD replay with on-device detector, simple pairing, feature extraction, Booleanisation, TM inference, and LVGL display; missing tracked headers prevent a self-contained build |
| `arduino/.../redd_inference.ino` | Arduino `setup()`/`loop()` | Wired/reachable in source | Repeats an embedded two-feature test array; its local model header is absent |
| `posix/main.c` | C `main()` and CMake target | Wired/reachable in source | File replay prototype; required input and model headers are absent |

The strongest evidence for the intended PC preparation/training order is the README command sequence, but the integrated Python entries reimplement rather than call that chain. The fixed tree therefore supports a set of candidates, not a single canonical workflow.

Evidence:

- `README.md : documented command block : lines 15-25 : a64118b23d828c5a52db9a5249faa304adbe8b51`
- `redd_edge_detect.py : __main__ : lines 147-195 : 0165635187847d0f13f4f45d03a7c3e1e98dedd9`
- `main.py : __main__ : lines 436-607 : c8ccecd19961c9a0cbfc72caf8c27a04902e9a44`
- `main_real_time.py : process_real_time/__main__ : lines 355-601 : 20e9483a8039adcb4c4b0f6ed41b2b3bf35036a6`

## 4. End-to-End Call Trace

### 4.1 Staged PC preparation and training

```text
redd/redd_house{house}_*.csv
  -> glob + pandas read/concat + whole-result backward fill
  -> EdgeDetector on main and selected appliance channels
  -> temp/building_*_*_transients.csv
  -> appliance-edge overlap labels added to main transients
  -> building_*_main_transients_train.csv
  -> label-filtered stateful rise/fall pairing
  -> episode statistics from building_*_raw.csv
  -> temp/building_*_*_matched_transitions.csv
  -> houses 1,2,4,5,6 train; house 3 test
  -> 23 ordered feature slots (22 unique names)
  -> mean/std from training rows, normal-CDF mapping, 8 bits per slot
  -> one multiclass TM
  -> training protobuf + compressed inference protobuf
  -> generated C structural header + requested model header
```

This route is **label-assisted event construction**: appliance-channel transitions first label main transitions, and the pairer filters on those labels. It is not an aggregate-mains-only inference pipeline.

Evidence:

- `redd_edge_detect.py : __main__ data load and detector loop : lines 155-193 : 0165635187847d0f13f4f45d03a7c3e1e98dedd9`
- `redd_edge_match.py : find_match/__main__ : lines 23-48 and 136-192 : 7c70251f495ae0920969d5142de76be485e9f693`
- `redd_event_pair.py : match_edges_stateful/__main__ : lines 50-144 and 440-511 : 6bdbba6407972abdd333d2597b26d32555a3eeab`
- `redd_tm_training.py : read_redd_data and training/export body : lines 62-143 and 185-294 : d49325cc51ea4d73065930a6830f4f22cdca66f8`

### 4.2 Integrated offline Python path

`main.py` loads and backward-fills every matched chunk for a building, detects edges on `main`, pairs those edges, derives episode features, optionally loads an inference protobuf and training CSV, Booleanises the features, predicts a class, and uses appliance channels only to construct a display/evaluation proxy. It does not call the staged scripts.

Evidence:

- `main.py : edge_detection and __main__ : lines 399-607 : c8ccecd19961c9a0cbfc72caf8c27a04902e9a44`
- `main.py : infer_with_tsetlin : lines 136-142 : c8ccecd19961c9a0cbfc72caf8c27a04902e9a44`
- `main.py : infer_ground_truth_appliance : lines 145-177 : c8ccecd19961c9a0cbfc72caf8c27a04902e9a44`

### 4.3 “Real-time” Python path

`main_real_time.py` first reads all matched chunks into one DataFrame and applies backward fill to the complete result. It then iterates row by row, runs the detector, accumulates transients, and triggers pairing/features/inference after 50 consecutive samples below the default 200 W threshold. This is sequential replay, not live acquisition. Whole-result backward fill can incorporate a later observation into an earlier missing sample, so the default path is not proven causal even though the processing loop is sequential.

Evidence:

- `main_real_time.py : parse_args : lines 339-352 : 20e9483a8039adcb4c4b0f6ed41b2b3bf35036a6`
- `main_real_time.py : process_real_time data load : lines 355-388 : 20e9483a8039adcb4c4b0f6ed41b2b3bf35036a6`
- `main_real_time.py : process_real_time streaming loop : lines 390-568 : 20e9483a8039adcb4c4b0f6ed41b2b3bf35036a6`

### 4.4 Export-to-firmware bridge

The training entry calls `tsetlin_compile("tsetlin_redd_inference_model.ipb", "redd_model.h")`. The compiler always writes `tsetlin_model.h` in its current working directory and writes the model arrays to the requested output path. The committed firmware model lives deeper under the Arduino example, while neither generated protobuf nor `tsetlin_model.h` is tracked. No command or script connects the root compiler outputs to the Arduino example directory. That placement step and the provenance of the committed model are unresolved manual gaps.

Evidence:

- `redd_tm_training.py : model save/reload/export : lines 270-294 : d49325cc51ea4d73065930a6830f4f22cdca66f8`
- `tsetlin/compiler/write.py : tsetlin_compile : lines 16-98 : f26ca9c973de54f557e1b8c5307b30624ddf315f`
- `arduino/lime-tm/examples/nilm_inference/redd_model.h : generated model metadata : lines 4020-4034 : fb25d363e4d6f3cc03061a7cd9f5b6cc7e205ab8`

## 5. Stage Inputs, Outputs, and Shapes

| Stage | Actual input | Actual output | Static shape/format | Status |
|---|---|---|---|---|
| Data load | Per-house CSV chunks | Concatenated, backward-filled pandas DataFrame | All CSV columns; row index discarded | Wired/reachable |
| Edge detection | One power column, sample/index time | Transients and steady states | Transient fields `transition`, `duration`, `start`, `end`; integrated route also stores `sequence` | Wired/reachable |
| Edge-to-appliance matching | Main and appliance transient CSVs | Main transients with per-appliance binary labels and `unknown` | Label-assisted overlap within ±2 index units | Wired/reachable in staged route |
| Event pairing | Label-filtered transients or aggregate-main transients | Rise/fall episode records | Staged and integrated Python use bounded subset selection; firmware uses FIFO one-rise/one-fall matching | Wired/reachable, inconsistent implementations |
| Feature extraction | Main samples plus episode start/end and signed deltas | Event statistics | 21 returned statistic keys including `duration`; outer row adds `transition`, start/end, and metadata | Wired/reachable |
| Ordered TM vector | Matched-event table | Numeric matrix | 23 ordered slots but 22 unique names because `duration` appears twice | Wired/reachable |
| Booleanisation | Numeric matrix + training mean/std | Boolean vectors | 8 MSB-first bits per slot; 23 × 8 = 184 inputs | Wired/reachable |
| TM | 184 Boolean inputs | Class votes and argmax prediction | Single multiclass TM; signed votes | Wired/reachable |
| Export | Training/inference protobuf | `tsetlin_model.h` and model-array header | Protobuf fields are `uint32`; generated literal positions/data are `uint16`; votes are `int32` | Wired/reachable from training entry |

## 6. Feature-Dimension Reconciliation

The current Python feature list contains 23 positions:

1. `transition`
2. `duration`
3. `pos_transition_magnitude`
4. `neg_transition_magnitude`
5. `abs_transition`
6. `log_abs_transition`
7. `duration` again
8. `log_duration`
9. `transition_duration_product`
10. `transition_duration_ratio`
11. `episode_mean_main`
12. `episode_std_main`
13. `episode_min_main`
14. `episode_max_main`
15. `episode_range_main`
16. `internal_diff_mean_abs`
17. `internal_diff_max_abs`
18. `internal_edge_count`
19. `subcycle_count_proxy`
20. `active_fraction_proxy`
21. `episode_energy_estimate`
22. `post_minus_pre_mean`
23. `event_internal_edge_count`

Consequently:

- raw ordered slots before Booleanisation: **23**;
- unique feature names/signals in that order: **22**;
- Boolean TM inputs at 8 bits: **184**;
- potential positive and negated literals per clause: **368**, while `n_feature` remains **184**;
- no current REDD path establishing **18** or **92** as an active dimension was found.

The firmware deliberately reproduces the duplicate positions: slots 0 and 2 both carry positive transition magnitude, and slots 1 and 6 both carry duration. The committed model declares `n_feature = 184`.

Evidence:

- `redd_tm_training.py : features : lines 22-45 : d49325cc51ea4d73065930a6830f4f22cdca66f8`
- `redd_event_pair.py : episode_feature_row : lines 157-203 : 6bdbba6407972abdd333d2597b26d32555a3eeab`
- `tsetlin/utils/booleanize.py : booleanize_features : lines 43-63 : 6fd94469cef1b3a42926547eb19d4ad3499ed5b5`
- `tsetlin/clause.py : Clause.__init__ : lines 11-30 : b6d7d4f241b09e1ad6e2ca7100a9050356c2b2dd`
- `arduino/lime-tm/examples/nilm_inference/features.cpp : episode_features_to_vector23 : lines 302-388 : 9efd457b9967832bf90f2529956e3dcee2678523`
- `arduino/lime-tm/examples/nilm_inference/redd_model.h : tsetlin_model : lines 4020-4034 : fb25d363e4d6f3cc03061a7cd9f5b6cc7e205ab8`

There is also a Booleanisation parity gap. Python uses round-to-even on `norm_cdf(z) * 255`. The integrated firmware uses `floor(norm_cdf(z) * 256)` with a clamp to 255. Those mappings are not generally identical. The older two-feature `redd.c` uses `lrintf(x * 255)`, but its test routine is commented out in the integrated sketch loop. No cross-language Boolean-vector fixture or parity assertion was found.

## 7. TM Training and Export

### Training configuration and loop

| Property | Fixed-tree behaviour |
|---|---|
| Structure | One multiclass TM; class count is the number of unique training labels |
| Class defaults | Current training default: `fridge`, `microwave`; four-class alternative is commented |
| Houses | Train 1, 2, 4, 5, 6; test 3 |
| Default epochs | 10 |
| Default clauses | 200 total per class: 100 positive and 100 negative |
| Default automaton states | 50 |
| Default threshold `T` | 20 |
| Default specificity `s` | 6.0 |
| Default Boolean bits | 8 |
| Sample order | Fixed DataFrame order each epoch; no epoch shuffle |
| Seeds | Python `random.seed(0)` only; the `fastrand` generator used in clause feedback is not shown seeded |
| Validation/model selection | No validation set. House 3 is the test set. Optional Optuna directly minimises House-3 test error, creating test-set selection if used |
| Final model after Optuna | Still constructed from command-line/default arguments; best Optuna parameters are printed but not wired into final construction |

The fixed model header instead declares four classes, 184 inputs, 200 clauses, and 50 states. It was introduced by commit `f9f3dcac2ec73215c78d04b6d44421ffc35633fe` with the message `[nilm] Add pre-trained model`. The tracked tree contains no generating `.pb`/`.ipb`, command record, data manifest, mean/std manifest, or parity fixture. Its exact training provenance is therefore **Not found/unresolved**.

Evidence:

- `redd_tm_training.py : module configuration and main : lines 1-60 and 185-294 : d49325cc51ea4d73065930a6830f4f22cdca66f8`
- `tsetlin/tsetlin.py : Tsetlin.__init__/predict/step : lines 12-109 : 071071e2174d13d5c521052b94adfcfe4f8837be`
- `tsetlin/clause.py : feedback RNG binding : lines 1-5 : b6d7d4f241b09e1ad6e2ca7100a9050356c2b2dd`

### Model formats and encodings

- Training `.pb`: protobuf with full clause state arrays.
- Inference `.ipb`: protobuf with only included positive and negative literal positions.
- Protobuf scalar fields and repeated state/position values: unsigned 32-bit logical fields.
- Generated C literal position/data arrays: `uint16_t`; generated bitpack type is `uint32_t` but the current compressed path emits position arrays.
- Runtime input: `uint8_t` Boolean array.
- Runtime votes: signed `int32_t`; predicted class: `uint8_t`.
- C header is source text compiled into native arrays; no runtime byte-stream endianness contract is defined.
- No weight quantisation exists; the model is represented by included literal indices.
- The generated header reports `TSETLIN_MODEL_TOTAL_BYTES 17244`. This is a compiler size-counter value, not measured flash/RAM use. The header file itself is 146,972 bytes.

The Python save/reload checks compare prediction accuracy after loading each protobuf. There is no Python-versus-C vote check, Boolean-bit check, file checksum record, or embedded parity check.

## 8. Firmware and Host-Native Trace

### Integrated Arduino/ESP32 sketch

The reachable `setup()` initialises Serial, LVGL/TFT, SD storage, opens `/main.bin`, and resets state. The reachable `loop()` reads one native `float` sample when more than 100 ms has elapsed, feeds the on-device detector, performs simple FIFO pairing after 20 stable samples, reads episode/pre/post samples from the SD file, derives 23 feature slots, Booleanises to 184 bits, evaluates the TM, updates class counters, and refreshes the display.

The input boundary is therefore **pre-recorded native float32 aggregate-main samples on an SD card**, not a meter, ADC, serial stream, or live sensor. No timestamps are read; an incrementing sample index is used. Feature extraction reads 32 post-event samples by seeking forward in the same SD file. This demonstrates file look-ahead and is incompatible with a live causal claim.

The event pairer is not the Python subset matcher. It takes the earliest stored rise and the next later fall one-to-one, without power-error optimisation or the Python duration/gap constraints.

Evidence:

- `arduino/lime-tm/examples/nilm_inference/nilm_inference.ino : reset/match/process : lines 40-210 : 211c678077b8c8e40dd8b67e48a7b4ef96a45266`
- `arduino/lime-tm/examples/nilm_inference/nilm_inference.ino : setup/loop : lines 325-430 : 211c678077b8c8e40dd8b67e48a7b4ef96a45266`
- `arduino/lime-tm/examples/nilm_inference/features.cpp : feature extraction and inference : lines 504-657 : 9efd457b9967832bf90f2529956e3dcee2678523`
- `arduino/lime-tm/examples/nilm_inference/chart.cpp : lv_chart_ui/lv_update_chart : lines 16-112 : aae2874e95ee5f47d4fa8174d38f29bb5f52108b`

### Timing boundary

The only `micros()` measurements are in `tm_redd_main()`, where Booleanisation and TM evaluation are timed separately over a compiled test array. That function is commented out in the integrated sketch loop. Edge detection, pairing, SD access, feature extraction, display, and end-to-end latency are not timed. No latency or real-time performance claim can be derived from this snapshot.

### Build completeness

- `nilm_inference.ino` includes `redd_test.h`, but that file is absent from its directory and the tracked tree provides it only in the sibling `redd_inference` example.
- The committed `redd_model.h` includes `tsetlin_model.h`, which is ignored and absent from the tracked tree.
- The sibling `redd_inference` example includes `redd_model.h`, but no such header is tracked in that directory.
- The POSIX target includes model headers and expects `redd_building_1_pruned.bin`; those assets are absent from `posix/`.
- The generated POSIX Makefile contains a machine-specific historical absolute path; CMake is the clearer build description.

These are static completeness findings. No compile was attempted.

## 9. Real-Time Boundary Matrix

| Stage | Offline or online in actual path | PC or device | Actual input | Wired evidence | Status |
|---|---|---|---|---|---|
| Data acquisition | Offline file replay | PC and device | CSV chunks on PC; `/main.bin` native float32 on SD | Python loaders; Arduino `setup/loop` | Wired/reachable; no live acquisition |
| Streaming sampling | Sequential replay after full load on PC; timed file reads on device | PC and device | Preloaded DataFrame rows; SD float values | `main_real_time.process_real_time`; Arduino `loop` | Wired/reachable replay only |
| Edge detection | Sequential | PC and device | Aggregate-main sample/index | `EdgeDetector.update`; `edge_detector_update` | Wired/reachable; parameters/implementations differ |
| Event pairing | Batch after idle/stable window | PC and device | Accumulated transients | Python subset matcher; Arduino FIFO matcher | Wired/reachable; not equivalent |
| Feature extraction | At episode finalisation | PC and device | Episode plus pre/post context | Python buffer/slices; Arduino SD seeks | Wired/reachable; device uses future file look-ahead |
| Booleanisation | Per matched event | PC and device | 23 numeric slots + mean/std | Python utility; firmware feature code | Wired/reachable; quantisers differ |
| TM inference | Per matched event | PC and device | 184 Boolean inputs | Python `predict`; C `tsetlin_evaluate` | Wired/reachable; no parity fixture |
| Display/output | Plot/CSV/console on PC; LVGL/Serial on device | PC and device | predictions, event metadata, counts | Python output code; `chart.cpp` | Wired/reachable |

## 10. Han Versus Approved Protocol R

| Contract item | Han fixed snapshot | Approved Protocol R | Gap/category |
|---|---|---|---|
| Houses | Train H1,H2,H4,H5,H6; test H3 | Development H1,H3,H5,H6; sealed candidate test H2,H4 | Protocol R wrapper required |
| Classes | Staged preparation uses fridge, microwave, dish washer, electric furnace; current trainer defaults to fridge and microwave | Fridge, microwave, dish washer, washer dryer | Configuration and label adaptation required |
| Split | Whole houses; no validation set | Per-segment three-block development folds; H2/H4 sealed | Protocol R wrapper required |
| Cadence | Row/sample index; no explicit cadence in pipeline | Nominal 3 seconds per segment | Metadata wrapper required |
| Chunk handling | Unsorted `glob` result concatenated, then backward fill across result | Every chunk independent; no cross-segment dependencies | Material incompatibility |
| House 1 `_10.csv` | Ordering follows filesystem/glob result; not explicitly sorted | Natural chunk identity retained as independent segments | Han order unresolved; Protocol R unaffected |
| State reset | Per concatenated building/script call | Every segment and fold block | Protocol R wrapper required |
| Support standard | No frozen support preflight in training path | D003/D004 frozen support standard | Separate governance contract |
| Missing labels | Missing event files are skipped; class count derives from observed labels | Missing target column means label unavailable, not appliance absence | Evaluation wrapper required |
| Event construction | Staged route uses appliance labels; integrated routes use aggregate main | Aggregate-mains-only and label-assisted routes must be separate | Explicit route separation required |
| Pairing | Python subset matcher; embedded FIFO matcher | Pending method, with full dependency containment | Tianhang decision required |
| Feature horizon | 32 pre and 32 post samples; full episode; max 1024 on device | Actual dependency horizons remain Pending | Non-causal/live limitation; decision required |
| Class order | Current trainer: two-class list; inference/firmware: four-class list | D004 order: fridge, microwave, dish washer, washer dryer | Explicit bundle contract required |
| Feature order | 23 slots with duplicate transition/duration positions | Final schema Pending | Explicit bundle contract required |
| Evaluation | H3 accuracy/report; optional Optuna selects on H3 test | Frozen metrics/aggregation still Pending; sealed candidate untouched | Not reusable as Protocol R evaluation |
| Firmware input | SD `/main.bin`, native float replay, no timestamps | Pico boundary planned as ordered numeric feature vector | Different deployment boundary |

Protocol R remains unchanged. Its approved manifest is [`protocol_r_approved_split.json`](../../artifacts/manifests/protocol_r_approved_split.json), canonical SHA-256 `b4509778dc15ccdf7a6ab48357cfcef90a28b58a5b12bbe57dfef0a590e24eb4`.

## 11. Reproduction Categories and Unresolved Items

### Directly reproducible from static structure, subject to a later execution task

- Python TM class/vote semantics and protobuf schema.
- The 23-slot/184-bit feature ordering as an observed Han compatibility target.
- C compressed-clause evaluation semantics.
- Root dependency resolution through the committed lock file.

### Requires path or configuration adaptation

- Explicit natural/lexicographic chunk order rather than relying on `glob` return order.
- Explicit class list, feature order, normalization statistics, and model paths.
- Placement/versioning of generated model headers and removal of missing-header ambiguity.
- A declared host-native input asset and build command.

### Requires a Protocol R wrapper

- Per-segment/per-fold state reset and full dependency containment.
- Approved house roles and D004 class set.
- Separation of aggregate-mains-only inference from label-assisted analysis.
- Training-only fit of preprocessing and validation-only selection.

### Missing evidence

- A unique canonical entry point.
- Original raw-REDD-to-submodule generation chain and original timestamps.
- Exact command, data, statistics, and `.ipb` that produced the committed model header.
- Any Python/C/Arduino parity fixture for features, Boolean bits, votes, or predictions.
- A self-contained Arduino or POSIX build at the fixed commit.
- Exact ESP32 board/core/compiler/library versions and any Pico implementation.
- Live sensor input, causal end-to-end operation, measured end-to-end latency, or sustained throughput.

### Requires Tianhang/ChatGPT review

- Which candidate defines the minimum Protocol H reproduction contract.
- Whether the duplicate 23-slot order is preserved for compatibility or corrected under an explicit deviation.
- Which components, if any, are approved for clean-room reuse or migration.
- Whether to reproduce Han’s two-class current trainer, the four-class committed header, or a separately declared compatibility class set.
- The exact PC/host/Pico boundary for the next task.

No reusable file or component is approved by this audit alone.

## 12. Evidence Ledger

| Conclusion | Source evidence | Status |
|---|---|---|
| README orders four staged scripts, then two integrated entries | `README.md : command block : lines 15-25 : a64118b23d828c5a52db9a5249faa304adbe8b51` | Documented only for cross-script order |
| Chunk load uses glob, concat, then backward fill | `redd_edge_detect.py : __main__ : lines 159-170 : 0165635187847d0f13f4f45d03a7c3e1e98dedd9` | Wired/reachable |
| Detector exposes threshold/noise/state tracking | `detector.py : EdgeDetector : lines 1-121 : 90ab3b0eeb4a59a1c83e54cef475036ec4db05f5` | Wired/reachable |
| Staged main-edge labels use appliance-channel overlap | `redd_edge_match.py : find_match : lines 23-48 : 7c70251f495ae0920969d5142de76be485e9f693` | Wired/reachable |
| Python event matcher supports many rises to one fall | `redd_event_pair.py : best_subset_dp/match_edges_stateful : lines 15-144 : 6bdbba6407972abdd333d2597b26d32555a3eeab` | Wired/reachable |
| Episode features use 32-sample pre/post context | `redd_event_pair.py : episode_feature_row : lines 157-203 : 6bdbba6407972abdd333d2597b26d32555a3eeab` | Wired/reachable |
| Current training split and feature/class order | `redd_tm_training.py : module constants : lines 18-60 : d49325cc51ea4d73065930a6830f4f22cdca66f8` | Wired/reachable |
| Booleanisation is CDF then round-to-even and MSB-first bits | `tsetlin/utils/booleanize.py : booleanize/booleanize_features : lines 26-63 : 6fd94469cef1b3a42926547eb19d4ad3499ed5b5` | Wired/reachable |
| TM is multiclass voting with positive-minus-negative clauses | `tsetlin/tsetlin.py : predict : lines 30-53 : 071071e2174d13d5c521052b94adfcfe4f8837be` | Wired/reachable |
| Training uses pairwise target/non-target feedback | `tsetlin/tsetlin.py : step : lines 55-109 : 071071e2174d13d5c521052b94adfcfe4f8837be` | Wired/reachable |
| Clause literal universe is positive and negated input features | `tsetlin/clause.py : Clause.__init__/evaluate : lines 11-61 : b6d7d4f241b09e1ad6e2ca7100a9050356c2b2dd` | Wired/reachable |
| Protobuf stores model dimensions and clause representations | `protobuf/tsetlin.proto : Tsetlin schema : lines 1-30 : d0d253ba58f0e7752bc5910cc218dcf2d7122baa` | Wired/reachable |
| Compiler emits fixed structural and requested model headers | `tsetlin/compiler/write.py : tsetlin_compile : lines 16-98 : f26ca9c973de54f557e1b8c5307b30624ddf315f` | Wired/reachable |
| Current integrated firmware model is four-class/184-input | `arduino/lime-tm/examples/nilm_inference/redd_model.h : tsetlin_model : lines 4020-4034 : fb25d363e4d6f3cc03061a7cd9f5b6cc7e205ab8` | Implemented; provenance unresolved |
| C evaluator uses signed class votes and argmax | `arduino/lime-tm/src/tsetlin.c : tsetlin_evaluate : lines 11-40 : 94ab6a0709523f2c38ca4712e9116586e690bd63` | Wired/reachable |
| Firmware input is SD `/main.bin` and a 100 ms file-replay loop | `arduino/lime-tm/examples/nilm_inference/nilm_inference.ino : setup/loop : lines 335-430 : 211c678077b8c8e40dd8b67e48a7b4ef96a45266` | Wired/reachable |
| Firmware pairs stored rises/falls FIFO | `arduino/lime-tm/examples/nilm_inference/nilm_inference.ino : match_edges_if_possible : lines 75-141 : 211c678077b8c8e40dd8b67e48a7b4ef96a45266` | Wired/reachable |
| Firmware feature extraction seeks into post-event file samples | `arduino/lime-tm/examples/nilm_inference/features.cpp : features_extract_and_log_matched_episode_features : lines 504-583 : 9efd457b9967832bf90f2529956e3dcee2678523` | Wired/reachable; non-live look-ahead |
| Integrated firmware quantiser produces 184 bits with floor×256 | `arduino/lime-tm/examples/nilm_inference/features.cpp : normalize_scale_and_booleanize8 : lines 334-388 : 9efd457b9967832bf90f2529956e3dcee2678523` | Wired/reachable; differs from Python |
| Display shows mains, edge/match counts, and class event counts | `arduino/lime-tm/examples/nilm_inference/chart.cpp : lv_chart_ui/lv_update_chart : lines 38-112 : aae2874e95ee5f47d4fa8174d38f29bb5f52108b` | Wired/reachable |
| POSIX entry replays a native-float file and invokes detector/features | `posix/main.c : main : lines 49-131 : f5c001015690bbaee65248bb8176597ff35f4761` | Wired/reachable in source; assets absent |
| Browser code reads `docs/redd` combined CSVs | `docs/js/script.js : loadBuildingCSV/caller : lines 40-45 and 192-192 : f82b6d4d71c33f08e0512e73fda01e9122875e6a` | Wired/reachable website path only |

The machine-readable companion is [`han_pipeline_source_inventory.json`](../../artifacts/manifests/han_pipeline_source_inventory.json). T003 remains **In progress** pending review; executable reproduction has not started.
