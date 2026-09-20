import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_editorial_resolution import (
    assert_no_auto_promotion,
    assert_preserves_alternatives,
    build_resolution_summary,
    compare_decision_to_preferred_reading,
    get_decision,
    get_recommendation,
    list_decisions_by_status,
    list_recommendations_by_status,
    load_editorial_resolutions,
    rank_readings_for_dhatu,
    score_reading_evidence,
    validate_editorial_resolutions,
)
from engines.dhatu_source_attribution import load_source_attribution
from engines.dhatu_variant_readings import load_recensions


ROOT = Path(__file__).resolve().parents[1]
RESOLUTIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "editorial_resolutions.v1.json"
RECENSIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "recensions.v1.json"
ATTRIBUTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}
CANONICAL_IDS = {
    "01.0001",
    "01.0002",
    "02.0001",
    "03.0001",
    "04.0001",
    "06.0001",
    "07.0001",
    "08.0001",
    "09.0001",
    "10.0001",
}


class DhatuEditorialResolutionTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_editorial_resolutions(RESOLUTIONS_PATH)
        self.recensions = load_recensions(RECENSIONS_PATH)
        self.attribution = load_source_attribution(ATTRIBUTION_PATH)

    def test_editorial_resolutions_file_loads(self):
        self.assertTrue(RESOLUTIONS_PATH.exists())
        self.assertEqual(self.payload["resolutionVersion"], "1.0.0")
        self.assertEqual(self.payload["model"], "aigaane-local-editorial-resolution")

    def test_validate_editorial_resolutions_passes(self):
        validated = validate_editorial_resolutions(
            copy.deepcopy(self.payload),
            recensions=self.recensions,
            source_attribution=self.attribution,
        )

        self.assertEqual(validated["resolutionVersion"], "1.0.0")

    def test_policy_auto_promote_is_false(self):
        self.assertFalse(self.payload["policy"]["autoPromote"])

    def test_mutation_target_is_none(self):
        self.assertEqual(self.payload["policy"]["mutationTarget"], "none")

    def test_preserve_rejected_alternatives_is_true(self):
        self.assertTrue(self.payload["policy"]["preserveRejectedAlternatives"])

    def test_current_ten_canonical_records_have_accepted_decisions(self):
        self.assertEqual(set(self.payload["decisions"]), CANONICAL_IDS)
        for dhatu_id in CANONICAL_IDS:
            self.assertEqual(self.payload["decisions"][dhatu_id]["status"], "accepted")

    def test_controlled_fifteen_candidates_have_defer_recommendations(self):
        self.assertEqual(len(self.payload["recommendations"]), 15)
        self.assertTrue(
            all(recommendation["status"] == "defer" for recommendation in self.payload["recommendations"].values())
        )

    def test_get_decision_returns_accepted_keep_canonical(self):
        decision = get_decision(self.payload, "01.0001")

        self.assertEqual(decision["status"], "accepted")
        self.assertEqual(decision["recommendedAction"], "keep-canonical")

    def test_list_decisions_by_status_returns_accepted_records(self):
        accepted = list_decisions_by_status(self.payload, "accepted")

        self.assertGreaterEqual(len(accepted), 10)

    def test_list_recommendations_by_status_returns_controlled_candidates(self):
        deferred = list_recommendations_by_status(self.payload, "defer")

        self.assertEqual(len(deferred), 15)
        self.assertEqual(get_recommendation(self.payload, "01.0101")["status"], "defer")

    def test_scoring_weights_sum_approximately_to_one(self):
        weights = self.payload["scoring"]["weights"]

        self.assertAlmostEqual(sum(weights.values()), 1.0, places=3)

    def test_evidence_scores_are_within_range(self):
        for decision in self.payload["decisions"].values():
            self.assertGreaterEqual(decision["evidenceScore"], 0.0)
            self.assertLessEqual(decision["evidenceScore"], 1.0)

        reading = self.recensions["variantReadings"]["01.0001"]["readings"][0]
        score = score_reading_evidence(
            {**reading, "canonicalDhatuId": "01.0001"},
            attribution=self.attribution,
            goldset_ids=CANONICAL_IDS,
            weights=self.payload["scoring"]["weights"],
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_compare_decision_to_preferred_reading_passes_for_canonical_records(self):
        for dhatu_id in CANONICAL_IDS:
            result = compare_decision_to_preferred_reading(self.payload["decisions"][dhatu_id], self.recensions)
            self.assertTrue(result["matches"], dhatu_id)

    def test_invalid_decision_status_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["decisions"]["01.0001"]["status"] = "approved"

        with self.assertRaises(ValueError):
            validate_editorial_resolutions(payload)

    def test_invalid_recommendation_id_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["recommendations"]["01.0101"]["recommendationId"] = "REC-01-0101"

        with self.assertRaises(ValueError):
            validate_editorial_resolutions(payload)

    def test_assert_no_auto_promotion_passes(self):
        self.assertTrue(assert_no_auto_promotion(self.payload))

    def test_assert_preserves_alternatives_passes(self):
        self.assertTrue(assert_preserves_alternatives(self.payload))

    def test_rank_readings_for_dhatu_returns_canonical_first(self):
        ranked = rank_readings_for_dhatu(
            self.recensions,
            "01.0001",
            attribution_payload=self.attribution,
            goldset_ids=CANONICAL_IDS,
        )

        self.assertTrue(ranked)
        self.assertEqual(ranked[0]["readingId"], "VR_01_0001_001")
        self.assertEqual(ranked[0]["readingType"], "canonical")

    def test_summary_counts_editorial_records(self):
        summary = build_resolution_summary(self.payload)

        self.assertEqual(summary["decisionCount"], 10)
        self.assertEqual(summary["recommendationCount"], 15)
        self.assertEqual(summary["acceptedDecisionCount"], 10)
        self.assertEqual(summary["deferRecommendationCount"], 15)

    def test_editorial_module_does_not_import_runtime_grammar_engines(self):
        module_path = ROOT / "api" / "engines" / "dhatu_editorial_resolution.py"
        import_lines = [
            line.strip()
            for line in module_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)


if __name__ == "__main__":
    unittest.main()
