# R002 — 评估协议一致性审查
# Evaluation Protocol Consistency Review

## Agent Brief

- Work ID: R002
- Track: R-series review
- Status: complete
- Date: 2026-07-23
- Outcome: material conflict found
- Evidence type: governance and manifest review
- Data access: no REDD rows read
- Formal decision changed: no

## 1. 审查问题

当前 D002、D003、approved candidate manifest 和项目文字对 Protocol R / Protocol X 的描述是否一致？现有证据是否足以称为 `raw-time blocked mixed-house Protocol R`？

## 2. 核心发现

目前存在两个不能靠措辞掩盖的冲突。

### 2.1 mixed-house 与 held-out-house 冲突

[D002](../decisions/D002-primary-evaluation-protocol.md) 将：

- Protocol R 定义为 primary mixed-house evaluation；
- Protocol X 定义为 held-out-house generalisation。

但 [D003](../decisions/D003-redd-sequence-time-contract.md) 和
[`protocol_r_approved_split.json`](../../artifacts/manifests/protocol_r_approved_split.json)
将 H1/H3/H5/H6 作为 development pool，并将 H2/H4 整栋房屋留作 candidate test。

完整留出 house 的评估测量的是 cross-house generalisation，结构上更接近 D002 中的 Protocol X。它不是普通的 mixed-house within-population test。

因此，当前 candidate manifest 虽然完成了 T002 support preflight，但不能在没有新决定的情况下同时被称为：

- mixed-house Protocol R；
- held-out-house Protocol X；
- 已冻结的 final test。

### 2.2 raw time 与 row position 冲突

当前 pinned `redd` submodule 提供的是 preprocessed CSV chunks。已确认的信息包括：

- 每个 chunk 是 independent segment；
- nominal cadence 为 3 seconds；
- segment 内有稳定 row order；
- original calendar timestamps、gaps 和完整 preprocessing provenance 未恢复。

因此当前可支持的准确表述是：

> sequence-first, row-position blocked evaluation over independent preprocessed segments

在取得 original timestamp provenance 前，不应写成已经完成 `raw-time blocked` evaluation。

## 3. 对 sealed-test 的影响

H2/H4 在 T002 中只查看过 support labels，用于判断 class feasibility；没有生成或查看 model predictions/metrics。它们随后又进入 T003 固定 Han Protocol H compatibility training split。

这不等于 Protocol R model development 泄漏，但必须公开记录：

- H2/H4 对项目人员并非完全 unseen；
- T003 从 H2/H4 学到的 model、threshold、normalizer 或其他 artifact 不能进入 clean Protocol R；
- ordinary development 仍不得读取 H2/H4；
- final claim 不能把它们描述成从未接触过的 blind test houses。

## 4. T004 必须作出的选择

### Option A — 保持 mixed-house Protocol R

- 在每个符合条件的 house/segment 内先进行 sequence-first train/validation/test block split；
- Protocol R 测量 within-population mixed-house performance；
- H2/H4 完整房屋留出改归 Protocol X；
- 创建新的 Protocol R manifest，并对 D002/D003 做明确修订或 supersession。

### Option B — 将 primary evaluation 改为 held-out-house

- 保留 H1/H3/H5/H6 development、H2/H4 held-out evaluation；
- 明确承认 primary claim 是 cross-house generalisation；
- 更新 D002，重新定义 Protocol R / Protocol X 的关系；
- 重新检查 washer dryer 在 H2/H4 的 support 和 uncertainty 是否足以支撑 macro claim。

本审查不替 Tianhang 选择 A 或 B。根据项目此前强调的 mixed-house event-level 主线，Option A 与原始研究问题更一致；但这只是建议，不能代替正式决定。

## 5. binary TM 输出合同

现有计划写了 `one binary TM per appliance`，但尚未定义完整的 evaluation semantics。T004 至少要冻结：

- 一个 candidate event 能否同时对应多个 positive appliances；
- 多个 TM 同时为正时保留 multi-label 输出还是使用 conflict resolver；
- 全部为负时表示 background/reject，还是强制选择一个 appliance；
- per-appliance decision threshold、tie rule 和 calibration；
- macro precision/recall/F1 是对哪些 binary tasks 取平均；
- `accuracy` 是 per-appliance binary accuracy、event exact-match accuracy，还是其他定义；
- confusion matrix 是每个 appliance 的 `TP/FP/FN/TN`，还是另有 unified matrix；
- model size 报告 per-TM、ensemble total，还是两者都报；
- latency 报告 per-TM、full ensemble、feature-to-decision 和 event waiting time；
- overlap/missing-label 情况下哪些 event 有资格进入 scoring。

在这些语义冻结前，通用字段名 `accuracy` 或 `confusion_matrix` 不能自动解释。

## 6. 结论

当前问题不是数据一定不能用，而是同一 manifest 被赋予了两个不同的研究问题。安全处理方式是：

1. H2/H4 继续对 development sealed；
2. 停止把现有 candidate manifest 称为 final locked Protocol R test；
3. 使用 `sequence-first, row-position blocked` 描述当前数据能力；
4. 由 [T004 — Protocol R Evaluation Contract and Test Freeze](../tasks/T004-protocol-r-evaluation-contract-and-test-freeze.md) 作出并记录正式选择；
5. 在决定前允许其他不访问 sealed test、且不依赖 final scoring semantics 的隔离工作继续。

这是一项 read-only review，不产生新的模型结果，也没有改变 D002、D003 或 approved manifest。
