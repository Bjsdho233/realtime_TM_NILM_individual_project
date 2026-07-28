# T005 — Protocol R Baseline Implementation

## Agent Brief

- Lifecycle outcome: completed development baseline
- Protocol scope: B1–B4 development only
- Primary summary: `full_eligible_macro_2class`
- Supplemental summary: `development_scope_macro_3class`
- Locked-test/Protocol X access: none
- Python-reference only: yes

## Result

固定 aggregate-main baseline 已完成四个 folds、五个 seeds 和三个 authorised
appliance。`washer dryer` 未训练或评分。

- `full_eligible_macro_2class` mean F1:
  `0.345818303824`，sample std `0.006093000187`；
- `development_scope_macro_3class` mean F1:
  `0.301675954177`，sample std
  `0.008474558968`。

第二项包含 development-only `dish washer`，不能称为完整或 confirmatory
Protocol R evidence。完整 fold × seed × house × appliance counts 和 metrics 见
`tables/development_metrics.csv`。

## Method boundary

使用 50 W first-difference detector、causal FIFO pairing、32-sample pre-history、
8-sample post-context、23-slot Han-compatible aggregate-main features、training-only
Gaussian-CDF 8-bit Booleanisation，以及每 appliance 独立的 200-clause、50-state、
`T=20`、`s=6.0`、10-epoch binary TM。

项目自有 TM repair 只修复 Han 初始化后 action/mask 未同步的问题，并将所有 RNG
绑定到 declared seed；学习规则和固定参数未改变。zero signed-vote tie 预测为
negative。

## Reproducibility

F1 / seed 0 / three-model clean sentinel exact match:
`true`。比较覆盖 candidate、encoder、model、
prediction 和 aggregate metric hashes。

## Limitations

- 这是 development evidence，不是 B5 locked-test result；
- latency 和 bytes 是 Python-reference/inference-serialization measurement，
  不是 host-native 或 Pico measurement；
- detector/pairer misses 作为 explicit no-output false negatives 进入指标；
- 没有根据结果进行 tuning 或第二方法运行。
