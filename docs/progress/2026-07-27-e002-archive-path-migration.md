# E002 — TM Training Dynamics Probe Archive Path Migration

## Agent Brief

- Status: complete
- Date: 2026-07-27
- Change type: direct governance maintenance
- Old path: `experiments/2026-07-22-tm-training-dynamics-probe/`
- New path: `experiments/E002-tm-training-dynamics-probe/`
- Research content changed: no
- Outcome changed: no

## 迁移原因

现行 repository governance 要求 `experiments/` 下的 named-work directory
使用 `T###-`、`E###-` 或 `R###-` 开头。E002 的历史归档最初使用日期开头
的目录名，导致 `python scripts/check_repo.py` 在 archive validation 开始时
停止，并使 PR #6 的 Windows 与 Ubuntu CI 同样失败。

本次迁移只把目录规范化为 E-series direct-name 形式：

```text
experiments/2026-07-22-tm-training-dynamics-probe/
    ->
experiments/E002-tm-training-dynamics-probe/
```

## 完整性处理

- 12 个 archive 文件全部按 Git rename 保留；
- 文件内容和 SHA-256 未改变；
- `experiment_manifest.json` 中的 historical `archive_id` 保持原值，没有
  重写执行时记录；
- `CHECKSUMS.sha256` 保持原字节；
- `schemas/legacy-archive-checksums.json` 新增当前 admitted Git blob hashes；
- `scripts/repo_governance.py` 将新目录登记为 explicit legacy archive；
- 5 个原始 result JSON 没有 final newline；validator 仅按各文件固定 SHA-256
  接受该 legacy byte exception，不改写 archive 内容，也不放宽其他文件；
- current links 更新到新路径；
- R001 中指向固定 commit `e7277cc4...` 的历史链接保持不变，因为旧路径
  在该固定 commit 中仍然正确。

这项迁移不改变 E002 的 `exploratory_only` 状态、指标、结论、限制或
Protocol R 边界，也不构成 formal promotion。
