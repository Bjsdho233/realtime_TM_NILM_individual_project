# T004 — Protocol R 评估合同与测试集冻结
# Protocol R Evaluation Contract and Test Freeze

## Agent Brief

- Work ID: T004
- Track: T-series
- Lifecycle status: planned specification
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
