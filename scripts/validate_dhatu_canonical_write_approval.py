#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from validate_large_scale_ingestion import ROOT


DEFAULT_APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.v1.json"
DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
)
DEFAULT_VALIDATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_validation.v1.json"
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
        raise ValueError(f"Approval validation source must be a JSON object: {display_path(resolved)}")
    return payload


def as_string_set(values: Any) -> Set[str]:
    if not isinstance(values, list):
        return set()
    return {str(value).strip() for value in values if str(value).strip()}


def build_refusal_reasons(
    approval: Dict[str, Any],
    authorization: Dict[str, Any],
    readiness_lock: Dict[str, Any],
    evidence: Dict[str, Any],
    approved_ids: Set[str],
    unexpected_ids: Set[str],
    missing_ids: Set[str],
) -> List[str]:
    reasons: List[str] = []
    if approval.get("approvalStatus") != "APPROVED":
        reasons.append("Approval status is not APPROVED.")
    if approval.get("approvalStatus") == "APPROVED" and not approved_ids:
        reasons.append("Approved approval token must include at least one approvedRecordId.")
    if unexpected_ids:
        reasons.append("Approval includes ids outside canonical write authorization.")
    if missing_ids:
        reasons.append("Approval does not include every authorized ready record id.")
    if not approval.get("approvedBy"):
        reasons.append("Approval token missing approvedBy.")
    if not approval.get("approvedAt"):
        reasons.append("Approval token missing approvedAt.")
    if sorted(authorization.get("authorizedRecordIds", [])) != sorted(readiness_lock.get("readyRecordIds", [])):
        reasons.append("Authorization ready ids do not match readiness lock ready ids.")
    return reasons


def build_safety_checks(
    approval: Dict[str, Any],
    authorization: Dict[str, Any],
    readiness_lock: Dict[str, Any],
    evidence: Dict[str, Any],
    approved_ids: Set[str],
    unexpected_ids: Set[str],
) -> Dict[str, Any]:
    authorized_ids = as_string_set(authorization.get("authorizedRecordIds", []))
    ready_ids = as_string_set(readiness_lock.get("readyRecordIds", []))
    return {
        "environmentFlagsUnchangedByValidation": True,
        "writerExecuted": False,
        "canonicalRegistryMutation": False,
        "goldsetMutation": False,
        "batchMutation": False,
        "approvalStatusApproved": approval.get("approvalStatus") == "APPROVED",
        "approvalMetadataPresent": bool(approval.get("approvedBy")) and bool(approval.get("approvedAt")),
        "approvedIdsPresentWhenApproved": approval.get("approvalStatus") != "APPROVED" or bool(approved_ids),
        "approvedIdsSubsetOfAuthorization": not unexpected_ids,
        "authorizedIdsMatchReadinessLock": authorized_ids == ready_ids,
        "authorizationReady": authorization.get("authorizationStatus") == "AUTHORIZED_FOR_MANUAL_WRITE",
        "evidenceReleaseGateReady": evidence.get("releaseGateStatus") == "READY_FOR_CONTROLLED_WRITE",
    }


def build_approval_validation(
    approval_path: Any = DEFAULT_APPROVAL_PATH,
    authorization_path: Any = DEFAULT_AUTHORIZATION_PATH,
    readiness_lock_path: Any = DEFAULT_READINESS_LOCK_PATH,
    evidence_path: Any = DEFAULT_EVIDENCE_REPORT_PATH,
) -> Dict[str, Any]:
    approval = load_json(approval_path)
    authorization = load_json(authorization_path)
    readiness_lock = load_json(readiness_lock_path)
    evidence = load_json(evidence_path)
    approved_ids = as_string_set(approval.get("approvedRecordIds", []))
    authorized_ids = as_string_set(authorization.get("authorizedRecordIds", []))
    unexpected_ids = approved_ids - authorized_ids
    missing_ids = authorized_ids - approved_ids
    rejected_ids = as_string_set(authorization.get("blockedRecordIds", [])) | unexpected_ids
    refusal_reasons = build_refusal_reasons(
        approval,
        authorization,
        readiness_lock,
        evidence,
        approved_ids,
        unexpected_ids,
        missing_ids,
    )
    safety_checks = build_safety_checks(
        approval,
        authorization,
        readiness_lock,
        evidence,
        approved_ids,
        unexpected_ids,
    )
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/validate_dhatu_canonical_write_approval.py",
        "approvalStatus": approval.get("approvalStatus"),
        "approvalValid": not refusal_reasons,
        "approvedRecordIds": sorted(approved_ids),
        "rejectedRecordIds": sorted(rejected_ids),
        "missingAuthorizedRecordIds": sorted(missing_ids),
        "unexpectedApprovedRecordIds": sorted(unexpected_ids),
        "safetyChecks": safety_checks,
        "refusalReasons": refusal_reasons,
    }


def write_approval_validation(validation: Dict[str, Any], path: Any = DEFAULT_VALIDATION_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(validation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "approvalStatus": validation["approvalStatus"],
        "approvalValid": validation["approvalValid"],
        "approvedCount": len(validation["approvedRecordIds"]),
        "rejectedCount": len(validation["rejectedRecordIds"]),
        "refusalCount": len(validation["refusalReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate human approval token for canonical dhatu write.")
    parser.add_argument("--approval", "--approval-file", dest="approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--authorization", default=str(DEFAULT_AUTHORIZATION_PATH))
    parser.add_argument("--readiness-lock", default=str(DEFAULT_READINESS_LOCK_PATH))
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_REPORT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_VALIDATION_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        validation = build_approval_validation(args.approval, args.authorization, args.readiness_lock, args.evidence)
        write_approval_validation(validation, args.output)
        print(json.dumps(build_summary(validation), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write approval validation failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
