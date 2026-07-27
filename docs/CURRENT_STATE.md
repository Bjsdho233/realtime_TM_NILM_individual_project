# 当前状态 / Current State

## Agent Brief

- Status: current governance snapshot
- Last updated: 2026-07-27
- Current formal state: Protocol H PC scope archived; primary evaluation contract unresolved; no formal Protocol R baseline
- Active T-series: none
- Active E-series: see the exact registry below
- Active R-series review: none
- Next planned formal task: T004 — Protocol R Evaluation Contract and Test Freeze
- T004 authority: not authorised
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

## 2. 当前授权

| Track | Active item | Authority |
|---|---|---|
| T-series | None | 不得开始 T004、Protocol R implementation、host/Pico、final evaluation 或 deployment |
| E-series | See exact registry below | Tianhang 可用一条明确指令启动新的隔离 E-series；执行前必须按下表登记、冻结并锚定 design |
| R-series review | None | 可在明确请求下进行 read-only review；不训练、不评分 |

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
| T004 — Protocol R Evaluation Contract and Test Freeze | Planned; not authorised | 必须解决 Protocol R/X、row-position wording、binary output、metrics 和 exact locked-test manifest |
| T005–T013 | Not started; not authorised | 见 [WORK_INDEX.md](WORK_INDEX.md) 和 [PROJECT_PLAN.md](../PROJECT_PLAN.md) |

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

## 8. 正式基线与当前未决冲突

正式 baseline 方向为：

`REDD → event detection → event pairing → feature extraction → Booleanisation → one binary TM per appliance → unified evaluation`

但它还不是可评分的 formal baseline，因为以下决定未冻结：

- Protocol R 是 mixed-house within-population，还是 held-out-house primary evaluation；
- H2/H4 最终属于 Protocol R 还是 Protocol X；
- 当前数据的 row-position contract 如何取代不准确的 `raw-time` 表述；
- missing-label 和 overlap eligibility；
- cross-house / per-house aggregation；
- simultaneous positives、all-negative 和 conflict resolution；
- accuracy/confusion-matrix 的准确定义；
- seeds、folds、uncertainty 和 weak-class support；
- per-model / ensemble model bytes 与 latency；
- final locked-test manifest/hash。

完整审查见 [R002](reviews/R002-evaluation-protocol-consistency-review.md)。这些事项必须由 [T004 task specification](tasks/T004-protocol-r-evaluation-contract-and-test-freeze.md) 在明确授权后解决。

## 9. Candidate-test 边界

- H2/H4 对 ordinary development 继续 sealed。
- 现有 candidate manifest 不是已经冻结的 final Protocol R test。
- T003 曾在固定 Protocol H training split 中读取 H2/H4。该访问是 compatibility-only，不得把 T003 model、normalizer、threshold 或 learned state 迁入 clean Protocol R。
- final report 不得声称 H2/H4 从未被项目人员接触。
- 在统一 data access gate 和拒绝测试完成前，不运行正式 Protocol R baseline。

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
- 不访问 H2/H4 的隔离 E-series；若研究 provisional output semantics，必须在
  frozen design 明示，它只能支撑 exploratory diagnostic/feasibility claim，
  不能被写成 final output contract 或 formal Protocol R result；
- repository tooling、documentation 和 evidence-index maintenance；
- 旧代码的 read-only provenance review。

不能自动进行：

- T004/T005；
- Protocol R training/scoring；
- H2/H4 development access；
- E-series → formal method promotion；
- dependency/network expansion；
- host-native、Pico、firmware 或 hardware work；
- final test、Protocol D 或论文正式 claim。

正式下一步建议是由 Tianhang 审查 R002，并明确授权 T004 解决 evaluation contract。T004 完成也不自动授权 T005。
