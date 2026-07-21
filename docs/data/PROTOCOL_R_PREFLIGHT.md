# Protocol R Preflight Status

**Status:** Incomplete; no candidate split is proposed or frozen\
**Date:** 2026-07-21

## Completed Evidence

- The authorised Han upstream and recursive `redd` snapshot were acquired and pinned by full commit identifiers.
- All 35 submodule chunk CSVs and six `docs/redd` combined CSVs were inventoried read-only.
- House, column, missing-value, type, appliance-presence, ordering, and content-correspondence evidence was recorded.
- Candidate-test information, event performance, feature quality, classifier scores, and model outputs were not inspected.

## Why T002 Is Not Complete

The submodule is explicitly described upstream as pre-processed and synchronized, not as the original raw REDD recording. Its CSVs contain per-file reset indices but no proven timestamps. Consequently this inventory cannot yet establish:

- raw recording identity and preprocessing provenance;
- timestamp coverage, sampling intervals, gaps, or cross-file chronology;
- label-assisted active duration or activation support under a declared rule;
- safe raw-time train, validation, and candidate test boundaries;
- a boundary containment or numerical purge rule;
- a candidate split manifest, access-controlled candidate block, or reproducible split hash.

House 1 also demonstrates that the upstream unsorted glob path produces lexicographic `_0`, `_1`, `_10`, `_2`, … order. The combined website file follows that order. Natural numeric order differs materially, but neither order has been proven to represent original chronology.

## Access Record Summary

Inspected fields were limited to repository metadata, relative paths, file sizes and hashes, CSV headers, row and column counts, empty fields, numeric parse compatibility, sequential index behavior, appliance-column presence, ordering correspondence, and static Python/JavaScript read paths.

No candidate test block was designated. No model or feature evidence was generated.

## Required Next Decision

T002 remains `In progress`. Tianhang must review whether the pre-processed submodule is sufficient for Han reproduction only, and separately identify evidence suitable for Protocol R raw-time evaluation. T003, T004, training, and implementation do not begin automatically.
