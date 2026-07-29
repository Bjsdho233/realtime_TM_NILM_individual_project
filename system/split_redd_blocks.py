"""Split prepared REDD segments into the frozen Protocol R blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd


PROTOCOL_R_HOUSES = (1, 3, 5, 6)
PROTOCOL_X_HOUSES = (2, 4)
BLOCK_NAMES = ("B1", "B2", "B3", "B4", "B5")
REDD_SUBMODULE_COMMIT = "a621bbd6399e49c6798550618fe43b113149455b"
SOURCE_NAME = re.compile(r"^redd_house(?P<house>\d+)_(?P<segment>\d+)\.csv$")

SYSTEM_ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SYSTEM_ROOT / "data" / "redd"
DEFAULT_OUTPUT_ROOT = SYSTEM_ROOT / "data"


def calculate_block_boundaries(row_count: int) -> list[tuple[int, int]]:
    """Return five half-open intervals using the frozen floor(n*k/5) rule."""
    if row_count <= 0:
        raise ValueError("row_count must be positive")

    # 余数分配由明确的整数边界公式决定，不依赖 pandas/numpy 的切分默认值。
    points = [(row_count * index) // 5 for index in range(6)]
    return list(zip(points[:-1], points[1:]))


def validate_block_boundaries(
    boundaries: list[tuple[int, int]], row_count: int
) -> None:
    if len(boundaries) != 5:
        raise ValueError("exactly five block intervals are required")
    if boundaries[0][0] != 0 or boundaries[-1][1] != row_count:
        raise ValueError("block intervals do not cover the complete segment")

    for index, (start, end) in enumerate(boundaries):
        if start > end:
            raise ValueError("block interval has a negative length")
        if index > 0 and boundaries[index - 1][1] != start:
            raise ValueError("block intervals overlap or leave a gap")


def parse_source_name(path: Path) -> tuple[int, int]:
    match = SOURCE_NAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unexpected CSV name: {path.name}")
    return int(match["house"]), int(match["segment"])


def discover_source_files(input_dir: Path) -> dict[int, list[tuple[int, Path]]]:
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"no REDD CSV files found in {input_dir}")

    by_house: dict[int, list[tuple[int, Path]]] = {}
    for path in csv_files:
        house, segment = parse_source_name(path)
        by_house.setdefault(house, []).append((segment, path))

    expected_houses = set(PROTOCOL_R_HOUSES) | set(PROTOCOL_X_HOUSES)
    actual_houses = set(by_house)
    if actual_houses != expected_houses:
        raise ValueError(
            f"source houses must be {sorted(expected_houses)}, "
            f"found {sorted(actual_houses)}"
        )

    for house, sources in by_house.items():
        sources.sort(key=lambda item: item[0])
        segment_numbers = [segment for segment, _ in sources]
        expected_numbers = list(range(segment_numbers[-1] + 1))
        if segment_numbers != expected_numbers:
            raise ValueError(
                f"H{house} segment numbers must be contiguous from 0: "
                f"found {segment_numbers}"
            )

    return by_house


def select_protocol_sources(
    all_sources: dict[int, list[tuple[int, Path]]],
    houses: tuple[int, ...],
) -> dict[int, list[tuple[int, Path]]]:
    selected = {house: all_sources[house] for house in houses}
    if set(selected) != set(houses):
        raise ValueError(f"protocol house set must be exactly {set(houses)}")
    return selected


def maximum_constant_run(values: np.ndarray) -> int:
    if len(values) == 0:
        return 0
    change_points = np.flatnonzero(values[1:] != values[:-1]) + 1
    run_boundaries = np.concatenate(([0], change_points, [len(values)]))
    return int(np.diff(run_boundaries).max())


def check_main(
    frame: pd.DataFrame,
    segment_id: str,
    constant_run_warning: int,
) -> dict[str, float | int]:
    if "main" not in frame.columns:
        raise ValueError(f"{segment_id}: missing main column")

    numeric_main = pd.to_numeric(frame["main"], errors="coerce")
    invalid_text = frame["main"].notna() & numeric_main.isna()
    if invalid_text.any():
        raise ValueError(f"{segment_id}: main contains non-numeric values")

    main = numeric_main.to_numpy(dtype=np.float64)
    if np.isinf(main).any():
        raise ValueError(f"{segment_id}: main contains infinite values")

    finite_main = main[np.isfinite(main)]
    if len(finite_main) == 0:
        raise ValueError(f"{segment_id}: main has no finite values")
    if np.any(finite_main < 0):
        raise ValueError(f"{segment_id}: main contains negative values")

    missing_values = int(np.isnan(main).sum())
    if missing_values:
        warnings.warn(
            f"{segment_id}: main has {missing_values} missing values; "
            "they are preserved as continuity breaks",
            stacklevel=2,
        )

    unique_values = int(np.unique(finite_main).size)
    if unique_values == 1:
        raise ValueError(f"{segment_id}: main is constant for the complete segment")

    longest_run = maximum_constant_run(main)
    if longest_run >= constant_run_warning:
        warnings.warn(
            f"{segment_id}: main has a constant run of {longest_run} rows",
            stacklevel=2,
        )

    return {
        "minimum": float(finite_main.min()),
        "maximum": float(finite_main.max()),
        "missing_values": missing_values,
        "unique_values": unique_values,
        "maximum_constant_run_rows": longest_run,
    }


def read_segment(
    path: Path,
    house: int,
    segment_number: int,
    constant_run_warning: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = pd.read_csv(path)
    segment_id = path.stem
    row_count = len(frame)
    if row_count == 0:
        raise ValueError(f"{segment_id}: empty segment")
    if "Unnamed: 0" not in frame.columns:
        raise ValueError(f"{segment_id}: missing Unnamed: 0 consistency column")

    source_rows = pd.to_numeric(frame["Unnamed: 0"], errors="coerce").to_numpy()
    expected_rows = np.arange(row_count)
    if not np.array_equal(source_rows, expected_rows):
        raise ValueError(f"{segment_id}: Unnamed: 0 must equal 0..N-1")

    frame = frame.drop(columns=["Unnamed: 0"])
    main_summary = check_main(frame, segment_id, constant_run_warning)
    frame.insert(0, "row_in_segment", expected_rows)
    frame.insert(0, "segment_id", segment_id)
    frame.insert(0, "house", house)

    source_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    summary: dict[str, object] = {
        "segment_id": segment_id,
        "segment_number": segment_number,
        "source_file": path.name,
        "source_sha256": source_sha256,
        "rows": row_count,
        "main": main_summary,
    }
    return frame, summary


def label_protocol_r_segment(
    frame: pd.DataFrame,
    summary: dict[str, object],
    min_block_rows: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    row_count = len(frame)
    boundaries = calculate_block_boundaries(row_count)
    validate_block_boundaries(boundaries, row_count)

    labels = np.empty(row_count, dtype=object)
    blocks: list[dict[str, int | str]] = []
    for block_name, (start, end) in zip(BLOCK_NAMES, boundaries):
        labels[start:end] = block_name
        block_rows = end - start
        if block_rows < min_block_rows:
            warnings.warn(
                f"{summary['segment_id']} {block_name} has only "
                f"{block_rows} rows",
                stacklevel=2,
            )
        blocks.append(
            {
                "block": block_name,
                "row_start_inclusive": start,
                "row_end_exclusive": end,
                "rows": block_rows,
            }
        )

    labelled = frame.copy()
    labelled.insert(3, "block", labels)
    summary["blocks"] = blocks
    return labelled, summary


def label_protocol_x_segment(
    frame: pd.DataFrame,
    summary: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, object]]:
    labelled = frame.copy()
    labelled.insert(3, "block", "PX")
    summary["blocks"] = [
        {
            "block": "PX",
            "row_start_inclusive": 0,
            "row_end_exclusive": len(frame),
            "rows": len(frame),
        }
    ]
    return labelled, summary


def combine_protocol_r_segments(frames: list[pd.DataFrame]) -> pd.DataFrame:
    # 同编号 block 物理合并；segment_id 明确保留文件边界。
    parts = [
        frame.loc[frame["block"] == block]
        for block in BLOCK_NAMES
        for frame in frames
    ]
    return pd.concat(parts, ignore_index=True)


def write_csv(frame: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    frame.to_csv(temporary_path, index=False)
    if output_path.exists():
        print(f"  overwrite {output_path}")
    os.replace(temporary_path, output_path)


def process_protocol_r(
    sources: dict[int, list[tuple[int, Path]]],
    output_dir: Path,
    min_block_rows: int,
    constant_run_warning: int,
) -> dict[str, object]:
    houses: dict[str, object] = {}
    expected_outputs: set[Path] = set()

    for house, house_sources in sources.items():
        frames: list[pd.DataFrame] = []
        segment_summaries: list[dict[str, object]] = []
        for segment_number, path in house_sources:
            frame, summary = read_segment(
                path, house, segment_number, constant_run_warning
            )
            frame, summary = label_protocol_r_segment(
                frame, summary, min_block_rows
            )
            frames.append(frame)
            segment_summaries.append(summary)

        combined = combine_protocol_r_segments(frames)
        output_path = output_dir / f"house_{house}.csv"
        write_csv(combined, output_path)
        expected_outputs.add(output_path)
        houses[f"H{house}"] = {
            "segments": len(segment_summaries),
            "rows": len(combined),
            "output_file": output_path.name,
            "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
            "segment_details": segment_summaries,
        }

    remove_stale_csv_outputs(output_dir, expected_outputs)
    return houses


def process_protocol_x(
    sources: dict[int, list[tuple[int, Path]]],
    output_dir: Path,
    constant_run_warning: int,
) -> dict[str, object]:
    houses: dict[str, object] = {}
    expected_outputs: set[Path] = set()

    for house, house_sources in sources.items():
        frames: list[pd.DataFrame] = []
        segment_summaries: list[dict[str, object]] = []
        for segment_number, path in house_sources:
            frame, summary = read_segment(
                path, house, segment_number, constant_run_warning
            )
            frame, summary = label_protocol_x_segment(frame, summary)
            frames.append(frame)
            segment_summaries.append(summary)

        combined = pd.concat(frames, ignore_index=True)
        output_path = output_dir / f"house_{house}.csv"
        write_csv(combined, output_path)
        expected_outputs.add(output_path)
        houses[f"H{house}"] = {
            "segments": len(segment_summaries),
            "rows": len(combined),
            "output_file": output_path.name,
            "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
            "segment_details": segment_summaries,
        }

    remove_stale_csv_outputs(output_dir, expected_outputs)
    return houses


def remove_stale_csv_outputs(output_dir: Path, expected_outputs: set[Path]) -> None:
    for path in output_dir.glob("*.csv"):
        if path not in expected_outputs:
            print(f"  remove stale output {path}")
            path.unlink()


def write_manifest(manifest: dict[str, object], output_path: Path) -> None:
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if output_path.exists():
        print(f"  overwrite {output_path}")
    os.replace(temporary_path, output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split prepared REDD CSV segments into protocol data tables."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--min-block-rows", type=int, default=30)
    parser.add_argument("--constant-run-warning", type=int, default=100)
    parser.add_argument("--redd-commit", default=REDD_SUBMODULE_COMMIT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_dir = args.input_dir.resolve()
    output_root = args.output_root.resolve()

    if args.min_block_rows <= 0 or args.constant_run_warning <= 0:
        raise ValueError("warning thresholds must be positive")
    if re.fullmatch(r"[0-9a-f]{40}", args.redd_commit) is None:
        raise ValueError("--redd-commit must be a 40-character lowercase Git SHA")

    all_sources = discover_source_files(input_dir)

    # 两个 protocol 从入口开始分流；Protocol X 不经过 Protocol R block 逻辑。
    protocol_r_sources = select_protocol_sources(all_sources, PROTOCOL_R_HOUSES)
    protocol_x_sources = select_protocol_sources(all_sources, PROTOCOL_X_HOUSES)

    print("Discovered REDD source segments:")
    for house in sorted(all_sources):
        print(f"  H{house}: {len(all_sources[house])} files")

    protocol_r_dir = output_root / "protocol_r"
    protocol_x_dir = output_root / "protocol_x"
    protocol_r = process_protocol_r(
        protocol_r_sources,
        protocol_r_dir,
        args.min_block_rows,
        args.constant_run_warning,
    )
    protocol_x = process_protocol_x(
        protocol_x_sources,
        protocol_x_dir,
        args.constant_run_warning,
    )

    manifest: dict[str, object] = {
        "schema_version": "1.0",
        "generator": "split_redd_blocks.py",
        "source": {
            "dataset": "preprocessed REDD from wuhanstudio/redd",
            "redd_submodule_commit": args.redd_commit,
            "input_directory": "data/redd",
            "segment_definition": "one source CSV file",
            "cross_file_continuity_assumed": False,
            "unnamed_index_use": "validated as 0..N-1 then removed",
        },
        "split_rule": {
            "protocol_r_houses": list(PROTOCOL_R_HOUSES),
            "protocol_x_houses": list(PROTOCOL_X_HOUSES),
            "protocol_r_blocks": list(BLOCK_NAMES),
            "protocol_r_boundary_formula": "floor(n*k/5), k=0..5",
            "protocol_x_block": "PX",
            "randomness": "none",
        },
        "sanity_checks": {
            "minimum_block_rows_warning": args.min_block_rows,
            "constant_main_run_warning_rows": args.constant_run_warning,
            "main_must_be_finite_and_nonnegative": True,
        },
        "protocol_r": {"output_directory": "data/protocol_r", "houses": protocol_r},
        "protocol_x": {
            "output_directory": "data/protocol_x",
            "development_split_created": False,
            "houses": protocol_x,
        },
    }
    write_manifest(manifest, output_root / "split_manifest.json")

    print("Completed:")
    print(f"  Protocol R houses: {', '.join(protocol_r)}")
    print(f"  Protocol X houses: {', '.join(protocol_x)}")
    print(f"  Manifest: {output_root / 'split_manifest.json'}")


if __name__ == "__main__":
    main()
