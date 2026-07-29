# 实验执行安全协议 / Experiment Execution Policy

## Agent Brief

- Status: mandatory repository-wide execution policy
- Authority: Tianhang direct governance instruction, 2026-07-29
- Applies to: training, benchmark, large data scan and parameter test
- Separation: execution state is not a scientific conclusion
- Real-data gate: forbidden until a complete frozen `RunSpec` is accepted
- Supervisor: `tools/governance/bounded_supervisor.py`

## 1. 核心原则

Codex 的目标不是“尽量把实验跑完”，而是：

> 在预先批准的资源预算内获得可恢复、可判断的证据；安全停止本身也是一次成功执行。

实现 runner 与运行真实实验是两项独立授权。Codex 可以在
`Implementation-only` 边界内编写、重构和测试 runner；这不会自动授权读取真实
数据、训练模型或产生 benchmark evidence。若 `RunSpec` 缺失或无效，只能准备
代码。

本协议不决定 sample、features、Booleanisation、target、model、split、metrics
或 tuning rule。它只实现已经批准方法外部的 execution safety。

## 2. 适用范围与阶段门

以下工作必须使用本协议：

- model training 或 fitting；
- benchmark、latency、memory 或 computation-cost probe；
- 大规模数据扫描、静态审计或批处理；
- 参数测试、ablation、seed/fold sweep；
- 可能长时间占用 CPU、RAM、GPU 或外部设备的任务。

新方法不得直接全量执行。正常顺序是：

1. `synthetic smoke`：验证接口、shape、finite values 和基本失败路径；
2. `small real probe`：在已授权的小规模真实数据上验证 execution path；
3. `staircase`：逐级放量，每步完成后重新估算；
4. `formal execution`：仅在前级通过并获得相应授权后启动。

跳过某一级必须由 Tianhang 在该轮 `RunSpec` 中明确批准，并说明原因。

## 3. RunSpec

每轮执行使用独立、冻结、machine-readable 的 `RunSpec`。模板位于
[`docs/templates/EXPERIMENT_RUN_SPEC.yaml`](../templates/EXPERIMENT_RUN_SPEC.yaml)。
为避免引入新的 parser dependency，仓库模板采用 JSON-compatible YAML：
它是合法 YAML 1.2，同时由 Python 标准库按 strict JSON 解析。

至少必须包含：

| Field | Meaning |
|---|---|
| `experiment_id` | 已授权任务或实验的直接身份 |
| `research_question` | 本轮只回答的问题 |
| `execution_type` | `smoke`, `cost_probe`, `capability`, `full` |
| `execution_authority` | Tianhang 对这一次真实 execution 的明确授权记录 |
| `implementation_commit` | 40-hex、clean worktree 的 exact commit |
| `data_allowlist` | 可访问的数据 population/role/path identity |
| `data_denylist` | 明确禁止的数据 population/role/path identity |
| `candidates` | 本轮允许执行的 candidate |
| `row_schedule` | 按顺序执行的 row staircase |
| `epochs` | 每个 fresh step 的固定 epochs |
| `seed` | 固定 seed |
| `max_workers` | 最大并发；默认并且当前 supervisor 只支持 `1` |
| `per_step_timeout_s` | 一个独立 step 的 hard wall timeout |
| `total_run_timeout_s` | 整个 run 的 hard wall timeout |
| `minimum_available_ram` | host 可用物理 RAM 下限，单位 bytes |
| `checkpoint_interval_s` | heartbeat 最大间隔 |
| `allowed_outputs` | child 可以生成的输出类型 |
| `forbidden_actions` | 禁止行为，必须包含自动重试与未授权改配置 |
| `stop_conditions` | 必须包含 step timeout、total timeout 和 RAM gate |
| `next_step_safety_factor` | 下一步预计时间的安全系数，不得小于 `2.0` |
| `step_command` | 无 shell 的 argument array；使用 frozen placeholders |

`RunSpec` 的 expected SHA-256、exact implementation commit 和
clean-worktree binding 必须在 child 启动前验证。实际 RunSpec 可以先保存在
repository 外或 ignored run root；启动后 supervisor 会保存其 byte-identical
snapshot。改变任意 execution budget、candidate、row、epoch、seed 或 command
都产生新的 `RunSpec`；不得覆盖旧 spec 或旧 run evidence。

### 默认预算

| Run kind | Per step | Whole run |
|---|---:|---:|
| 未特别批准的 probe | 120 s | 600 s |
| R006 类正式 cost probe | 300 s | 1,200 s |

正式长实验可以超过默认预算，但在批准前必须给出 worst-case wall time、最大
steps、最大并发和 RAM gate。运行后才发现“可能需要很久”不构成有效预算。

## 4. Supervisor 强制行为

每个 `(candidate, rows)` 是独立 step，并在独立 task subprocess 中运行。
supervisor 必须：

1. 启动前输出整轮最多时间、最多 steps、当前 candidate/rows、supervisor、
   step 和 task PID、spec hash、implementation commit，以及下一步 gate；
2. 使用 Windows Job Object 或 POSIX process group 包含 task 及其 descendants；
3. 从父进程执行 per-step timeout、total timeout 和 available-RAM gate；
4. timeout、RAM gate、interrupt 或 infrastructure error 时清理完整 process tree；
5. 每个 step 开始即原子保存 start record；
6. 按 `checkpoint_interval_s` 原子保存 heartbeat、elapsed time、available RAM、
   active process count 和 resource peak；
7. 每个 step 终止后立即原子保存 terminal record，再考虑下一 step；
8. 每次只启动一个 step；当前实现对 `max_workers != 1` fail closed；
9. 不通过 shell 执行 command，不自动 retry；
10. 不读取或解释 prediction quality。

Supervisor evidence 使用一个 event 一个 JSON 文件，并以 temporary file 加
`os.replace` 原子发布。已完成 event 不重写。`run_state.json` 可以原子更新，
但不能替代 immutable terminal event。

## 5. 自适应放量

第一步受 hard budget 约束。后续 step 启动前，用最近已完成 step 的 measured
wall time 和 row ratio 估算下一步，再乘 `next_step_safety_factor >= 2.0`。

若安全估算超过 `per_step_timeout_s` 或剩余 `total_run_timeout_s`，不得启动
下一步。该停止必须落盘，不能偷偷缩小 rows、clauses、epochs、features 或换
candidate。需要继续时，由 Tianhang 批准新的 `RunSpec`。

该 estimate 是 execution gate，不是模型 scaling claim。跨 candidate 的估计
只能作为保守 gate；不能代替真实 cost measurement。

## 6. 状态语义

Execution status：

| Status | Meaning |
|---|---|
| `COMPLETED` | RunSpec 中所有已声明 steps 完整执行 |
| `TIMED_OUT` | hard timeout 或安全放量 gate 停止；保留有效成本边界证据 |
| `MEMORY_STOPPED` | 启动前或运行中 available-RAM gate 触发 |
| `INTERRUPTED` | 人工中断，已有 checkpoint 和终态证据保留 |
| `INFRASTRUCTURE_FAILED` | child crash、supervisor、monitor 或 checkpoint 机制失败 |
| `PROTOCOL_INVALID` | RunSpec、commit、worktree、command 或协议 binding 无效 |

`TIMED_OUT`、`MEMORY_STOPPED` 和 `INTERRUPTED` 不是
`INFRASTRUCTURE_FAILED`，也不是模型失败。若 checkpoint 机制本身不能保留已
完成 step，则状态是 `INFRASTRUCTURE_FAILED`。

Scientific conclusion 单独记录：

- `SUPPORTED`
- `NOT_SUPPORTED`
- `INCONCLUSIVE`

Supervisor 不得自动生成 scientific conclusion。尤其不能把 timeout、OOM、
crash 或 manual stop 转成 `NOT_SUPPORTED`。

## 7. Retry 与变更

停止后禁止自动重试。不得自行：

- 缩小 row count、epoch、clauses、bits 或 window；
- 换 model、candidate、target、Booleanisation 或 data population；
- 调高 timeout、降低 RAM gate 或增加并发；
- 从失败 step 直接跳到另一配置；
- 覆盖旧 checkpoint 或把 partial run 标为 `COMPLETED`。

Implementation-only bug fix 可以准备和测试，但新的真实 execution 仍需新的
冻结 `RunSpec` 与 Tianhang 授权。

## 8. Supervisor 接入门

通用 supervisor 必须先用不接触 REDD/TMU 的 fake tasks 验证：

- 快速正常完成；
- 永久挂起并被 hard timeout；
- child 非零退出；
- child 派生 descendant 后完整 process-tree cleanup；
- 人工 interrupt 后保留 evidence；
- 缺字段或 commit/worktree 不匹配时在 child 启动前 fail closed。

上述测试全部通过前，禁止把 supervisor 接入真实 TMU。测试通过只批准
supervisor 的 implementation readiness，不批准任何真实实验。
