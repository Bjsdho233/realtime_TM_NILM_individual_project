# T003 / E001 归档校验和勘误
# T003 / E001 Archive Checksum Correction

## Agent Brief

- Date: 2026-07-23
- Status: corrected by append-only current-byte manifest
- Affected archives: T003 local reproduction, E001 Booleanisation probe
- Metrics changed: no
- Archived report/code changed: no
- Legacy checksum files rewritten: no
- Authoritative current-byte manifest: `schemas/legacy-archive-checksums.json`

## 1. 发现的问题

对 GitHub `main` 中已经 admitted 的两个 archive 重新执行原 `SHA256SUMS.txt` 后，发现：

- E001：`experiment.py` 通过，另外 4 个 listed files 不匹配；
- T003：6 个 listed files 全部不匹配。

这不是本轮 governance rewrite 引入的变化。`33a8bf0` 中的 admitted Git blobs 本身就无法通过 archive 内原 checksum list。

归档说明记录了 archive copies 曾进行以下 normalisation：

- machine-specific absolute path 替换为 placeholder；
- CommonMark line-break normalisation；
- T003 mixed PowerShell log 的 NUL-byte removal。

原 `SHA256SUMS.txt` 描述的是 normalisation 之前的 bytes，但在 archive copy 改变后没有重新生成。因此它不能继续被解释为 current admitted Git bytes 的完整校验。

## 2. 修复方式

为了不伪造历史，处理采用 append-only correction：

1. 不修改 T003/E001 的 report、code、CSV、JSON、log 或 environment record；
2. 不覆盖原 `SHA256SUMS.txt`；
3. 保留 `SOURCE_FILE_SHA256SUMS.txt` 和 `SOURCE_RUN_SHA256SUMS.txt` 的原始 provenance 含义；
4. 新增 [`legacy-archive-checksums.json`](../../schemas/legacy-archive-checksums.json)，记录当前 admitted archive 中每个 Git-tracked file 的 SHA-256；
5. `python scripts/check_repo.py` 实际读取并核验该 manifest，而不是只检查 allowlist/filename。

新 manifest 也包含 legacy `SHA256SUMS.txt` 自身的 current-byte hash，因此后续对任何 archive file 的修改都会被 repository check 检出。

## 3. 证据影响

该勘误只修复 integrity metadata，不改变：

- T003 的 410 events、accuracy `0.965854`、macro F1 `0.914298`、`9,058` C model bytes 或 reload mismatch；
- E001 的 paired-seed metrics、`inconclusive` outcome 或 data boundary；
- 两个 archive 的 protocol/claim scope；
- 原 source-file provenance。

原 `SHA256SUMS.txt` 现在应解释为：

> historical pre-normalisation checksum record

新的 `schemas/legacy-archive-checksums.json` 应解释为：

> authoritative checksum manifest for the currently admitted Git bytes

未来 archive 必须在所有 redaction/normalisation 完成之后再生成 final checksum，并由 repository validator 在 commit 前实际验证。
