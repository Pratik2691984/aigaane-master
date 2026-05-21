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
MANIFEST_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "large_scale_manifest.v1.json"
REVIEW_DECISIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "review_decisions.v1.json"
READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
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
                shutil.copyfile(promoter.DEFAULT_CANONICAL_REGISTRY_PATH, registry_path)
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


if __name__ == "__main__":
    unittest.main()
