import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_source_attribution import load_source_attribution
from engines.dhatu_variant_readings import (
    assert_no_network_sources,
    get_preferred_reading,
    get_variant_readings,
    list_unresolved_readings,
    list_variants_by_recension,
    load_recensions,
    summarize_recensions,
    validate_recensions,
)


ROOT = Path(__file__).resolve().parents[1]
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


class DhatuVariantReadingTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_recensions(RECENSIONS_PATH)
        self.attribution = load_source_attribution(ATTRIBUTION_PATH)

    def test_recensions_file_loads(self):
        self.assertTrue(RECENSIONS_PATH.exists())
        self.assertEqual(self.payload["recensionVersion"], "1.0.0")
        self.assertEqual(self.payload["model"], "aigaane-local-variant-readings")

    def test_validate_recensions_passes(self):
        validated = validate_recensions(copy.deepcopy(self.payload))

        self.assertEqual(validated["recensionVersion"], "1.0.0")

    def test_canonical_ten_records_have_canonical_readings(self):
        self.assertEqual(set(self.payload["variantReadings"]), CANONICAL_IDS)

        for dhatu_id in CANONICAL_IDS:
            readings = get_variant_readings(self.payload, dhatu_id)
            self.assertTrue(readings)
            self.assertTrue(any(reading["readingType"] == "canonical" for reading in readings))

    def test_controlled_fifteen_records_are_unresolved(self):
        unresolved = self.payload["unresolvedReadings"]

        self.assertEqual(len(unresolved), 15)
        self.assertIn("01.0101", unresolved)
        self.assertIn("01.0111", unresolved)

    def test_get_variant_readings_returns_seed_record(self):
        readings = get_variant_readings(self.payload, "01.0001")

        self.assertGreaterEqual(len(readings), 1)
        self.assertEqual(readings[0]["readingType"], "canonical")

    def test_get_preferred_reading_returns_canonical_seed_reading(self):
        preferred = get_preferred_reading(self.payload, "01.0001")

        self.assertEqual(preferred["readingId"], "VR_01_0001_001")
        self.assertEqual(preferred["recension"], "canonical-seed")

    def test_list_variants_by_recension_returns_canonical_records(self):
        readings = list_variants_by_recension(self.payload, "canonical-seed")
        dhatu_ids = {reading["canonicalDhatuId"] for reading in readings}

        self.assertEqual(len(readings), 10)
        self.assertEqual(dhatu_ids, CANONICAL_IDS)

    def test_list_unresolved_deferred_returns_controlled_batch_records(self):
        deferred = list_unresolved_readings(self.payload, "deferred")

        self.assertEqual(len(deferred), 15)
        self.assertTrue(all(reading["status"] == "deferred" for reading in deferred))

    def test_summarize_recensions_returns_counts(self):
        summary = summarize_recensions(self.payload)

        self.assertEqual(summary["recensionCount"], 2)
        self.assertEqual(summary["canonicalReadingCount"], 10)
        self.assertEqual(summary["unresolvedReadingCount"], 15)
        self.assertEqual(summary["deferredUnresolvedCount"], 15)

    def test_invalid_reading_type_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["variantReadings"]["01.0001"]["readings"][0]["readingType"] = "invented"

        with self.assertRaises(ValueError):
            validate_recensions(payload)

    def test_invalid_confidence_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["variantReadings"]["01.0001"]["readings"][0]["confidence"] = "certain"

        with self.assertRaises(ValueError):
            validate_recensions(payload)

    def test_invalid_preferred_reading_id_fails_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["variantReadings"]["01.0001"]["canonicalPreference"]["preferredReadingId"] = "VR_MISSING"

        with self.assertRaises(ValueError):
            validate_recensions(payload)

    def test_source_entities_resolve_against_source_attribution(self):
        validated = validate_recensions(copy.deepcopy(self.payload), source_attribution=self.attribution)

        self.assertEqual(validated["recensionVersion"], "1.0.0")

    def test_no_network_sources_exist(self):
        self.assertTrue(assert_no_network_sources(self.payload))

    def test_variant_module_does_not_import_runtime_grammar_engines(self):
        module_path = ROOT / "api" / "engines" / "dhatu_variant_readings.py"
        import_lines = [
            line.strip()
            for line in module_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_recensions_json_is_plain_local_json(self):
        with RECENSIONS_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertIn("variantReadings", payload)


if __name__ == "__main__":
    unittest.main()
