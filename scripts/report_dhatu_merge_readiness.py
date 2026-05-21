#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


RELEASE_BRANCH = "release/dhatu-canonical-write-approval"
TARGET_BRANCH = "feature/dhatu-goldset"
RELEASE_TAG = "sanskrit-v50-canonical-write-state-fixtures-stable"
ARCHIVE_TAG = "sanskrit-v51-release-archive-stable"

DEFAULT_ARCHIVE_MANIFEST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "releases" / "v50" / "release_archive_manifest.v50.json"
)
DEFAULT_BASELINE_FIXTURE_ROOT = ROOT / "data" / "sanskrit" / "ingestion" / "fixtures" / "baseline_blocked"
DEFAULT_EXECUTED_FIXTURE_ROOT = ROOT / "data" / "sanskrit" / "ingestion" / "fixtures" / "executed_write"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"
DEFAULT_POST_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_post_audit_verification.v1.json"
DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "releases" / "v50" / "merge_readiness_report.v50.json"
)

FIXTURE_FILES = [
    "canonical_write_approval.v1.json",
    "canonical_write_approval_validation.v1.json",
    "canonical_write_authorization.v1.json",
    "canonical_write_command_manifest.v1.json",
    "canonical_write_dry_run_diff.v1.json",
    "canonical_write_release_checklist.v1.json",
    "canonical_write_release_verification.v1.json",
    "canonical_write_preflight_snapshot.v1.json",
    "canonical_write_post_audit_verification.v1.json",
    "canonical_promotion_closeout_index.v1.json",
]
EXECUTED_EXTRA_FILES = ["canonical_promotion_audit.v1.json"]


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def run_git(args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def load_json(path: Any) -> Dict[str, Any]:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Merge readiness source must be a JSON object: {resolved}")
    return payload


def tag_exists(tag: str) -> bool:
    return tag in run_git(["tag", "--list", tag]).splitlines()


def fixture_summary(root: Any, required_files: List[str]) -> Dict[str, Any]:
    base = resolve_path(root)
    missing = [name for name in required_files if not (base / name).exists()]
    return {
        "path": str(base.relative_to(ROOT)).replace("\\", "/") if base.is_relative_to(ROOT) else str(base),
        "exists": base.exists(),
        "requiredFileCount": len(required_files),
        "missingFiles": missing,
        "complete": base.exists() and not missing,
    }


def canonical_registry_integrity(registry: Dict[str, Any], promoted_record_ids: List[str]) -> Dict[str, Any]:
    records = registry.get("records", {})
    ids = list(records.keys())
    duplicate_ids = sorted({record_id for record_id in ids if ids.count(record_id) > 1})
    promoted_present = sorted(
        source_id
        for source_id in promoted_record_ids
        if any(record.get("promotion", {}).get("sourceRootId") == source_id for record in records.values())
    )
    return {
        "recordCount": len(records),
        "expectedRecordCount": 13,
        "recordCountMatchesExpected": len(records) == 13,
        "duplicateCanonicalIds": duplicate_ids,
        "noDuplicateCanonicalIds": duplicate_ids == [],
        "promotedRecordIdsPresent": promoted_present,
        "promotedRecordIdsPresentCount": len(promoted_present),
    }


def build_blocking_reasons(checks: Dict[str, bool]) -> List[str]:
    labels = {
        "archiveManifestExists": "Release archive manifest is missing.",
        "v50TagReferenced": "v50 release tag is not referenced or missing.",
        "v51TagReferenced": "v51 archive tag is not referenced or missing.",
        "canonicalRegistryCountIs13": "Canonical registry count is not 13.",
        "promotedCountIs3": "Post-write audit promotedCount is not 3.",
        "postWriteVerified": "Post-write verification is not VERIFIED_TEST_WRITE.",
        "baselineFixturesComplete": "Baseline blocked fixtures are incomplete.",
        "executedFixturesComplete": "Executed write fixtures are incomplete.",
        "noDuplicateCanonicalIds": "Canonical registry has duplicate ids.",
    }
    return [labels[key] for key, passed in checks.items() if not passed]


def build_merge_readiness_report(
    archive_manifest_path: Any = DEFAULT_ARCHIVE_MANIFEST_PATH,
    baseline_fixture_root: Any = DEFAULT_BASELINE_FIXTURE_ROOT,
    executed_fixture_root: Any = DEFAULT_EXECUTED_FIXTURE_ROOT,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    audit_path: Any = DEFAULT_AUDIT_PATH,
    post_audit_path: Any = DEFAULT_POST_AUDIT_PATH,
) -> Dict[str, Any]:
    archive_path = resolve_path(archive_manifest_path)
    archive_manifest = load_json(archive_path)
    registry = load_json(canonical_registry_path)
    audit = load_json(audit_path)
    post_audit = load_json(post_audit_path)
    promoted_ids = list(post_audit.get("promotedRecordIds", archive_manifest.get("promotedRecordIds", [])))
    fixture_integrity = {
        "baselineBlocked": fixture_summary(baseline_fixture_root, FIXTURE_FILES),
        "executedWrite": fixture_summary(executed_fixture_root, [*FIXTURE_FILES, *EXECUTED_EXTRA_FILES]),
    }
    registry_integrity = canonical_registry_integrity(registry, promoted_ids)
    release_tag = archive_manifest.get("releaseTag", RELEASE_TAG)
    tests_expected = archive_manifest.get("mergeReadinessChecks", {}).get("testSuitePassingExpectation", {})
    checks = {
        "archiveManifestExists": archive_path.exists(),
        "v50TagReferenced": release_tag == RELEASE_TAG and tag_exists(RELEASE_TAG),
        "v51TagReferenced": tag_exists(ARCHIVE_TAG),
        "canonicalRegistryCountIs13": registry_integrity["recordCountMatchesExpected"],
        "promotedCountIs3": int(post_audit.get("promotedCount", 0)) == 3,
        "postWriteVerified": post_audit.get("verificationStatus") == "VERIFIED_TEST_WRITE",
        "baselineFixturesComplete": fixture_integrity["baselineBlocked"]["complete"],
        "executedFixturesComplete": fixture_integrity["executedWrite"]["complete"],
        "noDuplicateCanonicalIds": registry_integrity["noDuplicateCanonicalIds"],
    }
    blocking_reasons = build_blocking_reasons(checks)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/report_dhatu_merge_readiness.py",
        "releaseBranch": RELEASE_BRANCH,
        "targetBranch": TARGET_BRANCH,
        "releaseTag": release_tag,
        "archiveTag": ARCHIVE_TAG,
        "canonicalRegistryRecordCount": registry_integrity["recordCount"],
        "promotedRecordIds": promoted_ids,
        "testsExpected": tests_expected,
        "mergeReadinessStatus": "READY_TO_OPEN_PR" if not blocking_reasons else "BLOCKED",
        "fixtureIntegrity": fixture_integrity,
        "postWriteAuditSummary": {
            "verificationStatus": post_audit.get("verificationStatus"),
            "promotedCount": int(post_audit.get("promotedCount", 0)),
            "expectedAfterCount": int(post_audit.get("expectedAfterCount", 0)),
            "afterCount": int(post_audit.get("afterCount", 0)),
            "productionRegistryMutationDetected": post_audit.get("productionRegistryMutationDetected") is True,
            "liveAuditPromotedCount": int(audit.get("promotedCount", 0)),
        },
        "canonicalRegistryIntegrity": registry_integrity,
        "blockingReasons": blocking_reasons,
        "recommendedPRTitle": "Release dhatu canonical write approval and v50 archive",
        "recommendedPRSummary": [
            "Promotes three approved Bhvadi dhatu records into the canonical registry.",
            "Adds blocked-baseline and executed-write fixtures for reproducible safety tests.",
            "Archives the v50 canonical promotion release state with hashes and merge-readiness evidence.",
            "Targets feature/dhatu-goldset after 712-test release evidence and current merge-readiness checks.",
        ],
    }


def write_merge_readiness_report(report: Dict[str, Any], output_path: Any = DEFAULT_OUTPUT_PATH) -> Path:
    path = resolve_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report dhatu canonical promotion merge readiness.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = build_merge_readiness_report()
        write_merge_readiness_report(report, args.output)
        print(json.dumps({
            "mergeReadinessStatus": report["mergeReadinessStatus"],
            "canonicalRegistryRecordCount": report["canonicalRegistryRecordCount"],
            "promotedCount": report["postWriteAuditSummary"]["promotedCount"],
        }, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu merge readiness report failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
