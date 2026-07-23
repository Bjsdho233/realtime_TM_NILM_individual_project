# Han Minimum Reproduction Result

> **Supersession note — 2026-07-23:** This file is the earlier contextual
> pre-reproduction record. The authoritative current-project T003 local evidence
> is the later, twice-repeated
> [`LOCAL_REPRODUCTION_REPORT.md`](../../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md):
> 410 test events, accuracy `0.965854`, macro F1 `0.914298`, C model data
> `9,058` bytes, and 1 live-versus-reload prediction mismatch. This earlier
> record reports 413 events, accuracy `0.9758`, about `0.94` macro F1,
> `9,004` bytes, and 0 mismatches. The difference is unresolved. Preserve both
> records, but do not mix their values or use this file as the current T003
> result.

**Run date:** 2026-07-21  
**Protocol:** Protocol H compatibility reproduction  
**Status:** Contextual pre-reproduction; superseded as current evidence by the
later archived local run

## Reproduction contract

Tianhang approved the following minimum contract on 2026-07-21:

- execute Han's staged PC route: edge detection, label-assisted edge matching, event pairing, and TM training;
- retain the upstream two-class trainer behaviour for `fridge` and `microwave`;
- train on Houses 1, 2, 4, 5, and 6 and test on House 3;
- retain the ordered 23-slot feature list, including the repeated `duration` slot, and 8-bit Booleanisation to 184 TM inputs;
- verify training-model save/load, inference-model save/load, prediction parity, and C-header export;
- exclude Protocol R, Pico, firmware, live input, and real-time claims.

The fixed upstream revision was `8c5e90df34236ba0afcc4ec46ac083d829de4d51`. The REDD submodule revision was `a621bbd6399e49c6798550618fe43b113149455b`.

## Execution boundary

The upstream clone and REDD submodule remained unmodified. The scripts were executed by absolute path from an isolated scratch run directory. REDD CSVs were exposed there through hard links because the container rewrote directory symlinks. Generated CSVs, logs, models, and headers were kept outside this project repository.

The runtime used Python 3.12.13. Existing scientific packages were NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0, and Matplotlib 3.10.8. The isolated runtime added bitarray 3.8.0, fastrand 3.0.8, loguru 0.7.3, tqdm 4.67.3, and protobuf 7.34.0.

No plotting flag, Optuna run, source modification, algorithm repair, Protocol R processing, host-native build, Pico build, or hardware work was performed.

## Staged data result

Edge detection processed all 35 pinned CSV chunks and 1,508,578 rows. Han's scripts concatenate each house with the observed upstream glob order and apply backward fill before detection.

The two-class matched-event dataset contained:

| Role | Houses | Fridge | Microwave | Total |
|---|---|---:|---:|---:|
| Train | H1, H2, H4, H5, H6 | 533 | 148 | 681 |
| Test | H3 | 371 | 42 | 413 |

H4 contributed neither target class, H6 contributed no microwave events, and H5 contributed one microwave event. These cases were retained as upstream-compatible behaviour rather than repaired.

## TM result

The default trainer configuration was used:

| Parameter | Value |
|---|---:|
| Classes | 2 |
| Ordered numeric feature slots | 23 |
| Unique feature names | 22 |
| Boolean inputs | 184 |
| Clauses | 200 |
| States | 50 |
| Boolean bits per numeric slot | 8 |
| Threshold `T` | 20 |
| Specificity `s` | 6.0 |
| Epochs | 10 |

House 3 results from the unmodified upstream trainer were:

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Fridge | 0.99 | 0.98 | 0.99 | 371 |
| Microwave | 0.85 | 0.93 | 0.89 | 42 |
| Macro average | 0.92 | 0.95 | 0.94 | 413 |

Overall accuracy was 97.58%. The confusion matrix, using `fridge=0` and `microwave=1`, was:

```text
[[364, 7],
 [  3, 39]]
```

The training model, reloaded training model, and reloaded inference model all produced identical predictions for all 413 H3 events in the 10-epoch diagnostic. The compiler exported a two-class, 184-input, 200-clause, 50-state C header and reported 9,004 model bytes.

Two independent 10-epoch executions produced byte-identical model files:

- training model SHA-256: `a485f2b1c4b0199f6da0d9479c97e79fe1f723f66faabf57939349ced9596ff6`;
- inference model SHA-256: `7c601eb62c5eb54e0c511b43297e340cad8e31a4dcc3a140f5c4e8bb112926e8`;
- generated model header SHA-256: `990b2170fc5c33f03bfa74c764c4ee704c95dabea886eb94abe8edbfb560537c`.

## Compatibility defect found

A one-epoch smoke run changed 11 of 413 predictions after model reload. Diagnostic inspection found 354 literals whose clause masks disagreed with their automaton actions even though the serialised automaton states were exact. Recompressing the in-memory clauses made its predictions identical to the reloaded model.

The cause is the upstream clause initialisation sequence: automaton states are reassigned after construction without refreshing their actions before the initial clause masks are compressed. Training can eventually remove enough disagreement for observed predictions to match, but it does not guarantee internal state/mask consistency. After 10 epochs, 32 internal disagreements remained even though all H3 predictions matched across save/load.

No compatibility fix was applied. Any repair must be a separately approved deviation with a regression test.

## Interpretation and limitations

This run proves that the pinned Han staged PC route can generate a two-class event dataset, train and serialise a TM, reload the inference representation, and export a C model header in the current environment.

It is not a Protocol R result. Event labels are constructed with appliance submeter assistance, H3 was already designated by Han's script as the compatibility test house, post-event samples enter the feature vector, and the run uses upstream concatenation and backward fill. The 97.58% accuracy and 0.94 macro F1 therefore must not be presented as aggregate-mains-only, causal, real-time, Pico, or formal dissertation-test performance.

Generated data, models, logs, and headers were intentionally not committed. The machine-readable result record is [`han_minimum_reproduction_result.json`](../../artifacts/manifests/han_minimum_reproduction_result.json).
