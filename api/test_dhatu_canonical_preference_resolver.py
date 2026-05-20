import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_canonical_preference_resolver import (
    assert_no_auto_promotion,
    assert_no_canonical_mutation,
    build_preference_summary,
    compare_preference_to_editorial_decision,
    list_candidate_preferences_by_status,
    list_preferences_by_status,
    load_canonical_preferences,
    resolve_candidate_preference,
    resolve_preference_for_dhatu,
    validate_canonical_preferences,
)
from engines.dhatu_editorial_resolution import load_editorial_resolutions
from engines.dhatu_source_attribution import load_source_attribution
from engines.dhatu_variant_readings import load_recensions


ROOT = Path(__file__).resolve().parents[1]
PREFERENCES_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_preferences.v1.json"
EDITORIAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "editorial_resolutions.v1.json"
RECENSIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "recensions.v1.json"
ATTRIBUTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
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


class DhatuCanonicalPreferenceResolverTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_canonical_preferences(PREFERENCES_PATH)
        self.editorial = load_editorial_resolutions(EDITORIAL_PATH)
        self.recensions = load_recensions(RECENSIONS_PATH)
        self.attribution = load_source_attribution(ATTRIBUTION_PATH)

    def test_canonical_preferences_file_loads(self):
        self.assertTrue(PREFERENCES_PATH.exists())
        self.assertEqual(self.payload["preferenceVersion"], "1.0.0")
        self.assertEqual(self.payload["model"], "aigaane-canonical-preference-resolver")

    def test_validate_canonical_preferences_passes(self):
        validated = validate_canonical_preferences(
            copy.deepcopy(self.payload),
            editorial_payload=self.editorial,
            recension_payload=self.recensions,
        )

        self.assertEqual(validated["preferenceVersion"], "1.0.0")

    def test_policy_prevents_auto_promotion(self):
        self.assertTrue(assert_no_auto_promotion(self.payload))
        self.assertFalse(self.payload["policy"]["autoPromote"])

    def test_current_ten_canonical_dhatus_have_canonical_preferences(self):
        self.assertEqual(set(self.payload["preferences"]), CANONICAL_IDS)
        self.assertEqual(len(list_preferences_by_status(self.payload, "canonical")), 10)

    def test_controlled_fifteen_candidates_remain_deferred(self):
        deferred = list_candidate_preferences_by_status(self.payload, "deferred")

        self.assertEqual(len(deferred), 15)
        self.assertTrue(all(candidate["recommendedAction"] == "manual-review-required" for candidate in deferred))

    def test_resolve_preference_for_dhatu_returns_canonical_high(self):
        preference = resolve_preference_for_dhatu(
            "01.0001",
            self.editorial,
            self.recensions,
            attribution_payload=self.attribution,
        )

        self.assertEqual(preference["preferenceStatus"], "canonical")
        self.assertEqual(preference["confidence"], "high")

    def test_resolve_candidate_preference_returns_deferred_manual_review(self):
        preference = resolve_candidate_preference(
            "01.0101",
            self.editorial,
            self.recensions,
            attribution_payload=self.attribution,
        )

        self.assertEqual(preference["preferenceStatus"], "deferred")
        self.assertEqual(preference["recommendedAction"], "manual-review-required")

    def test_preference_references_valid_editorial_decision_ids(self):
        for dhatu_id, preference in self.payload["preferences"].items():
            comparison = compare_preference_to_editorial_decision(preference, self.editorial)
            self.assertTrue(comparison["matches"], dhatu_id)

    def test_invalid_preference_status_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["preferences"]["01.0001"]["preferenceStatus"] = "accepted"

        with self.assertRaises(ValueError):
            validate_canonical_preferences(payload)

    def test_invalid_recommended_action_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["preferences"]["01.0001"]["recommendedAction"] = "rewrite-registry"

        with self.assertRaises(ValueError):
            validate_canonical_preferences(payload)

    def test_summary_reports_canonical_and_deferred_counts(self):
        summary = build_preference_summary(self.payload)

        self.assertEqual(summary["canonicalCount"], 10)
        self.assertEqual(summary["deferredCandidateCount"], 15)
        self.assertEqual(summary["preferenceCount"], 10)
        self.assertEqual(summary["candidatePreferenceCount"], 15)

    def test_no_canonical_mutation_policy_passes(self):
        self.assertTrue(assert_no_canonical_mutation(self.payload))

    def test_dhatu_registry_files_are_not_modified_by_resolver(self):
        before = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        resolve_preference_for_dhatu("01.0001", self.editorial, self.recensions, self.attribution)
        resolve_candidate_preference("01.0101", self.editorial, self.recensions, self.attribution)
        after = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }

        self.assertEqual(before, after)

    def test_preference_module_does_not_import_runtime_grammar_engines(self):
        module_path = ROOT / "api" / "engines" / "dhatu_canonical_preference_resolver.py"
        import_lines = [
            line.strip()
            for line in module_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)


if __name__ == "__main__":
    unittest.main()
