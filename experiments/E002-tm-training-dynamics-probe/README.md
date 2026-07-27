# Exploratory TM Training-Dynamics Probe

**Run date:** 2026-07-22\
**Status:** Archived exploratory evidence; not formal model selection\
**Upstream revision:** `8c5e90df34236ba0afcc4ec46ac083d829de4d51`

## Purpose

This probe asked whether changes confined to TM training could improve Han-compatible four-class event classification without changing event pairing, the ordered 23-slot feature vector, 184-bit Booleanisation, exported clause format, or embedded inference.

It tested three different levels of intervention:

- `T=20` versus `T=10`: ordinary parameter calibration;
- per-epoch shuffle and class sampling: training-order and feedback-allocation changes;
- hard-negative selection: a small multiclass feedback-mechanism change that replaces a random non-target class with the highest-voting non-target class.

The scripts and raw JSON files are preserved exactly as executed. They are prototype evidence, not production code migrated into the project baseline.

## Experimental boundary

| Item | Value |
|---|---|
| Classes | fridge, microwave, dish washer, electric furnace |
| Training houses | H1, H2, H4, H5, H6 |
| Evaluation house | H3 |
| Training events | 857: 533 / 148 / 84 / 92 |
| Evaluation events | 500: 371 / 42 / 13 / 74 |
| Ordered numeric slots | 23 |
| Boolean inputs | 184 |
| Clauses / states | 200 / 50 |
| `T` / `s` / epochs | 20 / 6.0 / 10 unless varied |
| Repeated runs | 3 seeds for screening; 5 seeds for confirmation |

The matched-event inputs were produced by the isolated Han minimum-reproduction run. Sixteen matched-transition CSV files were read, but no CSV, REDD data, model, or upstream source file is included in this archive. The deterministic aggregate input fingerprint is recorded in `experiment_manifest.json`.

## Sequence of tests

1. `tm_mechanism_probe.py` screened `T=10`, shuffle, 50% hard-negative, and 100% hard-negative against Han's blocked training order with three seeds.
2. `tm_mechanism_followup.py` screened shuffle plus hard-negative, uniform class sampling, and uniform class sampling plus hard-negative.
3. `tm_mechanism_confirm.py` extended the blocked baseline, 100% hard-negative, and uniform class sampling to five seeds.
4. `tm_balance_sweep.py` tested

   \[
   P(c) \propto n_c^\alpha, \qquad \alpha \in \{1,0.75,0.5,0.25,0\},
   \]

   first with replacement and then with a coverage-preserving rule. The second rule avoids duplicates unless a class is oversampled and makes `alpha=1` exactly equivalent to ordinary shuffle.

The custom random-negative update was checked against upstream `Tsetlin.step()` on the first 20 training events at a fixed seed. A state-signature mismatch would have stopped each experiment.

## Main results

### Five-seed comparisons

| Training method | Macro F1, mean +/- sample SD | Accuracy | Paired result against blocked baseline |
|---|---:|---:|---:|
| Blocked upstream order | 0.4809 +/- 0.0210 | 0.7868 | Reference |
| Per-epoch unique shuffle | **0.5288 +/- 0.0097** | 0.7640 | +0.0479; 5/5 seeds higher |
| 100% hard-negative | 0.4920 +/- 0.0111 | 0.7844 | +0.0111; 3/5 seeds higher |
| Uniform class sampling, initial implementation | 0.5456 +/- 0.0267 | 0.7424 | Confounded by order and replacement sampling |

The initial uniform-sampling result should not be treated as a stable gain. It changed both class exposure and sample order, and it sampled with replacement. The later sweep separated these effects.

### Coverage-preserving balance sweep

| Training method | Class updates per epoch | Macro F1 | Accuracy | Dishwasher F1 | Furnace F1 |
|---|---:|---:|---:|---:|---:|
| Unique shuffle | 533 / 148 / 84 / 92 | **0.5288** | **0.7640** | 0.064 | **0.315** |
| `alpha=0.75` | 451 / 172 / 113 / 121 | 0.5175 | 0.7488 | 0.073 | 0.302 |
| `alpha=0.5` | 366 / 193 / 146 / 152 | 0.5243 | 0.7408 | **0.112** | 0.286 |
| `alpha=0.25` | 286 / 207 / 180 / 184 | 0.5145 | 0.7260 | 0.094 | 0.268 |
| `alpha=0` | 215 / 214 / 214 / 214 | 0.5200 | 0.7132 | 0.101 | 0.303 |

No tested balance strength exceeded unique shuffle in mean Macro F1 or accuracy. `alpha=0.5` improved dishwasher F1, but the gain came with lower accuracy and weaker performance elsewhere.

### Other screening results

- `T=10` reached `0.4392` Macro F1 over three seeds, below the corresponding `T=20` baseline at `0.4685`.
- The three-seed shuffle screen reached `0.4929`; the separate five-seed unique-shuffle run reached `0.5288`. Both used one copy of every training event per epoch but different shuffle random streams, so the size of the gain remains order-seed sensitive.
- Hard-negative feedback did not show a reliable gain. The five-seed paired comparison won three times and lost twice.
- Combining shuffle or class balance with hard-negative feedback did not show additive improvement.
- Mean clause length remained close to the baseline, so none of these training-only variants implies a material change to the exported inference structure.

## Interpretation

The only sufficiently consistent signal in this probe is that Han's appliance-blocked online training order is a weak baseline. Randomly shuffling every original event once per epoch should be the control condition for later mechanism work.

The probe does not support enabling global class balancing or hard-negative feedback by default. Those ideas may be revisited against a training-side validation split, especially if the objective explicitly prioritises dishwasher recall, but they are not current improvements to the formal method.

`T=10` was also not supported by this dataset. This is evidence against transferring a generic threshold heuristic directly to the current NILM task, not evidence that `T=20` is globally optimal.

## Limitations

- H3 was evaluated repeatedly during exploration. These metrics are diagnostic compatibility results and cannot be used as a locked dissertation-test result.
- The four-class set includes `electric furnace`, whereas the approved Protocol R candidate set uses `washer dryer`.
- Event construction is label-assisted and the feature vector includes post-event information. This is not aggregate-mains-only, causal, or real-time evidence.
- The experiment changes training only. It does not validate Pico execution, model export, firmware, latency, or memory.
- The archived scripts retain their original scratch-layout path assumptions. Reusing them requires an equivalent external Han checkout and matched-event directory or a separately reviewed path-only adaptation.

## Archive contents

- `scripts/`: exact source used for the probe, follow-up, confirmation, and balance sweep;
- `results/`: raw per-seed metrics, confusion matrices, clause summaries, vote summaries, and aggregate summaries;
- `experiment_manifest.json`: machine-readable scope, fingerprints, and final interpretation;
- `CHECKSUMS.sha256`: integrity hashes for every preserved source and result file.

No formal project phase is advanced by this archive.
