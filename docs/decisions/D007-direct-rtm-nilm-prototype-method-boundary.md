# D007 — Direct rTM NILM Prototype Method Boundary

## Agent Brief

- Status: Accepted by Tianhang
- Date: 2026-07-28
- Scope: post-R004 method boundary for the paused T006 direct rTM prototype
- Model training, prediction, or scoring: prohibited by this decision
- Locked-test or Protocol X access: prohibited
- Exact input and target preprocessing: not yet frozen

## Context

[R004 — rTM NILM Input and Booleanisation Review](../reviews/R004-rtm-nilm-input-and-booleanisation-review.md)
比较了本地 Protocol R development-training aggregate distribution、rTM/TMU
机制和多个 input/Booleanisation families。它建议不要原样恢复
`32 raw lags + StandardBinarizer`，并建议进一步审查 compact causal
level/change/multi-scale representation 与 hybrid cumulative thresholds。

R004 是 review，不具备方法批准权。Tianhang 在本决定中明确哪些方向可以进入
static audit、哪些结构暂不引入，以及恢复任何训练前仍需冻结什么。

## Decision

| Item | Accepted status |
|---|---|
| `32 raw lags + StandardBinarizer` | 降级为 diagnostic reference；不得原样恢复正式训练 |
| compact level/change/multi-scale family | 批准进入 static audit；不是已冻结 implementation |
| hybrid cumulative Booleanisation | 批准进入 static audit；不是已冻结 encoder |
| exact horizons/features/bits | Pending；不得由 implementation assumption 补定 |
| cTM gate | 当前最小原型不引入 |
| weighted rTM | 当前最小原型不引入 |
| OFF resampling | fridge 首轮不引入；R004 development-training audit 中 fridge ON share 为 38.14%，先验证基本能力 |
| vanilla direct rTM | 继续作为最小原型 architecture |
| target clipping/scaling | 必须在恢复任何训练前由 Tianhang 单独冻结 |

## Source classification

- vanilla Regression Tsetlin Machine mechanism 和固定 TMU interface：
  `Inherited`；
- 用 causal aggregate input 逐样本预测 current appliance power：
  `Adapted`；
- compact level/change/multi-scale feature composition、exact horizons、
  exact bits 和 hybrid threshold placement：`Project-designed`；
- 数据读取、缓存、批处理、日志、维度检查和不改变算法含义的性能优化：
  `Implementation-only`。

这些标签不构成 novelty claim。特别是 compact/hybrid 方向即使没有发现完全相同
的论文，也只能先称为 `Project-designed choices`。

## Static-audit boundary

本决定允许后续 static audit：

- 比较候选 causal features 的定义、单位、dependency horizon 和 boundary reset；
- 比较候选 Boolean thresholds 的 generation rule、bit occupancy、tail coverage
  和 representation size；
- 估算 dense/sparse representation、literal count、memory 和 CPU cost；
- 检查每个组件的 `Inherited`、`Adapted`、`Project-designed` 或
  `Implementation-only` 来源标签；
- 提交 exact horizons/features/bits 和 target transform 的候选给 Tianhang
  决策。

Static audit 不得：

- 调用 `TMRegressor.fit()`、加载已有模型、生成 predictions 或 model metrics；
- 把候选 feature/threshold 自动写成 T006 fixed method；
- 访问 B5、H2/H4 或 Protocol X；
- 引入 cTM gate、weighted rTM 或 fridge OFF resampling；
- 依据 audit 结果自行恢复 T006。

## Required decision before training

恢复任何 evidence-producing training 前，至少必须另行冻结：

1. exact causal horizons；
2. exact numeric features、单位和计算顺序；
3. exact Boolean bit budget、threshold generation 和 fit population；
4. target clipping lower/upper bound；
5. target scaling mapping、inverse mapping 和 out-of-range behaviour；
6. revised runtime cap、stop rule 和成功/失败解释。

上述决定应明确哪些内容继承现有 T006，哪些内容 supersede 旧的
32-lag/StandardBinarizer contract。完成 static audit 本身不授权训练。

## Consequences

- T006 保持 paused。
- 原 `32 raw lags + StandardBinarizer` implementation checkpoint 保留为
  diagnostic reference，不删除、不改写为成功结果。
- 后续最小架构限定为 vanilla direct rTM；若要加入 gate、weighted clauses 或
  resampling，必须由 Tianhang 新决定。
- 本决定不修改 T004 frozen manifest、support audit、class eligibility、
  development/test boundaries 或 evaluation semantics。
