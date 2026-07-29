import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from split_redd_blocks import (  # noqa: E402
    BLOCK_NAMES,
    assert_combined_shape,
    calculate_block_boundaries,
    discover_source_files,
    label_protocol_r_segment,
    label_protocol_x_segment,
    read_segment,
    validate_block_boundaries,
    validate_house_segment_columns,
)


class BlockBoundaryTests(unittest.TestCase):
    def test_frozen_floor_boundaries_are_exact(self):
        self.assertEqual(
            calculate_block_boundaries(12),
            [(0, 2), (2, 4), (4, 7), (7, 9), (9, 12)],
        )

    def test_boundaries_are_contiguous_and_cover_each_segment(self):
        for row_count in range(1, 101):
            boundaries = calculate_block_boundaries(row_count)
            validate_block_boundaries(boundaries, row_count)

            covered_rows = [
                row
                for start, end in boundaries
                for row in range(start, end)
            ]
            self.assertEqual(covered_rows, list(range(row_count)))


class SourceDiscoveryTests(unittest.TestCase):
    def make_complete_layout(self, root: Path):
        for house in range(1, 7):
            (root / f"redd_house{house}_0.csv").touch()

    def test_actual_file_counts_are_discovered_without_hardcoding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_layout(root)
            (root / "redd_house1_1.csv").touch()

            sources = discover_source_files(root)

            self.assertEqual(len(sources[1]), 2)
            self.assertEqual(len(sources[2]), 1)

    def test_missing_or_unexpected_house_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_layout(root)
            (root / "redd_house6_0.csv").unlink()
            (root / "redd_house7_0.csv").touch()

            with self.assertRaisesRegex(ValueError, "source houses"):
                discover_source_files(root)

    def test_missing_segment_number_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_complete_layout(root)
            (root / "redd_house1_2.csv").touch()

            with self.assertRaisesRegex(ValueError, "contiguous from 0"):
                discover_source_files(root)


class SegmentLabellingTests(unittest.TestCase):
    def write_segment(self, path: Path, main):
        pd.DataFrame(
            {
                "Unnamed: 0": np.arange(len(main)),
                "fridge": np.zeros(len(main)),
                "main": main,
            }
        ).to_csv(path, index=False)

    def test_protocol_r_drops_source_index_and_labels_every_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "redd_house1_0.csv"
            self.write_segment(path, np.arange(12, dtype=float) + 10)

            frame, summary = read_segment(path, 1, 0, constant_run_warning=100)
            labelled, summary = label_protocol_r_segment(
                frame, summary, min_block_rows=1
            )

            self.assertNotIn("Unnamed: 0", labelled.columns)
            self.assertEqual(
                labelled.columns[:4].tolist(),
                ["house", "segment_id", "row_in_segment", "block"],
            )
            self.assertEqual(
                labelled["block"].value_counts(sort=False).to_dict(),
                dict(zip(BLOCK_NAMES, [2, 2, 3, 2, 3])),
            )
            self.assertEqual(
                sum(block["rows"] for block in summary["blocks"]), 12
            )

    def test_protocol_x_uses_only_px(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "redd_house2_0.csv"
            self.write_segment(path, np.arange(10, dtype=float) + 10)

            frame, summary = read_segment(path, 2, 0, constant_run_warning=100)
            labelled, summary = label_protocol_x_segment(frame, summary)

            self.assertEqual(set(labelled["block"]), {"PX"})
            self.assertEqual(summary["blocks"][0]["rows"], 10)

    def test_missing_main_is_preserved_as_a_continuity_break(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "redd_house1_0.csv"
            self.write_segment(path, [np.nan, 10.0, 11.0])

            with self.assertWarnsRegex(UserWarning, "continuity breaks"):
                frame, summary = read_segment(
                    path, 1, 0, constant_run_warning=100
                )

            self.assertTrue(pd.isna(frame.loc[0, "main"]))
            self.assertEqual(summary["main"]["missing_values"], 1)

    def test_manifest_summary_includes_columns_and_appliance_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "redd_house1_0.csv"
            pd.DataFrame(
                {
                    "Unnamed: 0": np.arange(4),
                    "fridge": [0.0, 10.0, 20.0, np.nan],
                    "microwave": [0.0, 0.0, 30.0, 0.0],
                    "main": [100.0, 110.0, 150.0, 105.0],
                }
            ).to_csv(path, index=False)

            _, summary = read_segment(
                path, 1, 0, constant_run_warning=100
            )

            self.assertEqual(
                summary["columns"], ["fridge", "microwave", "main"]
            )
            fridge = summary["appliances"]["fridge"]
            self.assertEqual(fridge["minimum"], 0.0)
            self.assertEqual(fridge["maximum"], 20.0)
            self.assertEqual(fridge["missing_rows"], 1)
            self.assertEqual(fridge["nonzero_row_fraction"], 0.5)
            self.assertEqual(
                fridge["above_active_threshold_row_fraction"], 0.25
            )

    def test_index_and_main_sanity_checks_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad_index = root / "redd_house1_0.csv"
            self.write_segment(bad_index, [10.0, 11.0, 12.0])
            frame = pd.read_csv(bad_index)
            frame.loc[2, "Unnamed: 0"] = 4
            frame.to_csv(bad_index, index=False)

            with self.assertRaisesRegex(ValueError, "must equal 0..N-1"):
                read_segment(bad_index, 1, 0, constant_run_warning=100)

            negative_main = root / "redd_house1_1.csv"
            self.write_segment(negative_main, [10.0, -1.0, 12.0])
            with self.assertRaisesRegex(ValueError, "negative"):
                read_segment(negative_main, 1, 1, constant_run_warning=100)

            constant_main = root / "redd_house1_2.csv"
            self.write_segment(constant_main, [10.0, 10.0, 10.0])
            with self.assertRaisesRegex(ValueError, "constant"):
                read_segment(constant_main, 1, 2, constant_run_warning=100)


class HouseSchemaAndConcatTests(unittest.TestCase):
    def test_same_house_column_set_mismatch_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "H1 segment columns differ"
        ):
            validate_house_segment_columns(
                1,
                ["fridge", "microwave", "main"],
                ["fridge", "main"],
                "redd_house1_7",
            )

    def test_same_column_set_in_a_different_order_is_allowed(self):
        validate_house_segment_columns(
            1,
            ["fridge", "microwave", "main"],
            ["main", "fridge", "microwave"],
            "redd_house1_7",
        )

    def test_concat_shape_assertion_rejects_silent_column_expansion(self):
        first = pd.DataFrame(
            {
                "house": [1],
                "segment_id": ["redd_house1_0"],
                "row_in_segment": [0],
                "block": ["B1"],
                "main": [100.0],
            }
        )
        second = first.assign(fridge=20.0)
        silently_expanded = pd.concat([first, second], ignore_index=True)

        with self.assertRaisesRegex(
            AssertionError, "concat shape changed"
        ):
            assert_combined_shape([first, second], silently_expanded, house=1)


if __name__ == "__main__":
    unittest.main()
