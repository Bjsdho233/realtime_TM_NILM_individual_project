import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).parents[2]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


freeze = load_module(
    "freeze_protocol_r_evaluation",
    "tools/data/freeze_protocol_r_evaluation.py",
)
access = load_module("protocol_r_access", "tools/data/protocol_r_access.py")

MANIFEST_PATH = ROOT / "artifacts/manifests/protocol_r_evaluation_v1.json"
MANIFEST_HASH_PATH = ROOT / "artifacts/manifests/protocol_r_evaluation_v1.sha256"
PROTOCOL_R_AUDIT_PATH = (
    ROOT / "artifacts/manifests/protocol_r_support_audit_v1.json"
)
PROTOCOL_X_AUDIT_PATH = (
    ROOT / "artifacts/manifests/protocol_x_support_audit_v1.json"
)
ELIGIBILITY_PATH = (
    ROOT / "artifacts/manifests/protocol_r_class_eligibility_v1.json"
)
ELIGIBILITY_HASH_PATH = (
    ROOT / "artifacts/manifests/protocol_r_class_eligibility_v1.sha256"
)
CORE_SHA256 = "501fbfe1193154a471a932a4f1237ced4a7df9a7ce175fe8a621f1da6d433ae5"
PROTOCOL_R_AUDIT_SHA256 = (
    "c7fde29e9570417d12463e16f64ebf4eb1cb4736b775fc6fb2116e06fb68eed3"
)
PROTOCOL_X_AUDIT_SHA256 = (
    "ebeaffb4807d830cc47c48c9f67fc82827795bbcbaaf1e1d72ccef2bcdc4f163"
)
ELIGIBILITY_SHA256 = (
    "3a8e58db1551d5a24899b47f33701bfc8fe46c2ee6a26b3eb001bed7c04876de"
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class FrozenManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_json(MANIFEST_PATH)

    def test_exact_core_manifest_sha256_and_sidecar(self):
        digest = hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, CORE_SHA256)
        self.assertEqual(
            MANIFEST_HASH_PATH.read_text(encoding="ascii"),
            f"{CORE_SHA256}  artifacts/manifests/protocol_r_evaluation_v1.json\n",
        )

    def test_generator_reconstructs_byte_identical_core_manifest(self):
        sources = [
            {
                key: source[key]
                for key in (
                    "relative_path",
                    "sha256",
                    "segment_id",
                    "house",
                    "chunk",
                    "row_count",
                )
            }
            for source in self.manifest["source_files"]
        ]
        rebuilt = freeze.build_manifest(
            sources,
            self.manifest["house_channel_mapping"],
        )
        self.assertEqual(freeze.json_bytes(rebuilt), MANIFEST_PATH.read_bytes())

    def test_five_blocks_are_formula_exact_contiguous_and_complete(self):
        for source in self.manifest["source_files"]:
            if source["protocol_role"] != "protocol_r_population":
                self.assertEqual(source["blocks"], [])
                continue
            blocks = source["blocks"]
            expected = freeze.five_block_ranges(source["row_count"])
            actual = [
                (block["row_start_inclusive"], block["row_end_exclusive"])
                for block in blocks
            ]
            self.assertEqual(actual, expected)
            self.assertEqual(actual[0][0], 0)
            self.assertEqual(actual[-1][1], source["row_count"])
            self.assertTrue(
                all(left[1] == right[0] for left, right in zip(actual, actual[1:]))
            )

    def test_every_valid_window_is_contained_in_its_segment_and_block(self):
        for source in self.manifest["source_files"]:
            if source["protocol_role"] != "protocol_r_population":
                continue
            for block in source["blocks"]:
                valid = block["valid_target_range"]
                self.assertGreaterEqual(
                    valid["row_start_inclusive"] - 255,
                    block["row_start_inclusive"],
                )
                if valid["target_count"]:
                    last_target = valid["row_end_exclusive"] - 1
                    self.assertLess(
                        last_target + 8,
                        block["row_end_exclusive"],
                    )
                self.assertLessEqual(
                    block["row_end_exclusive"],
                    source["row_count"],
                )

    def test_manifest_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            manifest_path = root / access.MANIFEST_RELATIVE_PATH
            hash_path = root / access.HASH_RELATIVE_PATH
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_bytes(MANIFEST_PATH.read_bytes() + b" ")
            hash_path.write_text(
                f"{CORE_SHA256}  {access.MANIFEST_RELATIVE_PATH.as_posix()}\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                access.ProtocolRManifestError,
                "byte hash",
            ):
                access.development_slices(
                    root,
                    validation_fold=1,
                    role="training",
                )


class DevelopmentAccessTests(unittest.TestCase):
    def test_each_fold_admits_only_b1_through_b4(self):
        for fold in range(1, 5):
            training = access.development_slices(
                ROOT,
                validation_fold=fold,
                role="training",
            )
            validation = access.development_slices(
                ROOT,
                validation_fold=fold,
                role="validation",
            )
            self.assertEqual(len(training), 66)
            self.assertEqual(len(validation), 22)
            self.assertNotIn("B5", {item.block_id for item in training})
            self.assertNotIn("B5", {item.block_id for item in validation})
            self.assertEqual(
                {item.block_id for item in validation},
                {f"B{fold}"},
            )
            self.assertEqual(
                {item.house for item in training + validation},
                {1, 3, 5, 6},
            )

    def test_b5_and_locked_role_aliases_are_rejected(self):
        for role in ("B5", "locked_test", "test", "candidate_test"):
            with self.subTest(role=role):
                with self.assertRaises(access.ProtocolRAccessDenied):
                    access.development_slices(
                        ROOT,
                        validation_fold=1,
                        role=role,
                    )

    def test_protocol_x_role_and_houses_are_rejected(self):
        with self.assertRaises(access.ProtocolRAccessDenied):
            access.development_slices(
                ROOT,
                validation_fold=1,
                role="protocol_x",
            )
        for houses in ((2,), (4,), (1, 2)):
            with self.subTest(houses=houses):
                with self.assertRaises(access.ProtocolRAccessDenied):
                    access.development_slices(
                        ROOT,
                        validation_fold=1,
                        role="training",
                        houses=houses,
                    )


class SupportOnlyAuditTests(unittest.TestCase):
    def test_frozen_audit_hashes_match(self):
        self.assertEqual(
            hashlib.sha256(PROTOCOL_R_AUDIT_PATH.read_bytes()).hexdigest(),
            PROTOCOL_R_AUDIT_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(PROTOCOL_X_AUDIT_PATH.read_bytes()).hexdigest(),
            PROTOCOL_X_AUDIT_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(ELIGIBILITY_PATH.read_bytes()).hexdigest(),
            ELIGIBILITY_SHA256,
        )
        self.assertEqual(
            ELIGIBILITY_HASH_PATH.read_text(encoding="ascii"),
            f"{ELIGIBILITY_SHA256}  artifacts/manifests/protocol_r_class_eligibility_v1.json\n",
        )

    def test_support_audits_expose_only_aggregate_records(self):
        prohibited = {
            "target_rows",
            "target_values",
            "samples",
            "time_series",
            "predictions",
            "model_metrics",
        }
        allowed_support = {
            "finite_valid_targets",
            "missing_valid_targets",
            "on_valid_target_samples",
            "on_valid_target_duration_seconds",
            "complete_episodes",
            "dependency_contained_complete_episodes",
            "left_censored_runs",
            "right_censored_runs",
        }
        for path in (PROTOCOL_R_AUDIT_PATH, PROTOCOL_X_AUDIT_PATH):
            audit = load_json(path)
            self.assertIn("aggregate", audit["rules"]["output_boundary"])
            for record in audit["records"]:
                self.assertTrue(prohibited.isdisjoint(record))
                if record["support"] is not None:
                    self.assertEqual(set(record["support"]), allowed_support)

    def test_protocol_x_population_is_fixed_and_has_no_development_split(self):
        audit = load_json(PROTOCOL_X_AUDIT_PATH)
        population = audit["population"]
        self.assertEqual(population["houses"], ["H2", "H4"])
        self.assertTrue(population["composite_population_fixed"])
        self.assertFalse(
            population["house_deletion_exchange_or_selection_allowed"]
        )
        self.assertFalse(population["development_split_created"])
        self.assertEqual(
            {record["block_id"] for record in audit["records"]},
            {"PX"},
        )

    def test_protocol_x_dish_washer_support_is_per_house_and_pooled(self):
        summary = load_json(PROTOCOL_X_AUDIT_PATH)["summary"]
        h2 = summary["per_house"]["H2"]["dish washer"]
        h4 = summary["per_house"]["H4"]["dish washer"]
        pooled = summary["pooled_h2_h4"]["dish washer"]
        self.assertEqual(
            (
                h2["dependency_contained_complete_episodes"],
                h2["on_valid_target_duration_seconds"],
            ),
            (47, 13752),
        )
        self.assertEqual(
            (
                h4["dependency_contained_complete_episodes"],
                h4["on_valid_target_duration_seconds"],
            ),
            (11, 4419),
        )
        self.assertEqual(
            (
                pooled["dependency_contained_complete_episodes"],
                pooled["on_valid_target_duration_seconds"],
            ),
            (58, 18171),
        )
        self.assertTrue(
            summary["eligibility"]["dish washer"][
                "future_locked_confirmatory_evaluation_eligible"
            ]
        )

    def test_class_eligibility_matches_the_formal_decision(self):
        eligibility = load_json(ELIGIBILITY_PATH)["appliances"]
        self.assertEqual(
            eligibility["fridge"]["protocol_r_v1_status"],
            "full_eligible",
        )
        self.assertEqual(
            eligibility["microwave"]["protocol_r_v1_status"],
            "full_eligible",
        )
        self.assertEqual(
            eligibility["dish washer"]["protocol_r_v1_status"],
            "development_only",
        )
        self.assertFalse(
            eligibility["dish washer"]["protocol_r_b5"][
                "evaluation_eligible"
            ]
        )
        self.assertEqual(
            eligibility["washer dryer"]["protocol_r_v1_status"],
            "support_ineligible",
        )
        self.assertFalse(
            eligibility["washer dryer"]["future_e003_e004_development_scope"]
        )
        self.assertEqual(
            eligibility["dish washer"]["protocol_x"]["status"],
            "future_locked_confirmatory_evaluation_eligible",
        )


if __name__ == "__main__":
    unittest.main()
