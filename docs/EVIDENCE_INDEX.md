# 证据索引 / Evidence Index

## Agent Brief

- Purpose: map RQ and claim to exact evidence
- Current formal Protocol R result: none
- Historical evidence promotion: prohibited without T-series revalidation
- Update rule: append or supersede; do not silently replace

本索引用于论文、presentation 和答辩准备。它不只列“做过哪些实验”，而是回答每个 claim 由哪份 evidence 支撑、能说到什么程度、还缺什么。

## RQ1 — Engineering reproduction

| Claim | Evidence | Status | Permitted interpretation | Limitation |
|---|---|---|---|---|
| Pinned Han two-class staged PC workflow can run locally and repeat | [T003 local archive](../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md) | Verified Protocol H compatibility evidence | 两次完整 local run 的输入、generated CSV、metrics、model hash 和 C export 一致 | label-assisted；H3 matched-event evaluation；不是 Protocol R/Pico/real-time |
| Model save/reload parity is complete | 同上 | Not supported | 不能作该 claim | 10-epoch live vs reload 仍有 1 个 prediction mismatch |
| Python → host-native → Pico parity exists | No evidence yet | Missing | 不得声称 | 计划由 T006/T007 产生 |
| Exported C model storage size is known for T003 | 同上 | Verified within T003 | C model data 为 `9,058` bytes | 只适用于该 two-class compatibility model |

## RQ2 — Protocol R baseline

| Claim | Evidence | Status | Permitted interpretation | Limitation |
|---|---|---|---|---|
| REDD input inventory and class support are pinned | [T002 task](tasks/T002-redd-inventory-and-protocol-r-preflight.md), [inventory](data/REDD_INVENTORY.md), [manifest](../artifacts/manifests/protocol_r_approved_split.json) | Verified preflight | 当前 preprocessed segments、support 和 candidate identities 可复核 | original timestamp/provenance 未恢复 |
| Formal Protocol R evaluation contract is internally consistent | [T004 task](tasks/T004-protocol-r-evaluation-contract-and-test-freeze.md), [D005](decisions/D005-protocol-r-v1-class-and-support-eligibility.md), [frozen manifest](../artifacts/manifests/protocol_r_evaluation_v1.json) | Verified contract; no model result | H1/H3/H5/H6 mixed-house Protocol R、B1–B4 CV、B5 locked、H2/H4 Protocol X、row-position 和 output/metric semantics 已冻结 | fridge/microwave full eligible；dish washer development-only；washer dryer support-ineligible |
| Frozen class support permits a four-class Protocol R B5 claim | [T004 support audit](../artifacts/manifests/protocol_r_support_audit_v1.json), [eligibility record](../artifacts/manifests/protocol_r_class_eligibility_v1.json) | Not supported | 只能对 fridge/microwave 保留 full Protocol R v1 endpoint；dish washer B1–B4 development feasibility 可继续 | dish washer B5 support fail；washer dryer F1 support fail |
| Fixed H2+H4 Protocol X supports a future dish washer endpoint | [Protocol X support audit](../artifacts/manifests/protocol_x_support_audit_v1.json), [D005](decisions/D005-protocol-r-v1-class-and-support-eligibility.md) | Support-eligible; not evaluated | pooled 58 dependency-contained episodes、18,171 ON seconds；未来单独授权后可产生 Protocol X cross-house evidence | 没有模型结果；不得称为 Protocol R B5；ordinary development 仍 sealed |
| Formal Protocol R baseline performance is known | No evidence yet | Missing | 不得引用 T003/E001/历史 round 代替 | T004/T005 尚未完成 |
| H2/H4 are completely unseen to the project | T002/T003 records | Not supported | 可说 ordinary development 仍对 H2/H4 sealed | T002 看过 support labels；T003 compatibility training 读过 H2/H4 |

## RQ3 — Controlled improvements

| Claim | Evidence | Status | Permitted interpretation | Limitation |
|---|---|---|---|---|
| `threshold_8` is a reliable replacement for Han binary | [E001 report](../experiments/E001-booleanization-ab-probe/REPORT.md) | `inconclusive` | mean delta 为正，但未达到 predeclared rule；不能 promotion | legacy label-assisted data，5 seeds，H2/H4 未读 |
| Training order may affect Han TM performance | [E002 current archive](../experiments/E002-tm-training-dynamics-probe/README.md), [fixed source commit](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/e7277cc4a0326350f51fdfc5c17b8777572deddc/experiments/2026-07-22-tm-training-dynamics-probe/README.md), [R001](reviews/R001-legacy-evidence-and-reuse-map.md) | Legacy exploratory evidence | 可作为 formal E/T hypothesis 的来源 | H3 repeatedly viewed；未在 current formal protocol 下确认 |
| Historical bounded pre/post context is promising | [R001](reviews/R001-legacy-evidence-and-reuse-map.md), [workflow map](research_notes/2026-07-23-nilm-workflow-layer-map.md) | Historical mechanism evidence | 可支持提出新的 controlled experiment | 旧 task/split，不是 current Protocol R |
| Complex static FSM improves final system | Historical Round 10I locator in R001 | Historical negative evidence | 现有旧结果不支持用复杂 FSM 修补 upstream errors | 尚未在 current baseline 重验 |

## RQ4 — Embedded trade-offs

| Claim | Evidence | Status | Permitted interpretation | Limitation |
|---|---|---|---|---|
| T003 compatibility model C data size | [T003 local archive](../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md) | Verified | `9,058` bytes | 不是 total firmware/flash/RAM |
| Pico inference latency and parity | No evidence yet | Missing | 不得声称 | T007 尚未完成 |
| End-to-end real-time NILM | [Han source audit](reproduction/HAN_PIPELINE_SOURCE_AUDIT.md) | Not established | 可说明 current upstream route 包含 SD replay 和 future context | TM compute latency 不能替代 algorithmic decision latency |

## Feasibility and mechanism evidence

| Claim | Evidence | Status | Permitted interpretation | Limitation |
|---|---|---|---|---|
| Reviewed rTM papers and pinned public implementations define materially different target mapping, feedback, clipping and weighting behaviour | [R003 — Regression Tsetlin Machine Mechanism Review](reviews/R003-regression-tsetlin-machine-mechanism-review.md) | Literature and pinned-source review complete | 可用于界定后续 source-parity 与 mechanism checks；不能把某一实现行为泛化成所有 rTM | 没有训练、local wheel parity、REDD 或 NILM score |
| A reproducible Windows CPU TMU regression smoke configuration was prepared | [Historical smoke archive](research_notes/2026-07-24-tmu-regression-smoke-test/README.md) | `inconclusive` | 可复用 exact script、uv lock 和环境清单设计新的 authorised smoke run | 原始 stdout/result 未保存；reported pass 不是 authoritative local execution evidence；本轮未重跑 |

## Protocol / evidence boundary map

| Evidence | Protocol / scope | Formal dissertation use |
|---|---|---|
| T002 | data/protocol preflight | 可用于 Dataset、Protocol limitations 和 class selection |
| T003 local archive | Protocol H compatibility | 可用于 Implementation/Reproduction 和 parity defect analysis |
| E001 | exploratory legacy label-assisted | 可作为 Booleanisation ablation/negative or inconclusive evidence，不能当 final result |
| E002 | legacy exploratory H3 | 已固定到 remote commit；只可作为 hypothesis/history，不能直接变成 formal result |
| old repositories | historical/mechanism evidence | 通过 R001 定位；不得直接变成 current score |
| future T005/T009 development results | formal development evidence | 可用于 method selection，不是 locked-test result |
| future T011 | final Protocol R result | 只有 freeze 和 one-time evaluation 完整时才可作为 primary result |
| future T012 | Protocol D deployment | 可用于 hardware/deployment，不得冒充 unbiased Protocol R |

## 论文材料状态

| Section | 已有材料 | 仍缺 |
|---|---|---|
| Background / system overview | workflow map、Han source audit | literature synthesis 与最终 architecture figure |
| Dataset / protocol | T002 inventory、D002–D004、R002 conflict record | T004 accepted evaluation contract |
| Reproduction | T003 local report、repeatability、reload defect | host-native/Pico parity |
| Controlled experiments | E001、historical locators | formal baseline 后的 promoted experiments |
| Main results | none | T011 locked-test result |
| Embedded evaluation | T003 C bytes only | Pico flash/RAM/latency/parity |
| Limitations | timestamp provenance、Protocol conflict、H2/H4 prior access、weak class support | final method-specific limitations |

## 更新规则

每个新的有效 T/E result 至少登记：

- RQ 和 workflow layer；
- work ID and direct name；
- exact canonical `result.json` path（E-series 用它持久保存
  `design_sha256`/`design_commit`）和 narrative evidence path；
- protocol/claim scope；
- outcome；
- paper-ready claim；
- limitation；
- 是否已 promotion；
- figure/table path。

无效 run、coding error 和近似重复 hyperparameter attempts 不进入主索引；它们只在必要时保留 debugging record。有效 negative、`not_supported` 和 `inconclusive` 必须登记，因为它们能解释排除方向和最终方法选择。
