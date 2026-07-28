# 项目计划 / Project Plan

## Agent Brief

- Status: accepted direction; live authority is elsewhere
- Owner: Tianhang Tan
- Last updated: 2026-07-23
- Primary model: Tsetlin Machine
- Primary dataset: REDD
- Formal research protocol: Protocol R v1 contract frozen by T004; no formal model result
- Formal delivery line: T001–T013
- Parallel exploration: E-series
- Read-only analysis: R-series review

本计划定义项目方向、研究问题和正式交付路线，不代表其中任何 task 已自动授权。实时授权只看 [CURRENT_STATE.md](docs/CURRENT_STATE.md)。

## 1. 项目目标

本项目研究 causal、event-level、multi-appliance NILM，并建立一条可追溯的 TM workflow：

```text
REDD
  → event detection
  → event pairing
  → feature extraction
  → Booleanisation
  → one binary TM per appliance
  → train / validation / test evaluation
  → model export
  → host-native parity
  → Raspberry Pi Pico parity and measurement
```

项目同时回答三个层面的问题：

1. 工程上，能否将本地训练的 TM 可靠导出并在 host/Pico 得到一致结果？
2. 研究上，在 leakage-controlled protocol 下，baseline 的真实性能和主要瓶颈是什么？
3. 设计上，哪些受控修改能改善 macro/per-class F1，或者在更小模型、较低 latency、较短 decision delay 下保持性能？

目标不是把 Han 的仓库原样复制，也不是强行证明某个预设创新。event detection、pairing、alignment、features、Booleanisation、TM output structure、sampling、decoder 和 embedded representation 都可以成为研究对象。

理想研究目标是在冻结的正式任务上，以至少 3 个 appliance classes 达到 macro F1 ≥ `0.80`。这是 aspirational target，不是结果保证，也不是诚实完成论文的必要条件。

## 2. Research Questions

### RQ1 — Engineering reproduction

本地训练的 TM 能否经过 save/reload、C export、host-native inference 和 Pico inference，并在 numeric features、Boolean bits、signed votes 和 predictions 上保持 parity？

### RQ2 — Formal baseline

在最终冻结的 sequence-first、leakage-controlled evaluation protocol 下，event-level appliance recognition 的 baseline performance 是多少？

### RQ3 — Controlled improvements

哪些单变量、可解释的改变能够改善 macro F1、per-class recall/precision、class coverage 或 failure behaviour，同时不使用 future leakage 或 locked-test feedback？

### RQ4 — Embedded trade-offs

feature count、Boolean representation、TM structure 和 parameters 如何影响 model bytes、RAM/flash、inference latency、decision delay 和 Pico feasibility？

## 3. 三轨项目管理

### T-series — 正式工作

用于 protocol、shared implementation、formal baseline、evaluation、deployment 和最终 evidence pack。只有 Tianhang 明确授权后才能改变共享项目状态。一个 task 完成不自动开启下一个。

### E-series — 隔离探索

用于一个清晰 hypothesis、diagnostic 或 feasibility question。Tianhang 可以用一条明确指令授权，不需要先修改完整 roadmap。

每个 E-series：

- 使用 `E### — Direct Name`；
- 独占整个 experiment mutable root；
- 在首次 evidence-producing execution 前冻结并锚定 machine-readable design；
- 不读取 candidate/locked test；
- 不自动改变 formal method；
- 可得到 `supported`、`not_supported`、`inconclusive` 或 `invalid`；
- negative/inconclusive 可正常归档，不阻塞其他方向。

多个 E-series 可以并行，但只共享 hash-identical immutable inputs。

### R-series review — 只读审查

用于审查已有 code、protocol、literature、data description 或 results。它不训练、不评分，不产生新的实验结果。持久化审查报告放在 `docs/reviews/`。

## 4. 当前正式基线定义

预定的 Protocol R baseline 是：

- dataset: REDD；
- input: aggregate mains；
- event detection；
- event pairing；
- causal/declared-delay feature extraction；
- Boolean encoding；
- one binary TM per appliance；
- unified train/validation/test evaluation；
- macro/per-class precision、recall、F1；
- model size 和 latency。

T004 已在 frozen manifest 中把 “one binary TM per appliance” 定义为 independent
multi-label outputs，并冻结：

- simultaneous positives；
- all-negative/reject；
- multi-positive conflict；
- thresholds 和 tie rules；
- accuracy/confusion-matrix 形式；
- per-model 与 ensemble model size/latency；
- decision time 与 future context。

普通 `accuracy` 只能按 frozen contract 写成 per-appliance binary accuracy；
event exact-match 仅在四类 label 全部 observable 时可报告。

## 5. Han-compatible engineering path

Han repository 是 external reference implementation，不是逐文件照抄的 specification。

T003 已完成限定的 two-class Protocol H PC reproduction：

- pinned Han/REDD revisions；
- staged preprocessing；
- 23 numeric slots / 184 Boolean bits；
- TM training；
- save/reload；
- inference model export；
- C header export；
- repeatability 和 reload defect 记录。

权威 later local run 为 410 H3 matched events、accuracy `0.965854`、macro F1 `0.914298`、C model data `9,058` bytes，且 live model 与 reload 存在 1 个 prediction mismatch。

该结果只证明 label-assisted Protocol H PC compatibility。它不证明：

- aggregate-main-only inference；
- strict causality；
- Protocol R performance；
- host-native parity；
- Pico behaviour；
- end-to-end real-time NILM。

最初 Pico boundary 仍计划为：

- Python 负责 event detection、pairing 和 feature extraction；
- host-native/Pico 接收相同 ordered numeric feature vector；
- host-native/Pico 负责 Booleanisation 和 TM inference；
- 输出 Boolean bits、signed votes 和 prediction 用于 parity。

pre-Booleanised input 可以作为 smoke test，但不能代替 feature-to-TM parity。

## 6. Protocol 状态

| Protocol | Purpose | Current evidence |
|---|---|---|
| Protocol H | compatibility reproduction | T003 PC evidence exists |
| Protocol R | primary mixed-house dissertation evaluation | T004 contract frozen；no formal baseline/result |
| Protocol X | fixed H2+H4 held-out-house generalisation/stress test | support-only audit exists；no model result |
| Protocol D | final deployment model after method freeze | not run |

### T004 resolution

[D005](docs/decisions/D005-protocol-r-v1-class-and-support-eligibility.md) 已解决
R002 识别的冲突：

- Protocol R 使用 H1/H3/H5/H6 mixed-house within-population；
- 每 segment 为 B1–B5 floor split，B1–B4 四折 CV，B5 locked；
- Protocol X 固定 H2+H4，与 development/model selection 分离；
- 使用 `sequence-first, row-position blocked`，不声称 original raw time；
- fridge/microwave full eligible，dish washer development-only，washer dryer
  support-ineligible。

这只是 evaluation contract，不是 formal baseline result。

## 7. Scope

### In scope

- Han current workflow inspection 和 compatibility reproduction；
- REDD inventory、support 和 split preflight；
- aggregate-main event detection/pairing；
- event-level features 和 Booleanisation；
- TM training、validation、export、inference；
- one-vs-rest binary TM 与明确 alternatives；
- host-native/Pico parity；
- causal replay；
- model size、flash/RAM、latency 和 decision delay；
- controlled experiments；
- dissertation/demo figures、tables 和 evidence。

### Deferred from minimum formal loop

- Han full environment 的 file-for-file reproduction；
- full ESP32 UI/LVGL/TFT/SD-card stack；
- live electrical meter integration；
- on-device event detection/pairing/feature extraction；
- end-to-end real-time claim；
- broad hyperparameter optimisation；
- cross-dataset evaluation；
- optional Protocol X；
- production reliability test。

Deferred 不等于永久排除。可以用 isolated E-series 做 bounded feasibility probe，但正式采用仍需 T-series。

### Out of scope

- 整体复制旧仓库或 Han repo；
- 把 prototype 当成 verified shared code；
- 用 locked test 调参或选方法；
- 把 label-assisted event construction 写成 deployable aggregate-main inference；
- 用其他 learned classifier 替代 primary TM system；
- 只凭 compile success 声称 hardware behaviour；
- 把不同 protocol/class/split 的分数放在同一 performance ladder。

## 8. 数据与 split contract

当前 pinned input：

- Han commit: `8c5e90df34236ba0afcc4ec46ac083d829de4d51`
- REDD submodule: `a621bbd6399e49c6798550618fe43b113149455b`
- 35 preprocessed independent segments
- nominal 3-second cadence
- frozen recorded classes: fridge、microwave、dish washer、washer dryer
- Protocol R v1 eligibility: fridge/microwave full；dish washer
  development-only；washer dryer support-ineligible/deferred
- core manifest: `artifacts/manifests/protocol_r_evaluation_v1.json`

所有正式 data pipeline 必须：

- 从 approved manifest 和明确 role 加载；
- 不用 unrestricted glob 自动发现全部 houses；
- 在 segment/split boundary reset detector/pairer/state；
- 丢弃 dependencies crossing boundary 的 output；
- 只用 training data fit normalizer、threshold、sampling policy 或 learned preprocessing；
- development mode 明确拒绝 candidate/locked test；
- 用 automated tests 证明拒绝行为。

missing appliance column 不能自动解释为 appliance OFF。T004 eligibility record
按 house/appliance 保留 unavailable identity。

## 9. Feature、Booleanisation 与 model contracts

### Feature schema

每个 model bundle 必须包含：

- ordered feature names；
- units；
- extraction window/dependency；
- causal availability time；
- dtype/range；
- missing/non-finite policy；
- schema version/hash。

新增、删除、重排或重新定义 feature 都是 schema change。

### Booleanisation

必须记录：

- encoder type；
- bits per feature；
- threshold/statistics；
- fit data role；
- bit order；
- integer/float rule；
- schema/hash。

Python、host-native 和 Pico 必须使用同一个 frozen encoder contract。

### Model bundle

至少包含：

- model structure 和 parameters；
- class/output mapping；
- feature/encoder schema；
- thresholds/tie policy；
- seed/repeat provenance；
- source/config hashes；
- exported C identity；
- model bytes；
- version/hash。

### Parity fixtures

每个 fixture 至少比较：

- ordered numeric features；
- Boolean bits；
- signed votes for every output；
- threshold/tie behaviour；
- final prediction；
- invalid input behaviour。

只比较几个最终 predictions 不足以证明 parity。

## 10. Metrics

### Classification

正式报告至少包含：

- per-appliance precision、recall、F1、support；
- macro precision、recall、F1；
- repeated-run mean 和 sample standard deviation 或预声明 uncertainty；
- clearly named accuracy；
- clearly defined confusion representation；
- class/house/segment eligibility。

washer dryer 在某些 held-out houses support 很低，单个样本会显著改变 recall。不能只给单一 F1 而不报告 support/uncertainty。

### Event construction

根据 layer 记录：

- edge/event recall；
- candidate burden；
- precision；
- unmatched/ambiguous/overlap rate；
- pairing coverage；
- duration/power consistency；
- boundary discard count；
- causal delay。

### Embedded

至少区分：

- model data bytes；
- total firmware flash；
- runtime RAM；
- per-TM inference latency；
- ensemble inference latency；
- feature-to-decision latency；
- event closure / future-context waiting time；
- serial/logging overhead；
- repetitions、median、p95、max。

短 TM inference time 不等于 end-to-end real-time NILM。

## 11. Research evidence discipline

每个有效实验必须形成：

`question → frozen design → data/code/config identity → run → result → interpretation → limitation → decision → next question`

值得详细记录：

- 验证某个合理直觉不成立；
- 与最终方法形成清晰对照；
- 暴露数据、protocol 或 system limitation；
- 有可复现结果并能解释原因；
- 排除一条原本可信的方向。

不值得进入主研究叙事：

- coding error；
- configuration 未生效；
- data contamination；
- arbitrary parameter poking；
- 大量近似重复的 hyperparameter run。

近似设置压缩为一张 tidy table 或 appendix。任何 positive result 在成为正式方法前都需 repeated seeds 和 T-series revalidation。

详见 [RESEARCH_EVIDENCE_STANDARD.md](docs/RESEARCH_EVIDENCE_STANDARD.md)。

## 12. Formal T-series Delivery Line

| Task | Exit condition |
|---|---|
| T001 — Governance Review and Repository Bootstrap | governance 和 clean repository verified |
| T002 — REDD Inventory and Protocol R Preflight | data/support/candidate manifest recorded without model scoring |
| T003 — Han Two-Class PC Reproduction | minimum staged Protocol H PC route audited, run, repeated and bounded |
| T004 — Protocol R Evaluation Contract and Test Freeze | Completed with documented class limitations；protocol population、eligibility、binary outputs、metrics、access gate 和 exact test hash accepted |
| T005 — Protocol R Baseline Implementation | development baseline reproducibly runs without test access |
| T006 — Host-Native Inference Parity | host bits/votes/predictions match Python fixtures |
| T007 — Pico Feature-to-TM Deployment | board compiles、flashes、runs and records parity/resource evidence |
| T008 — Layered Baseline Error Analysis | per-layer/per-class bottlenecks supported by development evidence |
| T009 — Promoted Method Confirmation | selected E candidates revalidated under formal development protocol |
| T010 — Final Method and Evaluation Freeze | code/config/model/seeds/metrics/final manifest frozen |
| T011 — Final Protocol R Evaluation | predeclared method evaluated once on locked test |
| T012 — Protocol D Model and Pico Verification | deployment model exported、parity-checked and measured |
| T013 — Dissertation, Demo, and Optional Protocol X Evidence Pack | figures/tables/limitations/demo and approved stress test complete |

正式路线可以与 isolated E/R work 并行，但 dependencies 和 mutable paths 不能冲突。

## 13. Dissertation 与 presentation 输出

每个重要结果应尽早准备：

- paper-ready English claim；
- 中文解释；
- exact evidence path；
- figure/table；
- protocol/claim scope；
- limitation；
- whether promoted；
- connection to RQ。

[EVIDENCE_INDEX.md](docs/EVIDENCE_INDEX.md) 是论文和答辩材料的中央索引。最终写作不应重新搜索所有 branch 或重新跑一遍实验才能知道结果。

## 14. Claim boundaries

除非有直接证据，不得声称：

- complete Han reproduction；
- clean Protocol R baseline；
- unseen-house generalisation；
- aggregate-main-only deployment；
- strict causality；
- host/Pico parity；
- real-time NILM；
- hardware latency；
- final dissertation performance。

每个 claim 必须指出它属于 compatibility、exploratory、historical、formal development、locked test、deployment、oracle 还是 label-assisted evidence。

## 15. 主要风险与 fallback

| Risk | Response |
|---|---|
| Protocol 定义冲突 | T004/D005 已冻结 research question、population 和 class eligibility；后续不得静默改写 |
| 原始 timestamp provenance 缺失 | 使用 honest row-position contract，避免 raw-time claim |
| weak class support | 报告 support/uncertainty，必要时调整 formal class decision |
| event detection/pairing bottleneck | 分层诊断，不用 TM 参数掩盖 upstream error |
| save/reload/parity defect | 在 host/Pico 前逐层比较 bits/votes/predictions |
| macro F1 未达 0.80 | 保留可复现 baseline、negative results、failure analysis 和 embedded trade-offs |
| 时间不足 | 优先完成 coherent formal loop，不扩张 UI/live-meter scope |

论文可以包含失败但有价值的尝试，只要它们是合理设计、可复现、能解释并对最终选择有贡献。代码写错和随意乱调不是 research contribution。

## 16. 实时状态入口

本文件只保存研究方向、依赖和正式 roadmap，不复制 active work、PR 状态或当前
授权。实时状态唯一入口是 [CURRENT_STATE.md](docs/CURRENT_STATE.md)。
