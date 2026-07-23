# E### — 中文直接名称
# Direct English Name

> 优先使用 `python scripts/scaffold_e_series.py --help` 创建 E-series。本文件是 narrative report 结构，不替代 machine-readable schema。

## Agent Brief

- Work ID: E###
- Track: E-series
- Experiment kind: comparison / diagnostic / feasibility
- Status: planned / active / archived
- Lifecycle status: completed / superseded_before_execution
- Superseded by: null / E###
- Owner: Tianhang Tan
- Workflow layer: ...
- Protocol: development-only exploratory
- Claim scope: exploratory
- Sealed-test access: false
- Frozen design: `design_manifest.json`
- Design hash: `design_manifest.sha256`
- Design commit: 40-hex commit persisted in `result.json`
- Canonical result: `result.json`

## 研究问题

用一句话说明要减少哪个 uncertainty。

## Hypothesis

保留与 frozen design 完全一致的 hypothesis。

## 为什么值得做

说明它与 baseline、historical evidence、failure mode 或 RQ 的关系。

## 固定设计

- Experiment kind:
- Baseline / diagnostic question / capability:
- Single changed variable:
- Invariants:
- Data scope and manifest:
- Reused learned artifacts (tracked artifact manifest/hash/locator/fit roles):
- Artifact origin / availability limits:
- Seeds/folds/repeats:
- Primary metric/check:
- Aggregate table contracts (path/columns/max_rows/purpose/aggregation_unit):
- Supported rule:
- Not-supported rule:
- Inconclusive rule:
- Validity conditions:

## 执行与偏差

记录实际 commands、environment、Git-tracked canonical source/config/data
manifest hashes，以及与 frozen design 的任何偏差。大型或 local model artefact
只通过 tracked artifact manifest、content hash 和 locator 引用，不假设实体会在
fresh clone 中出现。偏差使结论无效时 outcome 为 `invalid`。

## 结果

引用 `result.json`、`tables/` 和 `figures/`。不要把 row-level predictions 放进 Git。

## 解释

说明 mechanism、class trade-off、variance 和 alternative explanations。不要只复述数值。

## 限制

- protocol/claim scope；
- data support；
- causality；
- generalisation；
- embedded boundary；
- unresolved defects。

## 决定

archive、retain-negative、retain-diagnostic、repeat、defer、supersede 或
`propose_promotion`。E-series 不能使用 `promote` 自行晋升。

## 论文素材 / Paper-ready takeaway

**Claim (EN):** ...

**中文解释：** ...

**Evidence:** ...

**Protocol / claim scope:** ...

**Limitation:** ...

**Figure / table:** ...
