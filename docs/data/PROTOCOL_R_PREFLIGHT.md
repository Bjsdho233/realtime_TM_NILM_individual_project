# Protocol R Preflight Status

**Status:** In progress; sequence-time and support contracts accepted, audit pending\
**Date:** 2026-07-21

## Completed Evidence

- The authorised Han upstream and recursive `redd` snapshot were acquired and pinned by full commit identifiers.
- All 35 submodule chunk CSVs and six `docs/redd` combined CSVs were inventoried read-only.
- House, column, missing-value, type, appliance-presence, ordering, and content-correspondence evidence was recorded.
- Candidate-test information, event performance, feature quality, classifier scores, and model outputs were not inspected.
- Tianhang accepted D003: independent chunk segments, nominal 3-second cadence, candidate house roles, three row-position blocks, full dependency containment, and a frozen label-assisted support standard.

## Why T002 Is Not Complete

The submodule is explicitly described upstream as pre-processed and synchronized, not as the original raw REDD recording. Its CSVs contain per-file reset indices but no proven timestamps. D003 permits reproducible nominal sequence time without asserting calendar time. The remaining Phase B work must establish:

- raw recording identity and preprocessing provenance;
- label-assisted active duration or activation support under a declared rule;
- exact half-open fold ranges for every train/validation segment;
- a candidate split manifest, sealed candidate-test designation, and reproducible split hash.

House 1 also demonstrates that the upstream unsorted glob path produces lexicographic `_0`, `_1`, `_10`, `_2`, … order. The combined website file follows that order. Natural numeric order differs materially, but neither order has been proven to represent original chronology.

## Access Record Summary

Inspected fields were limited to repository metadata, relative paths, file sizes and hashes, CSV headers, row and column counts, empty fields, numeric parse compatibility, sequential index behavior, appliance-column presence, ordering correspondence, and static Python/JavaScript read paths.

Houses 2 and 4 are now designated as the sealed candidate test for label-support preflight only. No model or feature evidence has been generated.

## Required Next Decision

T002 remains `In progress`. The D003 contract must be committed before support statistics are read. Then the authorised audit and candidate manifest may be generated. T003, T004, training, and NILM implementation do not begin automatically.
