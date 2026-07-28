# R005 — Compact rTM Input Static Audit

## Agent Brief

- Status: complete — aggregate static audit only; no method approved
- Owner: Tianhang Tan
- Authorised: 2026-07-28
- Track: R-series review
- Data boundary: Protocol R F1 development-training roles `B2/B3/B4`,
  houses `H1/H3/H5/H6`
- Execution boundary: aggregate static audit only; no model training,
  prediction or scoring
- Sealed data: B5, H2/H4 and Protocol X prohibited
- Decision authority: audit-only candidates do not freeze the T006 method

## Audit questions

本审计根据 D007 检查：

1. 不同 causal horizon 对 fridge ON-start context 的覆盖；
2. continuous candidate features 在不同 house 与 fridge ON/OFF state 下的分布；
3. Boolean bits 的 activation、entropy、duplicate 和 constant behaviour；
4. large changes 是否仍发生 tail saturation；
5. 同一 state 是否集中为大量完全相同的 Boolean patterns；
6. cross-house bit-activation drift；
7. total features、bits、literals 和预计 training cost；
8. compact summaries 在 Pico 上所需 causal state 和 RAM。

Exact horizons、features、bits 和 thresholds 在本审计结束后仍须由 Tianhang
决定；本报告不会自动恢复 T006。

## 1. Audit-only candidate definitions

本轮不是 feature selection experiment。为了让各项统计可以比较，临时定义一个
14-feature audit bank：

| Family | Features |
|---|---|
| Level | `level_t = main[t]` |
| Immediate change | `delta_1 = main[t] - main[t-1]` |
| Causal means | `mean_h`，`h ∈ {4,16,64,256}`，window 包含 current sample |
| Residuals | `residual_h = main[t] - mean_h` |
| Ranges | `range_h = max(main[t-h+1:t]) - min(main[t-h+1:t])` |

每个 feature 的单位都是 watts。所有 history 在 house、segment、block、split
以及 non-finite aggregate 处 reset。只有完整 256-sample dependency 和 finite
fridge target 的 F1 training rows 进入 audit，因此所有 candidate horizons 使用
同一 547,562-row population。

Boolean audit 使用以下临时 encoder：

- nonnegative `level/mean/range`：pooled training quantiles
  `{P10,P25,P50,P75,P90,P99}`，输出 `x >= threshold`，每项 6 bits；
- signed `delta/residual`：positive 和 negative magnitude 分开，各使用
  `{P50,P90,P99,P99.9}`，每项共 8 bits；
- 所有 thresholds 只从上述 F1 training population 拟合。

这称为 `hybrid_signed_core_tail_8_audit`，因为它把 sign、core 和 tail 分开；
它不是 D007 已冻结 encoder。TMU `StandardBinarizer(8)` 和普通
`q=1/9…8/9` thermometer 只作为 tail-saturation references。

候选组合为：

| Candidate | Numeric features | Horizons and content | Boolean bits |
|---|---:|---|---:|
| C8 | 8 | level、delta、mean/residual at 4/16/64 | 56 |
| C11 | 11 | C8 + range at 4/16/64 | 74 |
| C14 | 14 | C11 + mean/residual/range at 256 | 94 |

这些名称只服务本审计，不构成 T006 configuration。

## 2. Data scope and integrity

| House | Eligible rows | Fridge OFF | Fridge ON |
|---|---:|---:|---:|
| H1 | 200,561 | 150,779 | 49,782 |
| H3 | 140,493 | 85,437 | 55,056 |
| H5 | 13,719 | 7,288 | 6,431 |
| H6 | 192,789 | 95,226 | 97,563 |
| Pooled | 547,562 | 338,730 | 208,832 |

数据通过 frozen manifest 的 approved development loader 读取：

- fold `F1`；
- role `training`；
- blocks `B2/B3/B4`；
- houses `H1/H3/H5/H6`。

没有访问 B1 validation、B5、H2/H4 或 Protocol X。没有调用
`TMRegressor.fit()`、加载模型、产生 predictions 或 model metrics。输出全部是
aggregate tables，不包含 row positions、时间序列或可还原样本。

## 3. Causal horizon coverage

“看到启动背景”定义为：fridge ON row 的 dependency window 内包含同一
segment/block 中已观察到的最近一次 `OFF→ON` transition。ON threshold 仍为
strictly `>15 W`。left-censored 或被 missing/non-finite value 截断的 onset
视为未知，不算覆盖。

### 3.1 Pooled coverage curve

| Horizon | Nominal duration | Covered ON rows | Coverage |
|---:|---:|---:|---:|
| 1 | 3 s | 719 | 0.34% |
| 2 | 6 s | 1,385 | 0.66% |
| 4 | 12 s | 2,577 | 1.23% |
| 8 | 24 s | 4,741 | 2.27% |
| 16 | 48 s | 8,896 | 4.26% |
| 32 | 96 s | 17,174 | 8.22% |
| 64 | 192 s | 33,667 | 16.12% |
| 128 | 384 s | 66,515 | 31.85% |
| 256 | 768 s | 123,335 | 59.06% |

208,247 / 208,832 ON rows 最终能追溯到 dependency-contained onset；其余
585 rows 是 boundary/missingness 引起的未知 onset。即使忽略这 585 rows，
64 samples 也不足以解释大部分持续 ON state。

### 3.2 House differences

| House | 32 samples | 64 samples | 128 samples | 256 samples |
|---|---:|---:|---:|---:|
| H1 | 10.29% | 19.76% | 38.54% | 74.81% |
| H3 | 13.60% | 26.92% | 53.54% | 91.57% |
| H5 | 7.03% | 13.50% | 25.72% | 49.60% |
| H6 | 4.21% | 8.34% | 16.60% | 33.30% |

256 samples 对 H3 很充分，但对 H6 仍只覆盖三分之一。因而“更长 history
一定解决持续 ON”不成立；long-horizon summaries 可能提供背景，却不是可靠的
universal onset memory。

完整曲线见
[R005-horizon-coverage.csv](R005-horizon-coverage.csv)。

## 4. Continuous-feature distributions

### 4.1 Pooled OFF/ON comparison

| Feature | OFF P50 | ON P50 | OFF P90 | ON P90 | Interpretation |
|---|---:|---:|---:|---:|---|
| `level_t` | 170.95 | 345.53 | 549.68 | 820.62 | 最直接的 state-level separation，但 tails 大量重叠 |
| `delta_1` | 0.00 | 0.00 | 2.37 | 2.68 | 对 sustained state 几乎没有 median separation |
| `mean_64` | 174.54 | 340.07 | 617.36 | 874.43 | 保留 level separation，并降低瞬时噪声 |
| `residual_64` | -0.62 | -1.12 | 4.69 | 80.71 | median 无 separation；ON upper tail 更明显 |
| `range_64` | 9.17 | 14.81 | 182.18 | 898.44 | event/activity context 强，但分布很宽 |
| `mean_256` | 211.41 | 314.80 | 686.69 | 864.45 | state contrast 仍在，但更容易混合前一状态 |
| `residual_256` | -2.39 | 16.71 | 6.77 | 160.06 | 可表达 long-context departure，但高度依赖 cycle age |
| `range_256` | 92.45 | 194.54 | 1,215.09 | 1,772.74 | 捕获长时间 activity，house/event contamination 也最大 |

主要观察：

- `level_t` 和 `mean_h` 是唯一在 typical ON/OFF rows 上都有明显 median
  separation 的 families；
- `delta_1` 和 short residual 主要表示 sparse transitions，不能替代 level；
- `range_h` 显著提高 pattern diversity，但会把其他 appliance activity 和
  house noise 一并编码；
- 256-sample residual/range 并不是简单的“更好版本”：它们增加 context，
  也更容易跨越多次 unrelated aggregate events。

### 4.2 House sensitivity examples

`level_t` ON median 在 H1/H3/H5/H6 分别为
`358.15/291.64/320.61/345.37 W`；OFF median 为
`170.07/146.41/178.24/203.74 W`。level signal 的方向一致，但 absolute
threshold occupancy 必然随 house 改变。

`range_256` ON median 则为
`431.26/321.19/169.76/29.56 W`。这个数量级差异说明 long range 很容易成为
house-activity signature，而不只是 fridge signature。

所有 14 features × pooled/H1/H3/H5/H6 × ON/OFF 的 count、mean、std、
min、P1、P10、P25、P50、P75、P90、P99 和 max 见
[R005-feature-distributions.csv](R005-feature-distributions.csv)。

## 5. Boolean-bit audit

Full 14-feature bank 产生 94 bits：

- constant bits：`0/94`；
- repeated thresholds：`0/94`；
- exact duplicate output columns：`0/94`；
- median binary entropy：`0.469 bits`；
- entropy `<0.2 bits`：`29/94`；
- dominant value rate `>=99%`：`20/94`。

因此 hybrid bank 没有完全浪费的 constant/duplicate bit，但 q99/q99.9 tail
bits 中有相当一部分非常稀疏。它们的作用是区分 rare extremes，不能仅因低
entropy 判为无用；但 20 个近恒定 bits 说明 94-bit full bank 很可能
over-provisioned。

### 5.1 Cross-house activation

- median max–min house activation gap：约 `9.9 percentage points`；
- P90 gap：约 `36.3 points`；
- maximum gap：`54.86 points`；
- `16/94` bits 的 gap 至少 `25 points`。

最大 drift 出现在 `range_16 >= 2.84 W`：

| H1 | H3 | H5 | H6 | Max gap |
|---:|---:|---:|---:|---:|
| 71.77% | 60.10% | 37.12% | 91.98% | 54.86 points |

`level_t >= 166.59 W` 在 H5 activation 为 `100%`，H3 为 `63.57%`。
这进一步确认 pooled quantile thresholds 并不会自动消除 house identity。

每个 bit 的 exact threshold、pooled/house activation、entropy、
dominant-value rate、constant flag、threshold/output duplicate count 和
max house gap 见
[R005-bit-audit.csv](R005-bit-audit.csv)。

## 6. Tail saturation

Large change 定义为 `|delta_1| >= 50 W`，共有 6,017 rows。

| Encoder | Extreme thresholds | Pooled saturated | Large-change saturated | Distinct large-change codes |
|---|---|---:|---:|---:|
| TMU StandardBinarizer 8 reference | -6485.65 / +21.63 W | 0.74% | 44.51% | 3 |
| Pure quantile 8 reference | -2.42 / +2.24 W | 22.23% | 100.00% | 2 |
| Hybrid signed core+tail 8 | -1572.06 / +1610.19 W | 0.09% | 8.28% | 6 |

Hybrid encoding 显著缓解但没有消除 saturation。最大 positive/negative delta
仍分别约为最高 hybrid threshold 的 `7.31×` 和 `5.59×`；最极端约 0.09%
rows 仍会共享 terminal code。

TMU reference 的最低 threshold 极端偏负、最高 threshold 只有 +21.63 W，
体现 unique-value spacing 的明显 asymmetry。pure quantiles 则把所有
large changes 压成正负两个 terminal codes，不适合作为 tail representation。

完整结果见
[R005-tail-saturation.csv](R005-tail-saturation.csv)。

## 7. Identical Boolean patterns

`pair collision probability` 表示在同一 fridge state 中随机抽取两个不同 rows，
它们具有完全相同 Boolean pattern 的概率。相比单纯“重复 rows 比例”，它不易
被 50 万级 row count 误导。

| Candidate/state | Unique patterns | Dominant-pattern share | Pair collision |
|---|---:|---:|---:|
| C8 OFF | 8,253 | 9.37% | 2.3846% |
| C8 ON | 6,395 | 9.63% | 1.8407% |
| C11 OFF | 34,187 | 1.25% | 0.1077% |
| C11 ON | 25,555 | 0.76% | 0.0875% |
| C14 OFF | 82,943 | 0.50% | 0.0258% |
| C14 ON | 62,365 | 0.36% | 0.0182% |

C8 明显把大量 steady rows 压入少数 patterns。加入 range features 后，
C11 的 pooled collision 已下降约一个数量级；C14 再下降，但收益伴随更多
bits、long history 和 house drift。

H5 OFF 是最明显的 collapse：

| Candidate | Dominant-pattern share | Pair collision |
|---|---:|---:|
| C8 | 56.67% | 32.60% |
| C11 | 40.53% | 18.28% |
| C14 | 21.50% | 5.92% |

所以增加 pattern diversity 不能被直接解释为更好的 NILM：H5 的高度重复说明
aggregate steady state 本身信息有限，而 range bits 带来的多样性又可能主要是
house noise。只有未来经批准的 model experiment 才能判断其预测价值。

所有 pooled/per-house、ON/OFF pattern statistics 见
[R005-pattern-audit.csv](R005-pattern-audit.csv)。

## 8. Representation and expected training cost

T006 reference 有 256 Boolean inputs、512 positive/negated literals 和
16 个 32-bit literal chunks。下表保持 50,000 training rows、200 clauses、
8 TA state bits 和 5 epochs 不变，只比较 representation-dependent cost。

| Candidate | Features | Bits | Literals | 32-bit chunks | Relative chunk scan | Dense float64 encoded 50k | Core TA state-word payload |
|---|---:|---:|---:|---:|---:|---:|---:|
| T006 reference | 32 raw lags | 256 | 512 | 16 | 100% | 102.4 MB | 102.4 KB |
| C8 | 8 | 56 | 112 | 4 | 25.0% | 22.4 MB | 25.6 KB |
| C11 | 11 | 74 | 148 | 5 | 31.25% | 29.6 MB | 32.0 KB |
| C14 | 14 | 94 | 188 | 6 | 37.5% | 37.6 MB | 38.4 KB |

`Relative chunk scan` 是根据 TMU Boolean literal packing 推算的 core
representation cost，不是 measured wall time。47-minute stopped T006 run
没有完成，且包含 preprocessing/runtime overhead，不能据此线性宣称 C11
一定在某个分钟数内完成。

若 encoded matrix 立即转成 `uint32`，C8/C11/C14 的 50k matrix 分别约为
11.2/14.8/18.8 MB；T006 reference 为 51.2 MB。

完整 cost fields 见
[R005-cost-audit.csv](R005-cost-audit.csv)。

## 9. Pico causal state and RAM estimate

估算假设 aggregate 和 summaries 使用 `float32`，index 使用 compact integer，
thresholds 作为 `const float32` 放在 flash。它只覆盖 preprocessing state 和
Boolean buffer，不包含 TM model、CSV/SD I/O、stack、logging 或 display。

| Candidate | Max history | Scan-range working RAM, packed bits | Scan-range RAM, uint32/bool input | Optional monotonic-range deque worst case | Threshold flash |
|---|---:|---:|---:|---:|---:|
| C8 | 64 samples | 323 B | 540 B | 0 B | 224 B |
| C11 | 64 samples | 338 B | 624 B | +672 B | 296 B |
| C14 | 256 samples | 1,124 B | 1,488 B | +2,720 B | 376 B |

两种 range implementation：

- **RAM-minimal scan**：保留一个 64/256-sample ring buffer，每个新 sample
  重扫 range windows；C11/C14 分别约 84/340 次 window comparisons；
- **O(1)-style monotonic deques**：减少每步 comparisons，但 worst-case RAM
  增加约 672/2,720 B。

在 3-second cadence 下，scan-range 路径很可能更符合 prototype-first 目标；
但这是静态估算，不是 Pico benchmark。C8/C11 的 64-sample history 对 RAM
非常轻，C14 的 256 samples 也仍是 kilobyte 级 preprocessing state。

## 10. Decision interpretation

本轮 evidence 支持以下判断，但不替 Tianhang 冻结方法：

1. **C8 最便宜，但 pattern collapse 明显。** 其 64-sample onset coverage 只有
   16.12%，pooled dominant pattern 约 9–10%，H5 OFF 更达到 56.67%。
2. **C11 是当前最平衡的 static-audit candidate。** range features 在只增加
   18 bits 的情况下把 pooled collision 降低约一个数量级，预计 core chunk
   cost 仍只有 T006 reference 的 31.25%，scan implementation 的 preprocessing
   RAM 约 338 B。
3. **C11 的主要风险是 house drift。** 最大 activation gap 主要来自 range
   bits，因此不能仅凭 pattern diversity 就批准它。
4. **C14 的 long context 有信息，但不是普遍 onset solution。** 它把 pooled
   256-sample coverage 提到 59.06%、进一步降低 collision；H6 coverage 仍只有
   33.30%，且 range_256 极其 house-dependent。
5. **94-bit full bank 不宜直接冻结。** 20 bits 在至少 99% rows 上保持同一值，
   表明 tail allocation 需要 Tianhang 在“rare-event resolution”和 compactness
   之间做选择。
6. **Hybrid signed core+tail 比两个 references 更可信。** 它把 large-change
   saturation 从 pure-quantile 的 100% 降到 8.28%，但 extreme tail 仍存在。

如果下一步要冻结 exact input，R005 建议 Tianhang优先在以下两个方向间决定：

- 以 **C11 / 64-sample maximum horizon** 为小型首轮候选，并接受 range
  house drift 作为待验证风险；
- 加入 **256-sample summaries**，以更高 bits/state cost 换取部分 long-cycle
  context，但不能声称保存了完整 fridge onset history。

Target clipping/scaling、runtime cap 和 stop rule 仍必须另行冻结。R005 没有
批准、启动或恢复任何训练。
