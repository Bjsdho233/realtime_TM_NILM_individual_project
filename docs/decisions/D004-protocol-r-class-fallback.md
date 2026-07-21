# D004 — Protocol R Class Fallback

**Status:** Accepted by Tianhang\
**Date:** 2026-07-21\
**Applies to:** T002 Protocol R candidate split approval

## Context

[`D003`](D003-redd-sequence-time-contract.md) and the original support audit remain valid historical evidence. This decision does not overwrite or revise either record.

The original four-class candidate set was:

- `fridge`;
- `microwave`;
- `dish washer`;
- `electric furnace`.

Under the support standard frozen before the audit, `electric furnace` produced:

- 38 complete cycles in the train/validation pool;
- 10, 15, and 13 complete cycles in validation folds 1, 2, and 3;
- no `electric furnace` column in House 2;
- 1 complete cycle in House 4;
- 824,943 seconds of candidate active duration.

The candidate-test requirement is at least 10 complete cycles. Long active duration cannot substitute for complete-cycle support, and one complete cycle is insufficient for a credible test result.

`washer dryer` was declared by D003 before the audit as the optional fifth class and was audited under the same frozen standard. It produced:

- 89 complete cycles in the train/validation pool;
- 16, 55, and 18 complete cycles in validation folds 1, 2, and 3;
- 11 complete cycles across the Houses 2 and 4 candidate test;
- 11,811 seconds of candidate active duration.

It satisfies every frozen support minimum.

## Decision

Before viewing any model prediction, F1, accuracy, or other model metric, Tianhang explicitly approved the predeclared class fallback.

The approved Protocol R four-class set is:

- `fridge`;
- `microwave`;
- `dish washer`;
- `washer dryer`.

`electric furnace` is classified as:

> unsupported for the approved Protocol R candidate test under the frozen support standard

Its failed support evidence must remain available and must not be described as a model-performance failure.

## Unchanged Contract

The following remain unchanged:

- Houses 1, 3, 5, and 6 form the train/validation pool;
- Houses 2 and 4 form the sealed candidate test;
- three blocked validation folds;
- nominal cadence of 3 seconds;
- active threshold of 15 W;
- minimum active run of two samples;
- complete-cycle definition;
- minimum support thresholds;
- state reset at every segment and block boundary;
- full-dependency containment;
- `docs/redd` is not a Protocol R input.

No house, source file, row range, fold, threshold, boundary, or data-processing rule is changed by this fallback.

## Candidate-Test Access Statement

Candidate-test support labels were inspected for the predeclared feasibility audit. No model output, prediction, F1, accuracy, or other model metric was generated or viewed. Houses 2 and 4 remain sealed against model development and performance tuning.

The project must not claim that candidate-test labels were never viewed. It must state the limited support-label access accurately.

If a house lacks a target appliance column, the label is unavailable. This must not be interpreted automatically as proof that the appliance was absent, and it must not be filled with all-zero ground truth.

## Scope and Consequences

T002 establishes only that the approved four classes satisfy the frozen support standard when candidate support is pooled across Houses 2 and 4. Cross-house scoring, missing-label eligibility, and macro aggregation remain unresolved and must be frozen before the first model evaluation.

This decision authorises the successor approved manifest and T002 closure evidence. It does not authorise T003, the Han pipeline, detector or pairing execution, feature extraction, training, inference, model scoring, firmware, Pico, or hardware work.
