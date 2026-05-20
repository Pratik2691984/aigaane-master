import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_source_attribution import (
    assert_no_network_derived_sources,
    get_record_attribution,
    list_records_by_review_status,
    list_records_by_source_confidence,
    load_source_attribution,
    summarize_attribution,
    validate_record_against_promotion,
    validate_source_attribution,
)


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
PROMOTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "verified_promotions.v1.json"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


class DhatuSourceAttributionTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_source_attribution(ATTRIBUTION_PATH)
        self.promotion = json.loads(PROMOTION_PATH.read_text(encoding="utf-8"))

    def test_source_attribution_file_loads(self):
        self.assertTrue(ATTRIBUTION_PATH.exists())
        self.assertEqual(self.payload["attributionVersion"], "1.0.0")
        self.assertEqual(self.payload["model"], "aigaane-local-provenance")

    def test_validate_source_attribution_passes(self):
        validated = validate_source_attribution(copy.deepcopy(self.payload))

        self.assertEqual(validated["attributionVersion"], "1.0.0")

    def test_no_network_derived_source_exists(self):
        self.assertTrue(assert_no_network_derived_sources(self.payload))

    def test_all_activity_used_entities_resolve(self):
        entities = self.payload["entities"]

        for activity in self.payload["activities"].values():
            for entity_id in activity["usedEntities"]:
                self.assertIn(entity_id, entities)

    def test_all_activity_associated_agents_resolve(self):
        agents = self.payload["agents"]

        for activity in self.payload["activities"].values():
            for agent_id in activity["associatedAgents"]:
                self.assertIn(agent_id, agents)

    def test_all_record_source_entities_resolve(self):
        entities = self.payload["entities"]

        for attribution in self.payload["recordAttributions"].values():
            for entity_id in attribution["sourceEntities"]:
                self.assertIn(entity_id, entities)

    def test_all_record_review_agents_resolve(self):
        agents = self.payload["agents"]

        for attribution in self.payload["recordAttributions"].values():
            for agent_id in attribution["reviewAgents"]:
                self.assertIn(agent_id, agents)

    def test_all_record_validation_activities_resolve(self):
        activities = self.payload["activities"]

        for attribution in self.payload["recordAttributions"].values():
            for activity_id in attribution["validationActivities"]:
                self.assertIn(activity_id, activities)

    def test_seed_record_returns_approved_high_attribution(self):
        attribution = get_record_attribution(self.payload, "01.0001")

        self.assertEqual(attribution["reviewStatus"], "approved")
        self.assertEqual(attribution["sourceConfidence"], "high")

    def test_deferred_controlled_batch_records_are_queryable(self):
        deferred = list_records_by_review_status(self.payload, "deferred")

        self.assertEqual(len(deferred), 15)
        self.assertIn("01.0101", deferred)

    def test_high_confidence_returns_seed_canonical_records(self):
        high = list_records_by_source_confidence(self.payload, "high")

        self.assertEqual(len(high), 10)
        self.assertIn("01.0001", high)
        self.assertIn("10.0001", high)

    def test_summarize_attribution_returns_expected_counts(self):
        summary = summarize_attribution(self.payload)

        self.assertEqual(summary["entityCount"], 2)
        self.assertEqual(summary["agentCount"], 3)
        self.assertEqual(summary["activityCount"], 2)
        self.assertEqual(summary["recordCount"], 25)
        self.assertEqual(summary["approved"], 10)
        self.assertEqual(summary["deferred"], 15)
        self.assertEqual(summary["rejected"], 0)

    def test_validate_record_against_promotion_confirms_deferred_records(self):
        result = validate_record_against_promotion(self.payload, self.promotion)

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_record_against_promotion_detects_status_mismatch(self):
        payload = copy.deepcopy(self.payload)
        payload["recordAttributions"]["01.0101"]["reviewStatus"] = "approved"

        result = validate_record_against_promotion(payload, self.promotion)

        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])

    def test_validation_fails_for_network_derived_source(self):
        payload = copy.deepcopy(self.payload)
        payload["entities"]["raw/dhatupatha.csv"]["networkDerived"] = True

        with self.assertRaises(ValueError):
            validate_source_attribution(payload)

    def test_attribution_module_does_not_import_runtime_grammar_engines(self):
        module_path = ROOT / "api" / "engines" / "dhatu_source_attribution.py"
        import_lines = [
            line.strip()
            for line in module_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)


if __name__ == "__main__":
    unittest.main()
