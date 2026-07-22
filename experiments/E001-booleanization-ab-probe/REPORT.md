# E001 Booleanization A/B Probe

**Status:** Complete\
**Decision:** **inconclusive**\
**Scope:** Exploratory scratch probe only; not formal model selection, T004, a protocol change, or final thesis evidence.

## Data boundary

Only existing matched-transition CSVs for H1, H3, H5, and H6 were read. H2 and H4 remained sealed and were not read. Files were stably sorted by `start`; files with at least five events used the first floor(80%) for training and the remainder for validation.

| House | Appliance | Events | Train | Validation |
|---|---|---:|---:|---:|
| H1 | fridge | 224 | 179 | 45 |
| H1 | microwave | 91 | 72 | 19 |
| H1 | dish washer | 35 | 28 | 7 |
| H3 | fridge | 342 | 273 | 69 |
| H3 | microwave | 33 | 26 | 7 |
| H3 | dish washer | 10 | 8 | 2 |
| H3 | electric furnace | 48 | 38 | 10 |
| H5 | fridge | 17 | 13 | 4 |
| H5 | microwave | 1 | 1 | 0 |
| H5 | electric furnace | 8 | 6 | 2 |
| H6 | fridge | 103 | 82 | 21 |

The H5 microwave file contained one event and was retained entirely in training. Training contains 726 rows and validation contains 186 rows. Validation contains all four classes.

## Encoding comparison

`han_binary` exactly uses Han's training-set mean/std, standardisation, Gaussian CDF, and ordinary 8-bit binary representation. It can represent at most 256 levels per feature.

`threshold_8` fits q = 1/9 through 8/9 empirical quantiles from training rows only, using NumPy's deterministic `linear` quantile method, and emits `value >= threshold` bits. It can represent at most 9 levels per feature. Repeated thresholds and bits are retained.

Both use 23 × 8 = 184 bits. This is therefore an overall comparison of numerical resolution and monotonic structure under the same bit budget, not merely a bit reordering.

## Ordered feature slots

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

The duplicate `duration` slots 2 and 7 are retained.

## Fixed TM contract

- Han Tsetlin implementation at `${HAN_UPSTREAM_ROOT}`
- Four classes in the fixed requested order
- 200 clauses, 50 states, T=20, s=6.0
- 10 epochs
- Seeds 0–4
- One unique full training-event shuffle per epoch
- No balancing, hard negatives, Drop Clause, multigranular s, or hyperparameter search

## Results

| Encoding | Accuracy mean ± sample SD | Macro F1 mean ± sample SD | Training seconds mean ± sample SD |
|---|---:|---:|---:|
| han_binary | 0.938710 ± 0.004809 | 0.784087 ± 0.031076 | 11.401 ± 0.484 |
| threshold_8 | 0.943011 ± 0.007213 | 0.801266 ± 0.036470 | 10.827 ± 0.411 |

| Seed | han_binary Macro F1 | threshold_8 Macro F1 | Paired delta |
|---:|---:|---:|---:|
| 0 | 0.761802 | 0.817944 | +0.056142 |
| 1 | 0.831572 | 0.744516 | -0.087056 |
| 2 | 0.765157 | 0.821146 | +0.055989 |
| 3 | 0.761802 | 0.836086 | +0.074284 |
| 4 | 0.800101 | 0.786638 | -0.013463 |

Mean paired Macro-F1 delta: **+0.017179**.\
Wins/losses/ties for threshold_8: **3/2/0**.

The promising rule requires a mean improvement of at least 0.02 and wins in at least 4 of 5 seeds. Result: **inconclusive**.

Per-class F1 values, confusion matrices, training times, model-state hashes, fitted parameters, file hashes, and sample standard deviations are in `per_seed_metrics.csv` and `summary.json`.

## Checks

- Both encodings used identical training/validation rows and labels.
- Both emitted exactly 184 bits with only 0/1 values.
- All fitted parameters used training rows only.
- Raw and encoded values contained no NaN or infinity.
- Paired encodings used identical initial model state for each seed.
- Repeating seed 0 reproduced predictions, metrics, and final model state for both encodings.

## Limitations

This uses legacy label-assisted matched-event data and is not Protocol R. It does not test TMU, another trainer, model export, firmware, Pico, Arduino, deployment, causal aggregate-only inference, or real-time behaviour. No result here changes the approved research protocol or formal class decision.
