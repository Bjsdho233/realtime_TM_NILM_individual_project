import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repo_governance as governance


def design(method):
    kind = method["kind"]
    return {
        "$schema": "schemas/e-series-design.schema.json",
        "schema_version": "1.0",
        "work_id": "E002",
        "name": "Schema contract probe",
        "owner": "Tianhang Tan",
        "registered_at": "2026-07-23T12:00:00Z",
        "design_frozen_at": "2026-07-23T12:00:00Z",
        "track": "E-series",
        "experiment_kind": kind,
        "workflow_layer": "L4 — Booleanisation",
        "status": "design_frozen",
        "hypothesis": "The declared check can resolve the narrow exploratory question.",
        "protocol": {
            "name": "Development-only exploratory",
            "data_scope": "Development data only",
            "claim_scope": "exploratory",
            "sealed_test_access": False,
        },
        "task_definition": "Defined by this frozen design",
        "output_policy": "No formal binary-TM output semantics inferred",
        "input_contract": {"uses_data": False, "sources": []},
        "baseline": None,
        "reused_learned_artifacts": [],
        "reproducibility": {
            "seeds": [],
            "folds": [],
            "repeat_count": 1,
            "repeat_policy": "One deterministic check",
        },
        "execution_plan": {
            "base_git_commit": "0" * 40,
            "worktree_dirty": False,
            "source_files": [],
            "config_files": [],
            "environment": {
                "path": "experiments/E002-schema-contract-probe/environment.txt",
                "sha256": "1" * 64,
            },
            "commands_file": "experiments/E002-schema-contract-probe/commands.log",
        },
        "safety_assertions": {
            "no_candidate_or_locked_test_feedback": True,
            "no_candidate_or_locked_test_derived_learned_state": True,
            "preprocessing_fit_scope": "not_applicable",
            "shared_inputs_are_immutable_and_hashed": True,
            "mutable_paths_are_exclusive": True,
        },
        "registered_mutable_paths": ["experiments/E002-schema-contract-probe/"],
        "method": method,
        "acceptance_rule": {
            "supported": "The predeclared condition is observed",
            "not_supported": "The predeclared condition is not observed",
            "inconclusive": "The check cannot distinguish the alternatives",
            "validity_conditions": ["The declared check executes"],
        },
        "output_contract": {
            "result_schema": "schemas/work-result.schema.json",
            "archive_policy": "reviewed_whitelist",
            "row_level_outputs_allowed": False,
            "archive_directories": ["scripts", "configs", "tables", "figures", "docs"],
            "aggregate_tables": [],
        },
    }


class DesignSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / governance.DESIGN_SCHEMA_PATH).read_text(encoding="utf-8")
        )

    def assertValid(self, instance):
        self.assertEqual(governance.schema_errors(instance, self.schema), [])

    def test_diagnostic_does_not_require_classification_metric(self):
        self.assertValid(
            design(
                {
                    "kind": "diagnostic",
                    "question": "Does the parity check expose a mismatch?",
                    "observation_plan": "Compare the two declared representations.",
                    "checks": ["Compare the exact Boolean vectors"],
                }
            )
        )

    def test_feasibility_does_not_require_baseline(self):
        self.assertValid(
            design(
                {
                    "kind": "feasibility",
                    "capability": "Compile the isolated interface",
                    "check": "Run the declared build command",
                    "success_condition": "The command exits successfully",
                }
            )
        )

    def test_comparison_requires_control_and_metric_contract(self):
        instance = design(
            {
                "kind": "comparison",
                "baseline": {"name": "A", "description": "Current reviewed encoder"},
                "candidate": {"name": "B", "description": "Single-variable alternative"},
                "primary_metric": {"name": "macro_f1", "direction": "maximize"},
                "delta_rule": "Candidate mean exceeds baseline mean",
                "controlled_variables": [],
            }
        )
        errors = governance.schema_errors(instance, self.schema)
        self.assertTrue(any("controlled_variables" in error for error in errors))

    def test_method_fields_cannot_leak_between_kinds(self):
        instance = design(
            {
                "kind": "diagnostic",
                "question": "Does the check expose a mismatch?",
                "observation_plan": "Compare both representations.",
                "checks": ["Compare vectors"],
                "primary_metric": {"name": "accuracy", "direction": "maximize"},
            }
        )
        self.assertTrue(governance.schema_errors(instance, self.schema))


class ResultSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / governance.RESULT_SCHEMA_PATH).read_text(encoding="utf-8")
        )

    def result(self):
        return {
            "$schema": "schemas/work-result.schema.json",
            "schema_version": "1.0",
            "work_id": "E002",
            "name": "Schema contract probe",
            "owner": "Tianhang Tan",
            "completed_at": "2026-07-23T13:00:00Z",
            "lifecycle_status": "completed",
            "superseded_by": None,
            "track": "E-series",
            "work_kind": "experiment",
            "experiment_kind": "diagnostic",
            "workflow_layer": "L4 — Booleanisation",
            "protocol": {
                "name": "Development-only exploratory",
                "data_scope": "Development data only",
                "claim_scope": "exploratory",
                "sealed_test_access": False,
            },
            "status": "archived",
            "design_sha256": "2" * 64,
            "design_commit": "4" * 40,
            "task_definition": "Defined by the frozen design",
            "output_policy": "No formal binary-TM output semantics inferred",
            "execution": {"status": "succeeded", "notes": "The declared check ran."},
            "validity": {"status": "valid", "notes": "All validity checks passed."},
            "provenance": {
                "base_git_commit": "0" * 40,
                "worktree_dirty_at_execution": False,
                "executed_source_files": [],
                "config_files": [],
                "environment": {"path": "environment.txt", "sha256": "1" * 64},
                "data_manifests": [],
                "reused_learned_artifacts": [],
            },
            "reproducibility": {"seeds": [], "folds": [], "repeat_count": 1},
            "safety_assertions": {
                "no_candidate_or_locked_test_feedback": True,
                "no_candidate_or_locked_test_derived_learned_state": True,
                "preprocessing_fit_scope": "not_applicable",
                "shared_inputs_are_immutable_and_hashed": True,
            },
            "outcome": "inconclusive",
            "result_summary": "The check did not distinguish the two explanations.",
            "observations": ["Both representations remained plausible."],
            "evidence": [
                {
                    "claim": "The check was inconclusive.",
                    "path": "EXPERIMENT.md",
                    "scope": "exploratory",
                    "limitations": "Development-only diagnostic.",
                }
            ],
            "archive": {
                "files": [
                    {
                        "path": "EXPERIMENT.md",
                        "role": "narrative",
                        "sha256": "3" * 64,
                        "contains_row_level_data": False,
                        "contains_sensitive_data": False,
                    }
                ]
            },
            "decision": {"action": "retain-diagnostic", "notes": "Keep as a diagnostic."},
            "limitations": ["No formal evaluation was performed."],
        }

    def test_structured_diagnostic_result_is_valid(self):
        self.assertEqual(governance.schema_errors(self.result(), self.schema), [])

    def test_metric_requires_definition_aggregation_and_boundary(self):
        instance = self.result()
        instance["metrics"] = [
            {"name": "accuracy", "value": 0.9, "unit": "ratio", "scope": "development"}
        ]
        errors = governance.schema_errors(instance, self.schema)
        self.assertTrue(any("definition" in error for error in errors))

    def test_source_provenance_uses_only_path_and_hash(self):
        instance = self.result()
        instance["provenance"]["executed_source_files"] = [
            {"path": "experiments/E002-probe/scripts/probe.py", "sha256": "5" * 64}
        ]
        self.assertEqual(governance.schema_errors(instance, self.schema), [])

    def test_pre_execution_supersession_is_machine_readable(self):
        instance = self.result()
        instance.update(
            {
                "lifecycle_status": "superseded_before_execution",
                "superseded_by": "E003",
                "outcome": "not_applicable",
                "evidence": [],
            }
        )
        instance.pop("observations")
        instance["execution"] = {
            "status": "not_run",
            "notes": "Superseded before execution.",
        }
        instance["validity"] = {
            "status": "not_assessed",
            "notes": "No execution to assess.",
        }
        instance["decision"] = {
            "action": "supersede",
            "notes": "E003 replaces this design.",
        }
        self.assertEqual(governance.schema_errors(instance, self.schema), [])

    def test_t_series_contract_is_distinct_from_e_series(self):
        instance = self.result()
        instance.update(
            {
                "work_id": "T004",
                "track": "T-series",
                "work_kind": "protocol_decision",
                "experiment_kind": "not_applicable",
                "status": "complete",
                "design_sha256": None,
                "design_commit": None,
                "protocol": {
                    "name": "Formal development protocol",
                    "data_scope": "Development partition",
                    "claim_scope": "formal_development",
                    "sealed_test_access": False,
                },
                "outcome": "accepted",
                "decision": {
                    "action": "accept",
                    "notes": "The protocol contract was accepted.",
                },
            }
        )
        instance["evidence"][0]["scope"] = "formal_development"
        self.assertEqual(governance.schema_errors(instance, self.schema), [])
        instance["status"] = "archived"
        self.assertTrue(governance.schema_errors(instance, self.schema))

    def test_e_series_cannot_directly_promote_itself(self):
        instance = self.result()
        instance["decision"]["action"] = "promote"
        self.assertTrue(governance.schema_errors(instance, self.schema))


if __name__ == "__main__":
    unittest.main()
