# T004 — Protocol R 评估合同与测试集冻结
# Protocol R Evaluation Contract and Test Freeze

## Agent Brief

- Work ID: T004
- Track: T-series
- Lifecycle status: complete with documented class limitations — 2026-07-28
- Live authority: see `docs/CURRENT_STATE.md`
- Owner: Tianhang Tan
- Research scoring access: see `docs/CURRENT_STATE.md`
- Candidate/locked test access: see `docs/CURRENT_STATE.md` and the accepted access decision

## 1. 目标

在第一次正式 Protocol R model scoring 之前，消除 evaluation population、split、output semantics 和 metric aggregation 的歧义，并冻结唯一的 test manifest/hash。

本文件是 planned task specification，本身不构成开始 T004、读取 H2/H4、训练、
预测或评分的授权；live authority 只看
[CURRENT_STATE.md](../CURRENT_STATE.md)。

## 2. 输入

- [D002 — Primary Evaluation Protocol](../decisions/D002-primary-evaluation-protocol.md)
- [D003 — REDD Sequence-Time Contract](../decisions/D003-redd-sequence-time-contract.md)
- [D004 — Protocol R Class Fallback](../decisions/D004-protocol-r-class-fallback.md)
- [R002 — Evaluation Protocol Consistency Review](../reviews/R002-evaluation-protocol-consistency-review.md)
- [`protocol_r_approved_split.json`](../../artifacts/manifests/protocol_r_approved_split.json)
- T002 support audit and prior candidate-label access record
- T003 Protocol H H2/H4 compatibility access record

## 3. 必须冻结的决定

### Evaluation population

- 选择 mixed-house within-population Protocol R，或 held-out-house primary evaluation；
- 明确 Protocol X 的保留用途；
- 记录 D002/D003 的修订或 supersession；
- 只使用当前能证明的 `sequence-first, row-position blocked` 表述，除非补回 timestamp provenance。

### Data eligibility

- house、segment、block 和 appliance eligibility；
- missing appliance column 的处理；
- overlap 和 ambiguous event 的 scoring eligibility；
- train/validation/test roles；
- boundary reset 和 full dependency containment；
- candidate → locked test 的明确转换条件。

### Binary output semantics

- simultaneous positives；
- all-negative/reject；
- multi-positive conflict；
- threshold/tie rule；
- per-appliance versus event-level predictions；
- exact scoring unit。

### Metrics and uncertainty

- per-appliance precision、recall、F1、support；
- macro aggregation；
- accuracy 的完整名称和公式；
- confusion matrix 形式；
- repeated seeds/folds 和 summary statistics；
- washer dryer 等低 support class 的 uncertainty；
- model bytes、RAM/flash、per-model/ensemble latency；
- compute latency 与 algorithmic decision delay 分开报告。

## 4. 可执行安全门

T004/T005 必须提供统一 data access entry：

- development mode 只接受 approved development manifest/role；
- 请求 candidate-test 或 locked-test role 时直接报错；
- algorithm code 不允许宽泛扫描全部 houses；
- automated tests 明确验证 H2/H4 或最终 test identity 在 development mode 下被拒绝；
- final evaluation 使用独立命令、manifest 和显式 authority。

在该安全门和测试完成前，不运行正式 Protocol R baseline。

## 5. Deliverables

- accepted decision record；
- final protocol terminology；
- immutable evaluation manifest；
- canonical manifest SHA-256；
- machine-readable task/output contract；
- binary TM scoring specification；
- metric and uncertainty specification；
- development/test data-access tests；
- `CURRENT_STATE.md` 和 `WORK_INDEX.md` 更新。

## 6. Exit Criteria

T004 只有在以下条件全部满足后才能标记 complete：

- Tianhang 明确选择 evaluation population；
- D002/D003 冲突被正式解决；
- output/metric semantics 无歧义；
- candidate/locked test access gate 有自动测试；
- exact manifest 与 hash 已冻结；
- 尚未查看任何新的 locked-test predictions 或 metrics；
- repository health check 全部通过。

T004 完成不自动授权 T005，也不自动授权 test scoring。

## 7. 2026-07-28 execution checkpoint

## Agent Brief

- Authority: formally authorised by Tianhang on 2026-07-28
- Core manifest: `artifacts/manifests/protocol_r_evaluation_v1.json`
- Core manifest byte SHA-256: `501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5`
- Audit order: manifest frozen before aggregate support audit
- Model training/prediction/scoring: none
- Lifecycle outcome: blocked; not complete

本轮按明确规则冻结 H1/H3/H5/H6 mixed-house Protocol R、每 segment 五个
row-position blocks、B1–B4 四折 CV、B5 locked test、H2/H4 Protocol X，以及
`L_max=256`、`D_max=8`。冻结后才运行 aggregate-only support audit。

结果触发授权中的 stop rule：

| Appliance | F1 | F2 | F3 | F4 | B5 complete episodes | B5 ON seconds |
|---|---:|---:|---:|---:|---:|---:|
| fridge | 209 | 232 | 218 | 201 | 208 | 202,902 |
| microwave | 34 | 48 | 47 | 30 | 34 | 7,875 |
| dish washer | 21 | 20 | 70 | 52 | **0** | **15** |
| washer dryer | **0** | 24 | 39 | 14 | 10 | 5,766 |

表中 episode 是在同一 segment/block 内、且满足最大 history/post-context
containment 的 complete episode。既有 minimum 是每 validation fold 5 个、B5
10 个并有至少 600 秒 ON support。`dish washer` B5 同时失败 episode 和 ON
duration；`washer dryer` F1 validation 失败。

因此没有移动 boundary、调整 threshold、替换 class 或继续到模型工作。核心
manifest、hash sidecar、support audit、aggregate CSV、generator 与 access-guard
scaffold 保留在本地工作树供审查。T004 不标记 complete；D002/D003 conflict、
正式 decision record、完整 access tests 和 exit checks 仍待 blocker 决定后完成。

本节记录 stop-rule 当时的历史 checkpoint。随后 Tianhang 已通过
[D005](../decisions/D005-protocol-r-v1-class-and-support-eligibility.md)
正式决定 eligibility，并授权继续 T004 closure。

## 8. Eligibility continuation and closure evidence

正式 class identity 保存在
[`protocol_r_class_eligibility_v1.json`](../../artifacts/manifests/protocol_r_class_eligibility_v1.json)：

| Appliance | Development CV | Protocol R B5 | Protocol X |
|---|---|---|---|
| fridge | Eligible | Eligible | Support-eligible；H4 label unavailable |
| microwave | Eligible | Eligible | Support-eligible；H4 label unavailable |
| dish washer | Eligible；development-only claim | Ineligible | Future locked confirmatory evaluation support-eligible |
| washer dryer | Ineligible；deferred | Ineligible despite B5 support | Data support passes；formal evaluation deferred |

独立 Protocol X audit 固定使用完整 H2+H4 composite，没有建立 development split：

| Appliance | H2 episodes / ON s | H4 episodes / ON s | Pooled episodes / ON s |
|---|---:|---:|---:|
| fridge | 391 / 398,163 | unavailable | 391 / 398,163 |
| microwave | 64 / 92,976 | unavailable | 64 / 92,976 |
| dish washer | 47 / 13,752 | 11 / 4,419 | 58 / 18,171 |
| washer dryer | 0 / 0 | 11 / 11,784 | 11 / 11,784 |

`tests/data/test_t004_protocol_contract.py` 专项验证：

- exact core manifest SHA-256 和 deterministic byte reconstruction；
- manifest byte/hash drift fail-closed；
- development loader 只产生 B1–B4 slices；
- B5、`locked_test`、H2/H4 和 Protocol X development 请求被拒绝；
- support audits 只包含 aggregate records；
- 五块 floor boundary、segment/block/window dependency containment；
- fixed H2+H4 population 和 per-house/pooled `dish washer` support；
- machine-readable eligibility 与 D005 一致。

本任务没有训练、加载或运行模型，没有生成 prediction、model metric、B5 test
result 或 Protocol X model result。T004 completion 不授权 E003、E004、T005、
T011 或 Protocol X evaluation。

## 9. Completion checks

- Frozen core manifest SHA-256:
  `501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5`
- Frozen Protocol R audit SHA-256:
  `c7fde29e9570417d12463e16f64ebf4eb1cb4736b775fc6fb2116e06fb68eed3`
- Protocol X support audit SHA-256:
  `ebeaffb4807d830cc47c48c9f67fc82827795bbcbaaf1e1d72ccef2bcdc4f163`
- Class eligibility record SHA-256:
  `3a8e58db1551d5a24899b47f33701bfc8fe46c2ee6a26b3eb001bed7c04876de`
- T004 targeted tests: 13 passed
- Repository health: 82 tests discovered; 80 passed and 2 capability-dependent
  symlink tests skipped
- `git diff --check`: passed
- REDD source modification/copy: none
- Model training, loading, prediction, B5/Protocol X scoring: none
- Git stage/commit/push/branch/PR action: none

全部 exit criteria 已满足。T004 以 documented class limitations 完成，而不是以
四类均可评价完成。
