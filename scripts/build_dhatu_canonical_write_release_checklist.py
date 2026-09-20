#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)
DEFAULT_APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.v1.json"
DEFAULT_APPROVAL_VALIDATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_validation.v1.json"
)
DEFAULT_COMMAND_MANIFEST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_command_manifest.v1.json"
)
DEFAULT_DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"
DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"
DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_RELEASE_CHECKLIST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_checklist.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Release checklist source must be a JSON object.")
    return payload


def safe_to_write(
    authorization: Dict[str, Any],
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
) -> bool:
    return (
        approval_validation.get("approvalValid") is True
        and authorization.get("authorizationStatus") == "AUTHORIZED_FOR_MANUAL_WRITE"
        and command_manifest.get("commandStatus") == "READY_FOR_MANUAL_EXECUTION"
        and dry_run_diff.get("dryRunOnly") is True
        and dry_run_diff.get("duplicateIds", []) == []
        and dry_run_diff.get("missingStagedRecords", []) == []
    )


def build_gate_summary(
    authorization: Dict[str, Any],
    approval: Dict[str, Any],
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
    audit: Dict[str, Any],
    evidence: Dict[str, Any],
    readiness_lock: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "authorizationStatus": authorization.get("authorizationStatus"),
        "humanApprovalRequired": authorization.get("humanApprovalRequired") is True,
        "approvalStatus": approval.get("approvalStatus"),
        "approvalValid": approval_validation.get("approvalValid") is True,
        "commandStatus": command_manifest.get("commandStatus"),
        "dryRunOnly": dry_run_diff.get("dryRunOnly") is True,
        "dryRunContractPassed": dry_run_diff.get("contractChecks", {}).get("passed") is True,
        "canonicalWriteEnabled": audit.get("canonicalWriteEnabled") is True,
        "writeGuardSatisfied": audit.get("writeGuardSatisfied") is True,
        "evidenceReleaseGateStatus": evidence.get("releaseGateStatus"),
        "readinessReadyCount": int(readiness_lock.get("readyCount", 0)),
    }


def build_record_summary(
    authorization: Dict[str, Any],
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
    readiness_lock: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "readyRecordIds": sorted(readiness_lock.get("readyRecordIds", [])),
        "authorizedRecordIds": sorted(authorization.get("authorizedRecordIds", [])),
        "approvedRecordIds": sorted(approval_validation.get("approvedRecordIds", [])),
        "commandApprovedRecordIds": sorted(command_manifest.get("approvedRecordIds", [])),
        "dryRunRecordsToAdd": len(dry_run_diff.get("recordsToAdd", [])),
        "dryRunRecordsBlocked": len(dry_run_diff.get("recordsBlocked", [])),
        "beforeCount": int(dry_run_diff.get("beforeCount", 0)),
        "afterCountIfApplied": int(dry_run_diff.get("afterCountIfApplied", 0)),
    }


def build_blocking_reasons(
    authorization: Dict[str, Any],
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
) -> List[str]:
    reasons: List[str] = []
    if approval_validation.get("approvalValid") is not True:
        reasons.append("Approval validation is not valid.")
    if authorization.get("authorizationStatus") != "AUTHORIZED_FOR_MANUAL_WRITE":
        reasons.append("Authorization is not ready for manual write.")
    if command_manifest.get("commandStatus") != "READY_FOR_MANUAL_EXECUTION":
        reasons.append("Command manifest is not ready for manual execution.")
    if dry_run_diff.get("dryRunOnly") is not True:
        reasons.append("Dry-run diff is not marked dryRunOnly.")
    if dry_run_diff.get("duplicateIds", []):
        reasons.append("Dry-run diff contains duplicate canonical ids.")
    if dry_run_diff.get("missingStagedRecords", []):
        reasons.append("Dry-run diff contains missing staged records.")
    reasons.extend(approval_validation.get("refusalReasons", []))
    reasons.extend(command_manifest.get("refusalReasons", []))
    reasons.extend(dry_run_diff.get("refusalReasons", []))
    return list(dict.fromkeys(reasons))


def build_release_checklist(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(manifest_path)
    authorization = load_json(DEFAULT_AUTHORIZATION_PATH)
    approval = load_json(DEFAULT_APPROVAL_PATH)
    approval_validation = load_json(DEFAULT_APPROVAL_VALIDATION_PATH)
    command_manifest = load_json(DEFAULT_COMMAND_MANIFEST_PATH)
    dry_run_diff = load_json(DEFAULT_DRY_RUN_DIFF_PATH)
    audit = load_json(DEFAULT_AUDIT_PATH)
    evidence = load_json(DEFAULT_EVIDENCE_REPORT_PATH)
    readiness_lock = load_json(DEFAULT_READINESS_LOCK_PATH)
    safe = safe_to_write(authorization, approval_validation, command_manifest, dry_run_diff)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/build_dhatu_canonical_write_release_checklist.py",
        "releaseStatus": "READY_FOR_MANUAL_PRODUCTION_WRITE" if safe else "BLOCKED",
        "gateSummary": build_gate_summary(
            authorization,
            approval,
            approval_validation,
            command_manifest,
            dry_run_diff,
            audit,
            evidence,
            readiness_lock,
        ),
        "recordSummary": build_record_summary(
            authorization,
            approval_validation,
            command_manifest,
            dry_run_diff,
            readiness_lock,
        ),
        "requiredManualSteps": [
            "Review canonical_write_release_checklist.v1.json.",
            "Record real human approval in canonical_write_approval.v1.json.",
            "Regenerate approval validation, command manifest, dry-run diff, and this checklist.",
            "Set required environment guards manually only at execution time.",
            "Run the exact approved command only after safeToWriteProduction is true.",
        ],
        "requiredEnvironment": command_manifest.get("requiredEnvironment", {}),
        "requiredCommands": {
            "approvalValidation": "python scripts/validate_dhatu_canonical_write_approval.py",
            "commandManifest": "python scripts/prepare_dhatu_canonical_write_command.py",
            "dryRunDiff": "python scripts/diff_dhatu_canonical_write_dry_run.py",
            "productionWritePreview": command_manifest.get("exactPowerShellCommand", ""),
        },
        "blockingReasons": build_blocking_reasons(
            authorization,
            approval_validation,
            command_manifest,
            dry_run_diff,
        ),
        "safeToWriteProduction": safe,
        "sourceFiles": {
            "manifest": manifest.get("canonicalWriteReleaseChecklistFile", "data/sanskrit/ingestion/canonical_write_release_checklist.v1.json"),
            "authorization": manifest.get("canonicalWriteAuthorizationFile"),
            "approval": manifest.get("canonicalWriteApprovalFile"),
            "approvalValidation": manifest.get("canonicalWriteApprovalValidationFile"),
            "commandManifest": manifest.get("canonicalWriteCommandManifestFile"),
            "dryRunDiff": manifest.get("canonicalWriteDryRunDiffFile"),
            "audit": manifest.get("canonicalPromotionAuditFile"),
            "evidenceReport": manifest.get("dhatuPromotionEvidenceReportFile"),
            "readinessLock": manifest.get("promotionReadinessLockFile"),
        },
    }


def write_release_checklist(checklist: Dict[str, Any], path: Any = DEFAULT_RELEASE_CHECKLIST_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(checklist, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(checklist: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "releaseStatus": checklist["releaseStatus"],
        "safeToWriteProduction": checklist["safeToWriteProduction"],
        "blockingReasonCount": len(checklist["blockingReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical dhatu write release checklist.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", default=str(DEFAULT_RELEASE_CHECKLIST_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        checklist = build_release_checklist(args.manifest)
        write_release_checklist(checklist, args.output)
        print(json.dumps(build_summary(checklist), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write release checklist failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
