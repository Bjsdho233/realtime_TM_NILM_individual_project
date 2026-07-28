import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repo_governance as governance
import scaffold_e_series


def init_git_repo(root):
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "Repository Test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "core.autocrlf", "false"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "core.eol", "lf"],
        check=True,
    )


def write_utf8_lf(path, content):
    path.write_bytes(content.encode("utf-8"))


def registered_current_state():
    return (
        "# Current State\n\n"
        "## Active E-series Registry\n\n"
        "| ID | Direct name | Owner | Status | Mutable root | "
        "Design SHA-256 | Design commit |\n"
        "|---|---|---|---|---|---|---|\n"
        "| E002 | Alignment Diagnostic | Tianhang Tan | registered | "
        "experiments/E002-alignment-diagnostic/ | Pending | Pending |\n"
    )


def work_index():
    return (
        "# Work Index\n\n"
        "## E-series\n\n"
        "| ID and direct name | Layer | Status | Outcome / evidence |\n"
        "|---|---|---|---|\n"
        "| E002 — Alignment Diagnostic | L2 | Planned | None |\n"
    )


class MarkdownLinkTests(unittest.TestCase):
    def test_relative_link_is_resolved_from_source_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "docs").mkdir()
            (root / "target.txt").write_text("target\n", encoding="utf-8")
            (root / "docs" / "note.md").write_text(
                "[target](../target.txt)\n", encoding="utf-8"
            )
            result = governance.validate_markdown_links(
                root, [pathlib.Path("docs/note.md")]
            )
        self.assertEqual(result.name, "Markdown links")

    def test_missing_relative_link_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "note.md").write_text("[missing](absent.md)\n", encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                governance.validate_markdown_links(root, [pathlib.Path("note.md")])


class TextHygieneTests(unittest.TestCase):
    def test_hash_pinned_legacy_file_may_omit_final_newline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            relative = pathlib.Path("experiments/E002-test/legacy.json")
            path = root / relative
            path.parent.mkdir(parents=True)
            content = b'{"legacy": true}'
            path.write_bytes(content)
            expected = hashlib.sha256(content).hexdigest()
            with mock.patch.dict(
                governance.LEGACY_MISSING_FINAL_NEWLINE_SHA256,
                {relative.as_posix(): expected},
                clear=True,
            ):
                result = governance.validate_text_hygiene(root, [relative])
        self.assertEqual(result.name, "Text hygiene")

    def test_unpinned_file_without_final_newline_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            relative = pathlib.Path("result.json")
            (root / relative).write_text("{}", encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                governance.validate_text_hygiene(root, [relative])


class ArchiveSafetyTests(unittest.TestCase):
    def test_model_binary_is_not_an_admitted_script(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            with self.assertRaises(governance.GovernanceError):
                governance._validate_archive_path(
                    directory, pathlib.PurePosixPath("scripts/model.pkl")
                )

    def test_prediction_table_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "predictions.csv"
            path.write_text("class,f1\nfridge,0.9\n", encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path)

    def test_row_level_columns_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "metrics_summary.csv"
            path.write_text(
                "metric,value,truth,guess,target,label\n"
                "macro_f1,0.9,a,b,c,d\n",
                encoding="utf-8",
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path)

    def test_aggregate_summary_is_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "per_class.csv"
            path.write_text(
                "class,precision,recall,f1,support\nfridge,0.9,0.8,0.85,10\n",
                encoding="utf-8",
            )
            governance._validate_aggregate_table(path)

    def test_tables_json_is_never_admitted(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            with self.assertRaises(governance.GovernanceError):
                governance._validate_archive_path(
                    directory, pathlib.PurePosixPath("tables/metrics.json")
                )

    def test_pico_source_and_build_files_are_admitted(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            for relative in (
                "scripts/probe.cpp",
                "scripts/probe.hpp",
                "scripts/CMakeLists.txt",
            ):
                governance._validate_archive_path(
                    directory, pathlib.PurePosixPath(relative)
                )

    def test_ragged_csv_cannot_hide_row_level_cells(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "run_summary.csv"
            path.write_text(
                "metric,value\nmacro_f1,0.9,truth,prediction\n",
                encoding="utf-8",
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path)

    def test_predeclared_diagnostic_table_is_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "bit_parity.csv"
            path.write_text(
                "bit_position,parity_equal\n0,true\n1,false\n",
                encoding="utf-8",
            )
            design = {
                "output_contract": {
                    "aggregate_tables": [
                        {
                            "path": "tables/bit_parity.csv",
                            "columns": ["bit_position", "parity_equal"],
                            "max_rows": 8,
                            "purpose": "Record aggregate parity by bit position.",
                            "aggregation_unit": "One row per bit position.",
                        }
                    ]
                }
            }
            governance._validate_aggregate_table(path, design)

    def test_prediction_alias_is_rejected_even_when_predeclared(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "capability.csv"
            path.write_text(
                "capability,predictions_alias\ncompile,yes\n", encoding="utf-8"
            )
            design = {
                "output_contract": {
                    "aggregate_tables": [
                        {
                            "path": "tables/capability.csv",
                            "columns": ["capability", "predictions_alias"],
                            "max_rows": 8,
                            "purpose": "Capability matrix.",
                            "aggregation_unit": "One row per capability.",
                        }
                    ]
                }
            }
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path, design)

    def test_predeclared_aggregate_target_counts_are_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "episode_counts.csv"
            path.write_text(
                "fold,matched_target_episode_count,"
                "unmatched_target_episode_count,target_diagnostics_json\n"
                'F1,10,2,"{""incomplete"":1}"\n',
                encoding="utf-8",
            )
            design = {
                "output_contract": {
                    "aggregate_tables": [
                        {
                            "path": "tables/episode_counts.csv",
                            "columns": [
                                "fold",
                                "matched_target_episode_count",
                                "unmatched_target_episode_count",
                                "target_diagnostics_json",
                            ],
                            "max_rows": 4,
                        }
                    ]
                }
            }
            governance._validate_aggregate_table(path, design)

    def test_boolean_flags_and_non_applicable_cost_bytes_are_typed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "costs.csv"
            path.write_text(
                "scope,precision_zero_denominator,"
                "serialized_inference_bytes,shared_encoder_bytes,"
                "complete_bundle_bytes\n"
                "algorithmic_waiting,False,,,\n",
                encoding="utf-8",
            )
            design = {
                "output_contract": {
                    "aggregate_tables": [
                        {
                            "path": "tables/costs.csv",
                            "columns": [
                                "scope",
                                "precision_zero_denominator",
                                "serialized_inference_bytes",
                                "shared_encoder_bytes",
                                "complete_bundle_bytes",
                            ],
                            "max_rows": 4,
                        }
                    ]
                }
            }
            governance._validate_aggregate_table(path, design)
            path.write_text(
                "scope,precision_zero_denominator,"
                "serialized_inference_bytes,shared_encoder_bytes,"
                "complete_bundle_bytes\n"
                "algorithmic_waiting,not-a-boolean,,,\n",
                encoding="utf-8",
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path, design)

    def test_undeclared_table_does_not_fallback_to_builtin_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "run_summary.csv"
            path.write_text("metric,value\nmacro_f1,0.9\n", encoding="utf-8")
            design = {"output_contract": {"aggregate_tables": []}}
            with self.assertRaises(governance.GovernanceError):
                governance._validate_aggregate_table(path, design)

    def test_t_series_result_archive_uses_frozen_manifest_validator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            archive = (
                root
                / "experiments"
                / "T005-protocol-r-baseline-implementation"
            )
            archive.mkdir(parents=True)
            write_utf8_lf(archive / "result.json", "{}\n")
            schema_directory = root / "schemas"
            schema_directory.mkdir()
            write_utf8_lf(
                schema_directory / "legacy-archive-checksums.json",
                '{"archives": {}}\n',
            )
            paths = [
                pathlib.Path(
                    "experiments/T005-protocol-r-baseline-implementation/result.json"
                )
            ]
            with mock.patch.object(
                governance, "_validate_t_series_archive"
            ) as validate_t_archive:
                result = governance.validate_experiment_archives(root, paths)
            validate_t_archive.assert_called_once_with(
                root, archive, {"result.json"}
            )
        self.assertEqual(result.name, "Experiment archives")


class ArchivePathBypassTests(unittest.TestCase):
    def assertForbiddenTrackablePath(self, relative):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            directory = root / "experiments" / "E002-path-probe"
            target = directory / relative
            target.parent.mkdir(parents=True)
            target.write_text("metric,value\nf1,0.9\n", encoding="utf-8")
            init_git_repo(root)
            subprocess.run(
                ["git", "-C", str(root), "add", "-f", target.relative_to(root)],
                check=True,
            )
            with self.assertRaises(governance.GovernanceError):
                governance._new_archive_files(root, directory)

    def test_nested_mutable_segment_cannot_hide_trackable_prediction(self):
        self.assertForbiddenTrackablePath("scripts/work/predictions.csv")

    def test_forced_tracked_root_output_is_rejected(self):
        self.assertForbiddenTrackablePath("outputs/metrics.csv")


class ContractReferenceTests(unittest.TestCase):
    def test_deprecated_result_location_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            note = root / "note.md"
            deprecated = "results/" + "result.json"
            note.write_text(f"Use `{deprecated}`.\n", encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                governance.validate_contract_references(
                    root, [pathlib.Path("note.md")]
                )


class SensitiveContentTests(unittest.TestCase):
    def make_root(self):
        temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(temporary.name)
        (root / "schemas").mkdir()
        (root / governance.SCAN_ALLOWLIST_PATH).write_text(
            '{"schema_version":"1.0","absolute_path_lines":[],"sensitive_lines":[]}\n',
            encoding="utf-8",
        )
        return temporary, root

    def test_vendor_prefixed_credentials_are_detected(self):
        for assignment in (
            "OPENAI_API_" + "KEY=sk-real",
            "GITHUB_TO" + "KEN=ghp_real",
            "AWS_ACCESS_KEY_" + "ID=AKIAREALVALUE",
            "pass" + "word=none-but-real-secret",
        ):
            with self.subTest(assignment=assignment):
                temporary, root = self.make_root()
                with temporary:
                    path = root / "config.txt"
                    path.write_text(assignment + "\n", encoding="utf-8")
                    with self.assertRaises(governance.GovernanceError):
                        governance.validate_sensitive_content(
                            root, [pathlib.Path("config.txt")]
                        )

    def test_exact_environment_placeholder_is_allowed(self):
        temporary, root = self.make_root()
        with temporary:
            path = root / "config.txt"
            path.write_text(
                "OPENAI_API_" + "KEY=${OPENAI_API_" + "KEY}\n",
                encoding="utf-8",
            )
            governance.validate_sensitive_content(
                root, [pathlib.Path("config.txt")]
            )

    def test_quoted_json_and_yaml_credentials_are_detected(self):
        for assignment in (
            '"OPENAI_API_' + 'KEY": "sk-live-real"',
            "'GITHUB_TO" + "KEN': 'ghp_real'",
        ):
            with self.subTest(assignment=assignment):
                temporary, root = self.make_root()
                with temporary:
                    path = root / "config.json"
                    path.write_text(assignment + "\n", encoding="utf-8")
                    with self.assertRaises(governance.GovernanceError):
                        governance.validate_sensitive_content(
                            root, [pathlib.Path("config.json")]
                        )

    def test_quoted_environment_placeholder_is_allowed(self):
        temporary, root = self.make_root()
        with temporary:
            path = root / "config.json"
            path.write_text(
                '"OPENAI_API_' + 'KEY": "${OPENAI_API_' + 'KEY}"\n',
                encoding="utf-8",
            )
            governance.validate_sensitive_content(
                root, [pathlib.Path("config.json")]
            )

    def test_nul_cannot_make_governed_text_skip_scanning(self):
        temporary, root = self.make_root()
        with temporary:
            path = root / "config.txt"
            path.write_bytes(b"\0OPENAI_API_" + b"KEY=sk-real\n")
            with self.assertRaises(governance.GovernanceError):
                governance.validate_sensitive_content(
                    root, [pathlib.Path("config.txt")]
                )


class DevelopmentDataManifestTests(unittest.TestCase):
    def make_root(self):
        temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(temporary.name)
        shutil.copytree(ROOT / "schemas", root / "schemas")
        (root / "manifests").mkdir()
        init_git_repo(root)
        subprocess.run(["git", "-C", str(root), "add", "schemas"], check=True)
        return temporary, root

    def manifest(self, role="development_train", fit_allowed=True):
        return {
            "$schema": "schemas/development-data-manifest.schema.json",
            "schema_version": "1.0",
            "manifest_id": "dev-fixture-v1",
            "name": "Development fixture",
            "created_at": "2026-07-23T12:00:00Z",
            "protocol_scope": "development_only",
            "sealed_test_access": False,
            "candidate_or_locked_test_data_included": False,
            "entries": [
                {
                    "id": "fixture",
                    "path_or_locator": "content-addressed:fixture",
                    "content_sha256": "1" * 64,
                    "role": role,
                    "fit_allowed": fit_allowed,
                }
            ],
        }

    def write_and_stage(self, root, name, content):
        path = root / "manifests" / name
        governance.write_json(path, content)
        subprocess.run(
            ["git", "-C", str(root), "add", path.relative_to(root)], check=True
        )
        return path.relative_to(root).as_posix()

    def test_valid_development_manifest_is_accepted(self):
        temporary, root = self.make_root()
        with temporary:
            relative = self.write_and_stage(root, "dev.json", self.manifest())
            manifest, digest = governance.validate_development_data_manifest(
                root, relative
            )
            self.assertEqual(manifest["manifest_id"], "dev-fixture-v1")
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_candidate_or_locked_role_is_rejected(self):
        temporary, root = self.make_root()
        with temporary:
            relative = self.write_and_stage(
                root,
                "candidate.json",
                self.manifest(role="sealed_candidate_test", fit_allowed=False),
            )
            with self.assertRaises(governance.GovernanceError):
                governance.validate_development_data_manifest(root, relative)

    def test_same_dataset_cannot_cross_roles_with_different_ids(self):
        temporary, root = self.make_root()
        with temporary:
            manifest = self.manifest()
            duplicate = dict(manifest["entries"][0])
            duplicate.update(
                {
                    "id": "fixture-validation",
                    "role": "development_validation",
                    "fit_allowed": False,
                }
            )
            manifest["entries"].append(duplicate)
            relative = self.write_and_stage(root, "duplicate-role.json", manifest)
            with self.assertRaises(governance.GovernanceError):
                governance.validate_development_data_manifest(root, relative)

    def test_same_dataset_cannot_cross_separate_manifests(self):
        train = self.manifest()
        validation = self.manifest(
            role="development_validation", fit_allowed=False
        )
        validation["manifest_id"] = "dev-fixture-validation-v1"
        with self.assertRaises(governance.GovernanceError):
            governance._validate_data_role_disjointness(
                [train, validation], "cross-manifest fixture"
            )

    def test_boolean_const_does_not_accept_integer_zero(self):
        manifest = self.manifest()
        manifest["sealed_test_access"] = 0
        schema = governance.load_json(
            ROOT / governance.DEVELOPMENT_DATA_SCHEMA_PATH
        )
        self.assertTrue(governance.schema_errors(manifest, schema))

    def test_arbitrary_json_cannot_be_used_as_data_manifest(self):
        temporary, root = self.make_root()
        with temporary:
            relative = self.write_and_stage(root, "arbitrary.json", {"safe": True})
            with self.assertRaises(governance.GovernanceError):
                governance.validate_development_data_manifest(root, relative)

    def test_crlf_manifest_is_rejected_before_hash(self):
        temporary, root = self.make_root()
        with temporary:
            path = root / "manifests" / "crlf.json"
            path.write_bytes(b'{"safe": true}\r\n')
            subprocess.run(
                ["git", "-C", str(root), "add", path.relative_to(root)], check=True
            )
            with self.assertRaises(governance.GovernanceError):
                governance.canonical_file_sha256(
                    root, path.relative_to(root), "CRLF fixture"
                )

    def test_external_artifact_uses_tracked_manifest_not_local_entity(self):
        temporary, root = self.make_root()
        with temporary:
            data_relative = self.write_and_stage(root, "dev.json", self.manifest())
            data_hash = governance.canonical_file_sha256(
                root, data_relative, "data manifest"
            )
            artifact = {
                "$schema": "schemas/learned-artifact-manifest.schema.json",
                "schema_version": "1.0",
                "manifest_id": "model-lineage-v1",
                "artifact_id": "model-v1",
                "artifact_type": "model",
                "content_sha256": "2" * 64,
                "locator": {
                    "kind": "documented_local_store",
                    "value": "model-store:model-v1",
                },
                "origin": {
                    "source_work": "E001",
                    "repository": "fixture/repository",
                    "git_commit": "1" * 40,
                    "context": "Test-only learned artefact.",
                },
                "availability_limits": {
                    "available_in_fresh_clone": False,
                    "requires_local_store": True,
                    "retention": "Available only for this test fixture.",
                },
                "fit_data_roles": ["development_train"],
                "data_manifest": {"path": data_relative, "sha256": data_hash},
                "candidate_or_locked_test_derived": False,
            }
            artifact_relative = self.write_and_stage(
                root, "artifact.json", artifact
            )
            parsed, _ = governance.validate_learned_artifact_manifest(
                root, artifact_relative
            )
            self.assertEqual(parsed["artifact_id"], "model-v1")


class RegistrationTests(unittest.TestCase):
    def make_root(self, registry_rows="", prefix=""):
        temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(temporary.name)
        (root / "docs").mkdir()
        (root / "docs" / "WORK_INDEX.md").write_text(
            "# Work Index\n\n"
            "## E-series\n\n"
            "| ID and direct name | Layer | Status | Outcome / evidence |\n"
            "|---|---|---|---|\n"
            "| E002 — Alignment Diagnostic | L2 | Planned | None |\n",
            encoding="utf-8",
        )
        (root / "docs" / "CURRENT_STATE.md").write_text(
            prefix
            + "# Current State\n\n"
            + "## Active E-series Registry\n\n"
            + "| ID | Direct name | Owner | Status | Mutable root | "
            + "Design SHA-256 | Design commit |\n"
            + "|---|---|---|---|---|---|---|\n"
            + registry_rows
            + "\n",
            encoding="utf-8",
        )
        return temporary, root

    def test_exact_registration_is_required_before_scaffold(self):
        temporary, root = self.make_root(
            "| E002 | Alignment Diagnostic | Tianhang Tan | registered | "
            "experiments/E002-alignment-diagnostic/ | Pending | Pending |"
        )
        with temporary:
            scaffold_e_series._validate_registration(
                root,
                "E002",
                "Alignment Diagnostic",
                "Tianhang Tan",
                "E002-alignment-diagnostic",
            )

    def test_registration_without_mutable_root_fails(self):
        temporary, root = self.make_root(
            "| E002 | Alignment Diagnostic | Tianhang Tan | registered | "
            "experiments/E002-wrong-root/ | Pending | Pending |"
        )
        with temporary:
            with self.assertRaises(governance.GovernanceError):
                scaffold_e_series._validate_registration(
                    root,
                    "E002",
                    "Alignment Diagnostic",
                    "Tianhang Tan",
                    "E002-alignment-diagnostic",
                )

    def test_prose_or_comment_cannot_spoof_registration(self):
        temporary, root = self.make_root(
            "",
            prefix=(
                "<!-- | E002 | Alignment Diagnostic | Tianhang Tan | registered | "
                "experiments/E002-alignment-diagnostic/ | Pending | Pending | -->\n"
            ),
        )
        with temporary:
            with self.assertRaises(governance.GovernanceError):
                scaffold_e_series._validate_registration(
                    root,
                    "E002",
                    "Alignment Diagnostic",
                    "Tianhang Tan",
                    "E002-alignment-diagnostic",
                )

    def test_wrong_status_or_anchor_is_rejected(self):
        temporary, root = self.make_root(
            "| E002 | Alignment Diagnostic | Tianhang Tan | design_frozen | "
            f"experiments/E002-alignment-diagnostic/ | {'1' * 64} | {'2' * 40} |"
        )
        with temporary:
            with self.assertRaises(governance.GovernanceError):
                scaffold_e_series._validate_registration(
                    root,
                    "E002",
                    "Alignment Diagnostic",
                    "Tianhang Tan",
                    "E002-alignment-diagnostic",
                )


class HashTests(unittest.TestCase):
    def test_byte_hash_changes_when_frozen_design_changes(self):
        before = b'{"status":"design_frozen"}\n'
        after = b'{"status":"changed"}\n'
        self.assertNotEqual(
            governance.sha256_bytes(before),
            governance.sha256_bytes(after),
        )

    def test_hash_sidecar_has_one_canonical_name(self):
        digest = hashlib.sha256(b"design\n").hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / governance.DESIGN_HASH_NAME
            path.write_text(
                f"{digest}  {governance.DESIGN_NAME}\n", encoding="utf-8"
            )
            self.assertEqual(governance._parse_hash_sidecar(path), digest)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "duplicate.json"
            path.write_text('{"status":"a","status":"b"}\n', encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                governance.load_json(path)

    def test_nan_and_infinity_are_rejected(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                with self.assertRaises(governance.GovernanceError):
                    governance.strict_json_loads(
                        f'{{"value":{constant}}}', "non-finite fixture"
                    )

    def test_writer_refuses_non_finite_number(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "non-finite.json"
            with self.assertRaises(governance.GovernanceError):
                governance.write_json(path, {"value": float("nan")})

    def test_unknown_schema_keyword_fails_closed(self):
        errors = governance.schema_errors(
            {"value": 1},
            {"type": "object", "allOf": []},
        )
        self.assertTrue(any("unsupported schema keywords" in error for error in errors))


class GitHistoryTests(unittest.TestCase):
    def test_shallow_history_reports_fetch_depth_zero(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = pathlib.Path(temporary)
            source = base / "source"
            source.mkdir()
            init_git_repo(source)
            for index in range(2):
                (source / "history.txt").write_text(
                    f"{index}\n", encoding="utf-8"
                )
                subprocess.run(
                    ["git", "-C", str(source), "add", "history.txt"], check=True
                )
                subprocess.run(
                    ["git", "-C", str(source), "commit", "-qm", f"commit {index}"],
                    check=True,
                )
            clone = base / "shallow"
            subprocess.run(
                [
                    "git",
                    "clone",
                    "-q",
                    "--depth",
                    "1",
                    source.as_uri(),
                    str(clone),
                ],
                check=True,
            )
            with self.assertRaisesRegex(
                governance.GovernanceError, "fetch-depth: 0"
            ):
                governance.require_full_git_history(clone)


class ScaffoldIntegrationTests(unittest.TestCase):
    def diagnostic_args(self):
        return argparse.Namespace(
            id="E002",
            slug="alignment-diagnostic",
            name="Alignment Diagnostic",
            owner="Tianhang Tan",
            workflow_layer="L2 — Event Pairing",
            freeze_existing=False,
            kind="diagnostic",
            hypothesis="A deterministic check can expose an alignment-contract mismatch.",
            protocol_name="Development-only exploratory",
            data_scope="No data; interface diagnostic only",
            data_manifest=[],
            source=[],
            config=[],
            reused_artifact_manifest=[],
            preprocessing_fit_scope="not_applicable",
            task_definition="Defined by this frozen diagnostic",
            output_policy="Report only the declared observation",
            aggregate_table=[],
            pass_rule="The mismatch is observed",
            fail_rule="The mismatch is not observed",
            inconclusive_rule="The check cannot distinguish the alternatives",
            validity_condition=["The check executes"],
            seed=[],
            fold=[],
            repeat_count=1,
            repeat_policy="One deterministic check",
            baseline=None,
            baseline_id=None,
            baseline_evidence=None,
            candidate=None,
            primary_metric=None,
            metric_direction=None,
            delta_rule=None,
            controlled_variable=[],
            question="Does the interface expose a mismatch?",
            observation_plan="Compare the declared interface representations.",
            check=["Compare the exact representations"],
            capability=None,
            feasibility_check=None,
            success_condition=None,
        )

    def test_scaffold_freezes_registered_design_and_detects_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            (root / "docs").mkdir()
            (root / "experiments").mkdir()
            shutil.copytree(ROOT / "schemas", root / "schemas")
            write_utf8_lf(root / "AGENTS.md", "# Test\n")
            (root / "shared").mkdir()
            shared_source = root / "shared" / "shared_probe.py"
            write_utf8_lf(shared_source, "VALUE = 1\n")
            write_utf8_lf(root / "docs" / "WORK_INDEX.md", work_index())
            write_utf8_lf(
                root / "docs" / "CURRENT_STATE.md",
                registered_current_state(),
            )
            init_git_repo(root)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "test fixture"],
                check=True,
            )

            directory = root / "experiments" / "E002-alignment-diagnostic"
            (directory / "scripts").mkdir(parents=True)
            source_path = directory / "scripts" / "probe.py"
            write_utf8_lf(source_path, "print('probe')\n")
            subprocess.run(
                ["git", "-C", str(root), "add", source_path.relative_to(root)],
                check=True,
            )
            args = self.diagnostic_args()
            args.freeze_existing = True
            args.source = [
                source_path.relative_to(root).as_posix(),
                shared_source.relative_to(root).as_posix(),
            ]
            directory = scaffold_e_series.scaffold(root, args)
            frozen_design, design_hash = governance.validate_design_directory(root, directory)
            with self.assertRaises(governance.GovernanceError):
                governance.validate_active_e_registry(root)

            subprocess.run(
                ["git", "-C", str(root), "add", directory.relative_to(root)],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "freeze E002 design"],
                check=True,
            )
            design_commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            frozen_row = (
                "| E002 | Alignment Diagnostic | Tianhang Tan | design_frozen | "
                "experiments/E002-alignment-diagnostic/ | "
                f"{design_hash} | {design_commit} |"
            )
            current_state = root / "docs" / "CURRENT_STATE.md"
            write_utf8_lf(
                current_state,
                registered_current_state().replace(
                    "| E002 | Alignment Diagnostic | Tianhang Tan | registered | "
                    "experiments/E002-alignment-diagnostic/ | Pending | Pending |",
                    frozen_row,
                ),
            )
            governance.validate_active_e_registry(root)
            subprocess.run(
                ["git", "-C", str(root), "add", current_state.relative_to(root)],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "register frozen E002"],
                check=True,
            )
            main_branch = subprocess.run(
                ["git", "-C", str(root), "branch", "--show-current"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            subprocess.run(
                ["git", "-C", str(root), "checkout", "-qb", "anchor-merge-side"],
                check=True,
            )
            write_utf8_lf(root / "side-note.txt", "side\n")
            subprocess.run(["git", "-C", str(root), "add", "side-note.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "side descendant"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "checkout", "-q", main_branch], check=True
            )
            write_utf8_lf(root / "main-note.txt", "main\n")
            subprocess.run(["git", "-C", str(root), "add", "main-note.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "main descendant"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "merge",
                    "--no-ff",
                    "-qm",
                    "merge descendant",
                    "anchor-merge-side",
                ],
                check=True,
            )
            governance.validate_active_e_registry(root)
            governance._validate_new_archive(root, directory)

            prediction_path = directory / "tables" / "predictions.csv"
            prediction_path.parent.mkdir()
            write_utf8_lf(prediction_path, "metric,value\nmacro_f1,0.9\n")
            subprocess.run(
                ["git", "-C", str(root), "add", "-f", prediction_path.relative_to(root)],
                check=True,
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_new_archive(root, directory)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "rm",
                    "--cached",
                    "-q",
                    prediction_path.relative_to(root),
                ],
                check=True,
            )
            prediction_path.unlink()
            prediction_path.parent.rmdir()

            write_utf8_lf(
                directory / "EXPERIMENT.md",
                "# Alignment Diagnostic\n\nThe declared check was inconclusive.\n",
            )
            write_utf8_lf(directory / "commands.log", "python scripts/probe.py\n")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    (directory / "EXPERIMENT.md").relative_to(root),
                    (directory / "commands.log").relative_to(root),
                ],
                check=True,
            )
            archive_records = []
            for relative, role in (
                ("EXPERIMENT.md", "narrative"),
                ("commands.log", "command_log"),
                ("environment.txt", "environment"),
                ("scripts/probe.py", "source"),
            ):
                archive_records.append(
                    {
                        "path": relative,
                        "role": role,
                        "sha256": governance.canonical_file_sha256(
                            root,
                            (directory / relative).relative_to(root),
                            "archive fixture",
                        ),
                        "contains_row_level_data": False,
                        "contains_sensitive_data": False,
                    }
                )
            result = {
                "$schema": "schemas/work-result.schema.json",
                "schema_version": "1.0",
                "work_id": frozen_design["work_id"],
                "name": frozen_design["name"],
                "owner": frozen_design["owner"],
                "completed_at": "2026-07-23T13:00:00Z",
                "lifecycle_status": "completed",
                "superseded_by": None,
                "track": "E-series",
                "work_kind": "experiment",
                "experiment_kind": "diagnostic",
                "workflow_layer": frozen_design["workflow_layer"],
                "protocol": frozen_design["protocol"],
                "status": "archived",
                "design_sha256": design_hash,
                "design_commit": design_commit,
                "task_definition": frozen_design["task_definition"],
                "output_policy": frozen_design["output_policy"],
                "execution": {"status": "succeeded", "notes": "The check ran."},
                "validity": {"status": "valid", "notes": "The design was followed."},
                "provenance": {
                    "base_git_commit": frozen_design["execution_plan"]["base_git_commit"],
                    "worktree_dirty_at_execution": True,
                    "executed_source_files": frozen_design["execution_plan"]["source_files"],
                    "config_files": [],
                    "environment": frozen_design["execution_plan"]["environment"],
                    "data_manifests": [],
                    "reused_learned_artifacts": [],
                },
                "reproducibility": {
                    "seeds": [],
                    "folds": [],
                    "repeat_count": 1,
                },
                "safety_assertions": {
                    "no_candidate_or_locked_test_feedback": True,
                    "no_candidate_or_locked_test_derived_learned_state": True,
                    "preprocessing_fit_scope": "not_applicable",
                    "shared_inputs_are_immutable_and_hashed": True,
                },
                "outcome": "inconclusive",
                "result_summary": "The diagnostic did not distinguish the alternatives.",
                "observations": ["Both alternatives remained plausible."],
                "evidence": [
                    {
                        "claim": "The diagnostic was inconclusive.",
                        "path": "EXPERIMENT.md",
                        "scope": "exploratory",
                        "limitations": "No formal evaluation was performed.",
                    }
                ],
                "archive": {"files": archive_records},
                "decision": {
                    "action": "retain-diagnostic",
                    "notes": "Retain the useful diagnostic.",
                },
                "limitations": ["Interface-only check."],
            }
            governance.write_json(directory / governance.RESULT_NAME, result)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    (directory / governance.RESULT_NAME).relative_to(root),
                ],
                check=True,
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_new_archive(root, directory)
            write_utf8_lf(
                root / "docs" / "WORK_INDEX.md",
                work_index().replace(
                    "| E002 — Alignment Diagnostic | L2 | Planned | None |",
                    "| E002 — Alignment Diagnostic | L2 | Archived | "
                    "inconclusive; result.json; EXPERIMENT.md |",
                ),
            )
            governance._validate_new_archive(root, directory)

            bad_result = json.loads(json.dumps(result))
            bad_result["evidence"][0]["path"] = "tables/missing.csv"
            write_utf8_lf(
                directory / governance.RESULT_NAME,
                json.dumps(bad_result, indent=2) + "\n",
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    (directory / governance.RESULT_NAME).relative_to(root),
                ],
                check=True,
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_new_archive(root, directory)
            write_utf8_lf(
                directory / governance.RESULT_NAME,
                json.dumps(result, indent=2) + "\n",
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    (directory / governance.RESULT_NAME).relative_to(root),
                ],
                check=True,
            )

            write_utf8_lf(
                current_state,
                registered_current_state().replace(
                    "| E002 | Alignment Diagnostic | Tianhang Tan | registered | "
                    "experiments/E002-alignment-diagnostic/ | Pending | Pending |\n",
                    "",
                ),
            )
            write_utf8_lf(shared_source, "VALUE = 2\n")
            subprocess.run(
                ["git", "-C", str(root), "add", shared_source.relative_to(root)],
                check=True,
            )
            governance._validate_new_archive(root, directory)

            write_utf8_lf(source_path, "print('drifted')\n")
            subprocess.run(
                ["git", "-C", str(root), "add", source_path.relative_to(root)],
                check=True,
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_new_archive(root, directory)
            write_utf8_lf(source_path, "print('probe')\n")
            subprocess.run(
                ["git", "-C", str(root), "add", source_path.relative_to(root)],
                check=True,
            )

            design_path = directory / governance.DESIGN_NAME
            changed_design = json.loads(design_path.read_text(encoding="utf-8"))
            changed_design["hypothesis"] = (
                "A tampered but schema-valid hypothesis cannot replace the commit anchor."
            )
            write_utf8_lf(
                design_path,
                json.dumps(changed_design, indent=2, ensure_ascii=False) + "\n",
            )
            changed_hash = governance.sha256_file(design_path)
            write_utf8_lf(
                directory / governance.DESIGN_HASH_NAME,
                f"{changed_hash}  {governance.DESIGN_NAME}\n",
            )
            governance.validate_design_directory(
                root, directory, verify_current_shared_inputs=False
            )
            with self.assertRaises(governance.GovernanceError):
                governance._validate_new_archive(root, directory)

    def test_freeze_existing_symlink_cannot_write_outside_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary) / "repo"
            outside = pathlib.Path(temporary) / "outside"
            root.mkdir()
            outside.mkdir()
            (root / "docs").mkdir()
            (root / "experiments").mkdir()
            shutil.copytree(ROOT / "schemas", root / "schemas")
            (root / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (root / "docs" / "WORK_INDEX.md").write_text(
                work_index(), encoding="utf-8"
            )
            (root / "docs" / "CURRENT_STATE.md").write_text(
                registered_current_state(), encoding="utf-8"
            )
            init_git_repo(root)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "test fixture"],
                check=True,
            )
            outside_marker = outside / "marker.txt"
            outside_marker.write_text("unchanged\n", encoding="utf-8")
            experiment_link = root / "experiments" / "E002-alignment-diagnostic"
            try:
                experiment_link.symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            args = self.diagnostic_args()
            args.freeze_existing = True
            with self.assertRaises(governance.GovernanceError):
                scaffold_e_series.scaffold(root, args)
            self.assertEqual(outside_marker.read_text(encoding="utf-8"), "unchanged\n")
            self.assertFalse((outside / governance.DESIGN_NAME).exists())

    def test_prepared_tree_allows_local_venv_but_rejects_prefreeze_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            directory = root / "experiments" / "E002-alignment-diagnostic"
            (directory / ".venv" / "bin").mkdir(parents=True)
            try:
                (directory / ".venv" / "bin" / "python").symlink_to(
                    pathlib.Path(sys.executable)
                )
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            args = self.diagnostic_args()
            governance.validate_path_safety(root, [])
            scaffold_e_series._validate_prepared_directory(root, directory, args)
            output = directory / "results" / "metrics.csv"
            output.parent.mkdir()
            output.write_text("metric,value\nf1,0.9\n", encoding="utf-8")
            with self.assertRaises(governance.GovernanceError):
                scaffold_e_series._validate_prepared_directory(
                    root, directory, args
                )


if __name__ == "__main__":
    unittest.main()
