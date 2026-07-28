# D006 — Protocol R v1 Development Reporting Scope

## Agent Brief

- Status: Accepted by Tianhang
- Date: 2026-07-28
- Scope: T005 Protocol R development baseline class and reporting identities
- Frozen T004 manifest or audits changed: no
- Locked-test or Protocol X access: prohibited

## Context

T004 冻结了 Protocol R v1 的 population、B1–B5 boundaries、B1–B4 blocked
cross-validation、B5 locked-test identity 和 class eligibility。D005 随后确认
`fridge`、`microwave` full eligible，`dish washer` development-only，
`washer dryer` support-ineligible。

T005 需要在不重写 T004 文件、不把 development evidence 扩张为 confirmatory
claim 的前提下，明确 primary 和 supplemental aggregation scope。

## Decision

T005 只训练以下 aggregate-main-only binary classification TM：

| Appliance | T005 development model | Reporting identity |
|---|---|---|
| fridge | included | full-eligible |
| microwave | included | full-eligible |
| dish washer | included | development-only |
| washer dryer | deferred; do not train or score | support-ineligible |

结果必须分别使用两个明确名称：

- `full_eligible_macro_2class`：只含 `fridge` 和 `microwave`，是 T005 primary
  development summary；
- `development_scope_macro_3class`：含 `fridge`、`microwave` 和
  `dish washer`，是 supplemental development-only evidence。

不得报告 unnamed generic macro、four-class macro 或 event exact-match accuracy。
missing appliance column 表示 label unavailable，不得视为 OFF。

两模型 full-eligible ensemble 和三模型 development ensemble 的 serialized
inference bytes、TM-evaluation latency 和 feature-to-decision latency 也必须使用
上述 scope identity 分开报告。

## Evidence and claim boundary

- T005 的全部 model fitting、validation 和 reporting 只允许 B1–B4。
- `dish washer` development CV 不得称为完整或 confirmatory Protocol R result。
- T005 不生成 B5、H2/H4、Protocol X、final-fit、rTM/TMU、host-native、Pico、
  firmware 或 hardware evidence。
- 本决定不修改
  [`protocol_r_evaluation_v1.json`](../../artifacts/manifests/protocol_r_evaluation_v1.json)、
  [`protocol_r_support_audit_v1.json`](../../artifacts/manifests/protocol_r_support_audit_v1.json)
  或任何 T004 boundary/minimum。
