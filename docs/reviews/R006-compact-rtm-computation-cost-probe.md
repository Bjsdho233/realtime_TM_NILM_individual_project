# R006 — Compact rTM Computation Cost Probe

## Agent Brief

- Status: halted — first execution triggered the runtime/paging stop rule
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

## Halted run record

- Date: 2026-07-28
- Frozen implementation commit:
  `073b28167066532b8b2863f1fd3f99ef8fbf62d1`
- Candidate started: C8 only
- Candidate not started: C11
- TMU path: TMU 0.8.3 `TMRegressor`, CPU fallback, one process at a time
- Wrapper PID: `45108`
- TMU computation child PID: `26332`
- Process creation time: 2026-07-28 22:41:58 Europe/London
- Stop observation: the child had accumulated approximately 948.3 CPU seconds;
  its current 131,072-row fresh-model fit had not returned after more than 10
  minutes.
- Memory observation immediately before termination: `PageFileUsage` was
  543,020 KiB (approximately 530.3 MiB) while `WorkingSetSize` had been trimmed
  to 253,952 bytes. System free physical memory was previously observed between
  approximately 2.5 and 3.3 GiB during the run.
- Action: the exact C8 process was terminated under the frozen stop rule. No C11
  process was started.
- Partial output: none. The intended temporary
  `c8-staircase.json` did not exist after termination.

The runner writes its aggregate JSON only after the staircase returns, so the
completed smaller-step timings were not recoverable from this interrupted run.
They must not be reconstructed from total process CPU time. Consequently R006
does not provide a valid per-step timing table, scaling projection, C8/C11
comparison, or computational-suitability decision.

This is an invalid/incomplete engineering run, not negative predictive evidence.
No performance metric was calculated, no model was saved, no method was
approved, and T006 remains paused. Further execution requires a separate
instruction; a future implementation-only repair should checkpoint each
completed step before starting the next one and enforce the wall-time stop
outside the blocking TMU `fit()` call.
