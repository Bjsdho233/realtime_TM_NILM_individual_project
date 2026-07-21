# D003 — REDD Sequence-Time Contract

**Status:** Accepted by Tianhang\
**Date:** 2026-07-21\
**Applies to:** T002 Protocol R preflight and later Protocol R processing

## Decision

### Canonical input and two views

The canonical reproduction input is the `redd` submodule pinned at commit `a621bbd6399e49c6798550618fe43b113149455b`.

The Han upstream reproduction view preserves the current upstream `glob` + concatenate + `bfill` behaviour, including the observed Windows lexicographic House 1 order. This view exists only for exact upstream reproduction.

The Protocol R evaluation view uses each `redd_houseN_K.csv` as an independent segment. Row order is valid within a segment. No time order is defined across segments, and no window, event, pair, state, or feature row may cross a segment boundary. The `docs/redd` combined files are not Protocol R inputs.

### Sequence-time identity

The nominal cadence is 3 seconds per sample. A row is identified by:

- `segment_id`;
- zero-based `sample_index` within that segment;
- `nominal_offset_seconds = sample_index * 3`.

The nominal offset is not an original timestamp. Calendar-time coverage and original recording gaps cannot be recovered from the pinned CSVs.

### Protocol R candidate layout

- Train/validation pool: Houses 1, 3, 5, and 6.
- Sealed candidate test: Houses 2 and 4.
- Four-class base: `fridge`, `microwave`, `dish washer`, and `electric furnace`.
- Optional fifth exploratory class: `washer dryer`.
- `electric space heater` must not be mapped to `electric furnace`.

Each train/validation segment is split independently by row position into three contiguous blocks. The split does not depend on the order of files. Block row ranges use half-open `[start, end)` boundaries; quotient/remainder partitioning assigns one extra row to each earliest block until the remainder is exhausted.

### Boundary and containment policy

Every detector, pairer, and state machine must reset at the start of each segment and block. A sample, window, active run, event, pair, or feature row is eligible only when its complete dependency interval is contained within one block. Anything crossing a segment or block boundary is discarded.

This full-dependency containment rule is the Protocol R purge policy. No fixed numerical purge is asserted until the actual dependency horizons are known.

## Frozen Label-Assisted Support Standard

This standard is feasibility-only oracle evidence. It is not a detector, pairer, feature, classifier, or model result.

- An active sample has finite appliance power strictly greater than 15 W.
- An active run contains at least two consecutive active samples, equivalent to at least 6 nominal seconds.
- A complete cycle has an observable finite inactive sample before the run, the complete qualifying active run, and an observable finite inactive sample after it, all within the same segment or block.
- A qualifying run lacking an observable inactive leading edge is counted as left-censored, not complete.
- A qualifying run lacking an observable inactive trailing edge is counted as right-censored, not complete.
- Missing or non-finite values are counted explicitly and break observation continuity. They are not silently treated as active or inactive.
- Active duration is `active_sample_count * 3 seconds`.
- The Protocol R audit does not apply `bfill`; any future compatibility-only same-chunk `bfill` must be separately recorded.

Minimum full-category support is:

- at least 30 complete cycles across the train/validation pool;
- at least 5 complete cycles in each validation fold;
- at least 10 complete cycles across the sealed Houses 2 and 4 candidate test;
- at least 10 minutes of candidate-test active duration.

All four base classes must meet every minimum for T002 preflight to pass. `washer dryer` is audited by the same standard, but remains exploratory and does not block four-class T002 closure if it fails. These thresholds must not be changed after observing the audit.

## Source Evidence and Limits

The AAAI paper reports REDD aggregate acquisition at 1 second, appliance acquisition at 3 seconds, sequence splitting around missing intervals, backward filling within subsequences, retention of subsequences longer than one day, and a 15 W on/off threshold. The inspected fixed repository implementation aligns onto a 3-second grid, implements backward filling and gap-based subsequence splitting, and treats preprocessed CSV files as separate non-continuous long windows.

The implementation also contains a branch that retains a single subsequence even when it is shorter than the nominal one-day filter. This can explain how a short single subsequence could survive, but it does not prove the historical creation path of House 5.

Exact inspected sources:

- [`inesylla/energy-disaggregation-DL` at `4f5d71132356859cda70011532584dfdad028fa8`](https://github.com/inesylla/energy-disaggregation-DL/tree/4f5d71132356859cda70011532584dfdad028fa8)
- [Subtask Gated Networks for Non-Intrusive Load Monitoring](https://cdn.aaai.org/ojs/3908/3908-13-6967-1-10-20190702.pdf)

The following remain unresolved and must remain visible in provenance and limitations:

- calendar-time coverage and original gaps;
- the per-file original channel-to-column generation chain;
- the command that generated `docs/redd`;
- whether natural numeric file order equals historical chronology;
- the historical preprocessing path from raw REDD to every pinned CSV, including House 5.

## Consequences

Protocol R can perform reproducible row-position preflight without inventing timestamps or cross-segment chronology. The resulting candidate split remains a preflight artefact; it becomes the locked test only through the later explicit freeze process.

No model execution, event generation, feature extraction, or research evaluation is authorised by this decision.
