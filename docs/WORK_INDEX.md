# 工作索引 / Work Index

## Agent Brief

- Purpose: durable T/E/R identity and evidence-location registry
- Live authority: `docs/CURRENT_STATE.md`
- Naming rule: ID plus direct name
- Bare numeric references: prohibited as the only identity

本索引回答“这个编号具体做了什么、证据在哪里”。它不保存 active authority，也不把 roadmap row 当成已授权工作。

## T-series

| ID and direct name | 目标 | Status | Durable record |
|---|---|---|---|
| T001 — Governance Review and Repository Bootstrap | 建立 clean repository 和初始治理 | Complete | [Task](tasks/T001-governance-review-and-repository-bootstrap.md) |
| T002 — REDD Inventory and Protocol R Preflight | 固定数据证据、support 和 candidate manifest | Complete | [Task](tasks/T002-redd-inventory-and-protocol-r-preflight.md) |
| T003 — Han Two-Class PC Reproduction | 审查并执行 minimum Protocol H staged PC route | Complete for PC scope | [Archived local result](../experiments/T003-local-reproduction/LOCAL_REPRODUCTION_REPORT.md) |
| T004 — Protocol R Evaluation Contract and Test Freeze | 冻结 Protocol R/X、output、metrics、class eligibility 和 locked-test contract | Complete with documented class limitations — 2026-07-28 | [Task and completion record](tasks/T004-protocol-r-evaluation-contract-and-test-freeze.md), [D005](decisions/D005-protocol-r-v1-class-and-support-eligibility.md) |
| T005 — Protocol R Baseline Implementation | 实现并在 development folds 运行 aggregate-main baseline | Complete — 2026-07-28 | [Canonical result](../experiments/T005-protocol-r-baseline-implementation/result.json), [report](../experiments/T005-protocol-r-baseline-implementation/BASELINE_REPORT.md), [task](tasks/T005-protocol-r-baseline-implementation.md), [D006](decisions/D006-protocol-r-v1-development-reporting-scope.md) |
| T006 — Direct rTM NILM Prototype | 用 causal aggregate window 验证 vanilla TMU rTM 的 sample-wise fridge power feasibility | Paused pending separately authorised R004 review — 2026-07-28 | [Task](tasks/T006-direct-rtm-nilm-prototype.md) |
| T007 — Pico Feature-to-TM Deployment | 编译、烧录、运行并测量 declared Pico boundary | Not started | No task record |
| T008 — Layered Baseline Error Analysis | 形成 per-layer/per-class failure evidence | Not started | No task record |
| T009 — Promoted Method Confirmation | 在 formal development protocol 下重验晋升候选 | Not started | No task record |
| T010 — Final Method and Evaluation Freeze | 冻结 method、code、config、model 和 evaluation manifest | Not started | No task record |
| T011 — Final Protocol R Evaluation | 按预声明方法一次性运行 locked test | Not started | No task record |
| T012 — Protocol D Model and Pico Verification | 训练 deployment model 并重复 parity/resource checks | Not started | No task record |
| T013 — Dissertation, Demo, and Optional Protocol X Evidence Pack | 整理论文、答辩、demo 和可选 stress test | Not started | No task record |

T003 的早期 [pre-reproduction record](reproduction/HAN_MINIMUM_REPRODUCTION_RESULT.md) 只作为 contextual evidence；当前项目的权威 local evidence 是 archived 410-event run。

## E-series

| ID and direct name | Layer | Status | Outcome / evidence |
|---|---|---|---|
| E001 — Booleanisation Encoding A/B Probe | Booleanisation | Archived | [`inconclusive` report](../experiments/E001-booleanization-ab-probe/REPORT.md)；没有 promotion |
| E002 — TM Training Dynamics Probe | TM training and sampling | Legacy archive fixed at `e7277cc4a0326350f51fdfc5c17b8777572deddc` | exploratory H3 result；不得作为 locked dissertation-test evidence；见 [current archive](../experiments/E002-tm-training-dynamics-probe/README.md) 和 [R001](reviews/R001-legacy-evidence-and-reuse-map.md) |

新的 E-series 必须由 coordinating agent 串行分配下一个空闲 ID、direct name 和完整 mutable root，再调用 scaffold。experiment worker 不能自行占号。

## R-series reviews

| ID and direct name | Scope | Status | Durable record |
|---|---|---|---|
| R001 — Legacy Evidence and Reuse Map | 旧 repo、branch、commit、file 和 reuse boundary | Complete | [Review](reviews/R001-legacy-evidence-and-reuse-map.md) |
| R002 — Evaluation Protocol Consistency Review | Protocol R/X、row-position 和 binary-output semantics | Complete | [Review](reviews/R002-evaluation-protocol-consistency-review.md) |
| R003 — Regression Tsetlin Machine Mechanism Review | vanilla/weighted rTM 机制、固定公开源码差异、NILM 假设和验证边界 | Complete | [Review](reviews/R003-regression-tsetlin-machine-mechanism-review.md) |
| R004 — rTM NILM Input and Booleanisation Review | 审查 direct rTM input representation、Booleanisation 和运行成本边界 | Complete — 2026-07-28 | [Review](reviews/R004-rtm-nilm-input-and-booleanisation-review.md) |

`R-series review` 与 `Protocol R` 是两件不同的事。前者是只读工作轨道，后者是正式研究 evaluation protocol。

## 登记规则

- `CURRENT_STATE.md` 保存 active authority；
- 本文件保存 durable identity；
- `EVIDENCE_INDEX.md` 保存 claim/RQ → evidence mapping；
- branch、聊天标题或本地目录不能替代登记；
- result 完成后更新 status，并让 durable record link 到 canonical
  `result.json`/report，但不在索引重复 hash 或重写历史 conclusion；
- E-series archive 完整不等于 formal promotion。
