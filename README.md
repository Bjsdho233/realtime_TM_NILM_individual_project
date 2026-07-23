# Real-Time TM-NILM Individual Project

这是 Tianhang Tan 的 MSc individual project 主仓库，研究基于 Tsetlin Machine（TM）的 non-intrusive load monitoring（NILM），并建立从 REDD 数据、事件级建模到 Raspberry Pi Pico 推理验证的可追溯流程。

本仓库既是工程工作区，也是论文与答辩的证据库。代码能运行只是最低要求；正式结果还必须说明数据范围、protocol、configuration、seed、metrics、limitations 和 claim boundary。

第一次进入项目，请直接阅读 [START_HERE.md](START_HERE.md)。

## Agent Brief

- Canonical repository: `Bjsdho233/realtime_TM_NILM_individual_project`
- Stable rules: [AGENTS.md](AGENTS.md)
- Live state and authority: [CURRENT_STATE.md](docs/CURRENT_STATE.md)
- Formal roadmap: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Repository check: `python scripts/check_repo.py`
- Primary model family: Tsetlin Machine
- Formal Protocol R baseline: not yet established

## 当前状态

已完成并归档：

- [T001 — Governance Review and Repository Bootstrap](docs/tasks/T001-governance-review-and-repository-bootstrap.md)
- [T002 — REDD Inventory and Protocol R Preflight](docs/tasks/T002-redd-inventory-and-protocol-r-preflight.md)
- [T003 — Han Two-Class PC Reproduction](experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md)
- [E001 — Booleanisation Encoding A/B Probe](experiments/E001-booleanization-ab-probe/REPORT.md)

T003 的权威本地复现结果来自 later archived local run：410 个 H3 matched events，accuracy `0.965854`，macro F1 `0.914298`，C model data `9,058` bytes；10-epoch live model 与 reload 后仍有 1 个 prediction mismatch。早期 [Han Minimum Reproduction Result](docs/reproduction/HAN_MINIMUM_REPRODUCTION_RESULT.md) 中约 `0.94` macro F1、413 events 和 `9,004` bytes 属于 contextual pre-reproduction record，两组差异尚未解释，不能混用。

E001 比较了相同 184-bit budget 下的 Han binary 与 `threshold_8`。mean paired macro-F1 delta 为 `+0.017179`，只在 5 个 seeds 中赢 3 次，没有达到预设规则，因此 outcome 为 `inconclusive`，没有改变 formal baseline。

目前还没有：

- 正式 Protocol R baseline；
- aggregate-main-only locked-test result；
- host-native inference parity；
- Pico parity、resource 或 latency evidence；
- end-to-end causal real-time NILM evidence。

实时授权、开放冲突和下一步只看 [CURRENT_STATE.md](docs/CURRENT_STATE.md)，README 不复制频繁变化的 active task。

## 正式基线方向

```text
REDD
  → event detection
  → event pairing
  → feature extraction
  → Booleanisation
  → one binary TM per appliance
  → train / validation / test evaluation
```

正式报告指标包括 macro/per-class precision、recall、F1、support，以及 model size 和 latency。accuracy、confusion matrix、simultaneous positives、all-negative output、ensemble cost 和 decision delay 的准确语义仍需在 T004 冻结。

本项目不预设创新必须来自 event pairing。每一层都可以通过受控 E-series 进行 hypothesis test，但探索结果不能自动升级为论文正式结论。

## T/E/R 三轨工作方式

| Track | 用途 | 权限边界 |
|---|---|---|
| T-series | 正式 protocol、baseline、engineering、evaluation 和 deployment | 明确授权后可以改变共享项目状态 |
| E-series | 隔离的 comparison、diagnostic 或 feasibility experiment | 只产生 exploratory evidence；晋升后需 T-series 重验 |
| R-series review | 只读分析现有代码、协议、文献和结果 | 不训练、不评分、不产生新的实验结果 |

多个 E-series 可以并行，但不能共享可变输出目录。`not_supported`、`inconclusive` 或有效 negative result 都可以正常归档；代码错误、泄漏或无效配置不能包装成研究结论。

详细规则见 [AGENTS.md](AGENTS.md) 和 [Research Evidence Standard](docs/RESEARCH_EVIDENCE_STANDARD.md)。

## Protocol 状态

| Protocol | 用途 |
|---|---|
| Protocol H | Han-compatible engineering reproduction |
| Protocol R | primary dissertation research evaluation |
| Protocol X | held-out-house generalisation / stress test |
| Protocol D | method freeze 后的 deployment model |

当前存在一个必须在 T004 解决的冲突：D002 把 Protocol R 定义为 mixed-house evaluation、Protocol X 定义为 held-out-house generalisation；现有 candidate manifest 却完整留出了 H2/H4。与此同时，当前 preprocessed REDD 只能支持 independent segment 内的 row-position order，不能声称已恢复 raw timestamps。

因此 H2/H4 仍对 development sealed，但现有 candidate manifest 不能直接当作已经冻结的 final Protocol R test。详见 [R002 — Evaluation Protocol Consistency Review](docs/reviews/R002-evaluation-protocol-consistency-review.md)。

## 仓库导航

| 入口 | 内容 |
|---|---|
| [START_HERE.md](START_HERE.md) | 零上下文接管、阅读顺序和可复制 prompt |
| [CURRENT_STATE.md](docs/CURRENT_STATE.md) | 当前状态、授权、Git reality 和 unresolved decisions |
| [WORK_INDEX.md](docs/WORK_INDEX.md) | T/E/R 的编号、直接名称和证据位置 |
| [EVIDENCE_INDEX.md](docs/EVIDENCE_INDEX.md) | Research Question、claim 与证据映射 |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | 正式 T001–T013 路线和研究目标 |
| [RESEARCH_EVIDENCE_STANDARD.md](docs/RESEARCH_EVIDENCE_STANDARD.md) | 实验设计、归档、negative result 和论文材料规范 |
| [R001 — Legacy Evidence and Reuse Map](docs/reviews/R001-legacy-evidence-and-reuse-map.md) | 旧仓库、branch、commit、文件和复用边界 |
| [NILM Workflow Layer Map](docs/research_notes/2026-07-23-nilm-workflow-layer-map.md) | 从 data 到 Pico 的逐层研究脉络 |

旧仓库和 Han repository 不会整体复制进来。需要历史代码或实验设计时，先通过 R001 找到固定 commit 和文件，再建立命名明确的 migration task。

## 开始工作

在仓库根目录执行：

```bash
python scripts/check_repo.py
```

它是唯一的 repository health 入口，负责运行测试并检查 schema、链接、design hash、archive boundary、敏感信息、大文件和 Git diff。`0 tests` 不算通过。

同一命令由 [Repository Check workflow](.github/workflows/repository-check.yml) 在 pull request 和 `main` push 上自动执行。

REDD、matched-event CSV、row-level predictions、models、environment、cache 和大型 generated outputs 不进入 Git。正式 development code 必须通过批准的 manifest 和 data role 加载数据，不允许用宽泛 glob 自己发现全部 houses。

## 语言规范

- `AGENTS.md`、schema key、enum、configuration、identifier、command 和 code symbol 使用英文；
- README、CURRENT_STATE、PROJECT_PLAN、T/E/R report 和 research explanation 使用中文主叙述；
- 专业术语、文件名、branch 名和 JSON/CSV 字段保留英文；
- paper-ready figure/table 优先英文；
- 不维护两份独立的中英文全文版本。

目标不是让仓库“看起来正规”，而是让 AI 能稳定执行、Tianhang 能真正审查，并让论文写作不需要在最后重新寻找和复现实验。
