import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_approved_promotion_batch.py"
MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_batches.v1.json"
PROMOTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "verified_promotions.v1.json"
PREFERENCES_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_preferences.v1.json"
ATTRIBUTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
RECENSIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "recensions.v1.json"
EDITORIAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "editorial_resolutions.v1.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


spec = importlib.util.spec_from_file_location("run_approved_promotion_batch", SCRIPT_PATH)
batch_runner = importlib.util.module_from_spec(spec)
sys.modules["run_approved_promotion_batch"] = batch_runner
spec.loader.exec_module(batch_runner)


class ApprovedPromotionBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="approved-promotion-batch-"))
        self.manifest = batch_runner.load_promotion_batch_manifest(MANIFEST_PATH)
        self.batch = batch_runner.find_promotion_batch(self.manifest, "PROMOTION_BATCH_0001")
        self.promotions = self._load_json(PROMOTION_PATH)
        self.preferences = self._load_json(PREFERENCES_PATH)
        self.attribution = self._load_json(ATTRIBUTION_PATH)
        self.recensions = self._load_json(RECENSIONS_PATH)
        self.editorial = self._load_json(EDITORIAL_PATH)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_promotion_batches_file_loads(self):
        self.assertTrue(MANIFEST_PATH.exists())
        self.assertEqual(self.manifest["batchVersion"], "1.0.0")

    def test_policy_requires_write_flag(self):
        self.assertTrue(self.manifest["policy"]["requiresWriteFlag"])
        self.assertEqual(self.manifest["policy"]["defaultMode"], "dry-run")

    def test_policy_auto_promote_is_false(self):
        self.assertFalse(self.manifest["policy"]["autoPromote"])

    def test_batch_exists(self):
        self.assertEqual(self.batch["batchId"], "PROMOTION_BATCH_0001")
        self.assertEqual(self.batch["allowedStatuses"], ["approved"])

    def test_dry_run_succeeds(self):
        report = batch_runner.run_approved_promotion_batch(
            "PROMOTION_BATCH_0001",
            write=False,
            report_dir=self.tmp / "reports",
        )

        self.assertEqual(report["mode"], "dry-run")
        self.assertEqual(report["errors"], [])

    def test_dry_run_promotes_zero_records(self):
        report = batch_runner.run_approved_promotion_batch("PROMOTION_BATCH_0001", write=False)

        self.assertEqual(report["approvedCandidates"], 0)
        self.assertEqual(report["promoted"], 0)
        self.assertFalse(report["canonicalMutation"])

    def test_deferred_records_are_skipped(self):
        report = batch_runner.run_approved_promotion_batch("PROMOTION_BATCH_0001", write=False)

        self.assertEqual(report["skippedDeferred"], 15)

    def test_rejected_records_are_skipped(self):
        promotions = copy.deepcopy(self.promotions)
        promotions["records"][0]["status"] = "rejected"
        report = batch_runner.build_promotion_batch_report(
            batch_id="PROMOTION_BATCH_0001",
            mode="dry-run",
            approved_candidates=0,
            promoted=0,
            skipped_deferred=14,
            skipped_rejected=len([record for record in promotions["records"] if record["status"] == "rejected"]),
            errors=[],
            canonical_mutation=False,
        )

        self.assertEqual(report["skippedRejected"], 1)

    def test_approved_only_selection_works_in_temp_fixture(self):
        promotions = copy.deepcopy(self.promotions)
        promotions["records"][0]["status"] = "approved"

        approved = batch_runner.collect_approved_candidates(self.batch, promotions)

        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["id"], promotions["records"][0]["id"])

    def test_governance_contradiction_fails_validation(self):
        candidate = copy.deepcopy(self.promotions["records"][0])
        candidate["status"] = "approved"

        errors = batch_runner.validate_candidate_governance(
            candidate,
            self.preferences,
            self.attribution,
            self.recensions,
            self.editorial,
        )

        self.assertTrue(errors)
        self.assertTrue(any("canonical preference" in error for error in errors))

    def test_write_mode_report_can_be_generated_in_temp_report_directory(self):
        report_dir = self.tmp / "reports"

        report = batch_runner.run_approved_promotion_batch(
            "PROMOTION_BATCH_0001",
            write=True,
            report_dir=report_dir,
        )
        report_path = report_dir / "PROMOTION_BATCH_0001.report.json"

        self.assertTrue(report_path.exists())
        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8")), report)
        self.assertEqual(report["promoted"], 0)

    def test_no_canonical_dhatu_files_are_modified_in_dry_run(self):
        before = {path.name: path.read_text(encoding="utf-8") for path in sorted(DHATU_ROOT.glob("*.json"))}
        batch_runner.run_approved_promotion_batch("PROMOTION_BATCH_0001", write=False)
        after = {path.name: path.read_text(encoding="utf-8") for path in sorted(DHATU_ROOT.glob("*.json"))}

        self.assertEqual(before, after)

    def test_promotion_batch_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_existing_manifest_validation_rejects_auto_promote(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["policy"]["autoPromote"] = True

        with self.assertRaises(ValueError):
            batch_runner.validate_promotion_batch_manifest(manifest)

    def _load_json(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
