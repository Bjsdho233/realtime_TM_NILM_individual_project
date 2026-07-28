# D005 — Protocol R v1 Class and Support Eligibility

## Agent Brief

- Status: Accepted by Tianhang
- Date: 2026-07-28
- Scope: T004 Protocol R v1 class eligibility and Protocol X support eligibility
- Frozen Protocol R manifest changed: no
- Frozen Protocol R support audit changed: no
- Model training, prediction, or scoring: none

## Context

T004 先冻结了
[`protocol_r_evaluation_v1.json`](../../artifacts/manifests/protocol_r_evaluation_v1.json)，
再运行
[`protocol_r_support_audit_v1.json`](../../artifacts/manifests/protocol_r_support_audit_v1.json)。
固定的 B1–B5 row-position split 暴露了真实 support 不均衡：
`dish washer` 在 B5 不满足 test minimum，`washer dryer` 在 F1 不满足
development-fold minimum。

T004 的目标是冻结协议并诚实判定 eligibility，不要求所有 class 都通过。
因此 Tianhang 明确决定保留所有 frozen boundary、minimum、class record 和
negative support evidence，不根据 audit 结果重新划分数据。

## Decision

Machine-readable authority 是
[`protocol_r_class_eligibility_v1.json`](../../artifacts/manifests/protocol_r_class_eligibility_v1.json)。

| Appliance | B1–B4 development CV | Protocol R B5 | Protocol R v1 |
|---|---|---|---|
| fridge | Eligible | Eligible | Full eligible |
| microwave | Eligible | Eligible | Full eligible |
| dish washer | Eligible | Ineligible | Development-only |
| washer dryer | Ineligible | Ineligible despite B5 support | Support-ineligible; deferred |

`dish washer` 可在未来另行授权的 E003/E004 中使用 B1–B4 产生
direct-rTM feasibility development evidence，但不得生成或宣称 Protocol R B5
test result。development CV 不构成完整或 confirmatory Protocol R result。

`washer dryer` 的 B5 support 不能补偿 F1 validation fold 的缺失。它保留在
frozen manifest/audit 中，但从当前 E003/E004 scope deferred。

## Protocol X support decision

独立
[`protocol_x_support_audit_v1.json`](../../artifacts/manifests/protocol_x_support_audit_v1.json)
对固定 H2+H4 composite population 使用相同 `L_max=256`、`D_max=8`、15 W
threshold 和 10 episodes / 600 seconds test minimum。没有建立 development
split，也没有删除、交换或选择 house。

`dish washer` pooled H2+H4 有 58 个 dependency-contained complete episodes
和 18,171 秒 ON support，因此是 future Protocol X locked confirmatory
evaluation eligible。未来必须由单独正式任务一次性授权，其结果只可作为
Protocol X cross-house evidence，不得称为 Protocol R B5 result。

`fridge`、`microwave` 也通过 pooled minimum，但 H4 对这两个 class 没有 target
column；该 house-class label 是 unavailable，不得解释为全零。`washer dryer`
通过 Protocol X 数据 support minimum，但由于当前 Protocol R development CV
不 eligible，其 formal Protocol X evaluation scope 仍 deferred。

## Supersession and preserved history

本决定保留 D003 的 canonical input、independent-segment 和 row-position time
identity，但 supersede 其三块 candidate layout 作为未来正式 evaluation split
的地位。正式 T004 split 是五块 B1–B5。

本决定保留 D002 的 mixed-house Protocol R / held-out-house Protocol X 研究问题，
并以 `sequence-first, row-position blocked` 取代无法由当前数据证明的
`raw-time blocked` 表述。H2/H4 的旧 candidate-test support 和 Protocol H access
记录仍是历史事实，不被重写。

## Consequences

- T004 可以在 access guard、专项测试和 repository checks 完成后以
  `completed with documented class limitations` 关闭。
- T004 completion 不授权 E003、E004、T005、T011 或 Protocol X evaluation。
- B5 和 H2/H4 继续对 ordinary development fail-closed。
- 不得移动 boundary、降低 minimum、替换 class、删除 negative support evidence
  或把 development-only evidence 写成 confirmatory result。
