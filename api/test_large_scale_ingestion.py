import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_large_scale_ingestion.py"
MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "large_scale_manifest.v1.json"
RAW_BATCH_ROOT = ROOT / "raw" / "dhatupatha_batches"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}
EXPECTED_GANA_DIRS = {
    "01_bhvadi",
    "02_adadi",
    "03_juhotyadi",
    "04_divadi",
    "05_svadi",
    "06_tudadi",
    "07_rudhadi",
    "08_tanadi",
    "09_kryadi",
    "10_curadi",
}


spec = importlib.util.spec_from_file_location("validate_large_scale_ingestion", SCRIPT_PATH)
validator = importlib.util.module_from_spec(spec)
sys.modules["validate_large_scale_ingestion"] = validator
spec.loader.exec_module(validator)


class LargeScaleIngestionTests(unittest.TestCase):
    def setUp(self):
        self.payload = validator.load_large_scale_manifest(MANIFEST_PATH)

    def test_large_scale_manifest_loads(self):
        self.assertTrue(MANIFEST_PATH.exists())
        self.assertEqual(self.payload["manifestVersion"], "1.0.0")

    def test_manifest_policy_is_local_only(self):
        self.assertEqual(self.payload["policy"]["mode"], "local-only")

    def test_network_scraping_is_false(self):
        self.assertFalse(self.payload["policy"]["networkScraping"])

    def test_allow_direct_canonical_write_is_false(self):
        self.assertFalse(self.payload["policy"]["allowDirectCanonicalWrite"])

    def test_all_ten_gana_batch_folders_exist(self):
        self.assertTrue(RAW_BATCH_ROOT.exists())
        actual = {path.name for path in RAW_BATCH_ROOT.iterdir() if path.is_dir()}

        self.assertEqual(actual, EXPECTED_GANA_DIRS)
        for dirname in EXPECTED_GANA_DIRS:
            self.assertTrue((RAW_BATCH_ROOT / dirname / ".gitkeep").exists())

    def test_manifest_contains_exactly_ten_gana_batch_entries(self):
        self.assertEqual(len(self.payload["ganaBatches"]), 10)

    def test_gana_ids_are_unique(self):
        ids = [batch["ganaId"] for batch in self.payload["ganaBatches"]]

        self.assertEqual(len(ids), len(set(ids)))

    def test_slugs_are_unique(self):
        slugs = [batch["slug"] for batch in self.payload["ganaBatches"]]

        self.assertEqual(len(slugs), len(set(slugs)))

    def test_raw_dir_paths_are_under_batch_root(self):
        for batch in self.payload["ganaBatches"]:
            self.assertTrue(batch["rawDir"].startswith("raw/dhatupatha_batches/"))
            self.assertNotIn("data/sanskrit/dhatus", batch["rawDir"])

    def test_validator_script_exists(self):
        self.assertTrue(SCRIPT_PATH.exists())

    def test_validate_large_scale_manifest_passes(self):
        validated = validator.validate_large_scale_manifest(copy.deepcopy(self.payload))

        self.assertEqual(validated["manifestVersion"], "1.0.0")

    def test_find_gana_batch_works_by_id(self):
        batch = validator.find_gana_batch(self.payload, "01")

        self.assertEqual(batch["slug"], "bhvadi")

    def test_find_gana_batch_works_by_slug(self):
        batch = validator.find_gana_batch(self.payload, "curadi")

        self.assertEqual(batch["ganaId"], "10")

    def test_readiness_report_returns_planned_batches(self):
        report = validator.build_large_scale_readiness_report(self.payload)

        self.assertEqual(report["reportVersion"], "1.0.0")
        self.assertEqual(report["ganaCount"], 10)
        self.assertEqual(report["plannedBatches"], 10)

    def test_duplicate_ids_are_detected_in_fixture_data(self):
        records = [{"id": "01.0001"}, {"id": "01.0001"}, {"id": "01.0002"}]

        self.assertEqual(validator.detect_duplicate_ids(records), ["01.0001"])

    def test_cross_batch_collisions_are_detected_in_fixture_data(self):
        collisions = validator.detect_cross_batch_collisions(
            {
                "01": [{"id": "X001"}, {"id": "X002"}],
                "02": [{"id": "X001"}],
                "03": [{"id": "X003"}],
            }
        )

        self.assertEqual(collisions, {"X001": ["01", "02"]})

    def test_validator_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_report_writer_uses_temp_report_directory(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="large-scale-report-") as tmp:
            report = validator.build_large_scale_readiness_report(self.payload)
            path = validator.write_large_scale_report(report, tmp)

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
