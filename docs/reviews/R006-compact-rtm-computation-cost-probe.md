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
- Stop observation: the child had accumulated approximately 948.3 CPU seconds
  and the active fresh-model fit had not returned. The runner did not persist or
  print step boundaries, so the active staircase step and its exact elapsed time
  cannot be established retrospectively.
- Memory observation immediately before termination: `PageFileUsage` was
  543,020 KiB (approximately 530.3 MiB) while `WorkingSetSize` had been trimmed
  to 253,952 bytes. System free physical memory was previously observed between
  approximately 2.5 and 3.3 GiB during the run.
- Action: the exact C8 process was conservatively terminated under the
  unexplained-runtime-or-memory-growth stop rule. `PageFileUsage` alone is not
  treated as proof that operating-system swapping occurred. No C11 process was
  started.
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

## Bounded TMU adapter integration attempt

### Agent Brief

- Status: `INFRASTRUCTURE_FAILED`
- Date: 2026-07-29
- Scope: deterministic synthetic integration only
- Implementation commit:
  `8541cfdab69d3cdc36040579321f603f9bd73403`
- RunSpec SHA-256:
  `9c1585e54aa46fc31641740ed52e5ed608768146b901e65392626e009af340bd`
- Scientific conclusion: `INCONCLUSIVE`
- R006: remains halted
- T006: remains paused

在 fake-task 专项测试和完整 repository check 通过后，唯一获准的
real-TMU synthetic smoke 通过 `bounded_supervisor.py` 启动。RunSpec 冻结为
C8/C11 各 `256` rows、one epoch、`max_workers: 1`、per-step `120 s`、
total `300 s`、minimum available RAM `1.5 GiB`，并禁止 retry、REDD access、
predictive metrics 和 capability claim。

第一个 C8 step 在进入 TMU import 和 `fit()` 前被 worker contract 拒绝：

```text
WORKER_CONTRACT_ERROR: step authority bootstrap_pid mismatch: expected 4632, got 14376
```

观测到的 PID 是 supervisor `31756`、bootstrap `14376` 和 RunSpec command
launcher `4632`。Windows virtual-environment Python launcher 在 bootstrap
和实际 worker interpreter 之间增加了一层进程；现有 worker 错误地把其
direct parent `4632` 当成 bootstrap，而 supervisor 签发的正确 bootstrap
PID 是 `14376`。因此终态是 `INFRASTRUCTURE_FAILED`，wall time
`1.578 s`，completed steps `0/2`。C11 未启动，没有 retry，没有 child
result，没有模型、指标、REDD access 或科学结论。终止后复核三个已记录
PID 均不再存活。

机器可读的复核记录见
[R006 bounded adapter invalid run](R006-bounded-tmu-adapter-invalid-run-2026-07-29.json)。
该问题必须在另一轮明确授权的 implementation repair 中解决；本次不得
把 synthetic timing 用于估计 C8/C11 REDD cost，也不构成 T006 method
approval。
