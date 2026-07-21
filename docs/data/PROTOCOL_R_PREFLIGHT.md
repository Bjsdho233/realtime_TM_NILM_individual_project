# Protocol R Preflight Status

**Status:** In progress; audit complete, four-class closure gate failed\
**Date:** 2026-07-21

## Completed Evidence

- The authorised Han upstream and recursive `redd` snapshot were acquired and pinned by full commit identifiers.
- All 35 submodule chunk CSVs and six `docs/redd` combined CSVs were inventoried read-only.
- House, column, missing-value, type, appliance-presence, ordering, and content-correspondence evidence was recorded.
- Candidate-test information, event performance, feature quality, classifier scores, and model outputs were not inspected.
- Tianhang accepted D003: independent chunk segments, nominal 3-second cadence, candidate house roles, three row-position blocks, full dependency containment, and a frozen label-assisted support standard.
- The standard-library audit and ten synthetic tests completed without running the NILM pipeline.
- The candidate split manifest was generated with a reproducible canonical hash.

## Why T002 Is Not Complete

The submodule is explicitly described upstream as pre-processed and synchronized, not as the original raw REDD recording. Its CSVs contain per-file reset indices but no proven timestamps. D003 permits reproducible nominal sequence time without asserting calendar time.

T002 cannot close because the four-class support gate requires every base class to have at least 10 complete cycles in the sealed H2+H4 candidate test. `electric furnace` has no column in H2 and has 1 complete cycle in H4. Its candidate active duration is 824,943 nominal seconds, so duration passes while cycle support fails.

House 1 also demonstrates that the upstream unsorted glob path produces lexicographic `_0`, `_1`, `_10`, `_2`, … order. The combined website file follows that order. Natural numeric order differs materially, but neither order has been proven to represent original chronology.

## Access Record Summary

Inspected fields were limited to repository metadata, relative paths, file sizes and hashes, CSV headers, row and column counts, empty fields, numeric parse compatibility, sequential index behavior, appliance-column presence, ordering correspondence, and static Python/JavaScript read paths.

Houses 2 and 4 are designated as the sealed candidate test for label-support preflight only. Appliance labels, finite/missing counts, threshold samples, transitions, complete cycles, censored runs, and active duration were inspected. No model or feature evidence was generated.

## Required Next Decision

T002 remains `In progress`. No class, threshold, house role, or boundary was changed after the audit. A closure commit must not be created. T003, T004, training, and NILM implementation do not begin automatically.
