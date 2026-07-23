# 实验与复现归档 / Experiment Archive

本目录保存经过审查、适合进入 Git 的 T/E evidence。REDD、matched-event rows、row-level predictions、virtual environment、trained models、cache 和大型 generated outputs 不进入本目录。

## 已有归档

| Work | Evidence scope | Outcome | Archive |
|---|---|---|---|
| T003 — Han Two-Class PC Reproduction | Protocol H compatibility | later local run 可重复；410 events，macro F1 `0.914298`；与 earlier pre-reproduction 的差异未解决 | [`T003-local-reproduction/`](T003-local-reproduction/) |
| E001 — Booleanisation Encoding A/B Probe | exploratory, legacy label-assisted development data | `inconclusive`；没有达到 predeclared rule | [`E001-booleanization-ab-probe/`](E001-booleanization-ab-probe/) |

两份 archive 都不会自动启动 T004，也不会改变 formal Protocol R。

## Legacy archive checksum 勘误

archive copies 在进入 Git 前进行了 path placeholder、line-break 和 T003 NUL-byte normalisation，但原 `SHA256SUMS.txt` 没有在 normalisation 后重算：

- E001 原清单 1 项通过、4 项不匹配；
- T003 原清单 6 项全部不匹配。

为了保留历史，原 checksum files 不覆盖。它们现在解释为 pre-normalisation records。当前 admitted Git bytes 由：

- [`schemas/legacy-archive-checksums.json`](../schemas/legacy-archive-checksums.json)

统一记录，并由 `python scripts/check_repo.py` 实际核验。完整说明见 [archive checksum correction](../docs/progress/2026-07-23-archive-checksum-correction.md)。

`SOURCE_FILE_SHA256SUMS.txt` 和 T003 的 `SOURCE_RUN_SHA256SUMS.txt` 继续保存 original source/run provenance，不代表 current archive-copy bytes。

## 新 E-series layout

scaffold 在 anchor 前只创建 immutable design inputs：

```text
experiments/E###-direct-name/
├── design_manifest.json
├── design_manifest.sha256
└── environment.txt
```

如果使用 `--freeze-existing`，预先准备并声明的 `scripts/` 和 `configs/` 也属于
immutable design inputs。design anchor 与 registry anchor 验证后，再初始化可追加
的 `EXPERIMENT.md` 和 `commands.log`；实验完成后增加 root `result.json`。
`tables/`、`figures/`、`docs/` 和 local mutable directories 只在需要时创建。

canonical contract：

- design schema: [`schemas/e-series-design.schema.json`](../schemas/e-series-design.schema.json)
- result schema: [`schemas/work-result.schema.json`](../schemas/work-result.schema.json)
- design hash: `design_manifest.sha256`
- canonical result: root `result.json`
- aggregate tables: `tables/`
- paper-ready figures: `figures/`
- custom aggregate CSV: predeclare each contract with repeatable
  `--aggregate-table '<strict JSON object>'`

`work/`、`cache/`、`models/`、`outputs/`、`results/`、`raw/`、`predictions/` 和 logs 属于 mutable/local output，不归档。

## 启动新 E-series

1. coordinating agent 在 `CURRENT_STATE.md` 的唯一 `Active E-series Registry`
   以 `registered` 登记 exact ID、direct name、owner、完整 mutable root，并把
   design hash/commit 写成 `Pending`；同时在 `WORK_INDEX.md` 登记 durable identity；
2. 查看命令：

   ```bash
   python scripts/scaffold_e_series.py --help
   ```

3. scaffold 严格解析 exact registry row 和 Work Index identity，并创建 design；
4. 建立只含该 E 的 design/source/config/environment、且无结果的 design-only commit；
5. coordinator 把 registry row 更新为 `design_frozen`，写入 exact
   64-hex design hash 和 40-hex design commit；
6. checker 验证 commit 中的 design、hash、path scope、ancestor 和 drift 后，
   才能进行首次 evidence-producing execution；纯 scaffold/schema/static syntax
   check 不受此限制；
7. 完成后在 `result.json` 持久保存 design hash/commit，由 coordinator 先更新
   durable `WORK_INDEX`/`EVIDENCE_INDEX`，再删除 `CURRENT_STATE` active row；
8. 运行：

   ```bash
   python scripts/check_repo.py
   ```

comparison、diagnostic 和 feasibility 使用不同的 conditional requirements。不要为了模板给 diagnostic/feasibility 虚构 classification baseline。

`output_contract.aggregate_tables` 可以为空；需要 table 时必须在 frozen design
预声明 exact `tables/*.csv` path、ordered columns、`max_rows`、purpose 和
aggregation unit。未声明、row-level、ragged 或多出隐藏 cells 的 CSV 会被拒绝。

引用的 data/artifact manifests 必须在 design anchor 前已经
tracked/committed。design-only commit 不能包含 `EXPERIMENT.md`、
`commands.log`、result/table/figure；前两者是执行期间可追加的 lifecycle
records。包含 design anchor 的 PR 必须 merge-commit，不能 squash 或 rebase
merge；checker 需要 full Git history。

portable learned artifact 只通过 tracked manifest 引用；manifest 必须包含
structured `origin`、`availability_limits`、content hash、locator 和 fit-data
roles。E-series 若值得晋升，result action 使用 `propose_promotion`，不能直接
`promote`。

详细规则见 [Research Evidence Standard](../docs/RESEARCH_EVIDENCE_STANDARD.md)。
