# 从这里开始 / Start Here

这是一份零上下文接管入口。无论是新开的 Codex、普通 GPT 对话，还是隔了一段时间重新回到项目的 Tianhang，都应先通过本页确认项目目标、证据边界和下一步权限。

## Agent Brief

- Project: Real-Time TM-NILM Individual Project
- Canonical repository: `Bjsdho233/realtime_TM_NILM_individual_project`
- Authoritative published state: GitHub default branch
- Live local authority: `docs/CURRENT_STATE.md`
- Stable agent rules: `AGENTS.md`
- Repository check: `python scripts/check_repo.py`
- Formal evaluation: unresolved until T004
- Sealed-test rule: no development access

## 1. 这个项目在做什么

这是 Tianhang 的 MSc individual project，研究对象是基于 Tsetlin Machine（TM）的非侵入式负荷监测（NILM）。当前正式基线方向是：

`REDD → event detection → event pairing → feature extraction → Booleanisation → one binary TM per appliance → train/validation/test evaluation`

研究不预设创新一定来自某一层。event pairing、temporal alignment、feature design、Booleanisation、TM structure、sampling、embedded cost 和 causal replay 都可以通过受控实验研究。TM 仍是主要 learned classifier。

项目同时有三类目标：

- 研究：在无数据泄漏的协议下建立 baseline，并用可复现实验解释哪些方法有效、无效或受什么限制；
- 工程：完成 Python → host-native → Raspberry Pi Pico 的 model export 与 inference parity；
- 写作与答辩：让每一步结果都能直接转化为论文表格、图、限制分析和演示材料。

## 2. 目前已经确认了什么

- T001 — Governance Review and Repository Bootstrap：完成。
- T002 — REDD Inventory and Protocol R Preflight：完成；数据、class support 和候选 manifest 已归档。
- T003 — Han Two-Class PC Reproduction：完成其限定的 Protocol H PC reproduction 范围。
- E001 — Booleanisation Encoding A/B Probe：已归档，结论为 `inconclusive`，没有晋升为正式方法。

这些结果不能互相替代：

- Protocol H 只证明 compatibility；
- E-series 只提供 exploratory evidence；
- 历史仓库结果只作为 historical/mechanism evidence；
- 目前还没有正式 Protocol R baseline、host-native parity、Pico parity 或 end-to-end real-time 证据。

最新、最完整的状态只看 [CURRENT_STATE.md](docs/CURRENT_STATE.md)，不要从本页或 README 推断实时授权。

## 3. 当前最重要的未决问题

D002 将 Protocol R 定义为 primary mixed-house evaluation，将 Protocol X 定义为 held-out-house generalisation；但现有候选 manifest 把 H2/H4 整栋房屋留出。这两种定义目前存在实质冲突。

同时，当前数据只能可靠支持 independent segment 内的 row position，不能声称已经恢复 original raw timestamps。

因此 T004 必须在第一次正式评分前明确：

- Protocol R 采用 mixed-house within-population split，还是改为 held-out-house evaluation；
- H2/H4 最终属于 Protocol R 还是 Protocol X；
- missing-label eligibility、cross-house aggregation、seed/repeat policy 和 uncertainty；
- one-binary-TM-per-appliance 的 simultaneous positives、all-negative、accuracy 和 confusion-matrix 语义；
- per-model 与 ensemble model size/latency；
- exact locked-test manifest 和 hash。

在该决定完成前，可以继续做不依赖这些选择的只读审查、工程工具和隔离 E-series，但不能把候选 test 评分包装成正式 Protocol R 结果。

## 4. 新对话的五分钟接管流程

1. 确认你打开的是仓库根目录，并检查当前 branch、worktree 和 remote。
2. 完整阅读 [AGENTS.md](AGENTS.md)。
3. 阅读 [CURRENT_STATE.md](docs/CURRENT_STATE.md) 和 [WORK_INDEX.md](docs/WORK_INDEX.md)。
4. 根据任务再阅读 [PROJECT_PLAN.md](PROJECT_PLAN.md)、相关 decision、task 或 experiment record。
5. 从仓库根目录运行：

   ```bash
   python scripts/check_repo.py
   ```

6. 在修改前先汇报：

   - project goal；
   - verified evidence；
   - active authority；
   - unresolved decisions；
   - Git state；
   - intended work track 和 mutable paths；
   - supporting file paths。

如果默认分支、实际 worktree 和 `CURRENT_STATE.md` 互相矛盾，先报告并修复状态，不要凭较新的日期或聊天摘要猜哪一份是真相。运行出 `0 tests` 也不能算通过。

## 5. 想找某类信息时去哪里

| 需求 | 首选入口 |
|---|---|
| 当前做到哪里、现在授权了什么 | [CURRENT_STATE.md](docs/CURRENT_STATE.md) |
| 长期 agent 规则和权限边界 | [AGENTS.md](AGENTS.md) |
| 正式路线、Research Questions 和 T001–T013 | [PROJECT_PLAN.md](PROJECT_PLAN.md) |
| T/E/R 编号和直接名称 | [WORK_INDEX.md](docs/WORK_INDEX.md) |
| 哪个 claim 对应哪份结果 | [EVIDENCE_INDEX.md](docs/EVIDENCE_INDEX.md) |
| 实验应如何设计、归档和解释 | [RESEARCH_EVIDENCE_STANDARD.md](docs/RESEARCH_EVIDENCE_STANDARD.md) |
| 旧 `In progress`、phase 和 branch 记录是什么意思 | [Historical Progress Snapshots](docs/progress/README.md) |
| 旧仓库、旧 branch 和可复用代码在哪里 | [R001 — Legacy Evidence and Reuse Map](docs/reviews/R001-legacy-evidence-and-reuse-map.md) |
| 整条 NILM workflow 各层做过什么 | [NILM Workflow Layer Map](docs/research_notes/2026-07-23-nilm-workflow-layer-map.md) |
| Protocol R/X 当前冲突 | [R002 — Evaluation Protocol Consistency Review](docs/reviews/R002-evaluation-protocol-consistency-review.md) |
| Han workflow 的已核验边界 | [Han Pipeline Source Audit](docs/reproduction/HAN_PIPELINE_SOURCE_AUDIT.md) |
| T003 实际复现结果 | [Archived Local Reproduction Report](experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md) |

旧仓库不会整体复制进来。需要复用时，先从 R001 找到固定 commit 和具体文件，再通过命名明确的 T-series 迁移、复核和测试。

## 6. 工作轨道

| Track | 适合做什么 | 能否改变正式项目状态 |
|---|---|---|
| T-series | 正式协议、工程实现、baseline、evaluation、deployment | 可以，但必须有明确授权 |
| E-series | 隔离的 hypothesis test、diagnostic 或 feasibility probe | 不可以自动改变；晋升后需 T-series 重验 |
| R-series review | 只读审查代码、协议、文献或已有结果 | 不产生新的实验结论 |

多个 E-series 可以并行，但必须拥有不同的可变目录；失败、`not_supported` 或 `inconclusive` 可以正常归档，不阻塞其他路线。

新的 E-series 只有在 [CURRENT_STATE.md](docs/CURRENT_STATE.md) 的唯一
`Active E-series Registry` 出现 exact row 时才算 active。流程是：
coordinator 先以 `registered` 和两个 `Pending` anchor 登记，scaffold 冻结
design，建立无结果的 design-only commit，再由 coordinator 写入
`design_frozen`、exact design SHA-256 和 commit。checker 验证通过前不能开始
任何 evidence-producing execution（即任何可用于结论或方法选择的 metric、
observation、parity 或 feasibility check）；纯 scaffold、schema 和 static syntax
check 可以在此之前运行。聊天、目录或 branch 名都不能替代这条登记。

## 7. 语言规范

仓库只维护一份权威内容，不建立容易漂移的中英文全文副本：

- AI control layer 使用英文：`AGENTS.md`、prompt、schema key、enum、configuration、identifier 和 command；
- human research layer 使用中文主叙述：README、CURRENT_STATE、PROJECT_PLAN、T/E/R report、review 和 decision explanation；
- 专业术语、代码符号、文件名、branch 名、JSON/CSV 字段保留英文；
- 研究报告顶部保留简短英文 `Agent Brief`，正文用中文解释；
- paper-ready 表格和图可直接使用英文标题与列名。

这样 AI 可以稳定解析结构，Tianhang 也能真正审查每一步做了什么、为什么这样做。

## 8. 可直接复制给新 Codex/GPT 的提示词

```text
Open the repository default branch and treat it as the canonical published
state. Read AGENTS.md, START_HERE.md, docs/CURRENT_STATE.md,
docs/WORK_INDEX.md, and PROJECT_PLAN.md. Run `python scripts/check_repo.py`
if you have a local checkout. Do not modify anything yet.

Report in Chinese:
1. the project goal and baseline workflow;
2. verified evidence and its claim boundaries;
3. active T/E/R authority;
4. unresolved protocol or data decisions;
5. current Git/worktree state;
6. the next safe actions;
7. the exact repository files supporting each conclusion.

Flag contradictions before continuing. Do not infer current authority from an
old task record, do not access candidate/locked test data, and use
docs/reviews/R001-legacy-evidence-and-reuse-map.md before proposing legacy code
reuse.
```

普通 GPT 必须能够读取仓库；如果仓库是 private，只发送链接并不能保证访问，需要连接 GitHub 或提供相关文件。
