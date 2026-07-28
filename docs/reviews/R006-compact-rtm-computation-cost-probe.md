# R006 — Compact rTM Computation Cost Probe

## Agent Brief

- Status: active — pre-run specification stage
- Owner: Tianhang Tan
- Authorised: 2026-07-28
- Execution type: explicit engineering cost-measurement exception to ordinary
  read-only R-series rules
- Primary candidate: C11
- Low-cost reference: C8
- Deferred: C14 and the old 32-lag/256-bit design
- Claim boundary: computation cost only; no predictive performance or method
  approval
- T006 status: paused

## Frozen probe inputs

The exact execution contract is
[R006-probe-spec.json](R006-probe-spec.json). Its byte SHA-256 is recorded in
the adjacent sidecar before any TMU fit.

This probe does not approve its `FeatureSpec`, `BooleaniserSpec`, provisional
`ModelSpec`, or target stimulus for a later T006 capability run.
