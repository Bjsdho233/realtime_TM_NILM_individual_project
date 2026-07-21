# T002 Protocol R Class Fallback — 2026-07-21

**Task:** T002 — REDD Inventory and Protocol R Preflight\
**Status:** Complete

## Decision and Evidence

- The original four-class set failed because `electric furnace` had 1 complete cycle in the sealed H2+H4 candidate test against the frozen minimum of 10. Its pool and fold support and long active duration remain recorded as historical evidence.
- `washer dryer` was declared optional before the audit and passed the same frozen standard: 89 pool cycles, fold counts 16/55/18, 11 candidate cycles, and 11,811 candidate active seconds.
- Tianhang explicitly approved the fallback before any model prediction, F1, accuracy, or other model metric was generated or viewed.
- Thresholds, house allocation, folds, segment/block resets, boundary containment, and the prohibition on `docs/redd` input were unchanged.
- The approved classes are fridge, microwave, dish washer, and washer dryer.

## Commits and Manifest

- D004 decision commit: `c6ceb9a81da1fe24d79c935a0e9ffea3022fa0c2`.
- Approved split commit: `3669e900cb5fa9c4c1890413c238ef693a163ada`.
- Approved manifest: `artifacts/manifests/protocol_r_approved_split.json`.
- Approved manifest canonical SHA-256: `b4509778dc15ccdf7a6ab48357cfcef90a28b58a5b12bbe57dfef0a590e24eb4`.
- The predecessor manifest remains unchanged with canonical SHA-256 `480a738ad799860f6cdecbba9affb1d76c365a71468b276b8b0669ea55bba11a`.

## Completion Boundary

T002 completion proves that the approved four classes satisfy the frozen support standard when candidate support is pooled across H2 and H4. Candidate-test support labels were inspected only for feasibility. H2/H4 remain sealed for model development and performance tuning.

A missing target column means the label is unavailable; it is not an all-zero ground truth. Missing-label eligibility, cross-house scoring, and macro aggregation must be frozen before first model evaluation.

T003 has not started. No detector, pairing, feature, training, inference, model-scoring, firmware, Pico, or hardware work was performed.
