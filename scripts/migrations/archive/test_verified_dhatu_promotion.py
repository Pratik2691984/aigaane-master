import copy
import csv
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_registry import load_all_dhatus
from engines.dhatu_semantic_query import load_query_context


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "promote_verified_dhatus.py"
PROMOTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "verified_promotions.v1.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
GOLDSET_METADATA = ROOT / "data" / "sanskrit" / "goldset" / "goldset_metadata.v1.json"
VALID_STATUSES = {"approved", "deferred", "rejected"}
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


spec = importlib.util.spec_from_file_location("promote_verified_dhatus", SCRIPT_PATH)
promote = importlib.util.module_from_spec(spec)
sys.modules["promote_verified_dhatus"] = promote
spec.loader.exec_module(promote)


class VerifiedDhatuPromotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dhatu-promotion-"))
        self.payload = promote.load_promotion(PROMOTION_PATH)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_verified_promotions_file_loads(self):
        self.assertTrue(PROMOTION_PATH.exists())
        self.assertEqual(self.payload["promotionVersion"], "1.0.0")
        self.assertEqual(self.payload["sourceFile"], "raw/dhatupatha_controlled_batch_01.csv")

    def test_every_record_has_required_review_fields(self):
        required = {"id", "root", "canonicalForm", "gana_id", "status", "sourceConfidence"}

        for record in self.payload["records"]:
            self.assertTrue(required.issubset(record), record["id"])

    def test_statuses_are_limited_to_review_states(self):
        statuses = {record["status"] for record in self.payload["records"]}

        self.assertTrue(statuses.issubset(VALID_STATUSES))

    def test_dry_run_promotes_nothing(self):
        report_dir = self.tmp / "reports"

        report = promote.run_promotion(PROMOTION_PATH, write=False, report_dir=report_dir)

        self.assertEqual(report["mode"], "dry-run")
        self.assertEqual(report["promoted"], 0)
        self.assertFalse(report_dir.exists())

    def test_deferred_records_are_not_promoted(self):
        report = promote.run_promotion(PROMOTION_PATH, write=False, report_dir=self.tmp / "reports")

        self.assertEqual(report["approved"], 0)
        self.assertEqual(report["deferred"], len(self.payload["records"]))
        self.assertEqual(report["promoted"], 0)

    def test_rejected_records_are_not_promoted(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["status"] = "rejected"
        path = self._write_promotion(payload)

        report = promote.run_promotion(path, write=False, report_dir=self.tmp / "reports")

        self.assertEqual(report["approved"], 0)
        self.assertEqual(report["rejected"], 1)
        self.assertEqual(report["promoted"], 0)

    def test_approved_record_must_match_source_csv(self):
        payload = self._payload_with_first_record_status("approved")
        path = self._write_promotion(payload)

        report = promote.run_promotion(path, write=False, report_dir=self.tmp / "reports")

        self.assertEqual(report["approved"], 1)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["promoted"], 0)

    def test_approved_record_mismatch_fails_validation(self):
        payload = self._payload_with_first_record_status("approved")
        payload["records"][0]["root"] = "mismatch"
        path = self._write_promotion(payload)

        report = promote.run_promotion(path, write=False, report_dir=self.tmp / "reports")

        self.assertTrue(report["errors"])
        self.assertIn("mismatch", report["errors"][0])

    def test_source_csv_contains_every_promotion_id(self):
        source_rows = promote.load_source_rows(self.payload["sourceFile"])
        promotion_ids = {record["id"] for record in self.payload["records"]}

        self.assertTrue(promotion_ids.issubset(source_rows))

    def test_promotion_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_canonical_registry_remains_schema_valid(self):
        records = load_all_dhatus(DHATU_ROOT)

        self.assertGreaterEqual(len(records), 10)

    def test_goldset_data_still_loads(self):
        metadata = json.loads(GOLDSET_METADATA.read_text(encoding="utf-8"))

        self.assertEqual(metadata["goldsetVersion"], "1.0.0")
        self.assertGreaterEqual(metadata["recordCount"], 10)

    def test_semantic_query_context_still_loads(self):
        context = load_query_context()

        self.assertGreaterEqual(len(context["records"]), 10)
        self.assertIn("records", context["semanticOverlay"])

    def test_promotion_records_match_source_review_fields(self):
        source_rows = promote.load_source_rows(self.payload["sourceFile"])

        for record in self.payload["records"]:
            source = source_rows[record["id"]]
            for field in ("id", "root", "canonicalForm", "gana_id"):
                self.assertEqual(record[field], source[field])

    def test_all_current_records_are_deferred_until_id_review(self):
        self.assertEqual({record["status"] for record in self.payload["records"]}, {"deferred"})

    def _payload_with_first_record_status(self, status):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["status"] = status
        return payload

    def _write_promotion(self, payload):
        path = self.tmp / "promotion.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
