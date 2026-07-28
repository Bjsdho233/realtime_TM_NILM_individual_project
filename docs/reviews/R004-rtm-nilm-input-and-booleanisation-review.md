# R004 — rTM NILM Input and Booleanisation Review

## Agent Brief

- Status: complete — review only; no method approved
- Owner: Tianhang Tan
- Authorised: 2026-07-28
- Track: R-series review
- Question: which input representations and Booleanisation methods are credible
  candidates for a small rTM NILM prototype?
- Data boundary: one Protocol R development-training partition only; no B5 or
  Protocol X access
- Execution boundary: descriptive data/source/literature review only; no model
  training, prediction or scoring
- Decision authority: this review compares candidates; Tianhang selects or
  rejects every research-method choice

## 1. Executive conclusion

不建议直接恢复 T006 的固定方案：
`32 raw aggregate lags × StandardBinarizer(8 bits)`。它可以保留为一个
diagnostic reference，但不适合作为当前首选。主要原因不是 rTM 一定不适合
NILM，而是该表示同时存在三个问题：

1. 32 个 lags 产生 256 个 Boolean inputs，TMU 内部还要考虑其 negated
   literals；对一个逐样本更新的 CPU rTM 来说成本不小；
2. 相邻 raw lags 高度重复，却没有直接表达 level、change 和不同时间尺度；
3. TMU `StandardBinarizer` 按 sorted unique values 的位置取阈值。对本地
   REDD 中“零附近高度密集、同时有很长尾部”的 change distribution，
   它会产生多个极不平衡的 bits；而纯 quantile thresholds 又会把重要的
   大变化全部压到同一个最高 code。

当前最值得由 Tianhang 考虑的候选是两层结构：

- **输入表示：**少量 causal level/change/multi-scale context features；
- **Booleanisation：**monotonic cumulative threshold bits，其中一般 level
  features 使用 train-only global quantiles，signed change/residual features
  使用兼顾零附近和长尾的 hybrid thresholds。

这不是已发表的“标准 rTM NILM 方法”，也不是已证明的创新。rTM 的
threshold propositions、TMU 的 Boolean input interface 属于
`Inherited`；把它们用于 causal NILM、选择哪些统计量以及 hybrid threshold
位置分别属于 `Adapted` 和 `Project-designed`。精确 features、windows、
bits 和 thresholds 在 Tianhang 决定前均未冻结。

## 2. Review boundary and evidence labels

本审查结合：

- frozen Protocol R development loader 和 manifest；
- 本机固定的 TMU 0.8.3 source；
- [R003 rTM mechanism review](R003-regression-tsetlin-machine-mechanism-review.md)；
- [E001 Booleanisation probe](../../experiments/E001-booleanization-ab-probe/REPORT.md)；
- 可核验的 primary literature。

它只进行了 aggregate descriptive audit，没有训练模型、加载模型、生成
predictions 或计算 model metrics。没有访问 B5、H2、H4 或 Protocol X，
也没有恢复 T006。

方法组件按以下规则标注：

| Label | Meaning |
|---|---|
| `Inherited` | 直接采用已有论文或固定版本源码中的方法 |
| `Adapted` | 基于已有方法，但为本项目改变了任务或使用方式 |
| `Project-designed` | 项目依据假设提出、尚需决策和验证的设计 |
| `Implementation-only` | 不改变算法含义的编程、缓存或性能实现 |

“没有找到出处”只表示 `Project-designed` 或 evidence gap，不表示 novelty。

## 3. What rTM and TMU imply for the input

### 3.1 rTM favours Boolean propositions with useful ordering

原始 rTM 将 continuous feature 转换为类似 \(x \geq \theta\) 的 Boolean
propositions，然后通过 active clauses 的加和产生 regression output。
因此，能够表达“功率至少到达某个 level”或“变化超过某个 magnitude”的
cumulative threshold code，与 clause 的 inequality rules 直接匹配。
ordinary binary code 虽然可提供更多数值 levels，但相邻数值可能翻转多个
bits，数值顺序并不直接对应 literal 顺序。

rTM output 也是离散加和。TMU 将目标区间映射到 `T`，训练反馈强度依赖
normalized prediction error。输入编码不能单独解决 target scaling：
少量异常大的 appliance readings 会占用大部分输出范围，必须把 target
range/clipping/scaling 作为另一项研究决定。

### 3.2 TMU 0.8.3 `StandardBinarizer` is not a quantile encoder

固定 source 的行为是：

1. 对每个 numeric feature 排序其 unique training values，并跳过最小值；
2. unique values 超过 bit budget 时，在该 sorted unique list 上近似等间隔
   取阈值；
3. 输出 `value >= threshold`；
4. 当前实现分配 dense floating-point output matrix，并逐 feature/threshold
   填充。

因此它依赖 **unique-value positions**，不是 sample quantiles，也不是等距
watt thresholds。重复值多、噪声集中或有长尾时，阈值占用率可能很不均衡。
在 T006 中，50,000 rows × 256 dense `float64` bits 单是 encoded matrix
约为 97.7 MiB；32 × 8 = 256 Boolean inputs 对应最多 512 个 positive/negated
literals。五次 `fit()` 是五个逐样本 epochs。先缩减有效 input bits，比只做
I/O 或缓存优化更可能同时改善可解释性和运行时间。

这些是 fixed-source observations 和 mechanism inference，不是模型效果结论。

## 4. Local REDD descriptive audit

### 4.1 Exact scope

审查只通过 approved development loader 读取 Protocol R F1 的 training roles：
`B2/B3/B4`，houses 为 `H1/H3/H5/H6`。没有读取 F1 validation block `B1`，
没有读取 B5、H2 或 H4。segment/block boundaries 保持不变；所有统计只在
相邻有效 rows 位于同一 segment/block 时计算。

该单一 training partition 用于理解数量级和 distribution shape，不是一次
formal evaluation，也不能证明某个 encoding 会获得更好的 NILM metric。
没有保存 row-level data、时间序列、targets 或可还原样本。

### 4.2 Aggregate level is heavy-tailed and house-dependent

| House | Valid rows | Fridge ON rows | ON share | Aggregate median | Aggregate P99 |
|---|---:|---:|---:|---:|---:|
| H1 | 200,561 | 49,782 | 24.82% | 198.91 W | 6,077.19 W |
| H3 | 140,493 | 55,056 | 39.19% | 248.77 W | 5,345.63 W |
| H5 | 13,719 | 6,431 | 46.88% | 310.03 W | 4,047.24 W |
| H6 | 192,789 | 97,563 | 50.61% | 309.18 W | 3,126.44 W |
| Pooled | 547,562 | 208,832 | 38.14% | 258.07 W | 4,594.47 W |

Pooled aggregate 的
`[min, P1, P5, P25, P50, P75, P95, P99, max]` 为：

`[91.11, 94.86, 98.75, 166.59, 258.07, 362.02, 1403.78, 4594.47, 12065.06] W`。

这说明 fixed watt bins 容易把大量 bits 浪费在少数高功率 tail，而 per-house
normalisation 虽能减小 offset，却会引入 house-specific fitted state，并削弱
未来 cross-house interpretation。若使用 fitted thresholds，首选候选应从
pooled development-training data 拟合；不能利用 validation 或 held-out houses。

### 4.3 Changes are concentrated near zero but have rare large tails

Pooled signed one-step delta 的
`[min, P0.1, P1, P5, P50, P95, P99, P99.9, max]` 为：

`[-8788.24, -1044.07, -20.00, -4.72, 0.00, 4.34, 15.41, 1014.08, 11764.94] W`。

Absolute delta 的 `[P50, P75, P90, P95, P99, P99.9, max]` 为：

`[0.81, 2.06, 4.53, 7.91, 68.69, 1531.16, 11764.94] W`。

这是一种 quantiles-only 和 equal-width-only 都难以独立处理的 distribution：

- 8 个 sample quantile thresholds 对 signed delta 得到约
  `[-2.42, -1.05, -0.46, -0.06, 0, 0.38, 0.92, 2.24] W`；
  bits 很平衡，但超过 2.24 W 的正向 changes 全部同码，大事件 magnitude
  几乎丢失；
- TMU StandardBinarizer 得到约
  `[-6485.65, -11.15, -4.84, -2.18, -0.22, 1.65, 4.11, 9.57] W`；
  第一个 bit 几乎永远为 1，另一些 bits 也很稀疏。

因此 signed delta/residual 更适合将一部分 thresholds 放在 noise/core
区域，另一部分放在正负 tail；正向和负向 magnitude 应显式区分。

### 4.4 Short delta history cannot represent sustained ON by itself

对 fridge ON rows，最近一次 observed OFF→ON transition 位于过去 32 samples
以内的比例为：

| House | Onset within last 32 samples | Onset within last 256 samples | Median known ON age |
|---|---:|---:|---:|
| H1 | 10.33% | 75.08% | 498 s |
| H3 | 13.61% | 91.64% | 357 s |
| H5 | 7.19% | 50.76% | 754.5 s |
| H6 | 4.22% | 33.37% | 1,146 s |

所以 32-sample delta-only representation 只在少数 ON rows 中看得到启动 edge；
即使延伸到 256 samples，H5/H6 仍有大量持续状态看不到 onset。输入至少需要
保留 current level、较长尺度 context 或显式 state memory；delta-only 不应
成为首选。

### 4.5 Target and imbalance are separate decisions

本次 training scope 的 ON row shares 为：

| Appliance | ON rows / valid rows | ON share |
|---|---:|---:|
| fridge | 208,832 / 547,562 | 38.14% |
| microwave | 3,813 / 354,773 | 1.07% |
| dish washer | 13,913 / 547,562 | 2.54% |
| washer dryer | 11,759 / 547,562 | 2.15% |

fridge ON target 的典型值因 house 不同，median 约为 117–191 W，但观测 maximum
达到 1,565–2,257 W。对 rTM 来说，这会影响 `T` 所表达的 watt resolution。
对后三类，97–99% 左右的 OFF rows 又可能使 direct regression 倾向于近零输出。

因此 encoding 选择不能替代以下独立研究决定：target clipping/scaling、
OFF imbalance、是否使用 cTM gate、是否 weighted rTM，以及 training sampling。
R004 不批准其中任何一项。

## 5. Candidate comparison

| ID | Candidate and source type | What it preserves | Main advantage | Main limitation | R004 assessment |
|---|---|---|---|---|---|
| A | 32 raw causal lags + TMU `StandardBinarizer(8)`；TMU part `Inherited`，window/task `Project-designed` | 96 s raw level history | 最简单，已有 T006 implementation | 256 bits；lags 高度冗余；threshold occupancy 不均；47 min stopped run 暴露成本风险 | 只保留 diagnostic reference，不建议原样恢复 |
| B | Raw lags + train-only quantile thermometer；rTM threshold form `Inherited`，quantile placement `Project-designed` | raw history 和 ordered levels | bits 较平衡，逻辑单调 | 仍有 256-bit 问题；aggregate tail 被压缩；house mixture 影响阈值 | 比 A 更合理，但不是首选表示 |
| C | Recent signed/absolute deltas + quantile/hybrid code；event idea `Adapted` | 短期 edges | 抑制 house baseline，适合检测变化 | 无法单独表示长 ON state；simultaneous loads 使 edge 混杂 | 只适合作为组合中的一部分 |
| D | Compact causal level + change + multi-scale context；`Adapted` task + `Project-designed` feature set | current state、recent change、短/中/长 context | 信息互补，bits 和 literals 可明显减少，适合 streaming | exact features/windows 尚无依据；统计量可能平滑短 microwave event | **首选 representation family，待 Tianhang 决定** |
| E | Causal event-state features：last significant edge magnitude/age、state memory；event concept `Adapted`，online form `Project-designed` | long-lived state 与 sparse edges | 很少 features 就能携带长周期记忆 | event threshold、overlap ambiguity、reset 和 delay 都是新方法决定 | 可作为后续 comparator，不先做主线 |
| F | Han paired-event 23-slot features + Han 8-bit code；`Inherited/Adapted` historical path | episode shape、duration、pre/post context | 已有实现和可解释 event features | label-assisted historical route；依赖 pairing/post-event context；不是 direct samplewise rTM | 只作历史 comparator，不是主候选 |
| G | Ordinary binary integer code | 较多 discrete levels | 同 bit 数下数值分辨率高 | 相邻值的 Hamming distance 不连续；不直接表达 inequality | 不建议作为主要 rTM encoding |
| H | One-hot bins | exact interval identity | 每个 bin 含义直观 | bits 多；丢失 monotonic relation；tail bin 仍稀疏 | 不建议 |
| I | Fixed physical watt thresholds | absolute physical scale | 容易解释、跨 batch 固定 | exact cut-points 容易成为 appliance/data tuning；不能适应 level 与 delta 的不同 shape | 只适合作为 hybrid tail 的一部分 |
| J | Per-house standardisation/thresholds | house-relative levels | 可降低不同 house offset | 引入 house identity 和 fitted state；Protocol X/deployment interpretation 较弱 | 不建议作为 primary path |

此外，calendar/time-of-day features 因当前 frozen protocol 只承诺 row-position
ordering、没有完整 raw timestamp provenance，本轮排除；高频 transient、
reactive power 或 harmonics 在现有 3-second active-power数据中不存在，也不能
通过编码“创造”出来。

## 6. Recommended decision structure

### 6.1 Representation decision

建议 Tianhang 在以下三类中做明确选择：

1. **D — compact causal multi-scale representation（R004 推荐）**：
   少量 current level、signed change 以及不同 causal horizons 的 context。
2. **B — raw causal lags**：最少方法设计，但成本和冗余最大。
3. **E — causal event-state representation**：可能高效，但方法假设最多。

D 的 feature family 可讨论 current mains、one-step change、current-vs-causal
mean、causal range/variability 或不同 horizons 的 level summaries；这只是
candidate vocabulary，不是批准的 exact feature list。每个 horizon、是否使用
mean/range、是否允许 state memory 都需要 Tianhang 单独确认。

### 6.2 Booleanisation decision

若选择 D，建议优先考虑 **hybrid cumulative thresholds**：

- level/slow-context features：pooled development-training quantiles，保持
  ordered、较平衡的 threshold bits；
- signed change/residual features：分别编码 positive 和 negative magnitude；
  一部分 thresholds 表达 noise/core，另一部分表达 logarithmic 或
  physically interpretable tail；
- 所有 fitted thresholds 只来自当前 fold 的 training roles，并在
  segment/block boundaries reset 所有 causal state。

一个小型原型可把总 input budget 控制在约 24–72 bits 作为讨论范围，而不是
沿用 256 bits；这只是 cost envelope，不是冻结参数。exact numeric features、
每项 bits、quantiles、tail thresholds 和 total budget 都是
`Project-designed` choices。

### 6.3 Keep method questions separate

在恢复任何 evidence-producing run 前，至少应由 Tianhang分别决定：

1. sample/target 的精确定义和 causal delay；
2. exact numeric features 与每个 causal horizon；
3. Booleanisation family、fit population、bits 和 threshold generation；
4. target range、outlier/clipping/scaling；
5. OFF imbalance policy；
6. vanilla rTM、weighted rTM 或 cTM–rTM structure；
7. 仅用于跑通的 runtime cap 与停止条件。

这些项目不能一起写成“采用标准 rTM”。原型参数也不能被描述为文献证明的
optimal settings。

## 7. Literature and provenance

| Evidence | Use in this review | Source type |
|---|---|---|
| Abeyrathna et al., *The Regression Tsetlin Machine* | threshold propositions、additive regression mechanism、continuous-input precedent | `Inherited` mechanism；[DOI](https://doi.org/10.1098/rsta.2019.0165) |
| TMU v0.8.3, commit `df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483` | local `StandardBinarizer` and `TMRegressor` behaviour | `Inherited` fixed source；[repository](https://github.com/cair/tmu/tree/df55ecb3c200b85489ac77fbb8d9a3bc9f7e0483) |
| Zhang et al., *Sequence-to-Point Learning with Neural Networks for NILM* | mains-window-to-point target formulation | `Adapted` task precedent；[arXiv](https://arxiv.org/abs/1612.09106) |
| Alami et al., *Conv-NILM-Net, a causal and multi-appliance model for energy source separation* | past-only inference and causal temporal-context precedent | `Adapted` causality/context precedent；[arXiv](https://arxiv.org/abs/2208.02173) |
| Azizi et al., *A Novel Event-based Non-intrusive Load Monitoring Algorithm* | event/mode representation precedent | `Adapted` event precedent；[arXiv](https://arxiv.org/abs/2009.02656) |
| Kolter and Johnson, REDD | dataset provenance and low-frequency aggregate context | dataset source；[PDF](https://zicokolter.com/publications/kolter2011redd.pdf) |
| Local E001 | same-budget Han binary vs quantile-threshold historical evidence | exploratory, `inconclusive`; not Protocol R |

原始 sequence-to-point 方法以 window midpoint 为 target，并使用 target 两侧的
context；把它改成 past-only/current target 是项目 adaptation，不能声称原封不动
继承。causal CNN 和 event-based literature 只能支持“这些表示值得作为候选”的
判断，不能证明 rTM 上的效果。

## 8. Final interpretation and limitation

R004 的结论是一个决策建议，不是模型结果：

- **不建议**原样恢复 32-lag/8-bit T006 run；
- **建议优先讨论** compact causal level + change + multi-scale representation，
  再配 hybrid cumulative thresholds；
- delta-only、Han paired-event features、ordinary binary、one-hot 和 per-house
  normalisation 都不适合作为当前 direct rTM 主线；
- target handling、imbalance 和 model family 仍然开放，不能由 encoding
  review 代替；
- 所有 exact choices 均等待 Tianhang 批准，且在验证前只能称为
  `project-designed choices`。

本审查没有开始或恢复 T006，没有产生任何可宣称的 Protocol R performance
evidence，也没有改变已接受的 evaluation protocol。
