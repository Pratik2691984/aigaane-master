#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"
DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def display_path(path: Any) -> str:
    resolved = resolve_path(path)
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def load_json(path: Any) -> Dict[str, Any]:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Authorization source must be a JSON object: {display_path(resolved)}")
    return payload


def build_required_environment(audit: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    guard_policy = evidence.get("guardPolicy", {})
    safety = audit.get("safetyChecks", {})
    write_flag = guard_policy.get("canonicalWriteFlag") or safety.get("writeFlagName")
    test_guard = guard_policy.get("testCanonicalWriteGuard") or safety.get("testWriteGuardName")
    return {
        str(write_flag): {
            "requiredValue": "1",
            "currentlySatisfied": audit.get("canonicalWriteEnabled") is True,
            "purpose": "Enable controlled canonical dhatu writes.",
        },
        str(test_guard): {
            "requiredValue": "1",
            "currentlySatisfied": audit.get("writeGuardSatisfied") is True,
            "purpose": "Confirm guarded canonical write execution path.",
        },
    }


def build_evidence_summary(audit: Dict[str, Any], evidence: Dict[str, Any], readiness_lock: Dict[str, Any]) -> Dict[str, Any]:
    counts = evidence.get("counts", {})
    return {
        "releaseGateStatus": evidence.get("releaseGateStatus"),
        "contractPassed": evidence.get("contractSummary", {}).get("passed") is True,
        "canonicalWriteEnabled": audit.get("canonicalWriteEnabled") is True,
        "writeGuardSatisfied": audit.get("writeGuardSatisfied") is True,
        "readyCount": int(readiness_lock.get("readyCount", 0)),
        "deferredCount": int(readiness_lock.get("needsReviewCount", 0)),
        "blockedCount": int(readiness_lock.get("blockedCount", 0)),
        "auditPromotedCount": int(audit.get("promotedCount", 0)),
        "auditSkippedCount": len(audit.get("skippedRecordIds", [])),
        "canonicalRegistryBeforeCount": int(counts.get("canonicalRegistryBeforeCount", 0)),
        "canonicalRegistryAfterCount": int(counts.get("canonicalRegistryAfterCount", 0)),
    }


def build_safety_checks(audit: Dict[str, Any], evidence: Dict[str, Any], readiness_lock: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "humanApprovalRequired": True,
        "environmentFlagsUnchangedByAuthorization": True,
        "canonicalRegistryMutation": False,
        "goldsetMutation": False,
        "batchMutation": False,
        "readinessLockCanonicalWriteEnabled": readiness_lock.get("canonicalWriteEnabled") is True,
        "auditCanonicalMutation": audit.get("safetyChecks", {}).get("canonicalRegistryMutation") is True,
        "evidenceReportPresent": evidence.get("schemaVersion") == "1.0.0",
        "evidenceReleaseGateReady": evidence.get("releaseGateStatus") == "READY_FOR_CONTROLLED_WRITE",
        "contractChecksPassed": evidence.get("contractSummary", {}).get("passed") is True,
    }


def build_authorization(
    audit_path: Any = DEFAULT_AUDIT_PATH,
    evidence_path: Any = DEFAULT_EVIDENCE_REPORT_PATH,
    readiness_lock_path: Any = DEFAULT_READINESS_LOCK_PATH,
) -> Dict[str, Any]:
    audit = load_json(audit_path)
    evidence = load_json(evidence_path)
    readiness_lock = load_json(readiness_lock_path)
    ready_ids = sorted(readiness_lock.get("readyRecordIds", []))
    blocked_ids = sorted(
        set(readiness_lock.get("blockedRecordIds", []))
        | set(readiness_lock.get("deferredRecordIds", []))
        | (set(evidence.get("skippedRecordIds", [])) - set(ready_ids))
    )
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/authorize_dhatu_canonical_write.py",
        "authorizationStatus": "AWAITING_HUMAN_APPROVAL",
        "authorizedRecordIds": ready_ids,
        "blockedRecordIds": blocked_ids,
        "requiredEnvironment": build_required_environment(audit, evidence),
        "evidenceSummary": build_evidence_summary(audit, evidence, readiness_lock),
        "safetyChecks": build_safety_checks(audit, evidence, readiness_lock),
        "humanApprovalRequired": True,
    }


def write_authorization(authorization: Dict[str, Any], path: Any = DEFAULT_AUTHORIZATION_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(authorization, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(authorization: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "authorizationStatus": authorization["authorizationStatus"],
        "authorizedCount": len(authorization["authorizedRecordIds"]),
        "blockedCount": len(authorization["blockedRecordIds"]),
        "humanApprovalRequired": authorization["humanApprovalRequired"],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare final dhatu canonical write authorization gate.")
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT_PATH))
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_REPORT_PATH))
    parser.add_argument("--readiness-lock", default=str(DEFAULT_READINESS_LOCK_PATH))
    parser.add_argument("--output", default=str(DEFAULT_AUTHORIZATION_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        authorization = build_authorization(args.audit, args.evidence, args.readiness_lock)
        write_authorization(authorization, args.output)
        print(json.dumps(build_summary(authorization), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write authorization failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
