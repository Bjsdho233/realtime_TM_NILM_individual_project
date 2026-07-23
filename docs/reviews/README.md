# R-series 只读审查
# R-series Reviews

本目录保存对已有 code、protocol、literature、data description、external repository 或 existing results 的持久化只读审查。

“read-only”指：

- 被审查对象和项目 implementation 不修改；
- 不训练、不评分；
- 不访问 candidate/locked test；
- 不产生新的 experimental result；
- 不改变 accepted formal decision。

审查可以写入：

- `docs/reviews/R###-direct-name.md`
- 必要的 `CURRENT_STATE.md`、`WORK_INDEX.md` 和 `EVIDENCE_INDEX.md` lifecycle/index rows

shared indexes 由 coordinating agent 串行更新。

当前审查：

- [R001 — Legacy Evidence and Reuse Map](R001-legacy-evidence-and-reuse-map.md)
- [R002 — Evaluation Protocol Consistency Review](R002-evaluation-protocol-consistency-review.md)

新报告使用 [R-series template](../templates/R_SERIES_REVIEW_TEMPLATE.md)。建议不能替代 Tianhang 的正式决定，也不能自动启动 T/E work。
