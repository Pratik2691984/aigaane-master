import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_large_scale_ingestion.py"
PREVIEW_SCRIPT_PATH = ROOT / "scripts" / "preview_dhatu_batch_promotion.py"
PLAN_SCRIPT_PATH = ROOT / "scripts" / "plan_dhatu_canonical_promotion.py"
REVIEW_SCRIPT_PATH = ROOT / "scripts" / "apply_dhatu_review_decisions.py"
LOCK_SCRIPT_PATH = ROOT / "scripts" / "lock_dhatu_promotion_readiness.py"
PROMOTE_SCRIPT_PATH = ROOT / "scripts" / "promote_ready_dhatu_to_canonical.py"
EVIDENCE_SCRIPT_PATH = ROOT / "scripts" / "report_dhatu_promotion_evidence.py"
AUTHORIZATION_SCRIPT_PATH = ROOT / "scripts" / "authorize_dhatu_canonical_write.py"
COMMAND_SCRIPT_PATH = ROOT / "scripts" / "prepare_dhatu_canonical_write_command.py"
APPROVAL_VALIDATION_SCRIPT_PATH = ROOT / "scripts" / "validate_dhatu_canonical_write_approval.py"
SIMULATE_APPROVAL_SCRIPT_PATH = ROOT / "scripts" / "simulate_dhatu_canonical_write_approval.py"
DRY_RUN_DIFF_SCRIPT_PATH = ROOT / "scripts" / "diff_dhatu_canonical_write_dry_run.py"
RELEASE_CHECKLIST_SCRIPT_PATH = ROOT / "scripts" / "build_dhatu_canonical_write_release_checklist.py"
APPROVAL_PACKAGE_SCRIPT_PATH = ROOT / "scripts" / "build_dhatu_canonical_write_approval_package.py"
RELEASE_VERIFICATION_SCRIPT_PATH = ROOT / "scripts" / "verify_dhatu_canonical_write_release.py"
PREFLIGHT_SNAPSHOT_SCRIPT_PATH = ROOT / "scripts" / "snapshot_dhatu_pre_canonical_write_state.py"
POST_AUDIT_VERIFICATION_SCRIPT_PATH = ROOT / "scripts" / "verify_dhatu_post_canonical_write_audit.py"
CLOSEOUT_INDEX_SCRIPT_PATH = ROOT / "scripts" / "index_dhatu_canonical_promotion_closeout.py"
MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "large_scale_manifest.v1.json"
REVIEW_DECISIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "review_decisions.v1.json"
READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
EVIDENCE_REPORT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
AUTHORIZATION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.v1.json"
COMMAND_MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_command_manifest.v1.json"
APPROVAL_VALIDATION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_validation.v1.json"
SIMULATED_APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.simulated.v1.json"
DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"
RELEASE_CHECKLIST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_checklist.v1.json"
APPROVAL_PACKAGE_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_package.v1.md"
RELEASE_VERIFICATION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_verification.v1.json"
PREFLIGHT_SNAPSHOT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_preflight_snapshot.v1.json"
POST_AUDIT_VERIFICATION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_post_audit_verification.v1.json"
RUNBOOK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_runbook.v1.md"
CLOSEOUT_INDEX_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_closeout_index.v1.json"
FIXTURE_ROOT = ROOT / "data" / "sanskrit" / "ingestion" / "fixtures"
BASELINE_BLOCKED_FIXTURE_ROOT = FIXTURE_ROOT / "baseline_blocked"
EXECUTED_WRITE_FIXTURE_ROOT = FIXTURE_ROOT / "executed_write"
RAW_BATCH_ROOT = ROOT / "raw" / "dhatupatha_batches"
BHVADI_BATCH = RAW_BATCH_ROOT / "01_bhvadi" / "bhvadi_batch_001.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
GOLDSET_ROOT = ROOT / "data" / "sanskrit" / "goldset"
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
PROMOTED_SOURCE_IDS = ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"]
PROMOTED_CANONICAL_IDS = ["01.0005", "01.0013", "01.0008"]


def load_fixture_json(fixture_root, filename):
    return json.loads((fixture_root / filename).read_text(encoding="utf-8"))


spec = importlib.util.spec_from_file_location("validate_large_scale_ingestion", SCRIPT_PATH)
validator = importlib.util.module_from_spec(spec)
sys.modules["validate_large_scale_ingestion"] = validator
spec.loader.exec_module(validator)

preview_spec = importlib.util.spec_from_file_location("preview_dhatu_batch_promotion", PREVIEW_SCRIPT_PATH)
previewer = importlib.util.module_from_spec(preview_spec)
sys.modules["preview_dhatu_batch_promotion"] = previewer
preview_spec.loader.exec_module(previewer)

plan_spec = importlib.util.spec_from_file_location("plan_dhatu_canonical_promotion", PLAN_SCRIPT_PATH)
planner = importlib.util.module_from_spec(plan_spec)
sys.modules["plan_dhatu_canonical_promotion"] = planner
plan_spec.loader.exec_module(planner)

review_spec = importlib.util.spec_from_file_location("apply_dhatu_review_decisions", REVIEW_SCRIPT_PATH)
reviewer = importlib.util.module_from_spec(review_spec)
sys.modules["apply_dhatu_review_decisions"] = reviewer
review_spec.loader.exec_module(reviewer)

lock_spec = importlib.util.spec_from_file_location("lock_dhatu_promotion_readiness", LOCK_SCRIPT_PATH)
locker = importlib.util.module_from_spec(lock_spec)
sys.modules["lock_dhatu_promotion_readiness"] = locker
lock_spec.loader.exec_module(locker)

promote_spec = importlib.util.spec_from_file_location("promote_ready_dhatu_to_canonical", PROMOTE_SCRIPT_PATH)
promoter = importlib.util.module_from_spec(promote_spec)
sys.modules["promote_ready_dhatu_to_canonical"] = promoter
promote_spec.loader.exec_module(promoter)

evidence_spec = importlib.util.spec_from_file_location("report_dhatu_promotion_evidence", EVIDENCE_SCRIPT_PATH)
evidence_reporter = importlib.util.module_from_spec(evidence_spec)
sys.modules["report_dhatu_promotion_evidence"] = evidence_reporter
evidence_spec.loader.exec_module(evidence_reporter)

authorization_spec = importlib.util.spec_from_file_location("authorize_dhatu_canonical_write", AUTHORIZATION_SCRIPT_PATH)
authorizer = importlib.util.module_from_spec(authorization_spec)
sys.modules["authorize_dhatu_canonical_write"] = authorizer
authorization_spec.loader.exec_module(authorizer)

command_spec = importlib.util.spec_from_file_location("prepare_dhatu_canonical_write_command", COMMAND_SCRIPT_PATH)
command_preparer = importlib.util.module_from_spec(command_spec)
sys.modules["prepare_dhatu_canonical_write_command"] = command_preparer
command_spec.loader.exec_module(command_preparer)

approval_validation_spec = importlib.util.spec_from_file_location(
    "validate_dhatu_canonical_write_approval",
    APPROVAL_VALIDATION_SCRIPT_PATH,
)
approval_validator = importlib.util.module_from_spec(approval_validation_spec)
sys.modules["validate_dhatu_canonical_write_approval"] = approval_validator
approval_validation_spec.loader.exec_module(approval_validator)

simulate_approval_spec = importlib.util.spec_from_file_location(
    "simulate_dhatu_canonical_write_approval",
    SIMULATE_APPROVAL_SCRIPT_PATH,
)
approval_simulator = importlib.util.module_from_spec(simulate_approval_spec)
sys.modules["simulate_dhatu_canonical_write_approval"] = approval_simulator
simulate_approval_spec.loader.exec_module(approval_simulator)

dry_run_diff_spec = importlib.util.spec_from_file_location(
    "diff_dhatu_canonical_write_dry_run",
    DRY_RUN_DIFF_SCRIPT_PATH,
)
dry_run_differ = importlib.util.module_from_spec(dry_run_diff_spec)
sys.modules["diff_dhatu_canonical_write_dry_run"] = dry_run_differ
dry_run_diff_spec.loader.exec_module(dry_run_differ)

release_checklist_spec = importlib.util.spec_from_file_location(
    "build_dhatu_canonical_write_release_checklist",
    RELEASE_CHECKLIST_SCRIPT_PATH,
)
release_checklister = importlib.util.module_from_spec(release_checklist_spec)
sys.modules["build_dhatu_canonical_write_release_checklist"] = release_checklister
release_checklist_spec.loader.exec_module(release_checklister)

approval_package_spec = importlib.util.spec_from_file_location(
    "build_dhatu_canonical_write_approval_package",
    APPROVAL_PACKAGE_SCRIPT_PATH,
)
approval_packager = importlib.util.module_from_spec(approval_package_spec)
sys.modules["build_dhatu_canonical_write_approval_package"] = approval_packager
approval_package_spec.loader.exec_module(approval_packager)

release_verification_spec = importlib.util.spec_from_file_location(
    "verify_dhatu_canonical_write_release",
    RELEASE_VERIFICATION_SCRIPT_PATH,
)
release_verifier = importlib.util.module_from_spec(release_verification_spec)
sys.modules["verify_dhatu_canonical_write_release"] = release_verifier
release_verification_spec.loader.exec_module(release_verifier)

preflight_snapshot_spec = importlib.util.spec_from_file_location(
    "snapshot_dhatu_pre_canonical_write_state",
    PREFLIGHT_SNAPSHOT_SCRIPT_PATH,
)
preflight_snapshooter = importlib.util.module_from_spec(preflight_snapshot_spec)
sys.modules["snapshot_dhatu_pre_canonical_write_state"] = preflight_snapshooter
preflight_snapshot_spec.loader.exec_module(preflight_snapshooter)

post_audit_verification_spec = importlib.util.spec_from_file_location(
    "verify_dhatu_post_canonical_write_audit",
    POST_AUDIT_VERIFICATION_SCRIPT_PATH,
)
post_audit_verifier = importlib.util.module_from_spec(post_audit_verification_spec)
sys.modules["verify_dhatu_post_canonical_write_audit"] = post_audit_verifier
post_audit_verification_spec.loader.exec_module(post_audit_verifier)

closeout_index_spec = importlib.util.spec_from_file_location(
    "index_dhatu_canonical_promotion_closeout",
    CLOSEOUT_INDEX_SCRIPT_PATH,
)
closeout_indexer = importlib.util.module_from_spec(closeout_index_spec)
sys.modules["index_dhatu_canonical_promotion_closeout"] = closeout_indexer
closeout_index_spec.loader.exec_module(closeout_indexer)


class LargeScaleIngestionTests(unittest.TestCase):
    def setUp(self):
        self.payload = validator.load_large_scale_manifest(MANIFEST_PATH)

    def _write_pre_promotion_registry_fixture(self, registry_path):
        registry = json.loads(promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))
        for record_id, record in list(registry.get("records", {}).items()):
            promotion = record.get("promotion", {})
            if promotion.get("sourceRootId") in PROMOTED_SOURCE_IDS:
                registry["records"].pop(record_id)
        registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
        return registry

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

    def test_preview_script_exists(self):
        self.assertTrue(PREVIEW_SCRIPT_PATH.exists())

    def test_plan_script_exists(self):
        self.assertTrue(PLAN_SCRIPT_PATH.exists())

    def test_review_script_and_decisions_exist(self):
        self.assertTrue(REVIEW_SCRIPT_PATH.exists())
        self.assertTrue(REVIEW_DECISIONS_PATH.exists())

    def test_lock_script_exists(self):
        self.assertTrue(LOCK_SCRIPT_PATH.exists())

    def test_promote_script_exists(self):
        self.assertTrue(PROMOTE_SCRIPT_PATH.exists())

    def test_evidence_report_script_exists(self):
        self.assertTrue(EVIDENCE_SCRIPT_PATH.exists())

    def test_authorization_script_exists(self):
        self.assertTrue(AUTHORIZATION_SCRIPT_PATH.exists())

    def test_command_manifest_script_exists(self):
        self.assertTrue(COMMAND_SCRIPT_PATH.exists())

    def test_approval_validation_script_exists(self):
        self.assertTrue(APPROVAL_VALIDATION_SCRIPT_PATH.exists())

    def test_simulated_approval_script_exists(self):
        self.assertTrue(SIMULATE_APPROVAL_SCRIPT_PATH.exists())

    def test_dry_run_diff_script_exists(self):
        self.assertTrue(DRY_RUN_DIFF_SCRIPT_PATH.exists())

    def test_release_checklist_script_exists(self):
        self.assertTrue(RELEASE_CHECKLIST_SCRIPT_PATH.exists())

    def test_approval_package_script_exists(self):
        self.assertTrue(APPROVAL_PACKAGE_SCRIPT_PATH.exists())

    def test_release_verification_script_exists(self):
        self.assertTrue(RELEASE_VERIFICATION_SCRIPT_PATH.exists())

    def test_preflight_snapshot_script_exists(self):
        self.assertTrue(PREFLIGHT_SNAPSHOT_SCRIPT_PATH.exists())

    def test_post_audit_verification_script_exists(self):
        self.assertTrue(POST_AUDIT_VERIFICATION_SCRIPT_PATH.exists())

    def test_closeout_index_script_exists(self):
        self.assertTrue(CLOSEOUT_INDEX_SCRIPT_PATH.exists())

    def test_canonical_write_approval_file_exists(self):
        self.assertTrue(APPROVAL_PATH.exists())

    def test_canonical_write_runbook_exists(self):
        self.assertTrue(RUNBOOK_PATH.exists())

    def test_canonical_promotion_closeout_index_exists(self):
        self.assertTrue(CLOSEOUT_INDEX_PATH.exists())

    def test_canonical_write_fixture_folders_exist(self):
        self.assertTrue(BASELINE_BLOCKED_FIXTURE_ROOT.exists())
        self.assertTrue(EXECUTED_WRITE_FIXTURE_ROOT.exists())

    def test_first_bhvadi_batch_file_exists(self):
        self.assertTrue(BHVADI_BATCH.exists())
        bhvadi = validator.find_gana_batch(self.payload, "01")

        self.assertIn("raw/dhatupatha_batches/01_bhvadi/bhvadi_batch_001.json", bhvadi["batchFiles"])

    def test_discovered_batch_files_match_manifest_entries(self):
        discovered = validator.discover_staged_batch_files()
        manifest_files = validator.list_manifest_batch_files(self.payload)

        self.assertEqual(discovered, manifest_files)
        self.assertEqual(self.payload["batchFileCount"], len(discovered))

    def test_first_bhvadi_batch_json_is_valid(self):
        payload = json.loads(BHVADI_BATCH.read_text(encoding="utf-8"))

        self.assertEqual(payload["ganaId"], "01")
        self.assertGreaterEqual(len(payload["records"]), 10)
        self.assertLessEqual(len(payload["records"]), 25)

    def test_first_bhvadi_batch_records_have_required_fields(self):
        records = validator.scan_raw_batch_directory("raw/dhatupatha_batches/01_bhvadi")
        required = {"root_id", "devanagari", "iast", "gana", "pada", "artha", "source", "status"}

        self.assertGreaterEqual(len(records), 10)
        for record in records:
            self.assertTrue(required.issubset(record), record)
            self.assertEqual(record["status"], "staged")
            self.assertEqual(record["gana"], "01")

    def test_live_canonical_registry_has_promoted_records_after_write(self):
        registry = json.loads(promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))
        records = registry["records"]

        self.assertEqual(len(records), 13)
        for canonical_id, source_id in zip(PROMOTED_CANONICAL_IDS, PROMOTED_SOURCE_IDS):
            self.assertIn(canonical_id, records)
            self.assertEqual(records[canonical_id]["promotion"]["sourceRootId"], source_id)

    def test_live_canonical_registry_has_no_duplicate_dhatu_ids_after_write(self):
        registry = json.loads(promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))
        ids = list(registry["records"].keys())

        self.assertEqual(len(ids), len(set(ids)))

    def test_live_post_write_audit_records_three_promotions(self):
        audit = json.loads(POST_AUDIT_VERIFICATION_PATH.read_text(encoding="utf-8"))

        self.assertEqual(audit["promotedCount"], 3)
        self.assertEqual(audit["afterCount"], 13)
        self.assertEqual(audit["promotedRecordIds"], PROMOTED_SOURCE_IDS)

    def test_first_bhvadi_batch_root_ids_are_unique(self):
        records = validator.scan_raw_batch_directory("raw/dhatupatha_batches/01_bhvadi")

        self.assertEqual(validator.detect_duplicate_ids(records), [])

    def test_global_root_ids_are_unique_across_staged_batches(self):
        batch_records = validator.scan_all_staged_batch_files(self.payload)

        self.assertEqual(validator.detect_cross_batch_collisions(batch_records), {})

    def test_first_bhvadi_batch_readiness_has_records(self):
        readiness = validator.validate_batch_readiness(validator.find_gana_batch(self.payload, "01"))

        self.assertEqual(readiness["recordCount"], 12)
        self.assertEqual(readiness["errors"], [])

    def test_validate_large_scale_manifest_passes(self):
        validated = validator.validate_large_scale_manifest(copy.deepcopy(self.payload))

        self.assertEqual(validated["manifestVersion"], "1.0.0")

    def test_manifest_batch_file_count_mismatch_fails(self):
        payload = copy.deepcopy(self.payload)
        payload["batchFileCount"] = 2

        with self.assertRaises(ValueError):
            validator.validate_large_scale_manifest(payload)

    def test_manifest_missing_discovered_batch_file_fails(self):
        payload = copy.deepcopy(self.payload)
        payload["ganaBatches"][0]["batchFiles"] = []
        payload["batchFileCount"] = 0

        with self.assertRaises(ValueError):
            validator.validate_large_scale_manifest(payload)

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

    def test_manifest_declares_promotion_preview_file(self):
        self.assertEqual(
            self.payload["promotionPreviewFile"],
            "data/sanskrit/ingestion/promotion_preview.v1.json",
        )

    def test_manifest_declares_canonical_promotion_plan_file(self):
        self.assertEqual(
            self.payload["canonicalPromotionPlanFile"],
            "data/sanskrit/ingestion/canonical_promotion_plan.v1.json",
        )

    def test_manifest_declares_review_gate_files(self):
        self.assertEqual(
            self.payload["reviewDecisionsFile"],
            "data/sanskrit/ingestion/review_decisions.v1.json",
        )
        self.assertEqual(
            self.payload["reviewedCanonicalPromotionPlanFile"],
            "data/sanskrit/ingestion/canonical_promotion_plan.reviewed.v1.json",
        )

    def test_manifest_declares_promotion_readiness_lock_file(self):
        self.assertEqual(
            self.payload["promotionReadinessLockFile"],
            "data/sanskrit/ingestion/promotion_readiness_lock.v1.json",
        )

    def test_manifest_declares_canonical_promotion_audit_file(self):
        self.assertEqual(
            self.payload["canonicalPromotionAuditFile"],
            "data/sanskrit/ingestion/canonical_promotion_audit.v1.json",
        )

    def test_manifest_declares_dhatu_promotion_evidence_report_file(self):
        self.assertEqual(
            self.payload["dhatuPromotionEvidenceReportFile"],
            "data/sanskrit/ingestion/dhatu_promotion_evidence_report.v1.json",
        )

    def test_manifest_declares_canonical_write_authorization_file(self):
        self.assertEqual(
            self.payload["canonicalWriteAuthorizationFile"],
            "data/sanskrit/ingestion/canonical_write_authorization.v1.json",
        )

    def test_manifest_declares_canonical_write_approval_and_command_files(self):
        self.assertEqual(
            self.payload["canonicalWriteApprovalFile"],
            "data/sanskrit/ingestion/canonical_write_approval.v1.json",
        )
        self.assertEqual(
            self.payload["canonicalWriteCommandManifestFile"],
            "data/sanskrit/ingestion/canonical_write_command_manifest.v1.json",
        )

    def test_manifest_declares_canonical_write_approval_validation_file(self):
        self.assertEqual(
            self.payload["canonicalWriteApprovalValidationFile"],
            "data/sanskrit/ingestion/canonical_write_approval_validation.v1.json",
        )

    def test_manifest_declares_simulated_canonical_write_approval_file(self):
        self.assertEqual(
            self.payload["canonicalWriteSimulatedApprovalFile"],
            "data/sanskrit/ingestion/canonical_write_approval.simulated.v1.json",
        )

    def test_manifest_declares_canonical_write_dry_run_diff_file(self):
        self.assertEqual(
            self.payload["canonicalWriteDryRunDiffFile"],
            "data/sanskrit/ingestion/canonical_write_dry_run_diff.v1.json",
        )

    def test_manifest_declares_canonical_write_release_checklist_file(self):
        self.assertEqual(
            self.payload["canonicalWriteReleaseChecklistFile"],
            "data/sanskrit/ingestion/canonical_write_release_checklist.v1.json",
        )

    def test_manifest_declares_canonical_write_approval_package_file(self):
        self.assertEqual(
            self.payload["canonicalWriteApprovalPackageFile"],
            "data/sanskrit/ingestion/canonical_write_approval_package.v1.md",
        )

    def test_manifest_declares_canonical_write_release_verification_file(self):
        self.assertEqual(
            self.payload["canonicalWriteReleaseVerificationFile"],
            "data/sanskrit/ingestion/canonical_write_release_verification.v1.json",
        )

    def test_manifest_declares_canonical_write_preflight_snapshot_file(self):
        self.assertEqual(
            self.payload["canonicalWritePreflightSnapshotFile"],
            "data/sanskrit/ingestion/canonical_write_preflight_snapshot.v1.json",
        )

    def test_manifest_declares_canonical_write_post_audit_verification_file(self):
        self.assertEqual(
            self.payload["canonicalWritePostAuditVerificationFile"],
            "data/sanskrit/ingestion/canonical_write_post_audit_verification.v1.json",
        )

    def test_manifest_declares_canonical_write_runbook_file(self):
        self.assertEqual(
            self.payload["canonicalWriteRunbookFile"],
            "data/sanskrit/ingestion/canonical_write_runbook.v1.md",
        )

    def test_manifest_declares_canonical_promotion_closeout_index_file(self):
        self.assertEqual(
            self.payload["canonicalPromotionCloseoutIndexFile"],
            "data/sanskrit/ingestion/canonical_promotion_closeout_index.v1.json",
        )

    def test_manifest_declares_canonical_write_fixture_roots(self):
        self.assertEqual(
            self.payload["canonicalWriteBaselineBlockedFixtureRoot"],
            "data/sanskrit/ingestion/fixtures/baseline_blocked",
        )
        self.assertEqual(
            self.payload["canonicalWriteExecutedFixtureRoot"],
            "data/sanskrit/ingestion/fixtures/executed_write",
        )

    def test_canonical_write_runbook_contains_required_operational_guidance(self):
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

        self.assertIn("Do not set `AIGAANE_ENABLE_CANONICAL_DHATU_WRITE`", runbook)
        self.assertIn("approval validation", runbook)
        self.assertIn("post-write audit verification", runbook)
        self.assertIn("rollback reference", runbook)
        self.assertIn("sanskrit-v43-post-canonical-write-audit-verification-stable", runbook)

    def test_default_canonical_promotion_closeout_index_is_blocked(self):
        index = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_promotion_closeout_index.v1.json")

        self.assertEqual(index["schemaVersion"], "1.0.0")
        self.assertEqual(index["closeoutStatus"], "BLOCKED_NO_PRODUCTION_WRITE")
        self.assertFalse(index["safetySummary"]["approvalValid"])
        self.assertFalse(index["safetySummary"]["safeToProceed"])
        self.assertIn("canonicalWriteRunbook", [entry["name"] for entry in index["artifactIndex"]])

    def test_baseline_blocked_fixtures_preserve_blocked_gate_states(self):
        approval = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_approval.v1.json")
        validation = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_approval_validation.v1.json")
        authorization = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_authorization.v1.json")
        command = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_command_manifest.v1.json")
        dry_run = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_dry_run_diff.v1.json")
        checklist = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_release_checklist.v1.json")
        verification = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_release_verification.v1.json")
        preflight = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_preflight_snapshot.v1.json")
        post_audit = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_post_audit_verification.v1.json")

        self.assertEqual(approval["approvalStatus"], "NOT_APPROVED")
        self.assertFalse(validation["approvalValid"])
        self.assertEqual(authorization["authorizationStatus"], "AWAITING_HUMAN_APPROVAL")
        self.assertEqual(command["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertEqual(dry_run["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertEqual(checklist["releaseStatus"], "BLOCKED")
        self.assertEqual(verification["verificationStatus"], "BLOCKED")
        self.assertEqual(preflight["snapshotStatus"], "BLOCKED_PREWRITE")
        self.assertEqual(post_audit["verificationStatus"], "BLOCKED_NO_PRODUCTION_WRITE")

    def test_executed_write_fixtures_preserve_approved_ready_verified_states(self):
        approval = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_approval.v1.json")
        validation = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_approval_validation.v1.json")
        authorization = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_authorization.v1.json")
        command = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_command_manifest.v1.json")
        checklist = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_release_checklist.v1.json")
        verification = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_release_verification.v1.json")
        post_audit = load_fixture_json(EXECUTED_WRITE_FIXTURE_ROOT, "canonical_write_post_audit_verification.v1.json")

        self.assertEqual(approval["approvalStatus"], "APPROVED")
        self.assertTrue(validation["approvalValid"])
        self.assertEqual(authorization["authorizationStatus"], "AUTHORIZED_FOR_MANUAL_WRITE")
        self.assertEqual(command["commandStatus"], "READY_FOR_MANUAL_EXECUTION")
        self.assertEqual(checklist["releaseStatus"], "READY_FOR_MANUAL_PRODUCTION_WRITE")
        self.assertEqual(verification["verificationStatus"], "READY")
        self.assertEqual(post_audit["verificationStatus"], "VERIFIED_TEST_WRITE")
        self.assertEqual(post_audit["promotedCount"], 3)

    def test_closeout_index_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            index = closeout_indexer.build_closeout_index(MANIFEST_PATH)
            path = closeout_indexer.write_closeout_index(
                index,
                Path(tmp) / "canonical_promotion_closeout_index.v1.json",
            )

            self.assertTrue(path.exists())
            written = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(written["generatedBy"], "scripts/index_dhatu_canonical_promotion_closeout.py")

    def test_promotion_preview_reports_staged_totals(self):
        preview = previewer.build_promotion_preview(MANIFEST_PATH)

        self.assertEqual(preview["previewVersion"], "1.0.0")
        self.assertEqual(preview["mode"], "dry-run-preview")
        self.assertEqual(preview["totalStagedRecords"], 12)
        self.assertEqual(preview["recordsByGana"], {"01": 12})
        self.assertEqual(preview["recordsByPada"], {"atmanepada": 2, "parasmaipada": 10})

    def test_promotion_preview_does_not_allow_mutation(self):
        preview = previewer.build_promotion_preview(MANIFEST_PATH)

        self.assertFalse(preview["canonicalMutation"])
        self.assertFalse(preview["goldsetMutation"])
        self.assertFalse(preview["batchMutation"])

    def test_promotion_preview_duplicate_candidates_are_empty_for_current_batch(self):
        preview = previewer.build_promotion_preview(MANIFEST_PATH)

        self.assertEqual(preview["duplicateCanonicalCandidates"], [])

    def test_duplicate_canonical_candidates_are_detected_in_fixture_data(self):
        duplicates = previewer.detect_duplicate_canonical_candidates(
            [
                {"root_id": "A", "gana": "01", "devanagari": "गम्", "iast": "gam"},
                {"root_id": "B", "gana": "01", "devanagari": "गम्", "iast": "gam"},
                {"root_id": "C", "gana": "01", "devanagari": "स्था", "iast": "stha"},
            ]
        )

        self.assertEqual(duplicates[0]["rootIds"], ["A", "B"])

    def test_promotion_preview_reports_missing_optional_metadata(self):
        preview = previewer.build_promotion_preview(MANIFEST_PATH)

        self.assertEqual(len(preview["missingOptionalMetadata"]), 12)
        self.assertIn("01.STAGED.0001", preview["missingOptionalMetadata"])
        self.assertIn("upadesha", preview["missingOptionalMetadata"]["01.STAGED.0001"])

    def test_preview_summary_contains_required_counts(self):
        preview = previewer.build_promotion_preview(MANIFEST_PATH)
        summary = previewer.build_summary(preview)

        self.assertEqual(summary["totalStagedRecords"], 12)
        self.assertEqual(summary["recordsByGana"], {"01": 12})
        self.assertFalse(summary["canonicalMutation"])

    def test_canonical_promotion_plan_reports_review_counts(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)

        self.assertEqual(plan["schemaVersion"], "1.0.0")
        self.assertEqual(plan["totalRecords"], 12)
        self.assertEqual(plan["readyCount"], 0)
        self.assertEqual(plan["needsReviewCount"], 12)
        self.assertEqual(plan["blockedCount"], 0)

    def test_canonical_promotion_plan_assigns_deterministic_ids(self):
        plan_one = planner.build_canonical_promotion_plan(MANIFEST_PATH)
        plan_two = planner.build_canonical_promotion_plan(MANIFEST_PATH)
        ids_one = [record["proposedCanonicalId"] for record in plan_one["plannedRecords"]]
        ids_two = [record["proposedCanonicalId"] for record in plan_two["plannedRecords"]]

        self.assertEqual(ids_one, ids_two)
        self.assertEqual(ids_one, [f"01.{value:04d}" for value in range(3, 15)])

    def test_canonical_promotion_plan_safety_checks_prevent_mutation(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)

        self.assertTrue(plan["safetyChecks"]["stagedValidationPassed"])
        self.assertTrue(plan["safetyChecks"]["promotionPreviewRegenerated"])
        self.assertFalse(plan["safetyChecks"]["canonicalRegistryMutation"])
        self.assertFalse(plan["safetyChecks"]["goldsetMutation"])
        self.assertFalse(plan["safetyChecks"]["batchMutation"])

    def test_canonical_promotion_plan_conflict_summary_is_empty_for_current_batch(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)

        self.assertEqual(plan["conflictSummary"]["totalConflicts"], 0)
        self.assertEqual(plan["conflictSummary"]["blockedRootIds"], [])

    def test_canonical_conflict_blocks_record_in_fixture_data(self):
        canonical = {
            "ids": {"01.0003"},
            "rootsByGana": {"01": {"गम्"}},
            "iastByGana": {"01": {"gam"}},
        }
        record = {
            "root_id": "X",
            "devanagari": "गम्",
            "iast": "gam",
            "gana": "01",
        }
        conflicts = planner.detect_record_conflicts(record, "01.0003", canonical, set())

        self.assertEqual(planner.classify_record(conflicts, []), "blocked")
        self.assertIn("proposedCanonicalId already exists", conflicts)
        self.assertIn("canonical root already exists in gana", conflicts)
        self.assertIn("canonical IAST root already exists in gana", conflicts)

    def test_ready_classification_requires_no_conflicts_or_missing_optional_metadata(self):
        self.assertEqual(planner.classify_record([], []), "ready")
        self.assertEqual(planner.classify_record([], ["upadesha"]), "needs_review")
        self.assertEqual(planner.classify_record(["canonical root already exists in gana"], []), "blocked")

    def test_review_decisions_load_and_default_to_defer(self):
        decisions = reviewer.load_review_decisions(REVIEW_DECISIONS_PATH)

        self.assertEqual(decisions["policy"]["defaultDecision"], "defer")
        self.assertEqual(len(decisions["decisions"]), 12)
        self.assertEqual(
            {
                root_id
                for root_id, decision in decisions["decisions"].items()
                if decision["decision"] == "approve"
            },
            {"01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"},
        )

    def test_reviewed_plan_applies_seeded_approvals_and_defers_remainder(self):
        reviewed = reviewer.build_reviewed_promotion_plan(MANIFEST_PATH, REVIEW_DECISIONS_PATH)

        self.assertEqual(reviewed["totalRecords"], 12)
        self.assertEqual(reviewed["readyCount"], 3)
        self.assertEqual(reviewed["needsReviewCount"], 9)
        self.assertEqual(reviewed["blockedCount"], 0)
        self.assertEqual(reviewer.decision_counts(reviewed["plannedRecords"]), {"approve": 3, "defer": 9})

    def test_missing_review_decisions_still_default_to_defer_in_fixture_data(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)
        decisions = {
            "schemaVersion": "1.0.0",
            "policy": {
                "defaultDecision": "defer",
                "canonicalMutation": False,
                "goldsetMutation": False,
                "batchMutation": False,
            },
            "decisions": {},
        }
        reviewed = reviewer.apply_review_decisions(plan, reviewer.validate_review_decisions(decisions))

        self.assertEqual(reviewed["readyCount"], 0)
        self.assertEqual(reviewed["needsReviewCount"], 12)
        self.assertEqual(reviewer.decision_counts(reviewed["plannedRecords"]), {"defer": 12})

    def test_review_approve_converts_needs_review_to_ready(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)
        decisions = {
            "schemaVersion": "1.0.0",
            "policy": {
                "defaultDecision": "defer",
                "canonicalMutation": False,
                "goldsetMutation": False,
                "batchMutation": False,
            },
            "decisions": {
                plan["plannedRecords"][0]["sourceRootId"]: {
                    "decision": "approve",
                    "reviewer": "unit-reviewer",
                    "rationale": "Fixture approval",
                }
            },
        }
        reviewed = reviewer.apply_review_decisions(plan, reviewer.validate_review_decisions(decisions))

        self.assertEqual(reviewed["readyCount"], 1)
        self.assertEqual(reviewed["needsReviewCount"], 11)
        self.assertEqual(reviewed["blockedCount"], 0)

    def test_review_reject_converts_record_to_blocked(self):
        plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)
        decisions = {
            "schemaVersion": "1.0.0",
            "policy": {
                "defaultDecision": "defer",
                "canonicalMutation": False,
                "goldsetMutation": False,
                "batchMutation": False,
            },
            "decisions": {
                plan["plannedRecords"][0]["sourceRootId"]: {
                    "decision": "reject",
                    "reviewer": "unit-reviewer",
                    "rationale": "Fixture rejection",
                }
            },
        }
        reviewed = reviewer.apply_review_decisions(plan, reviewer.validate_review_decisions(decisions))
        record = reviewed["plannedRecords"][0]

        self.assertEqual(reviewed["blockedCount"], 1)
        self.assertEqual(record["classification"], "blocked")
        self.assertIn("reviewer rejected", record["conflicts"])

    def test_blocked_records_remain_blocked_after_approval(self):
        record = {
            "sourceRootId": "X",
            "classification": "blocked",
            "conflicts": ["canonical root already exists in gana"],
        }
        reviewed = reviewer.apply_decision_to_record(
            record,
            {"decision": "approve", "reviewer": "unit-reviewer", "rationale": "Fixture approval"},
        )

        self.assertEqual(reviewed["classification"], "blocked")

    def test_ready_records_remain_ready_unless_rejected(self):
        record = {
            "sourceRootId": "X",
            "classification": "ready",
            "conflicts": [],
        }
        deferred = reviewer.apply_decision_to_record(
            record,
            {"decision": "defer", "reviewer": "unit-reviewer", "rationale": "Fixture defer"},
        )
        rejected = reviewer.apply_decision_to_record(
            record,
            {"decision": "reject", "reviewer": "unit-reviewer", "rationale": "Fixture rejection"},
        )

        self.assertEqual(deferred["classification"], "ready")
        self.assertEqual(rejected["classification"], "blocked")

    def test_invalid_review_decision_fails_validation(self):
        payload = {
            "schemaVersion": "1.0.0",
            "policy": {
                "defaultDecision": "defer",
                "canonicalMutation": False,
                "goldsetMutation": False,
                "batchMutation": False,
            },
            "decisions": {
                "X": {"decision": "maybe", "reviewer": "unit-reviewer", "rationale": "Invalid"}
            },
        }

        with self.assertRaises(ValueError):
            reviewer.validate_review_decisions(payload)

    def test_promotion_readiness_lock_reports_seeded_ready_records(self):
        lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)

        self.assertEqual(lock["schemaVersion"], "1.0.0")
        self.assertEqual(lock["totalRecords"], 12)
        self.assertEqual(lock["readyCount"], 3)
        self.assertEqual(lock["needsReviewCount"], 9)
        self.assertEqual(lock["blockedCount"], 0)
        self.assertEqual(
            lock["readyRecordIds"],
            ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"],
        )
        self.assertEqual(lock["blockedRecordIds"], [])
        self.assertEqual(len(lock["deferredRecordIds"]), 9)

    def test_promotion_readiness_lock_keeps_canonical_write_disabled(self):
        lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)

        self.assertFalse(lock["canonicalWriteEnabled"])
        self.assertFalse(lock["safetyChecks"]["canonicalRegistryMutation"])
        self.assertFalse(lock["safetyChecks"]["goldsetMutation"])
        self.assertFalse(lock["safetyChecks"]["batchMutation"])

    def test_promotion_readiness_lock_is_deterministic(self):
        lock_one = locker.build_promotion_readiness_lock(MANIFEST_PATH)
        lock_two = locker.build_promotion_readiness_lock(MANIFEST_PATH)

        self.assertEqual(lock_one, lock_two)

    def test_disabled_promotion_audit_refuses_canonical_write(self):
        lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)
        audit = promoter.build_disabled_audit(lock)

        self.assertFalse(audit["canonicalWriteAttempted"])
        self.assertFalse(audit["canonicalWriteEnabled"])
        self.assertEqual(audit["promotedCount"], 0)
        self.assertEqual(audit["promotedRecordIds"], [])
        self.assertEqual(len(audit["skippedRecordIds"]), 12)
        self.assertIn("AIGAANE_ENABLE_CANONICAL_DHATU_WRITE", audit["refusalReason"])

    def test_default_promotion_path_writes_disabled_audit_only(self):
        import os
        import tempfile

        lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)
        original = os.environ.pop(promoter.WRITE_FLAG, None)
        try:
            with tempfile.TemporaryDirectory(prefix="disabled-audit-") as tmp:
                audit = promoter.build_disabled_audit(lock)
                path = promoter.write_promotion_audit(
                    audit,
                    Path(tmp) / "canonical_promotion_audit.v1.json",
                )

                self.assertTrue(path.exists())
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), audit)
                self.assertFalse(audit["canonicalWriteEnabled"])
        finally:
            if original is not None:
                os.environ[promoter.WRITE_FLAG] = original

    def test_enabled_flag_alone_refuses_canonical_write(self):
        import os
        import shutil
        import tempfile

        original_write = os.environ.get(promoter.WRITE_FLAG)
        original_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        try:
            os.environ[promoter.WRITE_FLAG] = "1"
            os.environ.pop(promoter.TEST_WRITE_FLAG, None)
            with tempfile.TemporaryDirectory(prefix="unsafe-promotion-") as tmp:
                registry_path = Path(tmp) / "index.json"
                audit_path = Path(tmp) / "audit.json"
                shutil.copyfile(promoter.DEFAULT_CANONICAL_REGISTRY_PATH, registry_path)
                before = registry_path.read_text(encoding="utf-8")

                exit_code = promoter.main(
                    [
                        "--manifest",
                        str(MANIFEST_PATH),
                        "--audit",
                        str(audit_path),
                        "--canonical-registry",
                        str(registry_path),
                    ]
                )
                audit = json.loads(audit_path.read_text(encoding="utf-8"))

                self.assertEqual(exit_code, 1)
                self.assertTrue(audit["canonicalWriteAttempted"])
                self.assertTrue(audit["canonicalWriteEnabled"])
                self.assertFalse(audit["writeGuardSatisfied"])
                self.assertTrue(audit["unsafeWriteRefused"])
                self.assertEqual(audit["promotedCount"], 0)
                self.assertEqual(before, registry_path.read_text(encoding="utf-8"))
        finally:
            if original_write is None:
                os.environ.pop(promoter.WRITE_FLAG, None)
            else:
                os.environ[promoter.WRITE_FLAG] = original_write
            if original_guard is None:
                os.environ.pop(promoter.TEST_WRITE_FLAG, None)
            else:
                os.environ[promoter.TEST_WRITE_FLAG] = original_guard

    def test_guarded_test_write_promotes_only_ready_records_to_temp_registry(self):
        import os
        import shutil
        import tempfile

        original_write = os.environ.get(promoter.WRITE_FLAG)
        original_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        try:
            os.environ[promoter.WRITE_FLAG] = "1"
            os.environ[promoter.TEST_WRITE_FLAG] = "1"
            with tempfile.TemporaryDirectory(prefix="guarded-promotion-") as tmp:
                registry_path = Path(tmp) / "index.json"
                audit_path = Path(tmp) / "audit.json"
                self._write_pre_promotion_registry_fixture(registry_path)
                before = json.loads(registry_path.read_text(encoding="utf-8"))
                lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)

                audit = promoter.promote_ready_dhatus(
                    MANIFEST_PATH,
                    audit_path=audit_path,
                    canonical_registry_path=registry_path,
                )
                after = json.loads(registry_path.read_text(encoding="utf-8"))

                self.assertTrue(audit["canonicalWriteAttempted"])
                self.assertTrue(audit["canonicalWriteEnabled"])
                self.assertTrue(audit["writeGuardSatisfied"])
                self.assertFalse(audit["unsafeWriteRefused"])
                self.assertEqual(audit["promotedCount"], len(lock["readyRecordIds"]))
                self.assertEqual(sorted(audit["promotedRecordIds"]), sorted(lock["readyRecordIds"]))
                self.assertEqual(
                    audit["skippedRecordIds"],
                    sorted(set(lock["deferredRecordIds"]) | set(lock["blockedRecordIds"])),
                )
                self.assertEqual(
                    audit["canonicalRegistryAfterCount"],
                    audit["canonicalRegistryBeforeCount"] + len(lock["readyRecordIds"]),
                )
                self.assertEqual(
                    len(after["records"]),
                    len(before["records"]) + len(lock["readyRecordIds"]),
                )
                self.assertTrue(audit["contractChecks"]["passed"])
                for source_id in lock["readyRecordIds"]:
                    self.assertIn(source_id, audit["promotedRecordIds"])
        finally:
            if original_write is None:
                os.environ.pop(promoter.WRITE_FLAG, None)
            else:
                os.environ[promoter.WRITE_FLAG] = original_write
            if original_guard is None:
                os.environ.pop(promoter.TEST_WRITE_FLAG, None)
            else:
                os.environ[promoter.TEST_WRITE_FLAG] = original_guard

    def test_default_promotion_does_not_modify_original_canonical_registry(self):
        import os
        import tempfile

        original_write = os.environ.pop(promoter.WRITE_FLAG, None)
        original_guard = os.environ.pop(promoter.TEST_WRITE_FLAG, None)
        before = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        try:
            with tempfile.TemporaryDirectory(prefix="default-promotion-audit-") as tmp:
                audit = promoter.promote_ready_dhatus(
                    MANIFEST_PATH,
                    audit_path=Path(tmp) / "audit.json",
                )

                self.assertFalse(audit["canonicalWriteAttempted"])
                self.assertFalse(audit["canonicalWriteEnabled"])
                self.assertFalse(audit["writeGuardSatisfied"])
                self.assertFalse(audit["unsafeWriteRefused"])
                self.assertEqual(before, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))
        finally:
            if original_write is not None:
                os.environ[promoter.WRITE_FLAG] = original_write
            if original_guard is not None:
                os.environ[promoter.TEST_WRITE_FLAG] = original_guard

    def test_evidence_report_default_release_gate_is_blocked(self):
        report = evidence_reporter.build_evidence_report(MANIFEST_PATH)

        self.assertEqual(report["schemaVersion"], "1.0.0")
        self.assertEqual(report["releaseGateStatus"], "BLOCKED")
        self.assertFalse(report["guardPolicy"]["canonicalWriteEnabled"])
        self.assertFalse(report["guardPolicy"]["writeGuardSatisfied"])
        self.assertEqual(
            report["sourceFiles"]["canonicalPromotionAudit"],
            "data/sanskrit/ingestion/canonical_promotion_audit.v1.json",
        )
        self.assertEqual(report["counts"]["previewTotalStagedRecords"], 12)
        self.assertEqual(report["readyRecordIds"], ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"])
        self.assertEqual(len(report["skippedRecordIds"]), 12)
        self.assertTrue(report["contractSummary"]["passed"])

    def test_evidence_report_ready_only_when_both_write_guards_satisfied(self):
        audit = {
            "canonicalWriteEnabled": True,
            "writeGuardSatisfied": True,
        }

        self.assertEqual(evidence_reporter.release_gate_status(audit), "READY_FOR_CONTROLLED_WRITE")
        self.assertEqual(evidence_reporter.release_gate_status({"canonicalWriteEnabled": True}), "BLOCKED")
        self.assertEqual(evidence_reporter.release_gate_status({"writeGuardSatisfied": True}), "BLOCKED")

    def test_canonical_write_authorization_defaults_to_human_approval(self):
        import os

        before_write_flag = os.environ.get(promoter.WRITE_FLAG)
        before_test_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        authorization = authorizer.build_authorization(
            approval_validation_path=BASELINE_BLOCKED_FIXTURE_ROOT / "canonical_write_approval_validation.v1.json",
        )

        self.assertEqual(authorization["schemaVersion"], "1.0.0")
        self.assertEqual(authorization["authorizationStatus"], "AWAITING_HUMAN_APPROVAL")
        self.assertTrue(authorization["humanApprovalRequired"])
        self.assertEqual(authorization["authorizedRecordIds"], ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"])
        self.assertEqual(len(authorization["blockedRecordIds"]), 9)
        self.assertEqual(
            set(authorization["requiredEnvironment"].keys()),
            {promoter.WRITE_FLAG, promoter.TEST_WRITE_FLAG},
        )
        self.assertFalse(authorization["requiredEnvironment"][promoter.WRITE_FLAG]["currentlySatisfied"])
        self.assertFalse(authorization["requiredEnvironment"][promoter.TEST_WRITE_FLAG]["currentlySatisfied"])
        self.assertEqual(authorization["evidenceSummary"]["releaseGateStatus"], "BLOCKED")
        self.assertIn("approvalValidationSummary", authorization)
        self.assertFalse(authorization["safetyChecks"]["evidenceReleaseGateReady"])
        self.assertFalse(authorization["safetyChecks"]["canonicalRegistryMutation"])
        self.assertTrue(authorization["safetyChecks"]["environmentFlagsUnchangedByAuthorization"])
        self.assertEqual(os.environ.get(promoter.WRITE_FLAG), before_write_flag)
        self.assertEqual(os.environ.get(promoter.TEST_WRITE_FLAG), before_test_guard)

    def test_canonical_write_authorization_transitions_when_approval_and_release_ready(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="canonical-authorization-ready-") as tmp:
            readiness_lock = json.loads(READINESS_LOCK_PATH.read_text(encoding="utf-8"))
            ready_ids = sorted(readiness_lock["readyRecordIds"])
            evidence = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
            evidence["releaseGateStatus"] = "READY_FOR_CONTROLLED_WRITE"
            evidence.setdefault("contractSummary", {})["passed"] = True
            approval_validation = json.loads(APPROVAL_VALIDATION_PATH.read_text(encoding="utf-8"))
            approval_validation["approvalStatus"] = "APPROVED"
            approval_validation["approvalValid"] = True
            approval_validation["approvedRecordIds"] = ready_ids
            approval_validation["missingAuthorizedRecordIds"] = []
            approval_validation["unexpectedApprovedRecordIds"] = []
            evidence_path = Path(tmp) / "evidence.json"
            approval_validation_path = Path(tmp) / "approval_validation.json"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            approval_validation_path.write_text(json.dumps(approval_validation), encoding="utf-8")

            authorization = authorizer.build_authorization(
                evidence_path=evidence_path,
                approval_validation_path=approval_validation_path,
            )

            self.assertEqual(authorization["authorizationStatus"], "AUTHORIZED_FOR_MANUAL_WRITE")
            self.assertTrue(authorization["approvalValidationSummary"]["approvalValid"])
            self.assertTrue(authorization["approvalValidationSummary"]["approvedRecordIdsMatchAuthorizedRecordIds"])
            self.assertTrue(authorization["safetyChecks"]["evidenceReleaseGateReady"])

    def test_canonical_write_authorization_waits_when_approved_ids_do_not_match(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="canonical-authorization-mismatch-") as tmp:
            evidence = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
            evidence["releaseGateStatus"] = "READY_FOR_CONTROLLED_WRITE"
            evidence.setdefault("contractSummary", {})["passed"] = True
            approval_validation = json.loads(APPROVAL_VALIDATION_PATH.read_text(encoding="utf-8"))
            approval_validation["approvalStatus"] = "APPROVED"
            approval_validation["approvalValid"] = True
            approval_validation["approvedRecordIds"] = ["01.STAGED.0001"]
            evidence_path = Path(tmp) / "evidence.json"
            approval_validation_path = Path(tmp) / "approval_validation.json"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            approval_validation_path.write_text(json.dumps(approval_validation), encoding="utf-8")

            authorization = authorizer.build_authorization(
                evidence_path=evidence_path,
                approval_validation_path=approval_validation_path,
            )

            self.assertEqual(authorization["authorizationStatus"], "AWAITING_HUMAN_APPROVAL")
            self.assertFalse(authorization["approvalValidationSummary"]["approvedRecordIdsMatchAuthorizedRecordIds"])

    def test_canonical_write_authorization_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="canonical-authorization-") as tmp:
            authorization = authorizer.build_authorization()
            path = authorizer.write_authorization(
                authorization,
                Path(tmp) / "canonical_write_authorization.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), authorization)

    def test_canonical_write_approval_defaults_to_not_approved(self):
        approval = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_approval.v1.json")

        self.assertEqual(approval["schemaVersion"], "1.0.0")
        self.assertEqual(approval["approvalStatus"], "NOT_APPROVED")
        self.assertIsNone(approval["approvedBy"])
        self.assertIsNone(approval["approvedAt"])
        self.assertEqual(approval["approvedRecordIds"], [])
        self.assertTrue(approval["approvalNotes"])
        self.assertTrue(approval["requiredBeforeWrite"])

    def test_simulated_approval_is_test_only_and_does_not_overwrite_default(self):
        import tempfile

        before_default = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="simulated-approval-") as tmp:
            approval = approval_simulator.build_simulated_approval()
            path = approval_simulator.write_simulated_approval(
                approval,
                Path(tmp) / "canonical_write_approval.simulated.v1.json",
            )
            simulated = json.loads(path.read_text(encoding="utf-8"))
            after_default = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))

            self.assertTrue(simulated["testOnly"])
            self.assertEqual(simulated["approvalStatus"], "APPROVED")
            self.assertEqual(simulated["approvedBy"], "test-fixture")
            self.assertEqual(simulated["approvedRecordIds"], ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"])
            self.assertEqual(after_default, before_default)

    def test_simulated_approval_validates_as_valid(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="simulated-validation-") as tmp:
            approval_path = Path(tmp) / "canonical_write_approval.simulated.v1.json"
            approval_simulator.write_simulated_approval(
                approval_simulator.build_simulated_approval(),
                approval_path,
            )
            validation = approval_validator.build_approval_validation(approval_path)

            self.assertEqual(validation["approvalStatus"], "APPROVED")
            self.assertTrue(validation["approvalValid"])
            self.assertEqual(validation["approvedRecordIds"], ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"])
            self.assertEqual(validation["missingAuthorizedRecordIds"], [])
            self.assertEqual(validation["unexpectedApprovedRecordIds"], [])
            self.assertFalse(validation["safetyChecks"]["writerExecuted"])
            self.assertFalse(validation["safetyChecks"]["canonicalRegistryMutation"])

    def test_canonical_write_command_manifest_refuses_without_approval(self):
        import os

        before_write_flag = os.environ.get(promoter.WRITE_FLAG)
        before_test_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        manifest = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_command_manifest.v1.json")

        self.assertEqual(manifest["schemaVersion"], "1.0.0")
        self.assertEqual(manifest["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertEqual(manifest["approvedRecordIds"], [])
        self.assertEqual(len(manifest["blockedRecordIds"]), 12)
        self.assertFalse(manifest["safetyChecks"]["writerExecuted"])
        self.assertFalse(manifest["safetyChecks"]["canonicalRegistryMutation"])
        self.assertFalse(manifest["safetyChecks"]["approvalTokenApproved"])
        self.assertFalse(manifest["safetyChecks"]["approvalValidationValid"])
        self.assertFalse(manifest["authorizationSummary"]["authorizationReady"])
        self.assertFalse(manifest["approvalValidationSummary"]["approvalValid"])
        self.assertIn("exactPowerShellCommand", manifest)
        self.assertIn("exactCmdCommand", manifest)
        self.assertIn("python", manifest["commandPreview"]["argv"])
        self.assertIn("scripts/promote_ready_dhatu_to_canonical.py", manifest["commandPreview"]["argv"])
        self.assertIn("Approval validation failed.", manifest["refusalReasons"])
        self.assertEqual(os.environ.get(promoter.WRITE_FLAG), before_write_flag)
        self.assertEqual(os.environ.get(promoter.TEST_WRITE_FLAG), before_test_guard)

    def test_default_command_manifest_remains_refused_after_simulated_validation(self):
        manifest = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_command_manifest.v1.json")

        self.assertEqual(manifest["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertFalse(manifest["approvalValidationSummary"]["approvalValid"])

    def test_canonical_write_command_manifest_refuses_when_authorization_not_ready(self):
        import tempfile

        validation = json.loads(APPROVAL_VALIDATION_PATH.read_text(encoding="utf-8"))
        validation["approvalStatus"] = "APPROVED"
        validation["approvalValid"] = True
        validation["approvedRecordIds"] = ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"]
        validation["missingAuthorizedRecordIds"] = []
        validation["unexpectedApprovedRecordIds"] = []
        validation["refusalReasons"] = []
        with tempfile.TemporaryDirectory(prefix="command-auth-not-ready-") as tmp:
            validation_path = Path(tmp) / "validation.json"
            authorization_path = Path(tmp) / "authorization.json"
            validation_path.write_text(json.dumps(validation), encoding="utf-8")
            authorization_path.write_text(
                (BASELINE_BLOCKED_FIXTURE_ROOT / "canonical_write_authorization.v1.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            manifest = command_preparer.build_command_manifest(
                authorization_path=authorization_path,
                approval_validation_path=validation_path,
            )

            self.assertEqual(manifest["commandStatus"], "REFUSED_AUTHORIZATION_NOT_READY")
            self.assertTrue(manifest["approvalValidationSummary"]["approvalValid"])
            self.assertFalse(manifest["authorizationSummary"]["authorizationReady"])
            self.assertIn(
                "Authorization packet is not marked AUTHORIZED_FOR_MANUAL_WRITE.",
                manifest["refusalReasons"],
            )

    def test_simulated_validation_can_reach_ready_with_ready_authorization(self):
        import tempfile

        authorization = json.loads(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
        authorization["authorizationStatus"] = "AUTHORIZED_FOR_MANUAL_WRITE"
        for requirement in authorization["requiredEnvironment"].values():
            requirement["currentlySatisfied"] = True
        evidence = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
        evidence["releaseGateStatus"] = "READY_FOR_CONTROLLED_WRITE"
        with tempfile.TemporaryDirectory(prefix="simulated-ready-chain-") as tmp:
            approval_path = Path(tmp) / "approval.simulated.json"
            validation_path = Path(tmp) / "validation.json"
            authorization_path = Path(tmp) / "authorization.json"
            evidence_path = Path(tmp) / "evidence.json"
            approval_simulator.write_simulated_approval(
                approval_simulator.build_simulated_approval(),
                approval_path,
            )
            validation = approval_validator.build_approval_validation(approval_path)
            approval_validator.write_approval_validation(validation, validation_path)
            authorization_path.write_text(json.dumps(authorization), encoding="utf-8")
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            manifest = command_preparer.build_command_manifest(
                authorization_path=authorization_path,
                approval_path=approval_path,
                approval_validation_path=validation_path,
                evidence_path=evidence_path,
            )

            self.assertTrue(validation["approvalValid"])
            self.assertEqual(manifest["commandStatus"], "READY_FOR_MANUAL_EXECUTION")
            self.assertFalse(manifest["safetyChecks"]["writerExecuted"])
            self.assertFalse(manifest["safetyChecks"]["canonicalRegistryMutation"])

    def _build_ready_command_fixture(self, tmp):
        authorization = json.loads(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
        authorization["authorizationStatus"] = "AUTHORIZED_FOR_MANUAL_WRITE"
        for requirement in authorization["requiredEnvironment"].values():
            requirement["currentlySatisfied"] = True
        evidence = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
        evidence["releaseGateStatus"] = "READY_FOR_CONTROLLED_WRITE"
        approval_path = Path(tmp) / "approval.simulated.json"
        validation_path = Path(tmp) / "validation.json"
        authorization_path = Path(tmp) / "authorization.json"
        evidence_path = Path(tmp) / "evidence.json"
        command_path = Path(tmp) / "command.json"
        approval_simulator.write_simulated_approval(approval_simulator.build_simulated_approval(), approval_path)
        validation = approval_validator.build_approval_validation(approval_path)
        approval_validator.write_approval_validation(validation, validation_path)
        authorization_path.write_text(json.dumps(authorization), encoding="utf-8")
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        command = command_preparer.build_command_manifest(
            authorization_path=authorization_path,
            approval_path=approval_path,
            approval_validation_path=validation_path,
            evidence_path=evidence_path,
        )
        command_preparer.write_command_manifest(command, command_path)
        return command_path, validation_path

    def test_default_canonical_write_dry_run_diff_is_refused(self):
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        diff = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_dry_run_diff.v1.json")

        self.assertTrue(diff["dryRunOnly"])
        self.assertEqual(diff["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertEqual(diff["recordsToAdd"], [])
        self.assertEqual(diff["beforeCount"], diff["afterCountIfApplied"])
        self.assertIn("Command manifest is not READY_FOR_MANUAL_EXECUTION.", diff["refusalReasons"])
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_simulated_ready_dry_run_diff_lists_records_to_add_against_temp_registry(self):
        import shutil
        import tempfile

        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="ready-dry-run-") as tmp:
            registry_path = Path(tmp) / "index.json"
            self._write_pre_promotion_registry_fixture(registry_path)
            command_path, validation_path = self._build_ready_command_fixture(tmp)
            diff = dry_run_differ.build_dry_run_diff(
                command_manifest_path=command_path,
                approval_validation_path=validation_path,
                canonical_registry_path=registry_path,
            )

            self.assertTrue(diff["dryRunOnly"])
            self.assertEqual(diff["commandStatus"], "READY_FOR_MANUAL_EXECUTION")
            self.assertEqual(len(diff["recordsToAdd"]), 3)
            self.assertEqual(diff["afterCountIfApplied"], diff["beforeCount"] + 3)
            self.assertEqual([record["sourceRootId"] for record in diff["recordsToAdd"]], [
                "01.STAGED.0001",
                "01.STAGED.0002",
                "01.STAGED.0003",
            ])
            self.assertEqual(diff["duplicateIds"], [])
            self.assertEqual(diff["missingStagedRecords"], [])
            self.assertTrue(diff["contractChecks"]["passed"])
            self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_duplicate_ids_block_canonical_write_dry_run_diff(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="duplicate-dry-run-") as tmp:
            registry_path = Path(tmp) / "index.json"
            self._write_pre_promotion_registry_fixture(registry_path)
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["records"]["01.0005"] = {"root": "fixture duplicate"}
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            command_path, validation_path = self._build_ready_command_fixture(tmp)
            diff = dry_run_differ.build_dry_run_diff(
                command_manifest_path=command_path,
                approval_validation_path=validation_path,
                canonical_registry_path=registry_path,
            )

            self.assertEqual(diff["recordsToAdd"], [])
            self.assertIn("01.0005", diff["duplicateIds"])
            self.assertFalse(diff["contractChecks"]["passed"])
            self.assertIn("Duplicate canonical ids would be created.", diff["refusalReasons"])

    def test_default_release_checklist_is_blocked(self):
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        checklist = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_release_checklist.v1.json")

        self.assertEqual(checklist["schemaVersion"], "1.0.0")
        self.assertEqual(checklist["releaseStatus"], "BLOCKED")
        self.assertFalse(checklist["safeToWriteProduction"])
        self.assertFalse(checklist["gateSummary"]["approvalValid"])
        self.assertEqual(checklist["gateSummary"]["commandStatus"], "REFUSED_APPROVAL_INVALID")
        self.assertTrue(checklist["gateSummary"]["dryRunOnly"])
        self.assertIn("Approval validation is not valid.", checklist["blockingReasons"])
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_release_checklist_safe_only_when_all_write_gates_are_green(self):
        authorization = {"authorizationStatus": "AUTHORIZED_FOR_MANUAL_WRITE"}
        approval_validation = {"approvalValid": True}
        command_manifest = {"commandStatus": "READY_FOR_MANUAL_EXECUTION"}
        dry_run_diff = {"dryRunOnly": True, "duplicateIds": [], "missingStagedRecords": []}

        self.assertTrue(
            release_checklister.safe_to_write(
                authorization,
                approval_validation,
                command_manifest,
                dry_run_diff,
            )
        )
        self.assertFalse(
            release_checklister.safe_to_write(
                authorization,
                approval_validation,
                command_manifest,
                {"dryRunOnly": True, "duplicateIds": ["01.0005"], "missingStagedRecords": []},
            )
        )
        self.assertFalse(
            release_checklister.safe_to_write(
                authorization,
                {"approvalValid": False},
                command_manifest,
                dry_run_diff,
            )
        )

    def test_release_checklist_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="release-checklist-") as tmp:
            checklist = release_checklister.build_release_checklist(MANIFEST_PATH)
            path = release_checklister.write_release_checklist(
                checklist,
                Path(tmp) / "canonical_write_release_checklist.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), checklist)

    def test_approval_package_contains_required_human_sections(self):
        before_approval = APPROVAL_PATH.read_text(encoding="utf-8")
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        markdown = approval_packager.build_approval_package()

        self.assertIn("# Canonical Write Approval Package", markdown)
        self.assertIn("Release status:", markdown)
        self.assertIn("Safe to write production:", markdown)
        self.assertIn("## Authorized Record IDs", markdown)
        self.assertIn("`01.STAGED.0001`", markdown)
        self.assertIn("## Ready Record IDs", markdown)
        self.assertIn("## Records That Would Be Added", markdown)
        self.assertIn("## Records Blocked Or Skipped", markdown)
        self.assertIn("## Exact Manual Approval Instructions", markdown)
        self.assertIn("## Exact Command Sequence After Approval", markdown)
        self.assertIn("No command should be run until human approval is edited, reviewed, and committed.", markdown)
        self.assertIn("python scripts/validate_dhatu_canonical_write_approval.py", markdown)
        self.assertEqual(before_approval, APPROVAL_PATH.read_text(encoding="utf-8"))
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_approval_package_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="approval-package-") as tmp:
            markdown = approval_packager.build_approval_package()
            path = approval_packager.write_approval_package(
                markdown,
                Path(tmp) / "canonical_write_approval_package.v1.md",
            )

            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(encoding="utf-8"), markdown)

    def test_default_release_verification_is_blocked(self):
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        verification = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_release_verification.v1.json")

        self.assertEqual(verification["schemaVersion"], "1.0.0")
        self.assertEqual(verification["verificationStatus"], "BLOCKED")
        self.assertFalse(verification["safeToProceed"])
        self.assertFalse(verification["consistencyChecks"]["checklistSafeToWriteProduction"])
        self.assertFalse(verification["consistencyChecks"]["commandReadyForManualExecution"])
        self.assertFalse(verification["consistencyChecks"]["approvalValidationValid"])
        self.assertTrue(verification["consistencyChecks"]["dryRunHasNoDuplicateIds"])
        self.assertTrue(verification["consistencyChecks"]["dryRunHasNoMissingStagedRecords"])
        self.assertTrue(verification["consistencyChecks"]["approvalPackageIncludesManualWarning"])
        self.assertIn("Release checklist is not safe for production write.", verification["blockingReasons"])
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_release_verification_requires_approval_package_warning(self):
        checks = release_verifier.build_consistency_checks(
            {"authorizedRecordIds": ["A"]},
            {"approvalValid": True, "approvedRecordIds": ["A"]},
            {"commandStatus": "READY_FOR_MANUAL_EXECUTION", "approvedRecordIds": ["A"]},
            {"dryRunOnly": True, "duplicateIds": [], "missingStagedRecords": []},
            {"safeToWriteProduction": True},
            "missing warning",
            {"readyRecordIds": ["A"]},
        )

        self.assertFalse(checks["approvalPackageIncludesManualWarning"])
        reasons = release_verifier.build_blocking_reasons(checks, [])
        self.assertIn("Approval package is missing the manual warning text.", reasons)

    def test_release_verification_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="release-verification-") as tmp:
            verification = release_verifier.build_release_verification(MANIFEST_PATH)
            path = release_verifier.write_release_verification(
                verification,
                Path(tmp) / "canonical_write_release_verification.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), verification)

    def test_default_preflight_snapshot_is_blocked_and_hashes_registry(self):
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        snapshot = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_preflight_snapshot.v1.json")

        self.assertEqual(snapshot["schemaVersion"], "1.0.0")
        self.assertEqual(snapshot["snapshotStatus"], "BLOCKED_PREWRITE")
        self.assertFalse(snapshot["safeToProceed"])
        self.assertTrue(snapshot["canonicalRegistrySha256"])
        self.assertEqual(len(snapshot["canonicalRegistrySha256"]), 64)
        self.assertTrue(snapshot["currentGitHead"])
        self.assertTrue(snapshot["currentBranch"])
        self.assertEqual(snapshot["canonicalRegistryRecordCount"], 10)
        self.assertEqual(snapshot["rollbackReference"]["canonicalRegistrySha256"], snapshot["canonicalRegistrySha256"])
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_preflight_snapshot_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="preflight-snapshot-") as tmp:
            snapshot = preflight_snapshooter.build_preflight_snapshot()
            path = preflight_snapshooter.write_preflight_snapshot(
                snapshot,
                Path(tmp) / "canonical_write_preflight_snapshot.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), snapshot)

    def test_default_post_audit_verification_blocks_no_production_write(self):
        before_registry = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        verification = load_fixture_json(BASELINE_BLOCKED_FIXTURE_ROOT, "canonical_write_post_audit_verification.v1.json")

        self.assertEqual(verification["schemaVersion"], "1.0.0")
        self.assertEqual(verification["verificationStatus"], "BLOCKED_NO_PRODUCTION_WRITE")
        self.assertFalse(verification["productionRegistryMutationDetected"])
        self.assertFalse(verification["canonicalWriteAttempted"])
        self.assertEqual(verification["promotedCount"], 0)
        self.assertEqual(verification["beforeCount"], verification["afterCount"])
        self.assertIn("Default state has no production canonical write to verify.", verification["blockingReasons"])
        self.assertEqual(before_registry, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_temp_registry_write_post_audit_verifies_count_delta(self):
        import os
        import shutil
        import tempfile

        original_write = os.environ.get(promoter.WRITE_FLAG)
        original_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        before_production = promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8")
        try:
            os.environ[promoter.WRITE_FLAG] = "1"
            os.environ[promoter.TEST_WRITE_FLAG] = "1"
            with tempfile.TemporaryDirectory(prefix="post-audit-temp-") as tmp:
                registry_path = Path(tmp) / "index.json"
                audit_path = Path(tmp) / "audit.json"
                dry_run_path = Path(tmp) / "dry-run.json"
                snapshot_path = Path(tmp) / "snapshot.json"
                self._write_pre_promotion_registry_fixture(registry_path)
                snapshot = preflight_snapshooter.build_preflight_snapshot(registry_path)
                preflight_snapshooter.write_preflight_snapshot(snapshot, snapshot_path)
                audit = promoter.promote_ready_dhatus(
                    MANIFEST_PATH,
                    audit_path=audit_path,
                    canonical_registry_path=registry_path,
                )
                dry_run = {
                    "recordsToAdd": [{"sourceRootId": source_id} for source_id in audit["promotedRecordIds"]],
                    "duplicateIds": [],
                    "missingStagedRecords": [],
                }
                dry_run_path.write_text(json.dumps(dry_run), encoding="utf-8")

                verification = post_audit_verifier.build_post_audit_verification(
                    preflight_snapshot_path=snapshot_path,
                    audit_file_path=audit_path,
                    dry_run_diff_path=dry_run_path,
                    canonical_registry_path=registry_path,
                )

                self.assertEqual(verification["verificationStatus"], "VERIFIED_TEST_WRITE")
                self.assertEqual(verification["promotedCount"], 3)
                self.assertEqual(verification["afterCount"], verification["beforeCount"] + 3)
                self.assertEqual(verification["expectedAfterCount"], verification["beforeCount"] + 3)
                self.assertFalse(verification["productionRegistryMutationDetected"])
                self.assertTrue(verification["consistencyChecks"]["promotedCountMatchesExpectedRecords"])
        finally:
            if original_write is None:
                os.environ.pop(promoter.WRITE_FLAG, None)
            else:
                os.environ[promoter.WRITE_FLAG] = original_write
            if original_guard is None:
                os.environ.pop(promoter.TEST_WRITE_FLAG, None)
            else:
                os.environ[promoter.TEST_WRITE_FLAG] = original_guard
        self.assertEqual(before_production, promoter.DEFAULT_CANONICAL_REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_mismatched_promoted_count_blocks_post_audit_verification(self):
        import os
        import shutil
        import tempfile

        original_write = os.environ.get(promoter.WRITE_FLAG)
        original_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        try:
            os.environ[promoter.WRITE_FLAG] = "1"
            os.environ[promoter.TEST_WRITE_FLAG] = "1"
            with tempfile.TemporaryDirectory(prefix="post-audit-mismatch-") as tmp:
                registry_path = Path(tmp) / "index.json"
                audit_path = Path(tmp) / "audit.json"
                dry_run_path = Path(tmp) / "dry-run.json"
                snapshot_path = Path(tmp) / "snapshot.json"
                self._write_pre_promotion_registry_fixture(registry_path)
                preflight_snapshooter.write_preflight_snapshot(
                    preflight_snapshooter.build_preflight_snapshot(registry_path),
                    snapshot_path,
                )
                audit = promoter.promote_ready_dhatus(
                    MANIFEST_PATH,
                    audit_path=audit_path,
                    canonical_registry_path=registry_path,
                )
                audit["promotedCount"] = audit["promotedCount"] + 1
                audit_path.write_text(json.dumps(audit), encoding="utf-8")
                dry_run_path.write_text(
                    json.dumps({
                        "recordsToAdd": [{"sourceRootId": source_id} for source_id in audit["promotedRecordIds"]],
                        "duplicateIds": [],
                        "missingStagedRecords": [],
                    }),
                    encoding="utf-8",
                )

                verification = post_audit_verifier.build_post_audit_verification(
                    preflight_snapshot_path=snapshot_path,
                    audit_file_path=audit_path,
                    dry_run_diff_path=dry_run_path,
                    canonical_registry_path=registry_path,
                )

                self.assertEqual(verification["verificationStatus"], "BLOCKED_AUDIT_MISMATCH")
                self.assertFalse(verification["consistencyChecks"]["promotedCountMatchesExpectedRecords"])
                self.assertIn(
                    "Audit promoted count does not match expected records to add.",
                    verification["blockingReasons"],
                )
        finally:
            if original_write is None:
                os.environ.pop(promoter.WRITE_FLAG, None)
            else:
                os.environ[promoter.WRITE_FLAG] = original_write
            if original_guard is None:
                os.environ.pop(promoter.TEST_WRITE_FLAG, None)
            else:
                os.environ[promoter.TEST_WRITE_FLAG] = original_guard

    def test_post_audit_verification_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="post-audit-writer-") as tmp:
            verification = post_audit_verifier.build_post_audit_verification()
            path = post_audit_verifier.write_post_audit_verification(
                verification,
                Path(tmp) / "canonical_write_post_audit_verification.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), verification)

    def test_canonical_write_command_manifest_ready_when_validation_and_authorization_ready(self):
        import tempfile

        authorization = json.loads(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
        authorization["authorizationStatus"] = "AUTHORIZED_FOR_MANUAL_WRITE"
        for requirement in authorization["requiredEnvironment"].values():
            requirement["currentlySatisfied"] = True
        validation = json.loads(APPROVAL_VALIDATION_PATH.read_text(encoding="utf-8"))
        validation["approvalStatus"] = "APPROVED"
        validation["approvalValid"] = True
        validation["approvedRecordIds"] = ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"]
        validation["missingAuthorizedRecordIds"] = []
        validation["unexpectedApprovedRecordIds"] = []
        validation["refusalReasons"] = []
        evidence = json.loads(EVIDENCE_REPORT_PATH.read_text(encoding="utf-8"))
        evidence["releaseGateStatus"] = "READY_FOR_CONTROLLED_WRITE"
        with tempfile.TemporaryDirectory(prefix="command-ready-") as tmp:
            authorization_path = Path(tmp) / "authorization.json"
            validation_path = Path(tmp) / "validation.json"
            evidence_path = Path(tmp) / "evidence.json"
            authorization_path.write_text(json.dumps(authorization), encoding="utf-8")
            validation_path.write_text(json.dumps(validation), encoding="utf-8")
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            manifest = command_preparer.build_command_manifest(
                authorization_path=authorization_path,
                approval_validation_path=validation_path,
                evidence_path=evidence_path,
            )

            self.assertEqual(manifest["commandStatus"], "READY_FOR_MANUAL_EXECUTION")
            self.assertEqual(manifest["approvedRecordIds"], ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"])
            self.assertEqual(len(manifest["blockedRecordIds"]), 9)
            self.assertEqual(manifest["refusalReasons"], [])
            self.assertIn("AIGAANE_ENABLE_CANONICAL_DHATU_WRITE", manifest["exactPowerShellCommand"])
            self.assertIn("set AIGAANE_ENABLE_CANONICAL_DHATU_WRITE=1", manifest["exactCmdCommand"])

    def test_canonical_write_command_manifest_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="canonical-command-") as tmp:
            manifest = command_preparer.build_command_manifest()
            path = command_preparer.write_command_manifest(
                manifest,
                Path(tmp) / "canonical_write_command_manifest.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), manifest)

    def test_canonical_write_approval_validation_default_is_invalid(self):
        import os

        before_write_flag = os.environ.get(promoter.WRITE_FLAG)
        before_test_guard = os.environ.get(promoter.TEST_WRITE_FLAG)
        validation = approval_validator.build_approval_validation(
            BASELINE_BLOCKED_FIXTURE_ROOT / "canonical_write_approval.v1.json",
            authorization_path=BASELINE_BLOCKED_FIXTURE_ROOT / "canonical_write_authorization.v1.json",
        )

        self.assertEqual(validation["schemaVersion"], "1.0.0")
        self.assertEqual(validation["approvalStatus"], "NOT_APPROVED")
        self.assertFalse(validation["approvalValid"])
        self.assertEqual(validation["approvedRecordIds"], [])
        self.assertEqual(
            validation["missingAuthorizedRecordIds"],
            ["01.STAGED.0001", "01.STAGED.0002", "01.STAGED.0003"],
        )
        self.assertEqual(validation["unexpectedApprovedRecordIds"], [])
        self.assertFalse(validation["safetyChecks"]["writerExecuted"])
        self.assertFalse(validation["safetyChecks"]["canonicalRegistryMutation"])
        self.assertTrue(validation["safetyChecks"]["approvedIdsSubsetOfAuthorization"])
        self.assertIn("Approval status is not APPROVED.", validation["refusalReasons"])
        self.assertEqual(os.environ.get(promoter.WRITE_FLAG), before_write_flag)
        self.assertEqual(os.environ.get(promoter.TEST_WRITE_FLAG), before_test_guard)

    def test_approved_empty_record_ids_fail_approval_validation(self):
        import tempfile

        approval = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
        approval["approvalStatus"] = "APPROVED"
        approval["approvedBy"] = "unit-reviewer"
        approval["approvedAt"] = "2026-05-21T00:00:00Z"
        approval["approvedRecordIds"] = []
        with tempfile.TemporaryDirectory(prefix="empty-approval-") as tmp:
            approval_path = Path(tmp) / "approval.json"
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            validation = approval_validator.build_approval_validation(approval_path)

            self.assertFalse(validation["approvalValid"])
            self.assertIn(
                "Approved approval token must include at least one approvedRecordId.",
                validation["refusalReasons"],
            )

    def test_unexpected_approved_ids_fail_approval_validation(self):
        import tempfile

        approval = json.loads(APPROVAL_PATH.read_text(encoding="utf-8"))
        approval["approvalStatus"] = "APPROVED"
        approval["approvedBy"] = "unit-reviewer"
        approval["approvedAt"] = "2026-05-21T00:00:00Z"
        approval["approvedRecordIds"] = ["01.STAGED.0001", "01.STAGED.9999"]
        with tempfile.TemporaryDirectory(prefix="unexpected-approval-") as tmp:
            approval_path = Path(tmp) / "approval.json"
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            validation = approval_validator.build_approval_validation(approval_path)

            self.assertFalse(validation["approvalValid"])
            self.assertEqual(validation["unexpectedApprovedRecordIds"], ["01.STAGED.9999"])
            self.assertFalse(validation["safetyChecks"]["approvedIdsSubsetOfAuthorization"])
            self.assertIn("Approval includes ids outside canonical write authorization.", validation["refusalReasons"])

    def test_canonical_write_approval_validation_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="approval-validation-") as tmp:
            validation = approval_validator.build_approval_validation()
            path = approval_validator.write_approval_validation(
                validation,
                Path(tmp) / "canonical_write_approval_validation.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), validation)

    def test_duplicate_ids_are_detected_in_fixture_data(self):
        records = [{"root_id": "01.0001"}, {"root_id": "01.0001"}, {"root_id": "01.0002"}]

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

    def test_empty_batch_file_fails_validation(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="empty-batch-") as tmp:
            path = Path(tmp) / "empty.json"
            path.write_text(json.dumps({"records": []}), encoding="utf-8")

            with self.assertRaises(ValueError):
                validator._validate_json_batch_file(path, validator.find_gana_batch(self.payload, "01"))

    def test_validation_does_not_modify_canonical_or_goldset_files(self):
        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }

        validator.build_large_scale_readiness_report(self.payload)

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)

    def test_preview_does_not_modify_canonical_goldset_or_batch_files(self):
        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        before_batch = BHVADI_BATCH.read_text(encoding="utf-8")

        previewer.build_promotion_preview(MANIFEST_PATH)

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)
        self.assertEqual(before_batch, BHVADI_BATCH.read_text(encoding="utf-8"))

    def test_planner_does_not_modify_canonical_goldset_or_batch_files(self):
        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        before_batch = BHVADI_BATCH.read_text(encoding="utf-8")

        planner.build_canonical_promotion_plan(MANIFEST_PATH)

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)
        self.assertEqual(before_batch, BHVADI_BATCH.read_text(encoding="utf-8"))

    def test_review_resolver_does_not_modify_canonical_goldset_or_batch_files(self):
        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        before_batch = BHVADI_BATCH.read_text(encoding="utf-8")

        reviewer.build_reviewed_promotion_plan(MANIFEST_PATH, REVIEW_DECISIONS_PATH)

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)
        self.assertEqual(before_batch, BHVADI_BATCH.read_text(encoding="utf-8"))

    def test_readiness_lock_does_not_modify_canonical_goldset_or_batch_files(self):
        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        before_batch = BHVADI_BATCH.read_text(encoding="utf-8")

        locker.build_promotion_readiness_lock(MANIFEST_PATH)

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)
        self.assertEqual(before_batch, BHVADI_BATCH.read_text(encoding="utf-8"))

    def test_disabled_promoter_does_not_modify_protected_files(self):
        import os

        before_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        before_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        before_batch = BHVADI_BATCH.read_text(encoding="utf-8")
        before_reviews = REVIEW_DECISIONS_PATH.read_text(encoding="utf-8")
        before_lock = READINESS_LOCK_PATH.read_text(encoding="utf-8")
        original = os.environ.pop(promoter.WRITE_FLAG, None)
        try:
            promoter.promote_ready_dhatus(MANIFEST_PATH)
        finally:
            if original is not None:
                os.environ[promoter.WRITE_FLAG] = original

        after_dhatus = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(DHATU_ROOT.glob("*.json"))
        }
        after_goldset = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(GOLDSET_ROOT.glob("*.json"))
        }
        self.assertEqual(before_dhatus, after_dhatus)
        self.assertEqual(before_goldset, after_goldset)
        self.assertEqual(before_batch, BHVADI_BATCH.read_text(encoding="utf-8"))
        self.assertEqual(before_reviews, REVIEW_DECISIONS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(before_lock, READINESS_LOCK_PATH.read_text(encoding="utf-8"))

    def test_validator_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_preview_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in PREVIEW_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_plan_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in PLAN_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_review_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in REVIEW_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_lock_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in LOCK_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_promote_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in PROMOTE_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_evidence_report_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in EVIDENCE_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_authorization_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in AUTHORIZATION_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_command_manifest_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in COMMAND_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_approval_validation_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in APPROVAL_VALIDATION_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_simulated_approval_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in SIMULATE_APPROVAL_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_dry_run_diff_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in DRY_RUN_DIFF_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_release_checklist_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in RELEASE_CHECKLIST_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_approval_package_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in APPROVAL_PACKAGE_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_release_verification_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in RELEASE_VERIFICATION_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_preflight_snapshot_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in PREFLIGHT_SNAPSHOT_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_post_audit_verification_script_does_not_import_runtime_grammar_engines(self):
        import_lines = [
            line.strip()
            for line in POST_AUDIT_VERIFICATION_SCRIPT_PATH.read_text(encoding="utf-8").splitlines()
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

    def test_preview_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="promotion-preview-") as tmp:
            preview = previewer.build_promotion_preview(MANIFEST_PATH)
            path = previewer.write_promotion_preview(preview, Path(tmp) / "promotion_preview.v1.json")

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), preview)

    def test_plan_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="canonical-plan-") as tmp:
            plan = planner.build_canonical_promotion_plan(MANIFEST_PATH)
            path = planner.write_canonical_promotion_plan(plan, Path(tmp) / "canonical_promotion_plan.v1.json")

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), plan)

    def test_reviewed_plan_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="reviewed-plan-") as tmp:
            reviewed = reviewer.build_reviewed_promotion_plan(MANIFEST_PATH, REVIEW_DECISIONS_PATH)
            path = reviewer.write_reviewed_promotion_plan(
                reviewed,
                Path(tmp) / "canonical_promotion_plan.reviewed.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), reviewed)

    def test_readiness_lock_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="readiness-lock-") as tmp:
            lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)
            path = locker.write_promotion_readiness_lock(
                lock,
                Path(tmp) / "promotion_readiness_lock.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), lock)

    def test_promotion_audit_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="promotion-audit-") as tmp:
            lock = locker.build_promotion_readiness_lock(MANIFEST_PATH)
            audit = promoter.build_disabled_audit(lock)
            path = promoter.write_promotion_audit(
                audit,
                Path(tmp) / "canonical_promotion_audit.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), audit)

    def test_evidence_report_writer_uses_requested_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory(prefix="promotion-evidence-") as tmp:
            report = evidence_reporter.build_evidence_report(MANIFEST_PATH)
            path = evidence_reporter.write_evidence_report(
                report,
                Path(tmp) / "dhatu_promotion_evidence_report.v1.json",
            )

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), report)


if __name__ == "__main__":
    unittest.main()
