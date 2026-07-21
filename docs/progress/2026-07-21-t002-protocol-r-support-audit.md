# T002 Protocol R Support Audit — 2026-07-21

**Task:** T002 — REDD Inventory and Protocol R Preflight\
**Status:** In progress; four-class closure gate failed

## Contract and Method

- Sequence contract commit: `5fb7f0e38c8e983969976dc4214038c77b5cafd9`.
- Input: pinned `redd` submodule `a621bbd6399e49c6798550618fe43b113149455b`.
- The audit used Python standard library only and streamed the source CSVs without modifying or copying them.
- Each chunk and validation block reset support state. No cross-chunk state or Protocol R concatenation was used.
- Missing and non-finite labels break continuity. No backward fill was applied.
- Ten synthetic unit tests passed.

## Frozen-Support Results

| Class | Pool cycles | Fold 1 | Fold 2 | Fold 3 | H2 cycles | H4 cycles | Candidate active seconds | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| fridge | 1,106 | 367 | 386 | 353 | 394 | no column | 400,530 | Pass |
| microwave | 206 | 78 | 69 | 59 | 66 | no column | 93,861 | Pass |
| dish washer | 169 | 41 | 85 | 43 | 47 | 11 | 18,171 | Pass |
| electric furnace | 38 | 10 | 15 | 13 | no column | 1 | 824,943 | **Fail: candidate cycles 1 < 10** |
| washer dryer (optional) | 89 | 16 | 55 | 18 | 0 | 11 | 11,811 | Pass; exploratory |

Electric furnace passes the pool minimum and every validation-fold minimum. In the sealed candidate test, H2 has no `electric furnace` column and H4 has 1 complete cycle. Its active-duration minimum passes, but its complete-cycle minimum fails. No fallback, alternate house allocation, class change, boundary change, or threshold change was applied.

## Evidence

- `artifacts/manifests/redd_support_audit.json`
- `artifacts/tables/redd_support_audit.csv`
- `artifacts/manifests/protocol_r_candidate_split.json`
- Candidate manifest canonical SHA-256: `480a738ad799860f6cdecbba9affb1d76c365a71468b276b8b0669ea55bba11a`.
- The manifest contains all 35 source CSV SHA-256 values, immutable revisions, segment roles, half-open fold ranges, sealed candidate status, and boundary policy without absolute paths.

## Closure Decision

T002 is not eligible for closure because all four base classes do not meet the frozen support standard. T002 remains `In progress`; the reserved closure commit was not created.

No event detection, event pairing, feature extraction, TM training, inference, model scoring, firmware, Pico, hardware, upstream modification, dependency installation, raw REDD download, Google Drive access, project remote, push, tag, or extra branch was performed.
