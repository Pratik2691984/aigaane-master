#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_PREFLIGHT_SNAPSHOT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_preflight_snapshot.v1.json"
)
DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"
DEFAULT_DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_POST_AUDIT_VERIFICATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_post_audit_verification.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Post-write audit verification source must be a JSON object.")
    return payload


def file_sha256(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def registry_count(registry_path: Any) -> int:
    return len(load_json(registry_path).get("records", {}))


def expected_records_to_add(dry_run_diff: Dict[str, Any], audit: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = dry_run_diff.get("recordsToAdd", [])
    if records:
        return records
    return [
        {"sourceRootId": source_id}
        for source_id in audit.get("promotedRecordIds", [])
    ]


def build_consistency_checks(
    audit: Dict[str, Any],
    preflight: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
    before_count: int,
    after_count: int,
    expected_after_count: int,
    registry_sha_before: str,
    registry_sha_after: str,
) -> Dict[str, bool]:
    promoted_count = int(audit.get("promotedCount", 0))
    expected_count = len(expected_records_to_add(dry_run_diff, audit))
    return {
        "preflightSnapshotPresent": bool(preflight.get("canonicalRegistrySha256")),
        "auditWriteAttempted": audit.get("canonicalWriteAttempted") is True,
        "auditWriteEnabled": audit.get("canonicalWriteEnabled") is True,
        "promotedCountMatchesExpectedRecords": promoted_count == expected_count,
        "promotedCountMatchesRecordIds": promoted_count == len(audit.get("promotedRecordIds", [])),
        "afterCountMatchesExpectedAfterCount": after_count == expected_after_count,
        "registryShaChangedOnlyWhenPromoted": (registry_sha_before != registry_sha_after) == (promoted_count > 0),
        "dryRunHadNoDuplicateIds": dry_run_diff.get("duplicateIds", []) == [],
        "dryRunHadNoMissingStagedRecords": dry_run_diff.get("missingStagedRecords", []) == [],
        "preflightBeforeCountMatchesRegistryBefore": int(preflight.get("canonicalRegistryRecordCount", before_count)) == before_count,
    }


def verification_status(audit: Dict[str, Any], checks: Dict[str, bool]) -> str:
    if audit.get("canonicalWriteAttempted") is not True or int(audit.get("promotedCount", 0)) == 0:
        return "BLOCKED_NO_PRODUCTION_WRITE"
    if all(checks.values()):
        return "VERIFIED_TEST_WRITE"
    return "BLOCKED_AUDIT_MISMATCH"


def build_blocking_reasons(audit: Dict[str, Any], checks: Dict[str, bool]) -> List[str]:
    labels = {
        "preflightSnapshotPresent": "Preflight snapshot is missing registry hash.",
        "auditWriteAttempted": "Canonical write was not attempted.",
        "auditWriteEnabled": "Canonical write was not enabled.",
        "promotedCountMatchesExpectedRecords": "Audit promoted count does not match expected records to add.",
        "promotedCountMatchesRecordIds": "Audit promoted count does not match promotedRecordIds length.",
        "afterCountMatchesExpectedAfterCount": "Registry after count does not match expected after count.",
        "registryShaChangedOnlyWhenPromoted": "Registry hash change does not match promotion count.",
        "dryRunHadNoDuplicateIds": "Dry-run diff contains duplicate ids.",
        "dryRunHadNoMissingStagedRecords": "Dry-run diff contains missing staged records.",
        "preflightBeforeCountMatchesRegistryBefore": "Preflight before count does not match registry before count.",
    }
    reasons = [labels[key] for key, value in checks.items() if not value]
    if audit.get("canonicalWriteAttempted") is not True:
        reasons.append("Default state has no production canonical write to verify.")
    return list(dict.fromkeys(reasons))


def build_post_audit_verification(
    preflight_snapshot_path: Any = DEFAULT_PREFLIGHT_SNAPSHOT_PATH,
    audit_file_path: Any = DEFAULT_AUDIT_PATH,
    dry_run_diff_path: Any = DEFAULT_DRY_RUN_DIFF_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> Dict[str, Any]:
    preflight = load_json(preflight_snapshot_path)
    audit = load_json(audit_file_path)
    dry_run_diff = load_json(dry_run_diff_path)
    after_count = registry_count(canonical_registry_path)
    before_count = int(audit.get("canonicalRegistryBeforeCount", preflight.get("canonicalRegistryRecordCount", after_count)))
    expected = expected_records_to_add(dry_run_diff, audit)
    expected_after_count = before_count + len(expected)
    registry_sha_before = str(preflight.get("canonicalRegistrySha256", ""))
    registry_sha_after = file_sha256(canonical_registry_path)
    production_registry_mutation_detected = (
        resolve_path(canonical_registry_path) == DEFAULT_CANONICAL_REGISTRY_PATH
        and registry_sha_before
        and registry_sha_before != registry_sha_after
    )
    checks = build_consistency_checks(
        audit,
        preflight,
        dry_run_diff,
        before_count,
        after_count,
        expected_after_count,
        registry_sha_before,
        registry_sha_after,
    )
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/verify_dhatu_post_canonical_write_audit.py",
        "verificationStatus": verification_status(audit, checks),
        "preflightSnapshotStatus": preflight.get("snapshotStatus"),
        "canonicalWriteAttempted": audit.get("canonicalWriteAttempted") is True,
        "canonicalWriteEnabled": audit.get("canonicalWriteEnabled") is True,
        "promotedCount": int(audit.get("promotedCount", 0)),
        "promotedRecordIds": audit.get("promotedRecordIds", []),
        "expectedRecordsToAdd": expected,
        "beforeCount": before_count,
        "afterCount": after_count,
        "expectedAfterCount": expected_after_count,
        "registrySha256Before": registry_sha_before,
        "registrySha256After": registry_sha_after,
        "consistencyChecks": checks,
        "blockingReasons": build_blocking_reasons(audit, checks),
        "productionRegistryMutationDetected": production_registry_mutation_detected,
    }


def write_post_audit_verification(verification: Dict[str, Any], path: Any = DEFAULT_POST_AUDIT_VERIFICATION_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(verification, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(verification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "verificationStatus": verification["verificationStatus"],
        "promotedCount": verification["promotedCount"],
        "productionRegistryMutationDetected": verification["productionRegistryMutationDetected"],
        "blockingReasonCount": len(verification["blockingReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify post canonical-write audit integrity.")
    parser.add_argument("--preflight-snapshot", default=str(DEFAULT_PREFLIGHT_SNAPSHOT_PATH))
    parser.add_argument("--audit-file", default=str(DEFAULT_AUDIT_PATH))
    parser.add_argument("--dry-run-diff", default=str(DEFAULT_DRY_RUN_DIFF_PATH))
    parser.add_argument("--canonical-registry", default=str(DEFAULT_CANONICAL_REGISTRY_PATH))
    parser.add_argument("--output", default=str(DEFAULT_POST_AUDIT_VERIFICATION_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        verification = build_post_audit_verification(
            args.preflight_snapshot,
            args.audit_file,
            args.dry_run_diff,
            args.canonical_registry,
        )
        write_post_audit_verification(verification, args.output)
        print(json.dumps(build_summary(verification), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu post canonical-write audit verification failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
