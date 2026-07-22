# Experiment Archive

This directory contains reviewed experiment evidence admitted under explicit
authorisation. It does not contain REDD data, matched-event CSVs, virtual
environments, model binaries, generated C headers, caches, or temporary files.

| Experiment | Evidential status | Result | Archive |
|---|---|---|---|
| T003 local reproduction | Han-compatible engineering reproduction | Successful and repeatable two-class PC reproduction. Differences from the earlier remote pre-reproduction remain unresolved. | [`T003-local-reproduction/`](T003-local-reproduction/) |
| E001 Booleanization A/B Probe | Exploratory only | `inconclusive`; the `promising` rule was not met. Han binary remains the current baseline. | [`E001-booleanization-ab-probe/`](E001-booleanization-ab-probe/) |

Neither archive starts T004 or changes formal Protocol R. E001 is not formal
model selection and must not be reported as a final thesis result.

## Archive integrity

Each experiment directory contains:

- `SOURCE_FILE_SHA256SUMS.txt`, recording hashes of the authorised source
  files before archival normalisation;
- `SHA256SUMS.txt`, recording hashes of the admitted archive files;
- the requested reports, manifests, logs, environment record, code, or metric
  tables.

The T003 directory also preserves the original complete-run checksum list as
`SOURCE_RUN_SHA256SUMS.txt`. It references external run artefacts that are not
admitted to this repository.

Machine-specific absolute roots and the local host name were replaced in
archive copies with explicit placeholders. Experimental metrics, conclusions,
configuration, and source archives were not changed. Original scratch
directories remain outside this repository. Markdown two-space hard breaks
were normalised to explicit CommonMark backslashes. NUL bytes introduced by
mixed PowerShell log encodings were removed from the archived T003 command log
so that it remains reviewable as UTF-8 text.
