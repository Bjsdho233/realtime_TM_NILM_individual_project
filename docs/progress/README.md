# 历史进度快照
# Historical Progress Snapshots

本目录保存任务执行当时的 dated checkpoints。文件中的 `In progress`、
`authorised`、`no remote`、branch 或 phase 描述只代表该日期的历史事实，不能
作为当前状态或权限。

零上下文接管时：

1. 当前 phase、active authority 和 blocker 只看
   [CURRENT_STATE.md](../CURRENT_STATE.md)；
2. 长期 work identity 和完成状态看 [WORK_INDEX.md](../WORK_INDEX.md)；
3. 本目录只用于追溯当时做了什么、运行了什么以及某个结论怎样形成；
4. 若历史快照与 current state 表面冲突，先按 provenance 核对，不要用较新的
   文件日期自动覆盖 durable evidence。

Historical progress files are immutable evidence snapshots, not live authority.
