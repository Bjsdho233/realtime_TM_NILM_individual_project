# D008 — Public rTM Workflow and Integer-Weighted Model Family

## Agent Brief

- Status: Accepted by Tianhang
- Date: 2026-07-29
- Scope: public `system/` workflow boundary and rTM model family
- Supersedes: D007 only where it retained vanilla rTM and deferred weighted rTM
- Training, prediction or scoring authority: none
- T006 status: paused

## Decision

The public prototype is a focused rTM NILM workflow, not a general NILM
platform. Its visible main path follows the practical separation used by small
research repositories:

```text
data generation / supply
  -> feature construction
  -> Booleanisation
  -> model definition
  -> training
  -> testing
  -> thin entry point
```

Feature and Booleanisation candidates may be replaced without changing the
training and testing flow. This is a direct module boundary, not a plugin system,
model registry or multi-dataset benchmark framework.

The selected model family is TMU 0.8.3 `TMRegressor` with
`weighted_clauses=True`, referred to in this project as the TMU
integer-weighted rTM. The first implementation remains CPU-side and does not add
a cTM gate or a model ensemble.

## Still pending

This decision does not freeze:

- the exact sample definition beyond the accepted causal/no-future boundary;
- C8, C11 or another exact feature set;
- Boolean thresholds, fit population or bit allocation;
- target clipping, scaling, inverse mapping or out-of-range behaviour;
- clause count, `T`, `s`, epochs or other training configuration;
- OFF resampling, post-processing or final evaluation metrics;
- any real-data, capability, cost-probe or formal evaluation run.

These items remain separate research decisions. No default in TMU or in the
workflow implementation may fill them silently.

## Source classification

- TMU 0.8.3 `TMRegressor(weighted_clauses=True)`: `Inherited`; the fixed TMU
  source is the executable model definition.
- The integer-weighted rTM paper: `Inherited` conceptual reference. TMU 0.8.3
  has implementation semantics documented in R003 that differ from the paper,
  so the paper is not a claim of source parity.
- Applying sample-wise weighted rTM regression to causal aggregate NILM:
  `Adapted`.
- Exact feature, Booleanisation and target choices: still
  `Project-designed` unless a later decision records another source.
- Separating data, model, training, testing and thin entry modules without
  changing their algorithmic meaning: `Implementation-only`.

## Consequences

- D007 remains historical and continues to govern its unchanged decisions:
  `32 raw lags + StandardBinarizer` is diagnostic only; exact input and target
  choices remain pending; cTM gating and fridge OFF resampling are not introduced.
- D007's vanilla-only architecture and weighted-rTM deferral are superseded.
- The old unweighted T006 implementation remains a diagnostic/historical
  checkpoint. It must not be resumed or silently rewritten as the new method.
- The halted unweighted R006 probe remains historical infrastructure/cost
  evidence only and cannot estimate the selected weighted model.
- Future public implementation belongs under `system/`, in small
  human-reviewed increments.
- T006 remains paused. This decision does not authorise TMU execution, REDD
  access, training, prediction, scoring or the next task.
