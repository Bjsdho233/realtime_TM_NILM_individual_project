# R001 — 旧证据与复用导航
# Legacy Evidence and Reuse Map

## Agent Brief

- **Status:** Complete
- **Owner:** Tianhang Tan
- **Created:** 2026-07-23
- **Track:** R-series review
- **Reviewed scope:** Historical NILM/TM repositories, the pinned Han reference,
  and the unmerged TM training-dynamics archive
- **Evidence class:** Navigation and reuse review only
- **Protocol status:** Not Protocol R evidence
- **External mutation:** None

## Review question

当后续 Codex、GPT 或 Tianhang 想解决一个具体问题时，应该去哪个旧仓库、哪条
branch、哪个固定 commit 和哪份文件查找已有代码、实验设计与结论？其中哪些内容
只适合参考，哪些可以进入后续的 named review / migration task，哪些负结果不应再
重复？

本文件只建立导航，不复制旧代码、数据或模型，也不把历史结果升级为当前项目的
正式证据。

## Evidence boundary

以下规则适用于本文件中的所有条目：

1. 链接固定到完整 commit SHA；branch 只用于说明历史位置。
2. `historical`、`Protocol H-style`、`label-assisted`、`oracle`、
   `aggregate-main-only diagnostic`、`bounded-delay` 和 `hardware evidence`
   是不同证据边界，不能互相替代。
3. 旧仓库中的 score 不能写成当前项目的 Protocol R baseline 或 final result。
4. `candidate_for_review` 只表示“值得审查”，不表示已经批准迁移。实际复用必须
   通过命名明确的 T-series 或隔离 E-series，重新记录 provenance、dependency、
   data scope 和 acceptance rule。
5. 旧代码不得整体复制。优先迁移最小算法单元、接口合同、测试思路或实验设计。
6. 如果当前项目已经有更严格的本地证据，当前项目证据优先；历史结果只用于解释
   机制、提出假设或构造对照。

## Evidence inspected

| Source | Branch | Fixed revision | Role |
|---|---|---|---|
| [`wuhanstudio/nilm`](https://github.com/wuhanstudio/nilm) | `main` | [`8c5e90df34236ba0afcc4ec46ac083d829de4d51`](https://github.com/wuhanstudio/nilm/tree/8c5e90df34236ba0afcc4ec46ac083d829de4d51) | External Han reference |
| [`Bjsdho233/nilm-fridge-tm-research`](https://github.com/Bjsdho233/nilm-fridge-tm-research) | Multiple Round 6–10 branches | Entry-specific SHAs below | Read-only historical research archive |
| [`Bjsdho233/tm-nilm-istm-lab`](https://github.com/Bjsdho233/tm-nilm-istm-lab) | `main` | [`7ab0193b52f3fa6b7a0c4b7da212386f98309c55`](https://github.com/Bjsdho233/tm-nilm-istm-lab/tree/7ab0193b52f3fa6b7a0c4b7da212386f98309c55) | Private ISTM / global-pairing archive |
| [`Bjsdho233/realtime_TM_NILM_individual_project`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project) | `main` | [`33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/tree/33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb) | Current-project T003/E001 evidence used to cross-check legacy claims |
| Same current repository | `agent/archive-tm-training-dynamics-probes` | [`e7277cc4a0326350f51fdfc5c17b8777572deddc`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/tree/e7277cc4a0326350f51fdfc5c17b8777572deddc) | Unmerged exploratory training-dynamics archive |

本次 review 时，local cached `tm-training-dynamics-archive` checkout 位于
`825a1fca5c14afc2ee2ef3d0476cd01a339bc98a`，而 live GitHub branch 解析到
`e7277cc4a0326350f51fdfc5c17b8777572deddc`。两个 revision 的
`CHECKSUMS.sha256` 所列 archived script/result hashes 一致。后续导航应使用上表
中的 live fixed GitHub revision；local SHA 仅作为 cached review copy 的
provenance 保留。

## Quick locator

| 想解决的问题 | 先看 | 当前用途 |
|---|---|---|
| 理解 Han 的完整 workflow、TM save/load/export 和 firmware 边界 | [L01 — Han Workflow and Export Chain](#l01--han-workflow-and-export-chain) | External reference and migration candidates |
| 改进 rise/fall event pairing | [L02 — Global Event Pairing](#l02--global-event-pairing) | Mechanism evidence; offline/label-assisted |
| 判断 detector、false candidate 或 label ambiguity 是否是瓶颈 | [L03 — Event Detection and Label Ambiguity](#l03--event-detection-and-label-ambiguity) | Diagnostic design and failure taxonomy |
| 区分 event attribution 与 appliance ON/OFF reconstruction | [L04 — Event Episode and State Semantics](#l04--event-episode-and-state-semantics) | Strong negative controls |
| 研究 feature separability、anchor shift 和 bounded delay | [L05 — Feature Alignment and Bounded Delay](#l05--feature-alignment-and-bounded-delay) | High-priority hypothesis source |
| 比较或实现 Booleanisation | [L06 — Booleanisation and Runtime Equivalence](#l06--booleanisation-and-runtime-equivalence) | Encoder candidates and parity tests |
| 选择 multiclass、joint state 或 one-binary-TM-per-appliance | [L07 — TM Output Structure](#l07--tm-output-structure) | Historical architecture rationale |
| 研究 shuffle、class balance、hard negative、`T`、`s` 或 capacity | [L08 — TM Training Dynamics](#l08--tm-training-dynamics) | Exploratory controls; requires revalidation |
| 研究 event gate、threshold、FSM 或 temporal state | [L09 — Event Gate and FSM](#l09--event-gate-and-fsm) | Ablation and negative evidence |
| 做 host-native / Pico feature-to-TM 路径 | [L10 — Runtime and Pico Reuse](#l10--runtime-and-pico-reuse) | Interface and skeleton candidates |
| 理解 random split 与 held-out-house 差距，或复用 benchmark packaging | [L11 — Cross-House Reference Benchmark](#l11--cross-house-reference-benchmark) | Historical generalisation warning |

---

## L01 — Han Workflow and Export Chain

**Question:** Han 的 staged PC route、TM implementation、model export 和 Arduino
route 实际分别做了什么？

**Primary locations**

- Current-project source audit, current repository `main`, commit
  `33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb`:
  [`HAN_PIPELINE_SOURCE_AUDIT.md`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb/docs/reproduction/HAN_PIPELINE_SOURCE_AUDIT.md)
- Authoritative archived local reproduction:
  [`LOCAL_REPRODUCTION_REPORT.md`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb/experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md)
- Earlier contextual pre-reproduction:
  [`HAN_MINIMUM_REPRODUCTION_RESULT.md`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb/docs/reproduction/HAN_MINIMUM_REPRODUCTION_RESULT.md).
  Its event counts, metrics, model hashes and export size differ from the later
  local archive; the discrepancy remains unresolved.
- Han staged scripts at `wuhanstudio/nilm`, `main`,
  `8c5e90df34236ba0afcc4ec46ac083d829de4d51`:
  [`redd_edge_detect.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/redd_edge_detect.py),
  [`redd_edge_match.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/redd_edge_match.py),
  [`redd_event_pair.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/redd_event_pair.py),
  and
  [`redd_tm_training.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/redd_tm_training.py)
- TM and export implementation:
  [`tsetlin/tsetlin.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/tsetlin/tsetlin.py),
  [`tsetlin/utils/booleanize.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/tsetlin/utils/booleanize.py),
  and
  [`tsetlin/compiler/write.py`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/tsetlin/compiler/write.py)
- Integrated Arduino route:
  [`nilm_inference.ino`](https://github.com/wuhanstudio/nilm/blob/8c5e90df34236ba0afcc4ec46ac083d829de4d51/arduino/lime-tm/examples/nilm_inference/nilm_inference.ino)

**Verified finding**

Han snapshot 中存在多条入口，并没有一条已经被证明是唯一 canonical workflow。
staged route 在 edge-label matching 时使用 appliance channels，生成 23 个有序
numeric slots，其中只有 22 个 unique feature names，再 Booleanise 为 184 个 TM
inputs，最后训练一个 multiclass TM。

权威 T003 local archive 在 410 个 H3 events 上完整复现两次 two-class PC route：
Macro F1 为 `0.9143`，C model data 为 `9,058` bytes，10 epochs 后 pre-save
与 reload 仍有 1 个 prediction mismatch。它证明 save/load、inference export
和 C-header 路径可以运行，同时确认了 upstream initialisation/state-mask
consistency defect。

integrated Arduino route 从 SD replay native floats，使用另一套 FIFO pairing
和 Boolean quantiser，并读取 post-event samples。它不是已经验证的 live causal
specification；该 snapshot 也没有完整的 Python-to-C-to-hardware parity fixture。

**Reusable content**

- TM class 与 clause representation；
- protobuf training/inference serialisation；
- C-header compiler structure；
- ordered-feature 与 signed-vote interface；
- 可供后续 parity implementation 参考的 C/Arduino evaluator。

**Evidence boundary:** `Protocol H compatibility`, `label-assisted`,
`post-event context`, `not Protocol R`, `not host-native parity`,
`not Pico evidence`, `not end-to-end real-time`.

**Migration status:** `candidate_for_named_review`。只审查并迁移最小必要组件，
不能把整个 repository 当作 package 导入。

---

## L02 — Global Event Pairing

**Question:** 当局部 rise/fall pairing 会错配或过早消耗 edge 时，global pairing
是否值得重新实现？

**Primary locations**

- Private ISTM archive, `main`,
  `7ab0193b52f3fa6b7a0c4b7da212386f98309c55`:
  [`experiments/event_pairing/README.md`](https://github.com/Bjsdho233/tm-nilm-istm-lab/blob/7ab0193b52f3fa6b7a0c4b7da212386f98309c55/experiments/event_pairing/README.md)
- Reviewable algorithm:
  [`global_event_pairing.py`](https://github.com/Bjsdho233/tm-nilm-istm-lab/blob/7ab0193b52f3fa6b7a0c4b7da212386f98309c55/experiments/event_pairing/global_event_pairing.py)
- Bounded downstream comparison:
  [`gcep_downstream_summary.csv`](https://github.com/Bjsdho233/tm-nilm-istm-lab/blob/7ab0193b52f3fa6b7a0c4b7da212386f98309c55/runs/istm_han_gcep_downstream_20260623_103259/gcep_downstream_summary.csv)
- Five-repeat comparison:
  [`repeatability_summary.csv`](https://github.com/Bjsdho233/tm-nilm-istm-lab/blob/7ab0193b52f3fa6b7a0c4b7da212386f98309c55/runs/istm_han_gcep_repeatability_20260623_111358/repeatability_summary.csv)
- Earlier aggregate-only oracle audit, branch
  `round7k-latency-event-episode-audit`, commit
  `7bba3d444faa7f5b0d3769198be4e840b3b8ac97`:
  [`Round 7K decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/7bba3d444faa7f5b0d3769198be4e840b3b8ac97/docs/experiments/round7k_latency_event_episode_audit/DECISION.md)

**Verified finding**

ISTM global pairing 先构造 candidate rise/fall pairs，再应用 power-consistency
与 training-house duration limits，最后用 dynamic programming 选择一组 pairs。
在 five-repeat downstream comparison 中，local-pairing baseline 的 Macro F1
为 `0.5082 ± 0.0279`，selected global-pairing route 为
`0.5986 ± 0.0124`。代表性 bounded run 中
`gcep_pt_abs100_rel0p25` 达到 `0.6711` Macro F1，但 five-repeat result
才是更可靠的 historical evidence。

Round 7K 另行显示了 aggregate-main episode pairing 的 diagnostic headroom，
但最好的 `P2` 只是 oracle upper bound，不是 deployable classifier。

**Reusable content**

- candidate-pair construction；
- one-edge-at-most-once selection；
- power-error 与 duration-cap design；
- unmatched-edge handling；
- downstream、common-subset 与 repeatability experiment structure。

private archive 同时包含 REDD-derived CSVs 与 generated artefacts，这些 data
files 不是 migration candidates。named review 只能读取必要的 compact method、
script、manifest 和 summary files。

**Evidence boundary:** `historical`, `offline`, `label-assisted`,
`four classes including electric furnace`, `not aggregate-main-only inference`,
`not causal streaming`, `not Protocol R`.

**Migration status:** `candidate_for_reimplementation`。未来的 aggregate-only
或 streaming pairer 必须重新设计和验证；复制旧 script 不能使该结果晋升。

---

## L03 — Event Detection and Label Ambiguity

**Question:** 当前错误主要来自 missed edges、false candidates、label matching，
还是 TM capacity？

**Primary locations**

- First-difference detector audit, branch
  `round7g-event-detector-audit`, commit
  `84a105c49a2784f15266872e7ae4ef306e4cdb97`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/84a105c49a2784f15266872e7ae4ef306e4cdb97/docs/experiments/round7g_event_detector_audit/DECISION.md)
- D2/R3 confirmation, branch
  `round9b-d2-r3-main-event-model-confirmation`, commit
  `957af9c023e2c80b150634dd2abd08c036294d46`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/957af9c023e2c80b150634dd2abd08c036294d46/docs/experiments/round9b_d2_r3_main_event_model_confirmation/DECISION.md)
  and
  [`script`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/957af9c023e2c80b150634dd2abd08c036294d46/scripts/round9b_d2_r3_main_event_model_confirmation.py)
- False-positive source analysis:
  [`Round 9C decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/19c6e2aed04aa1d35588b3ecbfa646ffb48f6046/docs/experiments/round9c_d2_fp_source_and_label_diagnosis/DECISION.md)
- Guard and matching revision:
  [`Round 9D decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/9f7599e46943738fc836b38fca8210a325d84a36/docs/experiments/round9d_appliance_specific_guard_and_matching_revision/DECISION.md)

**Verified finding**

Round 7G 选出的 first-difference detector 在 H3 diagnostic 上达到 `0.9839`
mean transition coverage，但 target transitions 附近的 event precision 只有
`0.0852`。这直接说明 edge coverage 很高并不等于已经得到有效 classifier。

后续 D2/R3 route 降低了部分 candidate burden，但 small binary TM 主要通过
压制 positive predictions 来减少 false positives，同时损失 recall。Round 9C
发现 dishwasher 的 `813` 个 false positives 中有 `529` 个靠近其他 labelled
appliance events；Round 9D 的 stricter guards 虽减少 FP，却损失了过多 recall。
在这条历史路线中，event/label ambiguity 比单纯增加 clauses 或 epochs 更像主要
bottleneck。

**Reusable content**

- detector coverage、precision 与 lag audit；
- candidate-event burden metrics；
- background 与 near-other-label FP taxonomy；
- appliance-specific support 与 ambiguity analysis；
- 可供后续 review 的 D2 detector 和 R3 feature formulas。

**Evidence boundary:** `historical aggregate-main-only diagnostic inputs`,
`appliance channels used for labels/evaluation`, `H3 repeatedly inspected`,
`class set differs from current candidate set`, `not Protocol R`.

**Migration status:** `candidate_for_design_review`。优先复用 audit questions
和 metrics；只有在 T004/T005 定义 formal loader、boundaries 与 label
eligibility 后，才审查是否 port code。

---

## L04 — Event Episode and State Semantics

**Question:** event classifier 识别到“这个 episode 包含某电器”后，能否直接把整个
episode 回填成该电器 ON？

**Primary locations**

- Aggregate-main episode oracle and latency audit, branch
  `round7k-latency-event-episode-audit`, commit
  `7bba3d444faa7f5b0d3769198be4e840b3b8ac97`:
  [`Round 7K decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/7bba3d444faa7f5b0d3769198be4e840b3b8ac97/docs/experiments/round7k_latency_event_episode_audit/DECISION.md)
- Event-episode TM and repaired metric semantics, branch
  `round8a-event-episode-tm-v2`, commit
  `8689729b9c229fba3ca01de684b8a41bcfe94865`:
  [`Round 8A decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/8689729b9c229fba3ca01de684b8a41bcfe94865/docs/experiments/round8a_event_episode_tm_v2/DECISION.md)
- Fridge/microwave event-gate pilot, branch
  `round8b-fridge-microwave-event-gate-pilot`, commit
  `63dc3cce7623be609a8dc7f6910b5ef0eb699ed9`:
  [`Round 8B decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/63dc3cce7623be609a8dc7f6910b5ef0eb699ed9/docs/experiments/round8b_fridge_microwave_event_gate_pilot/DECISION.md)

**Verified finding**

Round 7K 最好的 oracle pairing 显示出 episode-level headroom，但 mean
diagnostic finalisation latency 约为 `296` samples，p90 约为 `826` samples。
Round 8A 随后暴露了关键 semantic failure：overlap-based event label 只说明
某个 appliance 出现在 aggregate episode 中，并不意味着它在整个 episode 内都
处于 ON。其最佳 recomputed non-oracle full-backfill route 的 sample-level
Macro F1 仍只有 `0.2660`。

Round 8B 的 fridge/microwave event attribution 有一定信息，但 hard event gate
把 two-appliance Macro F1 从 J2 reference 的 `0.4889` 降到 `0.4257`。

**Reusable content**

- event attribution 与 state reconstruction 的区别；
- repaired denominator 和 threshold checks；
- event-label overlap audit；
- compute latency 与 event-finalisation latency 分开报告的方法；
- full-episode backfill 和 hard-gate negative controls。

**Evidence boundary:** `historical`, partly `oracle`, `dynamic latency`,
`sample-level state reconstruction`, `not Protocol R`.

**Migration status:** `negative_control`。保留这些 semantics 与 tests；不能把
full-episode backfill 或原 hard-gate policy 迁移为默认方案。

---

## L05 — Feature Alignment and Bounded Delay

**Question:** 当 event gate 已有较高覆盖时，feature/label temporal alignment 和
有限 post-event context 能否提高分类？

**Primary locations**

- Capacity versus feature-gap audit, branch
  `round10f-p0-performance-gap-audit`, commit
  `b846554daa09e6428c25e170a6a341820387a9c6`:
  [`PERFORMANCE_GAP_DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b846554daa09e6428c25e170a6a341820387a9c6/docs/experiments/round10f_p0_performance_gap_audit/PERFORMANCE_GAP_DECISION.md)
- Alignment audit, branch
  `round10g-p0-separability-alignment-audit`, commit
  `b433c75044d1e1ed5e9d6bda715bc84d7ae5afdf`:
  [`ALIGNMENT_SHIFT_AUDIT.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b433c75044d1e1ed5e9d6bda715bc84d7ae5afdf/docs/experiments/round10g_p0_separability_alignment_audit/ALIGNMENT_SHIFT_AUDIT.md)
  and
  [`PERFORMANCE_GAP_DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b433c75044d1e1ed5e9d6bda715bc84d7ae5afdf/docs/experiments/round10g_p0_separability_alignment_audit/PERFORMANCE_GAP_DECISION.md)
- Bounded-delay feature route, branch
  `round10h-bounded-delay-prepost-feature-extractor`, commit
  `a83cd00271ba995d7682e8d9b363102594cad85b`:
  [`BOUNDED_DELAY_RESULTS.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/a83cd00271ba995d7682e8d9b363102594cad85b/docs/experiments/round10h_bounded_delay_prepost_feature_extractor/BOUNDED_DELAY_RESULTS.md),
  [`FEATURE_DESIGN.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/a83cd00271ba995d7682e8d9b363102594cad85b/docs/experiments/round10h_bounded_delay_prepost_feature_extractor/FEATURE_DESIGN.md),
  and
  [`script`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/a83cd00271ba995d7682e8d9b363102594cad85b/scripts/round10h_bounded_delay_prepost_feature_extractor.py)

**Verified finding**

Round 10F 增大 TM capacity 后，historical Macro F1 提高到 `0.5912`，但剩余
gap 仍主要受 feature/label alignment 与 appliance selection 限制。Round 10G
发现不同 appliance 的最佳 shift 方向并不相同：fridge 为 `-8` samples，
microwave 为 `+8` samples，因此不能直接使用一个 blind global shift。

Round 10H 的 `R1_prepost_delay8` 将 two-target historical route 的 Macro F1
从 `0.6114` 提高到 `0.6791`（`+0.0677`），FP 从 `358` 降到 `182`，
同时 FN 从 `221` 增至 `269`；最明显的提升来自 microwave。

**Reusable content**

- shift audit 与 per-appliance alignment analysis；
- bounded pre/post feature definitions；
- dependency/latency accounting；
- route-level FP/FN trade-off tables；
- 将 alignment 与 TM capacity 分开的 experiment design。

**Evidence boundary:** `historical two-target P0 event split`,
`bounded-delay`, `not zero-latency`, `Mode A diagnostic`,
`not current sequence-first Protocol R`.

**Migration status:** `high_priority_hypothesis`。只有重新说明这些 feature
formulas 的 causal dependencies 与 split containment 后，才能把它们作为当前
baseline 上的 isolated E-series candidates。

---

## L06 — Booleanisation and Runtime Equivalence

**Question:** 应该怎样比较 encoder，同时保证 train-only fitting、bit order 和
batch/runtime parity？

**Primary locations**

- Round 6B encoder verification, branch
  `round6b-encoder-verification`, commit
  `37b86672baf7a95de44d8d81e7605d9489c62b48`:
  [`RUN_CONTEXT.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/37b86672baf7a95de44d8d81e7605d9489c62b48/docs/experiments/round6b_encoder_verification/runs/20260608_072742/RUN_CONTEXT.md)
- Runtime Boolean encoder, branch
  `round9j-runtime-booleanization-encoder-smoke`, commit
  `b43034b74e6a138d5a1284c376108c1f719172fe`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b43034b74e6a138d5a1284c376108c1f719172fe/docs/experiments/round9j_runtime_booleanization_encoder_smoke/DECISION.md)
  and
  [`script`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b43034b74e6a138d5a1284c376108c1f719172fe/scripts/round9j_runtime_booleanization_encoder_smoke.py)
- Current-project E001 archive, current repository `main`, commit
  `33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb`:
  [`REPORT.md`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/33a8bf0b3b240b2965ef705f4f5120a57a8ed5fb/experiments/E001-booleanization-ab-probe/REPORT.md)

**Verified finding**

Round 6B 在 House 1 three-appliance route 上验证了 `stats_bool`、
`stats_haar_bool` 和 `stats_haar_dct_bool` 的 batch/streaming equivalence。
三者分别约有 160、384 和 480 个 Boolean features，后续测试优先选择较紧凑的
`stats_bool`。

Round 9J 随后验证了另一套 10-numeric-feature / 40-bit runtime encoder，并使用
train-only threshold fitting。这些是有用的 implementation patterns，但不能合并
成一个已经稳定的 universal encoder specification。

对于 Han binary 与 threshold-8 的直接比较，应优先看 current-project E001。
在相同的 184-bit budget 下，其结论为 `inconclusive`：mean paired Macro-F1
delta 为 `+0.0172`，threshold-8 只赢得 3/5 seeds，没有满足 predeclared
acceptance rule。

**Reusable content**

- train-only threshold fitting；
- explicit ordered bit schema；
- batch/runtime equivalence fixture；
- activation、entropy 与 near-constant-bit audits；
- paired-seed encoder comparison。

**Evidence boundary:** Round 6B/9J are `historical`; E001 is
`current exploratory label-assisted evidence`; none is a formal Protocol R
encoder result.

**Migration status:** `candidate_for_interface_review`。优先复用 schema/parity
tests，不直接复制旧 encoder implementation。

---

## L07 — TM Output Structure

**Question:** 四个电器应该使用 16-class joint-state TM、single multiclass event
TM，还是 one binary TM per appliance？

**Primary location**

- Branch `round7b-four-appliance-dataset-builder`, commit
  `26de516cd3eb125657efe40098c6bdad497bd2f6`:
  [`docs/PROJECT_STATE.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/26de516cd3eb125657efe40098c6bdad497bd2f6/docs/PROJECT_STATE.md)

**Verified finding**

Round 7B 估算 four-appliance 16-class joint TM 约需要 `409,600` literal
positions，而 four binary TMs 约需要 `204,800`。因此当时建议先做
Pico-oriented binary ensemble，把 16-class joint state 保留为 secondary
ablation。

这是基于旧 class set（`electric furnace`）与旧 dataset assumptions 的
architecture/resource decision。Han pinned staged trainer 则是 single
multiclass event classifier。两种设计回答的 output question 不同：event
identity 与 simultaneous appliance state 不是同一个 target。

**Reusable content**

- literal-position resource estimate；
- output-task comparison criteria；
- per-appliance metric rationale；
- joint-state sparsity warning。

**Evidence boundary:** `historical architecture audit`, `not model-selection
evidence under current data`, `not Protocol R`.

**Migration status:** `reference_only`。当前 one-binary-TM-per-appliance 的
semantics、simultaneous positives、all-negative output、accuracy 和
confusion-matrix rules 必须由 T004 冻结，不能从 Round 7B 直接继承。

---

## L08 — TM Training Dynamics

**Question:** shuffle、class sampling、hard-negative feedback、`T`、`s` 和 larger
capacity 中，哪些值得成为新 baseline control？

**Primary locations**

- Unmerged current-repository branch
  `agent/archive-tm-training-dynamics-probes`, commit
  `e7277cc4a0326350f51fdfc5c17b8777572deddc`:
  [`README.md`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/e7277cc4a0326350f51fdfc5c17b8777572deddc/experiments/2026-07-22-tm-training-dynamics-probe/README.md),
  [`experiment_manifest.json`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/e7277cc4a0326350f51fdfc5c17b8777572deddc/experiments/2026-07-22-tm-training-dynamics-probe/experiment_manifest.json),
  and
  [`CHECKSUMS.sha256`](https://github.com/Bjsdho233/realtime_TM_NILM_individual_project/blob/e7277cc4a0326350f51fdfc5c17b8777572deddc/experiments/2026-07-22-tm-training-dynamics-probe/CHECKSUMS.sha256)
- Seed-stability negative result, branch
  `round7e-binary-tm-seed-stability`, commit
  `98db08eef2a682203b34aecf60c437f13f11948e`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/98db08eef2a682203b34aecf60c437f13f11948e/docs/experiments/round7e_binary_tm_seed_stability/DECISION.md)
- Capacity bottleneck check, branch `round10f-p0-performance-gap-audit`,
  commit `b846554daa09e6428c25e170a6a341820387a9c6`:
  [`Round 10F decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b846554daa09e6428c25e170a6a341820387a9c6/docs/experiments/round10f_p0_performance_gap_audit/PERFORMANCE_GAP_DECISION.md)

**Verified finding**

training-dynamics probe 得到一个相对稳定的 historical signal：每个 epoch 将
每个 original training event 唯一 shuffle 一次，five-seed Macro F1 从
`0.4809 ± 0.0210` 提高到 `0.5288 ± 0.0097`，paired seeds 为 5/5 wins；
但 accuracy 从 `0.7868` 降到 `0.7640`。

同一 probe 不支持把 `T=10`、hard-negative feedback 或 global class
balancing 设为默认改动。Round 7E 也留下了较早的警告：screening 中看似有希望
的 higher-`s`、longer-training candidate，在 3 个 confirmation seeds 上全部
输给 baseline。Round 10F 同样表明 larger capacity 没有消除明显的
feature/alignment bottleneck。

**Reusable content**

- 可作为 future control candidate 的 unique full-event shuffle；
- paired-seed confirmation；
- 针对 upstream `Tsetlin.step()` 的 state-signature check；
- 分离 order、replacement 与 exposure 的 class-balance sweep design；
- 将 broad hyperparameter attempts 压缩为一张表的记录方式。

**Evidence boundary:** `label-assisted Han-compatible events`, `H3 repeatedly
inspected`, `electric furnace rather than washer dryer`, `post-event features`,
`not Protocol R`, `not formal model selection`.

**Migration status:** `candidate_for_revalidation`。review 时该 archive 尚未
merge 到 `main`。不能把它追溯登记为 E001，也不能把 best row 当作 current
baseline；如果 Tianhang 决定晋升该问题，应在 formal development protocol 下
重新验证 selected control。

---

## L09 — Event Gate and FSM

**Question:** event evidence 应该作为 feature bits、row selector、hard gate，还是
交给 FSM 做 lifecycle correction？

**Primary locations**

- Event-gated stats_bool confirmation, branch
  `round10e-event-gated-statsbool-mainline-confirmation`, commit
  `939e0020f689b653e5e0724637c8ce3348832831`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/939e0020f689b653e5e0724637c8ce3348832831/docs/experiments/round10e_event_gated_statsbool_mainline_confirmation/DECISION.md)
- FSM dry-run, branch `round10i-appliance-fsm-dryrun`, commit
  `66d9d4978eb4ca1099347712229b951c0abb0405`:
  [`PERFORMANCE_DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/66d9d4978eb4ca1099347712229b951c0abb0405/docs/experiments/round10i_appliance_fsm_dryrun/PERFORMANCE_DECISION.md)
  and
  [`PROTOCOL_CAVEATS.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/66d9d4978eb4ca1099347712229b951c0abb0405/docs/experiments/round10i_appliance_fsm_dryrun/PROTOCOL_CAVEATS.md)

**Verified finding**

Round 10E 支持在该 historical route 中把 event evidence 作为 gate / row
selector，并暂停 full event-bit concatenation。Round 10I 随后发现
`V0_no_fsm_best_f1` 仍是最好方案，Macro F1 为 `0.6805`；其他 FSM variants
要么造成 false-positive explosion，要么移除了过多 positives。

Round 10I 的 event-level P0 split 也无法提供干净的 continuous stream：
train/calibration/test events 在 chronological masked diagnostic 中相互交错。
因此该实验既没有证明，也没有否定在正确 protocol 下评估的 streaming FSM。

**Reusable content**

- event-gate 与 event-bit ablation；
- no-FSM baseline；
- state-transition audit；
- 在 non-continuous splits 上做 temporal post-processing 的 protocol caveat。

**Evidence boundary:** `historical P0 event-level split`, `bounded-delay`,
`diagnostic FSM`, `not a continuous-stream result`, `not Protocol R`.

**Migration status:** `negative_control`。保留 no-FSM baseline 与 protocol
checks；不能为了遮盖 upstream errors 而直接增加 static FSM complexity。

---

## L10 — Runtime and Pico Reuse

**Question:** 哪些旧代码可以帮助建立
`numeric features -> Boolean bits -> TM votes/prediction` 的 host/Pico parity
路径？

**Primary locations**

- Runtime feature extractor, branch
  `round9i-pico-runtime-feature-extractor-smoke`, commit
  `0e4904f3b18366c48858b535bc14ca29192b16bf`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/0e4904f3b18366c48858b535bc14ca29192b16bf/docs/experiments/round9i_pico_runtime_feature_extractor_smoke/DECISION.md)
  and
  [`RUNTIME_FEATURE_EXTRACTOR_SPEC.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/0e4904f3b18366c48858b535bc14ca29192b16bf/docs/experiments/round9i_pico_runtime_feature_extractor_smoke/RUNTIME_FEATURE_EXTRACTOR_SPEC.md)
- Runtime Boolean encoder, branch
  `round9j-runtime-booleanization-encoder-smoke`, commit
  `b43034b74e6a138d5a1284c376108c1f719172fe`:
  [`Round 9J decision`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b43034b74e6a138d5a1284c376108c1f719172fe/docs/experiments/round9j_runtime_booleanization_encoder_smoke/DECISION.md)
- C++ skeleton, branch
  `round9l-cpp-runtime-extractor-boolean-encoder-skeleton`, commit
  `b5651fba1e47f7b33fcb69c635860902d9606ce3`:
  [`runtime README`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b5651fba1e47f7b33fcb69c635860902d9606ce3/runtime/round9l_pico_runtime_skeleton/README.md)
  and
  [`runtime_pipeline.cpp`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/b5651fba1e47f7b33fcb69c635860902d9606ce3/runtime/round9l_pico_runtime_skeleton/runtime_pipeline.cpp)
- Host compile follow-up, branch
  `round9m-host-compile-and-runtime-skeleton-hardening`, commit
  `5281928d5456ae72a3c2eb6a65e1a58e93d3796a`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/5281928d5456ae72a3c2eb6a65e1a58e93d3796a/docs/experiments/round9m_host_compile_and_runtime_skeleton_hardening/DECISION.md)
- Old Arduino feature-fixture inference example, branch
  `round10e-event-gated-statsbool-mainline-confirmation`, commit
  `939e0020f689b653e5e0724637c8ce3348832831`:
  [`redd_inference.ino`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/939e0020f689b653e5e0724637c8ce3348832831/arduino/lime-tm/examples/redd_inference/redd_inference.ino)

**Verified finding**

Round 9I 报告 aggregate-main R3 feature extractor 的 batch/streaming output
完全一致；Round 9J 报告其 40-bit Boolean interface 的 batch/runtime output
完全一致。Round 9L 保存了 C++ detector/feature/encoder skeleton，但 Round 9M
没有找到 host compiler，因此没有 build 或 validate 该 skeleton。

旧 `redd_inference.ino` 从 generated test header 读取 native feature fixtures，
执行 Booleanisation 与 TM evaluation 并报告 timing。它没有在 board 上运行
event detection、event pairing 或 feature extraction。reviewed commit 中存在
该 smoke path 的 source，但没有 fixed repository evidence 证明 Pico flash/run。

**Reusable content**

- ring-buffer 与 explicit runtime-state layout；
- numeric feature order 与 Boolean bit-order manifests；
- batch/runtime fixture design；
- feature-vector-to-vote Arduino smoke structure；
- host-first compilation 与 parity staging。

**Evidence boundary:** `historical feasibility`, `Python smoke evidence`,
`C++ skeleton not compile-confirmed`, `Arduino source only`,
`no verified Pico execution`, `no formal Python/host/Pico parity`.

**Migration status:** `candidate_for_component_review`。逐文件审查 Round 9L，
优先在 current project 中做 clean implementation。T006/T007 必须使用同一个
versioned model fixture，比较 numeric features、每一个 Boolean bit、signed
votes 和 prediction。

---

## L11 — Cross-House Reference Benchmark

**Question:** 为什么 random split 可能看起来很高，而 held-out house 明显下降？
旧 benchmark 的 reproducibility/PR packaging 是否值得参考？

**Primary locations**

- Branch `round8d-reproducibility-pack`, commit
  `3e20a4a31e2470021f051cc7fa63d14a20aa817c`:
  [`DECISION.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/3e20a4a31e2470021f051cc7fa63d14a20aa817c/docs/experiments/round8d_han_compatible_five_appliance_event_benchmark/DECISION.md),
  [`REPRODUCIBILITY.md`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/3e20a4a31e2470021f051cc7fa63d14a20aa817c/docs/experiments/round8d_han_compatible_five_appliance_event_benchmark/REPRODUCIBILITY.md),
  and
  [`reproduction script`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/3e20a4a31e2470021f051cc7fa63d14a20aa817c/scripts/reproduce_round8d_han_event_benchmark.py)
- Verified upstream-package snapshot, branch
  `round8d-upstream-pr-package`, commit
  `bc87092cba83eca3ca5a35d1f4d45eb2edde3e32`:
  [`package README`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/bc87092cba83eca3ca5a35d1f4d45eb2edde3e32/docs/upstream_pr/wuhanstudio_nilm_round8d_event_benchmark/README.md)
  and
  [`main_redd_tm_five_appliance_shape_benchmark.py`](https://github.com/Bjsdho233/nilm-fridge-tm-research/blob/bc87092cba83eca3ca5a35d1f4d45eb2edde3e32/docs/upstream_pr/wuhanstudio_nilm_round8d_event_benchmark/files/main_redd_tm_five_appliance_shape_benchmark.py)

**Verified finding**

final shape-feature row 在 H0 random split 上报告 `0.9259` Macro F1，在 H1
House-3-held-out route 上为 `0.6514`。这一降幅可以作为 historical evidence，
说明 appliance-derived event signatures 不会自动跨 house transfer。

reproducibility pack 与 upstream package 还展示了如何组合 single script、
commands、traceability tables 和范围受控的 PR description。但它们不能证明该
benchmark design、target classes 或 feature route 应成为 current baseline。

**Reusable content**

- 可作为 hypothesis 和 discussion point 的 cross-house degradation；
- 留待后续 review 的 shape-feature definitions；
- compact reproduction wrapper；
- evidence traceability 与 PR packaging structure。

**Evidence boundary:** `historical Han-compatible event benchmark`,
`label-assisted/appliance-derived event construction`, `post-event shape
features`, `random split and H3 held-out`, `not Protocol R or Protocol X`.

**Migration status:** scores 为 `reference_only`；documentation structure 为
`candidate_for_packaging_reuse`。任何 experiment 前都必须单独 review feature
code。

---

## Items that must remain Pending or excluded

| Item | Status | Reason |
|---|---|---|
| Presenting any legacy best score as the current baseline | `excluded` | Different data, classes, splits, labels and causal boundaries |
| Copying REDD-derived CSVs, matched events, models or generated headers from old/private repositories | `excluded` | Data/provenance/version-control boundary |
| Treating repeated H3 exploration as a locked test | `excluded` | H3 informed historical development repeatedly |
| Claiming old `redd_inference.ino` was run on Pico from repository source alone | `Pending verification` | Source exists; fixed hardware execution record was not found |
| Claiming Han's integrated firmware is live causal NILM | `excluded` | Audited route is SD replay with post-event access and different processing |
| Reusing the Round 9L C++ skeleton as verified code | `Pending verification` | Round 9M did not compile it |
| Claiming original REDD calendar timestamps or raw-channel lineage from the preprocessed chunks | `Pending verification` | Current source audit does not establish them |
| Assigning an E-series ID to the training-dynamics archive retrospectively | `registered as E002 — TM Training Dynamics Probe` | The durable identity is now recorded in `WORK_INDEX.md`; its evidence remains legacy/exploratory and unpromoted |

## Controlled reuse procedure

当后续任务准备复用某一项历史内容时：

1. 从本文件定位 fixed commit 和具体 path。
2. 先做只读 named review，明确要复用的是 algorithm、interface、test、
   experiment design、table 还是只有结论。
3. 记录 source repository、branch、commit、path、file hash、licence、
   dependency 和历史 evidence boundary。
4. 根据目的启动明确命名的 T-series migration 或隔离 E-series；不要把
   “参考过旧文件”写成“复现了旧结果”。
5. 只迁移最小必要部分，并为当前 data contract、causality、split containment
   和 output semantics 补测试。
6. 在当前 protocol 下重新验证。重新验证前，所有 score 和 claim 继续标为
   `historical` 或 `exploratory`。
7. 将正式结果登记到 current-project evidence index；本文件继续只做导航。

## Review conclusion

旧仓库的价值主要有三类：

- 已经暴露过的机制问题，例如 pairing error、label ambiguity、temporal
  alignment、event label 与 state reconstruction 不一致；
- 值得复用的工程合同，例如 ordered feature/bit schema、batch/runtime parity、
  model serialisation 和 host-first deployment staging；
- 可以避免重复的负结果，例如盲目增加 TM capacity、未经确认的
  hyperparameter gain、hard event gate、full-episode backfill 和静态 FSM。

最有价值的历史正向假设是 global pairing、bounded pre/post context 和
per-epoch unique shuffle；但三者都处在与当前 Protocol R 不同的证据边界内。
它们只能成为新 E-series/T-series 的 hypothesis source，不能直接成为正式方法。

## Recommendations

以下建议不是授权：

1. T004/T005 确定正式 data/output contract 后，优先审查 Han 的
   serialisation/compiler 和最小 C evaluator，而不是迁移完整 pipeline。
2. 正式 baseline 建立后，可分别用独立 E-series 重新测试 bounded-delay
   feature 与 unique-shuffle control，避免一次跨两层改动。
3. 如果 event pairing 成为研究重点，应把 ISTM global pairing 重新表达为
   aggregate-main-only、segment-contained、可声明 latency 的算法，再做正式
   comparison。
4. Round 9L skeleton 只有在 host compile、fixture parity 和 dependency review
   全部通过后，才值得进入 Pico-facing T-series。
