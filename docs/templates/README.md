# 文档模板 / Document Templates

本目录只保存 human-readable T/E/R narrative templates：

- [E-series report](E_SERIES_EXPERIMENT_TEMPLATE.md)
- [T-series task](T_SERIES_TASK_TEMPLATE.md)
- [R-series review](R_SERIES_REVIEW_TEMPLATE.md)

machine-readable design/result 不在这里维护第二套 JSON template，避免与 executable contract 漂移。唯一权威来源是：

- `schemas/e-series-design.schema.json`
- `schemas/work-result.schema.json`
- `scripts/scaffold_e_series.py`

启动 E-series 前先由 coordinating agent 在 `CURRENT_STATE.md` 的唯一
`Active E-series Registry` 以 `registered` 状态登记
ID/name/owner/mutable root 和两个 `Pending` design anchors，并在
`WORK_INDEX.md` 登记 durable identity，再运行：

```bash
python scripts/scaffold_e_series.py --help
```

scaffold 后必须先建立无结果的 design-only commit，再由 coordinator 把 registry
row 更新为 `design_frozen` 和 exact design hash/commit；checker 验证通过前不运行
任何 evidence-producing execution。完成时先把 design hash/commit 写入 durable
result/index，再移除 active registry row。

不要手工复制旧版 hash sidecar、nested result path 或独立 JSON result-template 结构；旧 contract 已废弃，并会被 repository checker 拒绝。
