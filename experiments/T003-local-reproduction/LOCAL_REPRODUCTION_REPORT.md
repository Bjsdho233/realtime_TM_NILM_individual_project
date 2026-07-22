# T003 Han Two-Class PC Pipeline Local Reproduction

**Status:** Complete\
**Project:** `${PROJECT_ROOT}` at `14f523033cf2aff185e61f30506552476e4afc81`\
**Han:** `${HAN_UPSTREAM_ROOT}` at `8c5e90df34236ba0afcc4ec46ac083d829de4d51`\
**REDD:** `${HAN_REDD_ROOT}` at `a621bbd6399e49c6798550618fe43b113149455b`\
**Run root:** `${T003_RUN_ROOT}`

## Boundary and authorised deviation

Both complete runs were executed locally in separate run directories with the same isolated Python 3.12.13 environment. Han and REDD remained read-only. The only harness deviation authorised after the prior stopped run was to mirror Han's trainer by skipping missing or empty house/class matched-transition files. No algorithm, feature, data, parameter, state, or mask repair was applied.

The project had been safely fast-forwarded to `origin/main` before execution. It was not manually edited. No commit, push, merge, rebase, Protocol R, Pico, firmware, or hardware operation occurred.

## Input and staged-event inventory

| House | Input rows | Main transients | Fridge transients | Microwave transients | Dishwasher transients | Furnace transients | Edge-matching rows | Paired fridge | Paired microwave |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H1 | 348731 | 1573 | 519 | 283 | 299 | missing | 1573 | 231 | 107 |
| H2 | 292063 | 2024 | 657 | 104 | 95 | missing | 2024 | 257 | 40 |
| H3 | 242044 | 1982 | 902 | 121 | 40 | 159 | 1982 | 368 | 42 |
| H4 | 274983 | 1165 | missing | missing | 23 | 303 | 1165 | 0 | 0 |
| H5 | 24181 | 171 | 45 | 4 | 0 | 57 | 171 | 7 | 1 |
| H6 | 326576 | 1062 | 589 | missing | 0 | missing | 1062 | 36 | 0 |

Training distribution: fridge 531, microwave 148, total 679.\
Test distribution: fridge 368, microwave 42, total 410.

All 35 REDD source CSV paths, sizes, and SHA-256 values were identical between the runs. Both runs generated 51 staged CSVs with zero path or content-hash mismatches.

## Ordered feature contract

1. `transition`
2. `duration`
3. `pos_transition_magnitude`
4. `neg_transition_magnitude`
5. `abs_transition`
6. `log_abs_transition`
7. `duration`
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

There are 23 ordered slots and 22 unique feature names. `duration` appears at slots 2 and 7. Booleanisation produced exactly 23 × 8 = 184 bits for every train and test sample.

## One-epoch smoke test

- Accuracy: 0.919512195122
- Confusion matrix: `[[365, 3], [30, 12]]`
- Before-save versus training reload: 12 prediction mismatches
- Before-save versus inference reload: 12 prediction mismatches
- Training reload versus inference reload: 0 prediction mismatches
- Training model: 149612 bytes, SHA-256 `2e45d636e63ce6407bba7ca1b81230b0c904bc0111379631e32cd2ff8b0f8243`
- Inference model: 6563 bytes, SHA-256 `83b90ca56dd3397202603380156a992ffe83bd4d2a5f796afe87e7fc022f9219`

## Ten-epoch result

| Scope | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Fridge | 0.991666666667 | 0.970108695652 | 0.980769230769 | 368 |
| Microwave | 0.780000000000 | 0.928571428571 | 0.847826086957 | 42 |
| Macro | 0.885833333333 | 0.949340062112 | 0.914297658863 | 410 |

- Accuracy: 0.965853658537
- Confusion matrix: `[[357, 11], [3, 39]]`
- Before-save versus training reload: 1 prediction mismatch
- Before-save versus inference reload: 1 prediction mismatch
- Training reload versus inference reload: 0 prediction mismatches
- Training model: 149612 bytes, SHA-256 `b975d5223e943b93a4351b3de429e9fca47c1a4b713a5342864ce5d65ba65932`
- Inference model: 5666 bytes, SHA-256 `22b932c433ae672dd128505d2f8c49bea47278a8f0eb90a9811aa9a5d67ba210`
- C header export: successful
- C model data: 9058 bytes
- Model header SHA-256: `3b112732c16327e344c7d5a16f3fe2b8514483d0802c34734c1b8ffe50a1db2b`

The non-zero 10-epoch reload mismatch means save/reload parity is not complete even though both reloaded representations agree with each other.

## State, action, and clause-mask diagnosis

| Point | Total automata | State/action disagreement | Action/mask disagreement | State/mask disagreement |
|---|---:|---:|---:|---:|
| Initialization | 147200 | 73600 | 0 | 73600 |
| After 1 epoch | 147200 | 0 | 374 | 374 |
| After 10 epochs | 147200 | 0 | 29 | 29 |

These are diagnostic observations only. No recompression or source repair was applied.

## Independent-run repeatability

The two complete runs were identical for:

- source-data inventories and staged house/event inventories;
- all 51 generated staged CSV hashes;
- 1-epoch and 10-epoch prediction vectors and metrics;
- diagnostics;
- training and inference model SHA-256 values;
- generated C headers.

Overall compared-evidence identity: **True**.

Measured from the first generated `building_1_raw.csv` artifact through `run_result.json`, run 1 took 959.854 seconds and run 2 took 949.943 seconds. These are lower-bound full-run intervals because they begin after H1 raw concatenation. The harness portions took 8.550 seconds and 8.954 seconds respectively. The full preprocessing command trace is retained in `commands.log`.

## Comparison with the remote pre-reproduction record

The fixed source revisions and pipeline contract agree, but the local evidence differs:

| Item | Local formal run | Remote pre-reproduction |
|---|---:|---:|
| Train fridge events | 531 | 533 |
| Test fridge events | 368 | 371 |
| Train microwave events | 148 | 148 |
| Test microwave events | 42 | 42 |
| Accuracy | 0.965854 | 0.9758 |
| Macro F1 | 0.914298 | approximately 0.94 |
| 1-epoch reload mismatches | 12 | 11 |
| 10-epoch reload mismatches | 1 | 0 |
| 10-epoch state/mask disagreements | 29 | 32 |
| C model bytes | 9058 | 9004 |

The model hashes also differ. The cause is unresolved and was not adjusted away. The remote record remains contextual pre-reproduction evidence, not a target or substitute for this local result.

## Interpretation

This proves the pinned Han-compatible, label-assisted two-class PC staged route can be executed twice reproducibly on this Windows host, including model serialization and C export. It does not establish Protocol R, aggregate-only, causal, real-time, Pico, firmware, or dissertation-test performance.
