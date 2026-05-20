import csv
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_semantic_query import load_query_context


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "ingest_dhatupatha_batches.py"
MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "manifest.v1.json"
REPORTS_DIR = ROOT / "data" / "sanskrit" / "ingestion" / "reports"
SCHEMA_PATH = ROOT / "data" / "sanskrit" / "schemas" / "dhatu.schema.v2.json"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


spec = importlib.util.spec_from_file_location("ingest_dhatupatha_batches", SCRIPT_PATH)
ingest = importlib.util.module_from_spec(spec)
sys.modules["ingest_dhatupatha_batches"] = ingest
spec.loader.exec_module(ingest)


class DhatupathaIngestionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = ingest.load_manifest(MANIFEST_PATH)
        self.tmp = Path(tempfile.mkdtemp(prefix="dhatu-ingest-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_manifest_exists_and_loads(self):
        self.assertTrue(MANIFEST_PATH.exists())
        self.assertEqual(self.manifest["manifestVersion"], "1.0.0")

    def test_manifest_has_local_only_source_policy(self):
        self.assertEqual(self.manifest["sourcePolicy"]["mode"], "local-only")
        self.assertTrue(self.manifest["sourcePolicy"]["requiresDryRunBeforeWrite"])

    def test_network_scraping_is_false(self):
        self.assertFalse(self.manifest["sourcePolicy"]["networkScraping"])

    def test_every_batch_has_required_fields(self):
        for batch in self.manifest["batches"]:
            self.assertIn("batchId", batch)
            self.assertIn("input", batch)
            self.assertIn("status", batch)
            ingest.validate_batch(batch)

    def test_batch_ids_are_unique(self):
        ids = [batch["batchId"] for batch in self.manifest["batches"]]

        self.assertEqual(len(ids), len(set(ids)))

    def test_reports_directory_exists(self):
        self.assertTrue(REPORTS_DIR.exists())

    def test_ingest_script_exists(self):
        self.assertTrue(SCRIPT_PATH.exists())

    def test_dry_run_batch_execution_does_not_create_report_files(self):
        report_dir = self.tmp / "reports"
        batch = ingest.find_batch(self.manifest, "BATCH_0001_GOLDSET_BASE")

        report = ingest.run_ingestion_batch(batch, write=False, report_dir=report_dir)

        self.assertEqual(report["mode"], "dry-run")
        self.assertFalse(report_dir.exists())

    def test_invalid_batch_id_fails_safely(self):
        with self.assertRaises(ValueError):
            ingest.find_batch(self.manifest, "NO_SUCH_BATCH")

    def test_batch_with_missing_input_fails_safely(self):
        batch = {
            "batchId": "BATCH_MISSING",
            "input": str(self.tmp / "missing.csv"),
            "status": "planned",
        }

        with self.assertRaises(FileNotFoundError):
            ingest.run_ingestion_batch(batch)

    def test_write_mode_report_format_can_be_generated_in_temp_directory(self):
        raw_path = self._write_sample_csv()
        output_dir = self.tmp / "dhatus"
        report_dir = self.tmp / "reports"
        batch = {
            "batchId": "BATCH_TEMP_WRITE",
            "input": str(raw_path),
            "status": "planned",
            "limit": 1,
            "outputDir": str(output_dir),
            "schema": str(SCHEMA_PATH),
        }

        report = ingest.run_ingestion_batch(batch, write=True, report_dir=report_dir)
        report_path = report_dir / "BATCH_TEMP_WRITE.report.json"
        written_report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report["reportVersion"], "1.0.0")
        self.assertEqual(report["mode"], "write")
        self.assertTrue(report["summary"]["index_rebuilt"])
        self.assertEqual(written_report["batchId"], "BATCH_TEMP_WRITE")
        self.assertEqual(written_report["postChecks"]["goldsetExpected"], "passed")
        self.assertEqual(written_report["postChecks"]["queryOverlay"], "passed")

    def test_wrapper_does_not_import_grammar_runtime_engines(self):
        import_lines = [
            line.strip()
            for line in SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_goldset_data_still_loads(self):
        metadata_path = ROOT / "data" / "sanskrit" / "goldset" / "goldset_metadata.v1.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertEqual(metadata["goldsetVersion"], "1.0.0")
        self.assertGreaterEqual(metadata["recordCount"], 10)

    def test_semantic_query_context_still_loads(self):
        context = load_query_context()

        self.assertGreaterEqual(len(context["records"]), 10)
        self.assertIn("records", context["semanticOverlay"])

    def _write_sample_csv(self):
        path = self.tmp / "sample.csv"
        row = {
            "id": "05.0001",
            "upadesha": "सु",
            "root": "सु",
            "romanized": "su",
            "canonicalForm": "सुनोति",
            "gana_id": "05",
            "itStatus": "set",
            "karmatva": "sakarmaka",
            "defaultPada": "parasmaipada",
            "semantics_sanskrit": "प्रसवे",
            "semantics_english": "to press",
            "lat_kartari_parasmaipada": "",
            "lot_kartari_parasmaipada": "",
            "lat_kartari_atmanepada": "",
            "lot_kartari_atmanepada": "",
            "lat_bhavaKarmani_atmanepada": "",
            "sananta_base": "",
            "nijanta_base": "",
            "yanganta_base": "",
            "upasarga_list": "",
            "ruleTriggers": "",
        }
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)
        return path


if __name__ == "__main__":
    unittest.main()
