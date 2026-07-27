# 研究证据与实验记录标准
# Research Evidence and Experiment Recording Standard

## Agent Brief

- Applies to: T-series, E-series, and persistent R-series research work
- Narrative language: Chinese
- Machine-readable language: English keys/enums
- Design schema: `schemas/e-series-design.schema.json`
- Result schema: `schemas/work-result.schema.json`
- Design hash: `design_manifest.sha256`
- Canonical result: `result.json`
- Repository check: `python scripts/check_repo.py`

## 1. 目的

本项目是围绕 research questions 展开的 engineering research。实验记录不能等项目做完后再补，否则很难恢复当时的数据范围、代码、设计理由和失败原因。

每一步有价值的工作都应能回答：

- 为什么做；
- 改了哪一层；
- 什么保持不变；
- 使用了哪些 data/code/configuration；
- 结果是否有效；
- 为什么好、为什么不好；
- 能支持什么 claim；
- 对下一步有什么影响。

目标不是记录所有尝试，而是留下可以复现、评估、写入 dissertation 或用于 viva 的证据。

### 1.1 Record-first workflow

一项 T/E/R work 或 governance work 获得授权后，在其 mutable/output boundary 内新增用于实现该 work 或保存上下文的 source、configuration、test、document 和 evidence file，不需要再次确认。记录工作本身不是额外研究范围，也不等于接受该方法。

每次 evidence-producing run、源码核对或有判断价值的 review 完成后，应在以下两个时间点中较早者到来前写入仓库：

- 开始下一个 materially different attempt；
- 结束、暂停或交接当前工作。

最小 checkpoint 应能恢复：

- work ID、direct name 和本次具体问题；
- data、code、configuration、environment 和 commit/provenance；
- 实际 command、run status 和 deviation；
- observation、metric 或 failure；
- validity 和 outcome；
- 当前 interpretation、limitation 和 next action。

记录深度按情况区分：

- `supported`、`not_supported`、`inconclusive`：按声明的 archive contract 保存；
- bug、run interruption、inactive configuration、contamination：保存 concise debugging/invalid-run note 和必要 command，不包装成 research result；
- near-duplicate hyperparameter runs：压缩为一个 tidy table、一个 search-family 说明和一个 decision；
- 尚未形成结果的 literature/source review：保存 source、版本、路径、已确认事实、待核对项和当前推论。

权限边界是：

- 可以在 authorised root 新增 task-scoped source、configuration、test、report、note、manifest、table、figure、progress record 和 append-only log；
- 可以更新该 work 必需的 live lifecycle/index rows；
- 不得借“记录”修改未授权的 shared code、protocol、accepted decision 或历史 conclusion；
- 当前指令若明确要求修改某个现有代码或文档，它本身就是该范围的确认，不需要逐文件重复询问；
- 历史证据有误时使用 erratum、supersession 或 linked correction，不静默覆盖。

除非 Tianhang 明确要求 local-only，新的记录应在安全 checkpoint commit，并 push 到 task branch / Draft PR。合入 default branch、formal promotion 和 publication 仍是独立决定。重要信息不能只留在 chat、terminal、后台 workspace 或未推送的本地 worktree。

## 2. 研究主线

正式 baseline 分层如下：

1. REDD data and split；
2. event detection；
3. event pairing；
4. feature extraction and temporal alignment；
5. Booleanisation；
6. one binary TM per appliance；
7. output/decoder semantics；
8. metrics；
9. model export；
10. host/Pico parity；
11. model size、latency 和 decision delay。

每个实验必须指出 primary workflow layer。跨层改变只有在无法拆分且已在 frozen design 中解释时才允许。

## 3. 什么值得记录

### 应进入研究证据

- 合理 hypothesis 得到 `supported`；
- 验证一个直觉不成立；
- 结果为 `inconclusive`，但暴露 support、variance 或 measurement limitation；
- 与最终方法形成清晰对照；
- 揭示 data leakage、alignment、overlap、state boundary 或 embedded constraint；
- 可复现的 negative result；
- 解释为什么某条路线不值得继续；
- performance 与 model size/latency/decision delay 的明确 trade-off。

### 不应包装成研究结论

- 代码 bug；
- parameter 没有真正生效；
- configuration/file 读错；
- run 中断；
- data contamination；
- sealed-test feedback；
- 只试一个 random seed 就下结论；
- 无 hypothesis 的 arbitrary parameter poking；
- 大量近似重复、没有结构的 grid search。

这些情况 outcome 应为 `invalid` 或 debugging note，修复后重新运行。错误本身只有在揭示了可推广的 system limitation 时才值得进入正文。

## 4. Evidence identity

每份有效证据必须能够定位：

- work ID and direct name；
- T/E track；
- experiment kind；
- protocol and claim scope；
- data manifest/hash 和 role；
- code commit、dirty state 和 source hashes；
- configuration/environment hashes；
- baseline evidence/path/hash；
- reused learned artifact lineage 和 fit roles；
- seeds/folds/repeat policy；
- frozen design hash；
- result schema；
- output files/checksums；
- outcome、interpretation 和 limitations。

聊天总结、branch 名、文件夹日期或“最新一次”不能单独作为 evidence identity。

## 5. E-series 生命周期

### 5.1 串行登记

coordinating agent 先在：

- `docs/CURRENT_STATE.md` 的唯一 `## Active E-series Registry` table
- `docs/WORK_INDEX.md`

登记 exact ID、direct name、owner、完整 mutable root、`registered` status，
并将两个 design anchor 写成 `Pending`。表头固定为：

| ID | Direct name | Owner | Status | Mutable root | Design SHA-256 | Design commit |
|---|---|---|---|---|---|---|
| E003 | Causal Pre/Post Feature Probe | Tianhang Tan | registered | experiments/E003-causal-prepost-feature-probe/ | Pending | Pending |

只有 coordinator 可以分配 ID 和更新 shared indexes。parallel workers 不自行占号。
scaffold 必须严格解析本表的唯一 exact row 和 `WORK_INDEX.md` 的 exact identity；
不能通过 prose、目录存在、branch 名或 substring match 推断授权。

Tianhang 一条明确的 E-series 指令自动包含完成上述登记、design-only anchor、
append-only execution/debug records、result archive、closure rows 和 GitHub
checkpoint 所需的 task-scoped commits。该权限只覆盖 exact shared lifecycle/index
rows、registered experiment root 和已声明的 evidence files；不得扫入其他 work，
也不包括 default-branch merge、formal promotion、publication、sealed-test access
或未授权的 shared implementation/protocol 修改。若 Tianhang 明确要求 local-only，
则保留本地 checkpoint 并在 handoff 中说明尚未 push。

### 5.2 Scaffold

从 repository root 使用：

```bash
python scripts/scaffold_e_series.py --help
```

工具必须先验证 `CURRENT_STATE.md` 与 `WORK_INDEX.md` 的 exact registration，再创建并冻结 pre-anchor immutable files：

```text
experiments/E###-direct-name/
├── design_manifest.json
├── design_manifest.sha256
└── environment.txt
```

`--freeze-existing` 可在 anchor 前加入已声明的 `scripts/` 和 `configs/`。
design commit 和 registry anchor 验证后，再初始化可追加的 `EXPERIMENT.md` 和
`commands.log`；完成后再写 root `result.json`。`tables/`、`figures/` 和
`docs/` 仅在需要时创建并接受 archive review；
`work/`、`cache/`、`models/`、`outputs/` 和 row-level generated data 是可选
local mutable paths，不归档。实际 layout 以 executable scaffold/schema 为准。

### 5.3 冻结设计

首次 evidence-producing execution 前，必须冻结：

- research question/hypothesis；
- experiment kind；
- baseline/candidate 或 diagnostic/feasibility contract；
- one main changed variable；
- invariants；
- data roles；
- primary metric/check；
- pass/fail/inconclusive rules；
- seeds/folds/repeats；
- code/config/environment provenance；
- safety assertions；
- expected outputs；
- 每个需要归档的 aggregate CSV 的 exact path、ordered columns、max rows、
  purpose 和 aggregation unit。

design 管理的 repository text inputs 必须在 freeze 前已经 Git-tracked，并使用
canonical LF bytes。工具必须按 raw bytes 检查并拒绝任何 `\r`；不能依赖
`read_text()` 的 universal-newline 行为，也不能假设 `.gitattributes` 会自动修改
当前 worktree bytes。fresh clone 必须能够从 committed bytes 重算完全相同的 hash。

生成 `design_manifest.sha256` 后，先建立一个 design-only commit。该 commit
只能包含这个 registered E-series 的 manifest/sidecar、source、config、
environment inputs；引用的 data/artifact manifests 必须在此之前已经 tracked
并 committed。anchor commit 不得包含
`EXPERIMENT.md`、`commands.log`、`result.json`、table、figure、metric、
prediction 或其他 evidence-producing output。之后 coordinating agent 将
registry row 更新为
`design_frozen`，写入 exact 64-hex design SHA-256 和 40-hex design commit。

repository checker 必须从该 commit 读取 design、重算 hash、检查 commit path
scope、确认它是当前历史的 ancestor，并逐个检查所有 committed immutable
design inputs。active `design_frozen` E 的所有 frozen inputs 必须与 current
bytes 一致；归档后，E-root 内的 frozen snapshot 仍不可变，但 E-root 外的 shared
input 以 design/base commit tree 为 provenance，后续正常演进不能让旧 archive
失败。registry
anchor 完成前不得进行任何 evidence-producing execution，即任何可用于结论或
方法选择的 metric、observation、parity 或 feasibility check。纯 scaffold、
schema validation 和 static syntax check 可以在 anchor 前运行。
`EXPERIMENT.md` 和 `commands.log` 只能在该验证通过后初始化，之后可以追加。

锚定后不得修改 `design_manifest.json`、sidecar 或 committed design inputs。
若设计需要改变，旧 E-series 必须在未继续执行的情况下以
`Superseded before execution` 关闭，分配新的 E-series ID，并在两个 report 和
durable index 中互相链接；不能事后改 acceptance rule，也不能重写 frozen
commit。它仍写 canonical `result.json`，使用
`lifecycle_status: superseded_before_execution`、`superseded_by: E###`、
`execution: not_run`、`outcome: not_applicable` 和 `decision: supersede`；这个
close status 不构成无效或负向实验 outcome。

### 5.4 执行

- 只写入 registered experiment root；
- shared baseline/input 只读；
- development data 只通过 schema-valid development-data manifest 声明，且
  role 只能是非 test role、sealed-test flag 必须为 false；任意 JSON 路径加一个
  自报 Boolean 不能构成安全门；
- learned preprocessing 只 fit training role；
- 不访问 candidate/locked test；
- 记录实际 commands 和 deviations；
- coding error 修复后重新形成有效 run；
- 不用中间结果反向修改 frozen hypothesis。

### 5.5 结果与关单

`result.json` 必须：

- 持久引用 exact design hash 和 40-hex design commit；
- 通过 `schemas/work-result.schema.json`；
- 区分 execution validity 与 research outcome；
- 记录 metrics/observations；
- 记录 limitations；
- 给出 disposition；
- 指向 aggregate tables/figures。

需要自定义 diagnostic/feasibility table 时，在 frozen design 的
`output_contract.aggregate_tables` 预声明，例如：

```json
{
  "path": "tables/bit_parity_summary.csv",
  "columns": ["stage", "comparison_count", "mismatch_count"],
  "max_rows": 20,
  "purpose": "Aggregate parity counts by pipeline stage",
  "aggregation_unit": "pipeline stage"
}
```

scaffold 可重复使用 `--aggregate-table '<strict JSON object>'`。validator 要求
exact columns、至少一行、row width 一致、finite values 和不超过 `max_rows`；
未声明 table、JSON table、prediction/sample/event-level 字段或额外隐藏 cells
都必须拒绝。`aggregate_tables` 可以为空，不能为了模板虚构 table。

完成后 coordinator 串行更新：

- `CURRENT_STATE.md`
- `WORK_INDEX.md`
- `EVIDENCE_INDEX.md`

coordinator 必须先把 design hash/commit 写入 `result.json`，并让 durable
`WORK_INDEX`/`EVIDENCE_INDEX` link 到该 canonical result，再从
`Active E-series Registry` 删除 live row。index 不重复 hash 值，避免双份
anchor 漂移。E-series 完成不自动 promotion。

包含 E-series design anchor 的 PR 必须使用 merge commit 保留原 commit
identity，不能 squash 或 rebase merge。CI/local checker 必须取得 full Git
history；shallow checkout 不能声称完成 anchor validation。

## 6. Experiment kinds

### comparison

用于 baseline A/B、ablation 或 controlled intervention。必须有：

- fixed baseline identity；
- candidate；
- primary metric；
- direction；
- paired delta/acceptance rule；
- controlled variables；
- repeated seeds/folds。

### diagnostic

用于定位 bug、failure mechanism、alignment、data quality 或 parity defect。可以没有 traditional performance baseline，但必须有：

- precise question；
- observation plan；
- checks；
- pass/fail/inconclusive rules；
- 可复核 output。

### feasibility

用于回答“能否编译、能否导出、是否能在限定资源内运行”等能力问题。必须有：

- capability；
- success condition；
- check；
- bounded environment；
- 不扩大 claim 的 limitation。

不得为了满足模板而给 diagnostic/feasibility 虚构 classification baseline。

## 7. Outcome rules

machine-readable outcome 统一为：

| Outcome | 含义 |
|---|---|
| `supported` | 有效结果达到 frozen pass/acceptance rule |
| `not_supported` | 有效结果没有支持 hypothesis，且 failure rule 清楚 |
| `inconclusive` | run 有效，但 variance、support、measurement 或 mixed effect 不足以作方向性结论 |
| `invalid` | leakage、bug、inactive config、contamination、broken provenance 或执行失败 |
| `not_applicable` | design 在任何 evidence-producing execution 前被 superseded；没有实验结论 |

不要用 `positive/negative/mixed` 作为机器枚举；这些可以出现在中文 interpretation 中。

`not_supported` 不等于失败的项目管理。它可以排除方向、解释最终选择并体现 research depth。

## 8. Minimum archive

有效 E-series 至少保留：

- `EXPERIMENT.md`
- `design_manifest.json`
- `design_manifest.sha256`
- `environment.txt`
- `commands.log`
- `result.json`
- experiment-local source/config 或其 patch/hash；
- 有结构化数值结果时保存 aggregate `tables/`；
- 纯 diagnostic/feasibility 可使用 `result.observations` 和 concise report；
- 有解释价值时保存 paper-ready `figures/`；
- checksum/integrity record。

### 可以进入 Git

- small source/config text；
- JSON manifest；
- aggregate CSV；
- small SVG/PNG figures；
- concise report；
- hashes。

进入 frozen design 的 small source、config、data/artifact manifest 和 baseline
evidence 必须是 Git-tracked canonical blobs。ignored/untracked local file 不能作为
可复现 provenance。大型、外部或 model artefact 不直接归档；design 只能引用一个
已跟踪的 artifact manifest，其中保存 content hash、stable locator、origin、
fit-data roles 和 availability limitation。repository-wide checker 验证 manifest，
不要求被忽略的大型实体永久留在每台机器。

portable learned-artifact manifest 的 structured lineage 至少包括：

- `origin.source_work`、`origin.repository`、40-hex/null `origin.git_commit` 和
  `origin.context`；
- `availability_limits.available_in_fresh_clone`、
  `availability_limits.requires_local_store` 和 `availability_limits.retention`；
- content hash、locator 和 training-only fit-data roles。

### 不进入 Git

- REDD；
- matched-event rows；
- row-level predictions；
- raw samples；
- virtual environment；
- trained model；
- cache/checkpoint；
- large logs；
- generated header/model binary，除非 formal deployment task 明确批准；
- credentials、absolute machine paths。

archive validator 对文件名、type、size、row count 和 suspicious prediction/sample tables 做检查。`.gitignore` 只是第一层保护，不是 evidence validator 的替代。

## 9. Classification metrics

正式 classification result 至少提供：

- per-appliance precision；
- per-appliance recall；
- per-appliance F1；
- support；
- macro precision/recall/F1；
- repeated-run summary；
- clearly named accuracy；
- clearly defined confusion representation。

在 T004 冻结 binary-output contract 前：

- 不假定一个 event 只能有一个 positive appliance；
- 不强制 argmax；
- 不把 all-negative 自动解释成 background；
- 不把 generic accuracy 当作 event accuracy；
- 不把一个 multiclass confusion matrix 当成 binary ensemble 的自然表示。

E-series 可以使用 experiment-local provisional semantics，但必须写入 frozen design，且不能升级为 formal Protocol R definition。

## 10. Engineering cost

根据实验范围报告：

- numeric features；
- Boolean inputs；
- per-TM model bytes；
- ensemble model bytes；
- flash/RAM；
- per-TM inference latency；
- ensemble inference latency；
- feature-to-decision latency；
- event waiting/context delay；
- repetitions、median、p95、max。

如果 cost 由设计保证不变，也必须写明 basis。不要用 Python object size 代替 embedded model bytes。

## 11. Hyperparameter 和 ablation 压缩

大量近似 setting 不逐个写成长报告。应压缩为：

- frozen search family；
- variables/ranges；
- selection data；
- seed policy；
- tidy result table；
- best/median/worst 或 Pareto summary；
- overfitting risk；
- final confirmation。

只有形成不同机制结论的设置才值得单独成段。参数搜索不能先于可信 baseline 和主要 bottleneck diagnosis。

## 12. Dissertation-ready material

每个值得进入论文的 result 应在 report 中附：

```md
## 论文素材 / Paper-ready takeaway

**Claim (EN):** ...

**中文解释：** ...

**Evidence:** ...

**Protocol / claim scope:** ...

**Limitation:** ...

**Figure / table:** ...
```

还应说明：

- 对哪个 RQ 有贡献；
- 与 baseline/final method 的关系；
- 是 adoption、rejection、diagnosis 还是 future work；
- 是否已 formal promotion。

中央映射写入 [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md)。

## 13. Validation and archival checks

archive 前至少运行：

```bash
python scripts/check_repo.py
```

检查必须覆盖：

- non-zero tests；
- JSON schema；
- design hash；
- result→design hash；
- current-byte archive checksums；
- Markdown relative links；
- allowed paths/types/sizes；
- suspicious row-level output；
- secrets/absolute paths；
- `git diff --check`；
- worktree/status report。

final report 必须明确：

- changed files；
- commands；
- checks passed；
- failures；
- material checks not run；
- Git state。

## 14. Promotion

promotion 路径固定为：

```text
E-series candidate
  → Tianhang review
  → named T-series
  → minimal migration/reimplementation
  → formal development revalidation
  → decision update
```

因此 E-series 的 machine-readable decision action 只能是
`propose_promotion`，不能是 `promote`。

即使一个 E-series 做得很完整，也不能直接：

- 改 Protocol R；
- 访问 locked test；
- 替换 formal baseline；
- 成为 final method；
- 产生 deployment claim。

formal revalidation 必须使用 T004/T005 定义的 data access、output semantics 和 repeated-run policy。
