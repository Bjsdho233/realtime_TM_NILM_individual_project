# NILM 工作流分层研究图
# NILM Workflow Layer Map

## Agent Brief

- Status: current research orientation note
- Date: 2026-07-23
- Purpose: connect workflow layers, evidence and future questions
- Formal Protocol R result: none
- Legacy locator: `docs/reviews/R001-legacy-evidence-and-reuse-map.md`

## 1. 为什么要分层

TM 的最终 F1 不是只由 TM parameters 决定。NILM pipeline 前面任何一层出错，都会改变后面看到的 training examples：

```text
data/protocol
  → event detection
  → label association
  → event pairing
  → feature/alignment
  → Booleanisation
  → TM training/output
  → decoder/state
  → export/parity
  → Pico/latency
  → evidence and claims
```

因此研究必须逐层问：

- 这一层输入和输出是什么；
- 它会造成哪类 false positive/false negative；
- 以前试过什么；
- 结果适用于哪个 protocol；
- 下一步最小实验是什么。

旧仓库中的 Round 编号只用于定位历史，不能替代当前 T/E/R identity。精确 repo、commit、branch 和 file 见 [R001](../reviews/R001-legacy-evidence-and-reuse-map.md)。

## 2. Data、protocol 与 event construction

| Layer | 主要作用 | 已有证据 | 当前解释 |
|---|---|---|---|
| 1. Evaluation protocol | 决定 train/validation/test population、leakage boundary 和 claim | D002 定义 mixed-house Protocol R、held-out-house Protocol X；D003 candidate layout 又完整留出 H2/H4 | 当前存在 protocol conflict。H2/H4 继续 sealed，但不能直接称为 final Protocol R test；T004 必须选择 |
| 2. Dataset and class support | 决定哪些 appliance 有足够 independent evidence | T002 固定 35 segments、1,508,578 rows；electric furnace 未达到 candidate support，D004 改用 washer dryer | class set 是 data/protocol decision，不是模型偏好；missing column 不等于 OFF |
| 3. Time and boundaries | 决定 event order、state reset、future leakage 和 window validity | 当前只能证明 independent segment 内 row order 和 nominal 3-second cadence | 使用 `sequence-first, row-position blocked`；不能声称已恢复 raw timestamps |
| 4. Event detection | 从 aggregate mains 找正负变化 | 历史 Round 7G first-difference detector 有较高 transition coverage，但 candidate burden/precision 弱；Round 9 倾向 D2 adaptive detector | detector 决定 event recall 上限；高 edge recall 不等于有用 event precision |
| 5. Edge-label association | 用 appliance channel 给 aggregate event 建 reference label | Han `redd_edge_match.py` 为 label-assisted route；旧 Round 9C/9D 显示 dishwasher FP 常靠近其他 appliance events | 可用于训练/诊断，但 appliance channels 不能进入 deployable inference；overlap/ambiguity 是真实瓶颈 |
| 6. Event pairing | 将 rise 与后续 fall 组合成 activity episode | ISTM historical global pairing 五 seed macro F1 约 `0.5082 → 0.5986`；旧 Round 7K/8A 研究 aggregate-only episodes | pairing 有价值，但成功结果是 offline/label-assisted；不能直接证明 causal real-time pairing |

## 3. Representation、TM 与 decoder

| Layer | 主要作用 | 已有证据 | 当前解释 |
|---|---|---|---|
| 7. Features and temporal alignment | 把 event/window 转成 transition、duration、stats、shape、pre/post features | Han 为 23 ordered slots/22 unique names；旧 Round 10F 指向 alignment bottleneck；Round 10H bounded pre/post historical macro F1 `0.6114 → 0.6791` | bounded causal context 是较强 future hypothesis，但必须在 current protocol 重验 |
| 8. Booleanisation | 将 continuous features 映射为 TM bits | 旧项目研究 q4/q8/q16 与 train-only quantile encoders；E001 在相同 184-bit budget 比较 Han binary 和 `threshold_8` | E001 mean delta `+0.017179`，只赢 3/5 seeds，outcome `inconclusive`；不能把 Booleanisation 当唯一瓶颈 |
| 9. Output task and TM structure | 决定 multiclass、one-vs-rest、joint state 和 overlap 表达 | Han staged trainer 为 multiclass；历史 Round 7B 比较 sparse 16-class joint state 与 per-appliance binary TMs，后者更合适于当时任务 | 当前 baseline 计划 one binary TM per appliance，但 simultaneous positives/all-negative/metrics 仍由 T004 定义 |
| 10. TM training and sampling | clauses、states、`T`、`s`、epochs、seed、shuffle、balance、hard negatives | 历史 Round 7D candidate 在 Round 7E confirmation 0/3 seeds；class balance/hard negative 有 class trade-off；E002 显示 training order 可能重要 | repeated seeds 必须；training trick 不能修复错误 event/label/alignment；先 baseline 和 bottleneck，再调参 |
| 11. Decoder and temporal state | 将 votes 变成 event/state decision | 历史 Round 7F filtering gain 很小；Round 8B hard gating 下降；Round 10I no-FSM variant `0.6805` 最好 | 当前证据不支持用复杂 static FSM 掩盖 upstream weakness；优先简单、validation-selected decoder |

## 4. Export、parity 与 Pico

| Layer | 主要作用 | 已有证据 | 当前解释 |
|---|---|---|---|
| 12. Serialisation and C export | 将 training model 变成可 reload/embedded representation | T003 later local archive 成功 save/reload/inference export/C header，C model data `9,058` bytes | export route 可运行，但不能从“导出成功”推断 parity 完整 |
| 13. Python/host/Pico parity | 核对 features、bits、votes、predictions | T003 410-event run 中 training reload 与 inference reload 完全一致，但 live model 与两种 reload 各有 1 个 prediction mismatch；state/mask 仍有 29 disagreements | T003 不是完整 parity。T006/T007 必须逐层比较 bits 和 every-class votes |
| 14. Embedded boundary | 决定 PC/Pico 各自运行哪些 stages | Han firmware 使用 SD native-float replay、不同 FIFO pairer/quantiser 和 post-event samples；当前计划先做 numeric feature → Booleanisation/TM on Pico | 第一阶段证明 feature-to-TM parity；on-device detection/pairing/live meter 仍 deferred |
| 15. Latency and real-time | 区分 compute、event closure、future context 和 I/O delay | Han/历史 demo 的 sub-ms TM inference 不能证明完整 causal route | 同时报告 TM compute latency 和 algorithmic decision latency；没有 full causal chain 不称 end-to-end real-time |
| 16. Evidence and claims | 将 run 变成论文可评估证据 | T002/T003/E001 已有不同 evidence scope；新 schema/checker 建立统一 entry | protocol、data、code、config、seed、metrics、hash 和 limitation 缺一不可；不同任务分数不能直接排序 |

## 5. 当前项目中最容易混淆的两份 T003 结果

| Record | Events | Accuracy | Macro F1 | C model bytes | Reload mismatch | Status |
|---|---:|---:|---:|---:|---:|---|
| [Later archived local reproduction](../../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md) | 410 | `0.965854` | `0.914298` | `9,058` | 1 | authoritative current-project local evidence |
| [Earlier pre-reproduction record](../reproduction/HAN_MINIMUM_REPRODUCTION_RESULT.md) | 413 | `0.9758` | about `0.94` | `9,004` | 0 | contextual pre-reproduction only |

两份记录使用相同 pinned source revisions，但 event counts、metrics、model hashes 和 parity observation 不同，原因未解决。当前状态、README、论文表格和 presentation 必须使用 later local archive；early record 只用于说明 provenance discrepancy。

## 6. 主要分数分别回答什么

| Evidence | Reported value | 回答的问题 | 允许的解释 |
|---|---:|---|---|
| T003 later local Protocol H | macro F1 `0.914298` | pinned two-class label-assisted PC workflow 能否在本机重复运行、reload/export？ | verified compatibility；不是 Protocol R/Pico/real-time |
| E001 Booleanisation probe | Han `0.784087`；threshold `0.801266`；delta `+0.017179` | monotonic thresholds 是否稳定替代 Han binary？ | archived exploratory `inconclusive`；没有 promotion |
| ISTM historical global pairing | `0.5082 → 0.5986` | stronger offline label-assisted pairing 能否改善 downstream classifier？ | pairing mechanism evidence；不是 aggregate-main real-time |
| Historical Round 8D | random `0.9259`；H3 held-out `0.6514` | appliance-derived signatures 在 random split 与 house shift 下差多少？ | historical reference only |
| Historical Round 10H/10I | bounded-delay `0.6791`；no-FSM `0.6805` | bounded context 和简单 decoder 是否改善旧 two-target route？ | future hypothesis source；不是 current formal result |

这些数值的 data、classes、target、split、label assistance 和 evidence grade 不同，不能放在同一个 leaderboard。

## 7. 当前 baseline 仍缺什么

1. T004 evaluation population 和 output/metric contract；
2. manifest-enforced data loader 和 sealed-test denial tests；
3. T005 clean aggregate-main detector→pairer→features→binary-TM baseline；
4. repeated development results；
5. per-layer/per-class error analysis；
6. promoted experiments；
7. final freeze 和 one-time test；
8. host/Pico parity、model bytes、RAM/flash、latency 和 decision delay。

## 8. 未来实验优先顺序

1. 先解决 protocol、population、input/output definitions；
2. 建立可重复 baseline；
3. 定位 error 来自 detector、label association、pairing、alignment、support、Booleanisation 还是 TM training；
4. 每次只改变一个主要 layer；
5. 同时看 macro/per-class effect 和 engineering cost；
6. promising result 用 repeated seeds confirmation；
7. 在 locked test 前冻结 method；
8. 用 exact exported model 做 Python→host→Pico parity；
9. 分开报告 compute latency 和 waiting time。

当前 evidence 更支持优先研究：

- correct Protocol R baseline；
- event construction 与 temporal alignment；
- class support/ambiguity；
- binary output semantics；
- strict model bundle/parity。

优先级较低：

- 反复只改 quantile count；
- broad TM grid；
- naive event-bit concatenation；
- complex static FSM；
- 在 event/feature error 未诊断前单纯加 clauses。

## 9. 每个未来实验最少回答的问题

| Field | Required record |
|---|---|
| Research question | 要减少哪个 uncertainty？ |
| Workflow layer | 改哪一层？ |
| Invariants | 哪些 data/events/features/model settings 保持不变？ |
| Evidence scope | Protocol H/R/X/D、historical、label-assisted、oracle 或 aggregate-main-only？ |
| Data identity | houses、segments、roles、support、manifest/hash |
| Model identity | schema、Booleanisation、TM structure、parameters、seed、export |
| Metrics/checks | primary metric、per-class、confusion/diagnostic evidence |
| Engineering cost | bits、model bytes、RAM/flash、latency、delay |
| Outcome | `supported`、`not_supported`、`inconclusive` 或 `invalid` |
| Decision | adopt、reject、repeat、diagnose、defer 或 promote candidate |
| Next question | 结果产生的最小后续问题 |

论文证据映射见 [EVIDENCE_INDEX.md](../EVIDENCE_INDEX.md)。
