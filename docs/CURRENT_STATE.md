# 当前状态 / Current State

## Agent Brief

- Status: current governance snapshot
- Last updated: 2026-07-28
- Delivery posture: prototype-first student dissertation; runnable, readable and explainable over production-grade completeness
- Current formal state: T006 remains paused; R005 is accepted and closed; R006 halted after its first C8 run triggered the runtime/paging stop rule
- Active T-series: T006 — Direct rTM NILM Prototype (paused; no training resume is authorised)
- Active E-series: see the exact registry below
- Active R-series review: R006 — Compact rTM Computation Cost Probe (halted; no further execution authorised)
- Next planned formal task: Tianhang reviews the R006 halted-run record; do not resume R006 or T006 without a separate instruction
- T004 authority: completed on 2026-07-28; no continuing execution authority
- Candidate/locked test development access: prohibited
- Repository health command: `python scripts/check_repo.py`

## 1. 本文件的作用

本文件是当前 phase、active authority、open blocker 和最新 verified state 的唯一实时登记处。

- [AGENTS.md](../AGENTS.md) 保存长期稳定的 agent rules；
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) 保存正式方向和 T-series roadmap；
- [WORK_INDEX.md](WORK_INDEX.md) 保存 T/E/R 的长期编号和直接名称；
- [progress/README.md](progress/README.md) 说明 dated progress snapshot 的历史边界；
- task、progress 和 experiment report 保存历史事实，不是第二份授权登记。

如果本文件与实际 worktree、GitHub default branch 或已归档结果冲突，必须先检查并修正状态，不能根据日期或聊天摘要猜测。

### 1.1 Prototype-first dissertation posture

本项目是学生个人毕设原型，不按公司交付级系统建设。后续工作的排序是：

1. 关键问题做到可信；
2. 次要问题做到可解释；
3. 前沿难题明确边界后放过。

项目架构、代码、配置、实验和报告应尽量精简，优先保证 Tianhang 能跑通、读懂、
解释和演示。新增 abstraction、schema、validator、实验矩阵或 infrastructure 必须
直接服务于主线 claim、数据/评价安全边界或可运行实现；否则省略或 deferred。
T004/T005 保留为有效历史记录，但其规格重量不再作为后续任务的默认模板。

本项目允许按以下边界诚实使用 real-time terminology：

- 数据按时间顺序进入；
- 已输出决定不利用之后的整段信息回头修改；
- processing/algorithmic delay 固定、可接受并明确报告。

满足相应 evidence boundary 时，可称为 `real-time replay`、
`bounded-delay streaming inference` 或 `real-time-capable inference`。默认不要求
bit-level perfection、zero latency 或全流程全部上板；只需说明具体延迟以及
host/device 上实际覆盖的 pipeline boundary。

## 2. 当前授权

| Track | Active item | Authority |
|---|---|---|
| T-series | T006 — Direct rTM NILM Prototype (paused) | D007 保留 vanilla direct rTM，允许 compact/hybrid families 进入 static audit；exact horizons/features/bits 和 target clipping/scaling 未冻结；不得恢复 training |
| E-series | See exact registry below | Tianhang 可用一条明确指令启动新的隔离 E-series；执行前必须按下表登记、冻结并锚定 design |
| R-series review | R006 — Compact rTM Computation Cost Probe (halted) | 首次 C8 run 在 131,072-row fit 中触发 runtime/paging stop rule；C11 未启动，后续 execution 需另行指示 |

## Active E-series Registry

| ID | Direct name | Owner | Status | Mutable root | Design SHA-256 | Design commit |
|---|---|---|---|---|---|---|

这是 E-series 的唯一 live authority registry。空表表示没有 active E-series。
`Status` 只允许：

- `registered`：`Design SHA-256` 和 `Design commit` 都必须写 `Pending`；
- `design_frozen`：两列必须分别为 frozen design 的 64-hex SHA-256 和只含
  registered design/source/config/environment、且不含结果的 40-hex commit。

scaffold 只能接受本表中的 exact row；其他段落、目录、branch、聊天记录或
substring match 都不构成授权。只有 coordinating agent 可以增加、更新或删除
本表行；experiment worker 不得编辑。

2026-07-23 的 direct governance maintenance 已用于：

- 将临时 phase lock 从长期规则中移除；
- 建立 T/E/R 三轨；
- 增加 zero-context handoff；
- 增加 legacy evidence navigation；
- 建立 machine-readable schema、scaffold 和 repository check；
- 采用英文 control layer＋中文 research narrative；
- 记录 Protocol R/X 和 output semantics 的未决冲突；
- 修正 archive/current-state 的证据漂移。

该治理维护不授权新的 NILM run、dependency installation、REDD processing、candidate-test scoring、firmware、Pico 或 hardware work。

## 3. T-series 状态

| ID and direct name | Status | Evidence boundary |
|---|---|---|
| T001 — Governance Review and Repository Bootstrap | Complete — 2026-07-21 | clean repository 和初始 governance baseline |
| T002 — REDD Inventory and Protocol R Preflight | Complete — 2026-07-21 | pinned data inventory、support audit、class fallback 和 candidate manifest；没有 model scoring |
| T003 — Han Two-Class PC Reproduction | Complete for declared PC scope — 2026-07-22 | label-assisted Protocol H staged PC training/save/reload/export；不是 Protocol R、Pico 或 real-time |
| T004 — Protocol R Evaluation Contract and Test Freeze | Complete with documented class limitations — 2026-07-28 | 冻结 manifest/audit byte-identical；fridge/microwave full eligible，dish washer development-only，washer dryer support-ineligible；Protocol X support-only audit、machine-readable eligibility、fail-closed access guard 和 tests 完成；没有模型结果 |
| T005 — Protocol R Baseline Implementation | Complete — 2026-07-28 | 固定 aggregate-main detector/pairer、Han-compatible features/Booleanisation、one binary TM per appliance；仅 B1–B4 development folds；primary two-class macro F1 `0.345818303824`；dish washer 仅 development-only |
| T006 — Direct rTM NILM Prototype | Paused — 2026-07-28；D007 static-audit boundary accepted | implementation checkpoint `a8ee6f7eb8691e81f603c6960b4ae812c9b91793`；32-lag/StandardBinarizer 降级为 diagnostic reference；vanilla direct rTM 保留；没有 training authority |
| T007–T013 | Not started; not authorised | 见 [WORK_INDEX.md](WORK_INDEX.md) 和 [PROJECT_PLAN.md](../PROJECT_PLAN.md) |

T003 的“complete”只覆盖 declared PC Protocol H scope。它没有完成 host-native parity、Pico inference、aggregate-main-only evaluation、strict causality 或 real-time system。

## 4. E-series 历史与归档状态

| ID and direct name | Status | Outcome and boundary |
|---|---|---|
| E001 — Booleanisation Encoding A/B Probe | Archived — 2026-07-22 | `inconclusive`; legacy label-assisted development data；H2/H4 未读；没有 promotion |
| E002 — TM Training Dynamics Probe | Legacy archive merged via PR #2 — 2026-07-27 | exploratory H3 evidence；H3 被反复查看，不能作为 locked dissertation-test result；没有 formal promotion |

E001 的 Han binary mean macro F1 为 `0.784087`，`threshold_8` 为 `0.801266`，mean paired delta 为 `+0.017179`，wins 为 3/5。它没有达到预设 `promising` rule，因此 Han binary 仍只是 current compatibility baseline，不是 formal Protocol R baseline。

E002 对 training order、`T=10`、hard-negative feedback 和 class balancing 做了 historical exploratory probe。它在合并后仍与正式 Protocol R 分离；当前 archive 路径为 [`experiments/E002-tm-training-dynamics-probe/`](../experiments/E002-tm-training-dynamics-probe/README.md)，路径迁移记录见 [E002 archive path migration](progress/2026-07-27-e002-archive-path-migration.md)，历史来源见 [R001 — Legacy Evidence and Reuse Map](reviews/R001-legacy-evidence-and-reuse-map.md)。

## 5. R-series 状态

| ID and direct name | Status | Main output |
|---|---|---|
| R001 — Legacy Evidence and Reuse Map | Complete — 2026-07-23 | 按研究问题定位旧 repo、fixed commit、branch、file 和 reuse boundary |
| R002 — Evaluation Protocol Consistency Review | Complete — 2026-07-23 | 发现 mixed-house/held-out-house 与 raw-time/row-position 两组冲突 |
| R003 — Regression Tsetlin Machine Mechanism Review | Complete — 2026-07-24 | 综述 vanilla/weighted rTM 机制、固定公开源码差异、NILM 假设与后续验证边界；没有训练或 REDD 访问 |
| R004 — rTM NILM Input and Booleanisation Review | Complete — 2026-07-28 | 比较 direct rTM 的 input/Booleanisation 候选；建议优先考虑 compact causal multi-scale representation 加 hybrid cumulative thresholds，但未批准或运行任何方法 |
| R005 — Compact rTM Input Static Audit | Complete — 2026-07-28 | 64/256-sample onset coverage 为 16.12%/59.06%；C11 在 static cost 与 pattern diversity 间最平衡，但 range bits 有明显 house drift；没有批准方法或训练 |
| R006 — Compact rTM Computation Cost Probe | Halted — 2026-07-28 | 首次 C8 staircase 在 131,072-row fit 中超过 10 分钟并出现 working-set trimming/pagefile pressure；进程已停止、无 partial result、C11 未启动 |

R-series 只审查已有材料，不产生新的 model result。

### 5.1 Historical archive maintenance — 2026-07-27

- [TMU regression synthetic smoke archive](research_notes/2026-07-24-tmu-regression-smoke-test/README.md) 保存了 Windows CPU bootstrap 的脚本、uv 锁和环境清单。因原始 stdout/result 未保存且本轮未重跑，证据分类为 `inconclusive`，不能升级为正式接口或模型结论。
- [T003 first local attempt](research_notes/2026-07-21-t003-failed-pre-training-run.md) 在 Booleanisation 和训练前因 diagnostic harness 的 missing-file handling bug 中断，分类为 `invalid` / debugging，不是研究结论。
- 后续完整 T003 两次复现、E001、E002 和 R003 已在 default branch 有 durable record；本次没有重复归档其受限输入、预测、模型或大型本地输出。

## 6. 已核验的项目证据

### T002 — REDD Inventory and Protocol R Preflight

- Han snapshot: `8c5e90df34236ba0afcc4ec46ac083d829de4d51`
- REDD submodule: `a621bbd6399e49c6798550618fe43b113149455b`
- 35 个 preprocessed CSV segments，覆盖 6 houses 和 1,508,578 rows
- CSV content-tree SHA-256: `5e1ee53cdce2a5ad2d5007a08527bd1fc9486130d56dc008cf8c8ba8e336e73d`
- approved candidate classes: fridge、microwave、dish washer、washer dryer
- approved candidate manifest: [`protocol_r_approved_split.json`](../artifacts/manifests/protocol_r_approved_split.json)
- canonical manifest SHA-256: `b4509778dc15ccdf7a6ab48357cfcef90a28b58a5b12bbe57dfef0a590e24eb4`

T002 查看过 H2/H4 support labels，用于 class feasibility；没有生成或查看 model predictions/metrics。

### T003 — Han Two-Class PC Reproduction

权威 current-project local evidence 是：

- [archived local report](../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md)
- [local reproduction manifest](../experiments/T003-local-reproduction/local_reproduction_manifest.json)

固定范围：

- classes: fridge、microwave
- train: H1/H2/H4/H5/H6，共 679 matched events
- test: H3，共 410 matched events
- ordered numeric slots: 23，其中 unique feature names 为 22
- Boolean inputs: 184
- TM: 200 clauses、50 states、`T=20`、`s=6.0`、10 epochs

10-epoch local result：

- accuracy: `0.965853658537`
- macro precision: `0.885833333333`
- macro recall: `0.949340062112`
- macro F1: `0.914297658863`
- C model data: `9,058` bytes
- live model vs training reload: 1 prediction mismatch
- live model vs inference reload: 1 prediction mismatch
- training reload vs inference reload: 0 prediction mismatches
- two complete local runs produced identical compared evidence

[早期 pre-reproduction record](reproduction/HAN_MINIMUM_REPRODUCTION_RESULT.md) 报告了 413 events、accuracy `97.58%`、约 `0.94` macro F1、`9,004` bytes 和 0 个 10-epoch reload mismatch。它与 later local archive 的 source revision 相同但结果不同，原因未解决。该文件保留为 contextual pre-reproduction evidence，不能替代或与 local archive 数字混用。

T003 是 label-assisted、使用 future post-event context 的 Protocol H compatibility route。它不证明 aggregate-main-only、strictly causal、Protocol R、host-native、Pico、firmware、hardware 或 real-time performance。

### E001 — Booleanisation Encoding A/B Probe

- archive: [`experiments/E001-booleanization-ab-probe/`](../experiments/E001-booleanization-ab-probe/)
- development houses only: H1/H3/H5/H6
- H2/H4 not read
- 5 paired seeds
- same 184-bit budget
- outcome: `inconclusive`
- formal baseline/protocol changed: no

## 7. Evidence integrity correction

2026-07-23 复核发现，T003/E001 archive 在归档 normalisation 后没有重算原 `SHA256SUMS.txt`，导致 legacy checksum list 与 admitted current bytes 不一致。

处理原则：

- 不改写 archived report、code、metrics 或原 `SOURCE_FILE_SHA256SUMS.txt`；
- 保留失效的原 `SHA256SUMS.txt` 作为归档过程记录；
- 新增 current-byte correction manifest 和 human-readable erratum；
- repository validator 必须实际核验 correction manifest，而不是只检查文件名。

修复已完成，详情见 [Archive Checksum Correction](progress/2026-07-23-archive-checksum-correction.md)。该勘误不改变 T003/E001 的 metrics 或 evidence boundary，只纠正 archive integrity metadata。

## 8. 正式基线与 T004 contract

正式 baseline 方向为：

`REDD → event detection → event pairing → feature extraction → Booleanisation → one binary TM per appliance → unified evaluation`

T004 已冻结 evaluation contract，但尚未运行 formal baseline：

- Protocol R：H1/H3/H5/H6 mixed-house within-population；
- Protocol X：固定 H2+H4 held-out composite，与 development/model selection 分离；
- time contract：`sequence-first, row-position blocked`，不声称 raw timestamps；
- 每个 Protocol R segment 使用 B1–B5 floor split；B1–B4 四折 CV，B5 locked；
- `L_max=256`、`D_max=8`，所有 dependency 必须完整包含在 segment/block 内；
- multi-label one-binary-TM-per-appliance output、rTM target/metric、cTM latency、
  seed/fold aggregation、model-size 和 latency semantics 已进入 frozen manifest；
- ordinary development access 只允许 B1–B4，B5 和 H2/H4 fail-closed。

完整 conflict history 见 [R002](reviews/R002-evaluation-protocol-consistency-review.md)，
accepted resolution 和 class scope 见
[D005 — Protocol R v1 Class and Support Eligibility](decisions/D005-protocol-r-v1-class-and-support-eligibility.md)。

### 8.1 T004 frozen support and eligibility — 2026-07-28

Tianhang 已正式授权 T004。工作区按固定规则先生成
[`protocol_r_evaluation_v1.json`](../artifacts/manifests/protocol_r_evaluation_v1.json)，
其 byte SHA-256 为
`501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5`；
之后才运行
[`protocol_r_support_audit_v1.json`](../artifacts/manifests/protocol_r_support_audit_v1.json)。

冻结后的 B5 support audit 发现：

- `dish washer`：0 个 dependency-contained complete episodes、15 秒 ON target
  support，低于既有 minimum 10 episodes / 600 seconds；
- `washer dryer`：B5 通过，但 F1 validation 只有 0 个
  dependency-contained complete episodes，低于 minimum 5；
- `fridge`、`microwave` 的 F1–F4 与 B5 support 均通过。

Tianhang 随后正式决定：

- `fridge`、`microwave`：full Protocol R v1 eligible；
- `dish washer`：B1–B4 development-only；不得生成 Protocol R B5 result；
- `washer dryer`：Protocol R v1 support-ineligible，从当前 E003/E004 scope
  deferred；B5 support 不能补偿 F1 failure。

独立
[`protocol_x_support_audit_v1.json`](../artifacts/manifests/protocol_x_support_audit_v1.json)
确认 `dish washer` 在固定 H2+H4 composite 有 58 个 dependency-contained
complete episodes 和 18,171 秒 ON support，因此 future Protocol X locked
confirmatory evaluation support-eligible。该未来 evaluation 仍需单独授权，且
只能作为 Protocol X cross-house evidence。

### 8.2 T005 fixed development baseline — 2026-07-28

[T005 — Protocol R Baseline Implementation](tasks/T005-protocol-r-baseline-implementation.md)
已在 pre-run commit
`4fb5129ee1afcdc50fee2033eedf7b2f2f03aa9f` 冻结后完成唯一一次
F1–F4 × seeds 0–4 × three-appliance canonical matrix，以及 clean
F1/seed-0 sentinel。canonical archive 为
[`experiments/T005-protocol-r-baseline-implementation/`](../experiments/T005-protocol-r-baseline-implementation/BASELINE_REPORT.md)。

- `fridge` seed-fold mean F1：`0.421679382593`，sample std `0.017083083900`；
- `microwave`：`0.269957225055`，sample std `0.020825136079`；
- `dish washer` development-only：`0.213391254881`，sample std
  `0.018117993143`；
- primary `full_eligible_macro_2class`：`0.345818303824`，sample std
  `0.006093000187`；
- supplemental `development_scope_macro_3class`：`0.301675954177`，sample std
  `0.008474558968`；
- F1/seed-0 sentinel 的 candidate、encoder、model、prediction 和 aggregate
  metric hashes 全部 exact match。

这些是 aggregate-main-only B1–B4 formal development evidence，不是 B5
locked-test、Protocol X、host-native、Pico 或 confirmatory result。没有基于结果
tuning；没有训练 `washer dryer`；B5/H2/H4 未进入 T005 loader。

## 9. Locked-test 与 Protocol X 边界

- B5 是唯一 frozen Protocol R locked test；只能由未来 T011 一次性正式 evaluation
  访问。
- H2/H4 是固定 Protocol X composite，对 ordinary development 继续 sealed；
  support-only audit 不构成 development access 或 model evaluation。
- T002 的三块 candidate manifest 保留为 historical preflight，不是 T004 final
  split。
- T003 曾在固定 Protocol H training split 中读取 H2/H4。该访问是 compatibility-only，不得把 T003 model、normalizer、threshold 或 learned state 迁入 clean Protocol R。
- final report 不得声称 H2/H4 从未被项目人员接触。
- unified development access guard 已有 exact-hash、B5/H2/H4 refusal 和
  boundary-containment tests；T004 completion 不自动授权 baseline execution。

## 10. GitHub 与仓库现实

- canonical repository: `https://github.com/Bjsdho233/realtime_TM_NILM_individual_project`
- canonical published state: GitHub default branch
- project identity 不由本地文件夹名决定
- PR #2 已将 E002 legacy exploratory archive 合入 default branch；该合并不构成 formal promotion
- 截至 2026-07-27，PR #6 已通过 merge commit `29e8ce17594ea49fede16b1d5c8c789ff8694c6b` 合入：归档 TMU smoke、T003 invalid run，并将 E002 迁移到当前路径；这些维护没有 promotion 任何实验结果，也没有授权 T004
- branch 不是长期证据索引；durable identity 必须进入 `WORK_INDEX.md` 和 `EVIDENCE_INDEX.md`

新对话必须实际运行 `git status`、检查 default branch，并执行：

```bash
python scripts/check_repo.py
```

本文件不保存容易立即过时的 ahead/behind 数字。若 Git、default branch 与本文冲突，先报告和修正，不能直接 push 或把旧 branch 当最新现实。

## 11. 下一步安全动作

可以在新授权下进行：

- R-series read-only review；
- 不访问 B5/H2/H4 的隔离 E-series；`fridge`、`microwave` 和 `dish washer`
  可在未来明确授权的 E003/E004 中使用 B1–B4，且 `dish washer` 只能产生
  development feasibility evidence；`washer dryer` deferred；
- repository tooling、documentation 和 evidence-index maintenance；
- 旧代码的 read-only provenance review。

不能自动进行：

- T005 的任何追加 run、方法变化、数据扩展或后续任务；
- E003/E004；
- 任何进一步 Protocol R training/scoring；
- B5 test access；
- H2/H4 development access；
- E-series → formal method promotion；
- dependency/network expansion；
- host-native、Pico、firmware 或 hardware work；
- final test、Protocol D 或论文正式 claim。

T005 closure 不改变这些 authorization boundary。下一项 T/E work 必须由 Tianhang
另行明确授权；不得把 development baseline 当成 locked-test evidence。
