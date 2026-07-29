# T006 — Direct rTM NILM Prototype

## Agent Brief

- Status: paused pending separately authorised R004 review
- Owner: Tianhang Tan
- Authorised: 2026-07-28
- Track: T-series prototype
- Claim scope: Protocol R development feasibility only
- External action: local commits only; no push, branch, PR or merge

## 1. Question

不使用 event detection、pairing、future context 或 appliance label features，vanilla TMU
regression Tsetlin Machine 能否从一个严格 causal 的 aggregate mains window，逐样本输出有意义的
fridge power estimate？

本任务是小型学生毕设原型，不是正式 Protocol R result，也不是生产级系统。完成标准首先是代码可读、
可运行、边界可解释；结果可以是正面、负面或有限。

## 2. Fixed run

- appliance: `fridge`
- Protocol R fold: `F1`
- training blocks: `B2`, `B3`, `B4`
- validation block: `B1`
- houses: `H1`, `H3`, `H5`, `H6`
- seed: `0`
- target at row `t`: `max(0, fridge[t])`
- ON threshold: `> 15 W`
- output time: `t`; future delay `D=0`
- input: `main[t-31:t+1]`, 32 samples / nominal 96 seconds
- eligible target population: frozen T004 common valid target range
  (`block_start + 255 <= t < block_end - 8`)
- training cap: at most 50,000 rows, selected by evenly spaced row positions
- validation: every eligible row

Every segment/block boundary resets the causal window. A non-finite aggregate value invalidates the current
window; unavailable or non-finite fridge targets are excluded and are never replaced with zero.

## 3. Preprocessing and model

- environment: reviewed Python 3.11 / NumPy 1.26.4 / TMU 0.8.3 lock under
  `docs/research_notes/2026-07-24-tmu-regression-smoke-test/`
- Booleanisation: `StandardBinarizer(max_bits_per_feature=8)`, fitted only on selected training rows
- model: fresh CPU `TMRegressor`
- clauses `200`, `T=200`, `s=3.0`, unweighted clauses
- max included literals `16`, number of state bits `8`
- feature negation enabled; clause/literal drop `0`
- five explicit one-epoch `fit(..., shuffle=True)` calls

Before REDD access, a synthetic import/fit/predict check must confirm finite, correctly shaped,
non-constant predictions and record the installed TMU version plus SHA-256 of `vanilla_regressor.py`.

## 4. Comparisons and reporting

The same validation rows compare:

1. zero prediction;
2. selected-training-target mean;
3. raw rTM prediction;
4. rTM prediction clipped to `[0, selected training target maximum]`.

Report validation/ON counts, prediction range and unique count, raw outside-range fraction, full MAE,
median absolute error, pooled NAE, ON MAE, state precision/recall/F1, mean OFF false-positive watts,
and fit/predict times. One relative-time figure shows true fridge, clipped rTM and aggregate mains around
the first complete validation fridge ON interval.

The implementation is operational if the synthetic and real runs complete with finite arrays of the
expected length and produce the metrics and figure. It shows useful signal only if clipped pooled
`NAE < 1` and predictions are non-constant. Otherwise the fixed interpretation is:
“did not yet show useful signal”.

## 5. Explicit exclusions

- no B5 or Protocol X access;
- no tuning, second fold, second seed, weighted rTM, gate or post-processing experiment;
- no event/pairing or hand-designed appliance feature path;
- no model export, host parity, Pico or hardware work;
- no E-series registry, new schema, checksum bundle, provenance archive or experiment matrix;
- no automatic start of another task.

## 6. Planned durable outputs

- this task record;
- minimal implementation under `tools/rtm/`;
- focused tests under `tests/rtm/`;
- `experiments/T006-direct-rtm-nilm-prototype/result.json`;
- `experiments/T006-direct-rtm-nilm-prototype/PROTOTYPE_REPORT.md`;
- one figure under `experiments/T006-direct-rtm-nilm-prototype/figures/`.

The implementation/source/test checkpoint is committed locally before the real run. The final result is
committed locally after checks. Neither commit is pushed by this task.

## 7. Pause record — 2026-07-28

The first real-data process was stopped before completion. At termination it had run for approximately
47 minutes 37 seconds wall time and accumulated 2786.125 CPU seconds. No prototype archive directory,
`result.json`, report, figure, model or row-level output had been created.

The implementation checkpoint remains
`a8ee6f7eb8691e81f603c6960b4ae812c9b91793`. T006 is paused pending a separately authorised
`R004 — rTM NILM Input and Booleanisation Review`; this note does not authorise that review or a resumed run.

## 8. Post-R004 method boundary — 2026-07-28

Tianhang accepted
[D007 — Direct rTM NILM Prototype Method Boundary](../decisions/D007-direct-rtm-nilm-prototype-method-boundary.md).
The original `32 raw lags + StandardBinarizer` route is retained only as a
diagnostic reference and must not be resumed as the formal run.

Compact causal level/change/multi-scale input and hybrid cumulative
Booleanisation may proceed to static audit. Exact horizons, features, bits and
target clipping/scaling remain pending. The minimum architecture remains vanilla
direct rTM; the first fridge prototype does not add a cTM gate, weighted rTM or
OFF resampling. T006 remains paused and this update creates no training authority.

## 9. D008 workflow and model-family decision — 2026-07-29

Tianhang accepted
[D008 — Public rTM Workflow and Integer-Weighted Model Family](../decisions/D008-public-rtm-workflow-and-integer-weighted-model.md).
The public implementation will be a flat workflow under `system/`, with clear
data generation/supply, feature, Booleanisation, model, training, testing and
thin-entry responsibilities. Replacing a feature or Booleanisation candidate
must not change the main training/testing flow.

The selected model family is TMU 0.8.3 `TMRegressor` with
`weighted_clauses=True`. This supersedes D007's vanilla-only boundary and
weighted-rTM deferral. It does not modify or validate the old unweighted
checkpoint, which remains diagnostic/history only.

Exact features, Boolean bits and thresholds, target transformation, model
hyperparameters and run configuration remain pending. T006 remains paused; this
decision creates no implementation, REDD-access, training, prediction or
scoring authority.
