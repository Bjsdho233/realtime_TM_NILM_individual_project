# T003 and E001 Experiment Archive

**Date:** 2026-07-22\
**Status:** Complete

Tianhang explicitly authorised archival of the completed T003 local
reproduction and E001 Booleanization A/B Probe, including one local commit and
push.

## Archived evidence

- T003 is archived under `experiments/T003-local-reproduction/`.
- E001 is archived under `experiments/E001-booleanization-ab-probe/`.
- Source-file and archive-file SHA-256 records were verified.
- Machine-specific roots and the local host name were normalised only in the
  repository copies.
- Original experiment directories were copied, not moved or deleted.

T003 records a successful and repeatable two-class Han-compatible PC
reproduction. Its local event counts, metrics, model hashes, reload parity, and
model size differ from the earlier remote pre-reproduction record; the cause
remains unresolved.

E001 records an exploratory Booleanization A/B probe. Its result is
`inconclusive`: the mean paired Macro-F1 improvement was below `0.02` and
threshold encoding won only three of five seeds. Han binary therefore remains
the current baseline.

No REDD source data, matched-event CSV, model binary, generated C header,
virtual environment, cache, or temporary output was admitted. T004 was not
started, formal Protocol R was not modified, and no firmware, Pico, Arduino,
TMU, or hardware work was performed.
