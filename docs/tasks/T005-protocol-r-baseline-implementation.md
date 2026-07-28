# T005 — Protocol R Baseline Implementation

## Agent Brief

- Work ID: T005
- Track: T-series
- Lifecycle status: active — authorised 2026-07-28
- Owner: Tianhang Tan
- Execution boundary: local-only Protocol R B1–B4 development
- Classes: fridge, microwave, dish washer development-only
- Protected data: B5, H2/H4 and Protocol X prohibited
- External actions: local task-scoped commits only; no push/branch/PR

## 1. Objective

在冻结的 Protocol R v1 contract 下，实现并执行第一个 clean
aggregate-main-only classification-TM development baseline。该任务是固定
baseline，不是 tuning experiment；低或零 performance 是有效结果，不能据此
改变 detector、pairer、features、Booleanisation、TM parameters 或 sampling。

## 2. Starting identity

授权指定并已核验：

- repository default branch: `main`;
- local starting HEAD and `origin/main`:
  `233e5ea064cda2e4c65b0e06001e23667ec906f2`;
- starting worktree: clean;
- frozen Protocol R manifest SHA-256:
  `501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5`;
- frozen Protocol R support audit SHA-256:
  `c7fde29e9570417d12463e16f64ebf4eb1cb4736b775fc6fb2116e06fb68eed3`;
- repository health: 82 tests discovered, passed with two Windows
  capability-dependent symlink skips.

## 3. Frozen execution contract

Machine-readable method identity will be frozen in
[`protocol_r_baseline_v1.json`](../../artifacts/manifests/protocol_r_baseline_v1.json)
before REDD model execution. The accepted class/reporting decision is
[D006 — Protocol R v1 Development Reporting Scope](../decisions/D006-protocol-r-v1-development-reporting-scope.md).

The implementation must:

- load only admitted slices through `tools/data/protocol_r_access.py`;
- keep every detector, pairer, feature and target dependency within one
  segment/block/split;
- use the authorised fixed edge detector, FIFO pairer, 23-slot feature schema,
  8-bit Gaussian-CDF Booleanisation and binary TM parameters;
- fit one fresh model per fold/seed/appliance;
- include explicit no-output false negatives in end-to-end event metrics;
- retain only compact aggregate evidence and hashes.

## 4. Stop boundary

Stop before or during execution if a protected role/house is requested, source
or frozen identity drifts, dependency containment fails, label columns influence
aggregate-main candidates/features, a training run lacks usable positive or
negative candidates, deterministic seeds or exact save/reload parity fail, or
the frozen design changes after the pre-run commit.

This task does not authorise E003/E004, rTM/TMU, T006+, B5, Protocol X,
combined B1–B4 final fit, host-native, Pico, firmware, hardware, publication or
any external write.

## 5. Lifecycle checkpoints

- Pre-run design commit: pending.
- Canonical run: pending.
- F1/seed-0 sentinel rerun: pending.
- Final or blocked checkpoint commit: pending.
- Push: prohibited.
