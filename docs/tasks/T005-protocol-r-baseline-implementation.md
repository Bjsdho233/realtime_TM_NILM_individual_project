# T005 — Protocol R Baseline Implementation

## Agent Brief

- Work ID: T005
- Track: T-series
- Lifecycle status: complete — 2026-07-28
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

- Initial pre-run attempt: `a59507b`；因 commit command 的 sequencing 未在
  `git diff --cached --check` warning 后停止，不作为 canonical anchor；历史保留，
  没有 amend/rewrite，也没有 REDD model execution。
- Valid pre-run design commit:
  `4fb5129ee1afcdc50fee2033eedf7b2f2f03aa9f`。
- Canonical run: complete；F1–F4 × seeds 0–4 × fridge/microwave/dish washer，
  one fixed matrix。
- F1/seed-0 sentinel rerun: complete；全部声明 hashes exact match。
- Final local commit: the commit titled
  `Complete T005 Protocol R development baseline` containing this record。
- Push: not performed and prohibited by this task authority。

## 6. Canonical development result

Canonical machine-readable result：
[`result.json`](../../experiments/T005-protocol-r-baseline-implementation/result.json)；
human narrative：
[`BASELINE_REPORT.md`](../../experiments/T005-protocol-r-baseline-implementation/BASELINE_REPORT.md)。

### 6.1 Named summaries

| Scope | Mean F1 | Sample std | Interpretation |
|---|---:|---:|---|
| `fridge` | 0.421679382593 | 0.017083083900 | full-eligible development model |
| `microwave` | 0.269957225055 | 0.020825136079 | full-eligible development model |
| `dish washer` | 0.213391254881 | 0.018117993143 | development-only |
| `full_eligible_macro_2class` | 0.345818303824 | 0.006093000187 | primary T005 summary |
| `development_scope_macro_3class` | 0.301675954177 | 0.008474558968 | supplemental development-only |

Aggregation is each seed’s unweighted F1–F4 mean followed by mean and sample
standard deviation across five seeds。完整 fold × seed × appliance counts、
metrics 和 zero-denominator flags 见
[`development_metrics.csv`](../../experiments/T005-protocol-r-baseline-implementation/tables/development_metrics.csv)。

### 6.2 Fold × seed pooled F1

下表每格使用该 fold 的四个 development houses pooled end-to-end event F1。

| Fold | Seed | Fridge | Microwave | Dish washer |
|---|---:|---:|---:|---:|
| F1 | 0 | 0.537500 | 0.296296 | 0.375000 |
| F1 | 1 | 0.523077 | 0.269231 | 0.285714 |
| F1 | 2 | 0.460993 | 0.227273 | 0.325581 |
| F1 | 3 | 0.461538 | 0.204082 | 0.322581 |
| F1 | 4 | 0.477419 | 0.360656 | 0.312500 |
| F2 | 0 | 0.307692 | 0.250000 | 0.240000 |
| F2 | 1 | 0.300654 | 0.204545 | 0.181818 |
| F2 | 2 | 0.305164 | 0.171429 | 0.188679 |
| F2 | 3 | 0.272981 | 0.157895 | 0.250000 |
| F2 | 4 | 0.275000 | 0.321429 | 0.160000 |
| F3 | 0 | 0.508475 | 0.100000 | 0.027778 |
| F3 | 1 | 0.483582 | 0.361702 | 0.054795 |
| F3 | 2 | 0.485714 | 0.387097 | 0.098765 |
| F3 | 3 | 0.501408 | 0.451613 | 0.054795 |
| F3 | 4 | 0.502825 | 0.109091 | 0.054054 |
| F4 | 0 | 0.431746 | 0.307692 | 0.307692 |
| F4 | 1 | 0.393103 | 0.264151 | 0.320000 |
| F4 | 2 | 0.430034 | 0.259259 | 0.179104 |
| F4 | 3 | 0.435331 | 0.350877 | 0.275000 |
| F4 | 4 | 0.339350 | 0.344828 | 0.253968 |

### 6.3 Event and support boundary

Across the four validation folds the aggregate-main pipeline observed 7,581
main edges，formed 2,797 FIFO pairs，emitted 2,670 contained candidates，
expired 613 rises，discarded 1,374 unmatched falls，and excluded 127 paired
events for containment；one non-finite main sample reset continuity。

| Appliance | Eligible positive | Eligible negative | Excluded/unavailable | Matched targets | No-output FN targets |
|---|---:|---:|---:|---:|---:|
| fridge | 890 | 1,997 | 95 | 578 | 312 |
| microwave | 170 | 1,973 | 555 | 142 | 28 |
| dish washer | 168 | 2,488 | 24 | 158 | 10 |

这些 support totals 对 seeds 不重复计数。house-level、fold-level reason counts 和
candidate burden 见 aggregate tables。

## 7. Cost and reproducibility result

Serialized inference model bytes across the 20 fold/seed bundles：

- fridge `4,280–4,836` bytes；
- microwave `4,176–4,628` bytes；
- dish washer `4,564–5,226` bytes；
- full-eligible two-model complete bundle（shared encoder once）
  `9,906–10,644` bytes；
- development three-model complete bundle `14,542–15,460` bytes；
- shared encoder metadata by fold：F1 `1,298`，F2 `1,300`，F3 `1,298`，
  F4 `1,297` bytes。

Across the 20 bundles，median of per-run median Python-reference latency：

- individual TM：fridge `255,250 ns`，microwave `206,525 ns`，
  dish washer `219,275 ns`；
- named two-model ensemble TM-only `460,800 ns`；Booleanisation plus ensemble
  `596,000 ns`；
- named three-model ensemble TM-only `712,575 ns`；Booleanisation plus ensemble
  `739,950 ns`。

对应 per-run P95 的中位数分别为 `437,300`、`419,820`、`416,670`、
`829,482.5`、`956,065`、`1,222,395` 和 `1,338,320 ns`。这些都是
Python-reference，不能解释为 host/Pico latency。fall-to-output 固定为 8 samples
/ 24 nominal seconds；onset-to-output median/P95 由各 fold 的 candidate duration
决定，见
[`model_costs.csv`](../../experiments/T005-protocol-r-baseline-implementation/tables/model_costs.csv)。

F1/seed-0 sentinel 重新加载数据、重新 fit encoder 并训练三个 fresh models；
training/validation candidate、encoder、model、prediction 和 pooled metric hashes
全部 exact match。save/reload parity 在每个 canonical model 内也为 zero mismatch。

## 8. Completion boundary

T005 完成仅建立 B1–B4 fixed development baseline。没有访问或评分 B5、H2/H4
或 Protocol X；没有启动 rTM/TMU、E003/E004、T006+、host-native、Pico、
firmware 或 hardware；没有 combined final fit、tuning、第二方法、push、branch
或 PR。
