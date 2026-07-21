# REDD Inventory — Han Upstream Snapshot

**Status:** Verified snapshot inventory; T002 remains incomplete\
**Inventory date:** 2026-07-21\
**Dataset identifier:** `han-upstream-redd-a621bbd6399e49c6798550618fe43b113149455b`

## Snapshot Identity

| Item | Verified value |
|---|---|
| Han upstream URL | `https://github.com/wuhanstudio/nilm.git` |
| Han upstream branch | `main` |
| Han upstream commit | `8c5e90df34236ba0afcc4ec46ac083d829de4d51` |
| REDD submodule URL | `https://github.com/wuhanstudio/redd` |
| REDD submodule commit | `a621bbd6399e49c6798550618fe43b113149455b` |
| Upstream status after inspection | Clean |
| Submodule status after inspection | Clean, detached at the pinned commit |
| Tracked dataset root | `${HAN_UPSTREAM_SNAPSHOT}/redd` |
| Combined web files | `${HAN_UPSTREAM_SNAPSHOT}/docs/redd` |

The submodule README identifies its content as a “Pre-processed REDD dataset (synchronized).” It does not establish the original raw REDD revision, acquisition path, preprocessing procedure, timestamps, sampling interval, or original channel mapping. Those links remain `Unresolved`.

For Han upstream reproduction, the pinned `redd` submodule is the input source. `docs/redd` is a web-distribution and scoring derivative, not an independent dataset.

## Method

- CSVs were parsed read-only with Python's standard `csv` module.
- Data-row counts exclude the header.
- Chunk statistics exclude the unnamed physical index column from the reported data-column count.
- A column is `float-compatible` when every non-missing textual value parses as a floating-point number.
- Missing values are empty CSV fields.
- The content-tree fingerprint is SHA-256 over sorted records containing relative path, NUL, and each file's raw-byte SHA-256.
- No support threshold, activation count, event detector, feature, classifier, or model score was used.

Content-tree SHA-256:

```text
5e1ee53cdce2a5ad2d5007a08527bd1fc9486130d56dc008cf8c8ba8e336e73d
```

## Submodule House Inventory

All data columns are float-compatible. Every chunk has an unnamed, zero-based sequential integer index that resets to zero for each file; this index is not proven to be a timestamp.

| House | Files | Data rows | Data columns | Missing fields | Appliance coverage; `main` excluded |
|---:|---:|---:|---:|---:|---|
| 1 | 11 | 348,731 | 7 | 2 | dish washer; electric space heater; electric stove; fridge; microwave; washer dryer |
| 2 | 7 | 292,063 | 7 | 0 | dish washer; electric stove; fridge; microwave; washer dryer; waste disposal unit |
| 3 | 6 | 242,044 | 8 | 0 | CE appliance; dish washer; electric furnace; fridge; microwave; washer dryer; waste disposal unit |
| 4 | 6 | 274,983 | 5 | 0 | dish washer; electric furnace; electric stove; washer dryer |
| 5 | 1 | 24,181 | 9 | 2 | CE appliance; dish washer; electric furnace; electric space heater; fridge; microwave; washer dryer; waste disposal unit |
| 6 | 4 | 326,576 | 7 | 0 | CE appliance; dish washer; electric space heater; electric stove; fridge; washer dryer |
| **Total** | **35** | **1,508,578** | — | **4** | — |

Missing fields are limited to:

- House 1, `redd_house1_10.csv`, first row: `washer dryer` and `main`;
- House 5, `redd_house5_0.csv`, first row: `electric space heater` and `washer dryer`.

No file has a row-width error.

## `docs/redd` Combined CSV Inventory

All combined columns are float-compatible, all have zero missing fields, and no file has a row-width error.

| House | File | Rows | Columns | Raw-byte SHA-256 |
|---:|---|---:|---:|---|
| 1 | `docs/redd/building_1_combined.csv` | 348,731 | 7 | `292a63f313ba829eaa869fed0b67738fd5718f5eedfe3e05bdfa73d25fd8cea2` |
| 2 | `docs/redd/building_2_combined.csv` | 292,063 | 7 | `ffcc7896281e5e1d83fd826e9c6faf1c5a31942beb1f57c0b7414158e426b71b` |
| 3 | `docs/redd/building_3_combined.csv` | 242,044 | 8 | `a9e8e37e93dc7b5616091fac0a0037a9aa1439539e9643e131faa29c8be37ef9` |
| 4 | `docs/redd/building_4_combined.csv` | 274,983 | 5 | `953c74a31d70ffafcaa0d5b7f13c81ad10b0d0d37628e40c8ed0eac3cc10784e` |
| 5 | `docs/redd/building_5_combined.csv` | 24,181 | 9 | `7fbc6464ee666c7daa4975e619709083533f9d52a87e619fcce093f1db68a481` |
| 6 | `docs/redd/building_6_combined.csv` | 326,576 | 7 | `ecf1c19aa1ac7a69965a381d319e1d6ceafc09d3e4c566fde7ab8ffffc8e1023` |

## Combined Correspondence and House 1 Ordering

The upstream Python readers use `glob.glob("redd/redd_house{building_id}_*.csv")`, concatenate the returned files without an explicit sort, then call `bfill()`.

On the verified Windows clone, `glob.glob` returned lexicographic order. Applying that order and backward fill to the submodule chunks reproduces all six combined CSVs exactly.

| House | Lexicographic + bfill | Natural numeric + bfill | Finding |
|---:|---|---|---|
| 1 | Exact | Not exact; 299,564 row mismatches | Lexicographic order places `_10.csv` after `_1.csv` and before `_2.csv`. |
| 2 | Exact | Exact | Filenames contain only single-digit suffixes. |
| 3 | Exact | Exact | Filenames contain only single-digit suffixes. |
| 4 | Exact | Exact | Filenames contain only single-digit suffixes. |
| 5 | Exact | Exact | One file only. |
| 6 | Exact | Exact | Filenames contain only single-digit suffixes. |

For House 1, raw lexicographic concatenation differs from the combined CSV in one row: the first row of `_10.csv`. Backward fill replaces its missing `washer dryer` and `main` values from the following row. House 5 has the analogous two-cell backward fill in its first row.

The combined-file content is therefore reproducible from the pinned chunks, local glob ordering, and backward fill. The tracked code does not explicitly sort filenames and no tracked script was found that writes directly to `docs/redd/building_*_combined.csv`; the historical generation and publication step remains `Unresolved`.

## Actual Data-Reading Paths

| Consumer | Actual read path or input |
|---|---|
| `main.py` | `glob.glob("redd/redd_house{building_id}_*.csv")`; `pd.read_csv(..., index_col=0)`; concatenate; `bfill()`; normalization stats from configurable `--stats-csv`, default `redd_data_train.csv` |
| `main_real_time.py` | Same chunk glob, `pd.read_csv`, concatenate, and `bfill()`; configurable normalization-stats CSV |
| `redd_edge_detect.py` | Same chunk glob, `pd.read_csv`, concatenate, and `bfill()`; writes a root-level `building_*_raw.csv` if executed |
| `tests/redd_prune_data.py` | Same chunk glob and `bfill()`; also accepts an input CSV and would write test outputs if executed |
| `redd_edge_match.py` | Reads generated `output/building_*_*_transients.csv` and root-level `building_*_raw.csv` |
| `redd_event_pair.py` | Reads root-level `building_*_raw.csv` and `building_*_main_transients_train.csv` |
| `redd_tm_training.py` | Reads generated matched-transition CSVs from the configured output directory |
| `docs/js/script.js` | Fetches `redd/building_${i}_combined.csv` relative to the website and exposes the same path for download |
| `docs/js/upload.js` | Parses a user-selected CSV with Papa Parse, then fetches `redd/building_${activeBuildingId}_combined.csv` as scoring ground truth |

Other readers such as `iris.py` and Tsetlin model serialization do not establish a REDD data path.

## Source Chain

Verified locally:

1. Han upstream commit `8c5e90d...` contains a gitlink to the `redd` submodule.
2. `.gitmodules` identifies `https://github.com/wuhanstudio/redd`.
3. Recursive clone checked out `a621bbd...` at `redd/`.
4. Upstream Python code reads `redd/redd_house*_*.csv`, concatenates unsorted glob results, and applies backward fill.
5. The six `docs/redd` files exactly match lexicographic concatenation plus backward fill for this snapshot.
6. Website JavaScript fetches `docs/redd` content for display, download, and upload scoring.

Unresolved:

- provenance from original raw REDD to the pre-processed synchronized submodule;
- timestamp and sampling semantics;
- original channel identifiers and transformations;
- the tracked command or commit that generated and published `docs/redd`;
- whether natural numeric suffix order is the intended chronological order;
- active-support thresholds, activation counts, and class feasibility;
- candidate train, validation, and test blocks, purge, and boundary rules.
