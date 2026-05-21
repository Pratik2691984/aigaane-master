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
DEFAULT_RELEASE_CHECKLIST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_checklist.v1.json"
)
DEFAULT_APPROVAL_PACKAGE_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_package.v1.md"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_VERIFICATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_verification.v1.json"
)
WARNING_TEXT = "No command should be run until human approval is edited, reviewed, and committed."


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
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Release verification source must be a JSON object.")
    return payload


def build_checked_files(manifest: Dict[str, Any]) -> Dict[str, str]:
    return {
        "manifest": display_path(DEFAULT_MANIFEST),
        "authorization": manifest.get("canonicalWriteAuthorizationFile", display_path(DEFAULT_AUTHORIZATION_PATH)),
        "approval": manifest.get("canonicalWriteApprovalFile", display_path(DEFAULT_APPROVAL_PATH)),
        "approvalValidation": manifest.get("canonicalWriteApprovalValidationFile", display_path(DEFAULT_APPROVAL_VALIDATION_PATH)),
        "commandManifest": manifest.get("canonicalWriteCommandManifestFile", display_path(DEFAULT_COMMAND_MANIFEST_PATH)),
        "dryRunDiff": manifest.get("canonicalWriteDryRunDiffFile", display_path(DEFAULT_DRY_RUN_DIFF_PATH)),
        "releaseChecklist": manifest.get("canonicalWriteReleaseChecklistFile", display_path(DEFAULT_RELEASE_CHECKLIST_PATH)),
        "approvalPackage": manifest.get("canonicalWriteApprovalPackageFile", display_path(DEFAULT_APPROVAL_PACKAGE_PATH)),
        "readinessLock": manifest.get("promotionReadinessLockFile", display_path(DEFAULT_READINESS_LOCK_PATH)),
    }


def build_consistency_checks(
    authorization: Dict[str, Any],
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
    release_checklist: Dict[str, Any],
    approval_package_text: str,
    readiness_lock: Dict[str, Any],
) -> Dict[str, bool]:
    authorized_ids = sorted(authorization.get("authorizedRecordIds", []))
    ready_ids = sorted(readiness_lock.get("readyRecordIds", []))
    approved_ids = sorted(approval_validation.get("approvedRecordIds", []))
    return {
        "checklistSafeToWriteProduction": release_checklist.get("safeToWriteProduction") is True,
        "commandReadyForManualExecution": command_manifest.get("commandStatus") == "READY_FOR_MANUAL_EXECUTION",
        "approvalValidationValid": approval_validation.get("approvalValid") is True,
        "dryRunHasNoDuplicateIds": dry_run_diff.get("duplicateIds", []) == [],
        "dryRunHasNoMissingStagedRecords": dry_run_diff.get("missingStagedRecords", []) == [],
        "approvalPackageIncludesManualWarning": WARNING_TEXT in approval_package_text,
        "authorizedIdsMatchReadinessLock": authorized_ids == ready_ids,
        "approvedIdsMatchCommandManifest": approved_ids == sorted(command_manifest.get("approvedRecordIds", [])),
        "dryRunIsDryRunOnly": dry_run_diff.get("dryRunOnly") is True,
    }


def build_blocking_reasons(checks: Dict[str, bool], artifacts: List[Dict[str, Any]]) -> List[str]:
    labels = {
        "checklistSafeToWriteProduction": "Release checklist is not safe for production write.",
        "commandReadyForManualExecution": "Command manifest is not READY_FOR_MANUAL_EXECUTION.",
        "approvalValidationValid": "Approval validation is not valid.",
        "dryRunHasNoDuplicateIds": "Dry run contains duplicate ids.",
        "dryRunHasNoMissingStagedRecords": "Dry run contains missing staged records.",
        "approvalPackageIncludesManualWarning": "Approval package is missing the manual warning text.",
        "authorizedIdsMatchReadinessLock": "Authorized ids do not match readiness lock ready ids.",
        "approvedIdsMatchCommandManifest": "Approved ids do not match command manifest approved ids.",
        "dryRunIsDryRunOnly": "Dry run is not marked dryRunOnly.",
    }
    reasons = [labels[key] for key, value in checks.items() if not value]
    for artifact in artifacts:
        reasons.extend(artifact.get("blockingReasons", []))
        reasons.extend(artifact.get("refusalReasons", []))
    return list(dict.fromkeys(reasons))


def next_required_action(safe_to_proceed: bool) -> str:
    if safe_to_proceed:
        return "Proceed only by running the exact approved manual command with required environment guards."
    return "Keep canonical writes disabled; resolve blocking reasons and regenerate release artifacts."


def build_release_verification(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(manifest_path)
    authorization = load_json(DEFAULT_AUTHORIZATION_PATH)
    load_json(DEFAULT_APPROVAL_PATH)
    approval_validation = load_json(DEFAULT_APPROVAL_VALIDATION_PATH)
    command_manifest = load_json(DEFAULT_COMMAND_MANIFEST_PATH)
    dry_run_diff = load_json(DEFAULT_DRY_RUN_DIFF_PATH)
    release_checklist = load_json(DEFAULT_RELEASE_CHECKLIST_PATH)
    readiness_lock = load_json(DEFAULT_READINESS_LOCK_PATH)
    approval_package_text = resolve_path(DEFAULT_APPROVAL_PACKAGE_PATH).read_text(encoding="utf-8")
    checks = build_consistency_checks(
        authorization,
        approval_validation,
        command_manifest,
        dry_run_diff,
        release_checklist,
        approval_package_text,
        readiness_lock,
    )
    safe = all(checks.values())
    blocking_reasons = build_blocking_reasons(
        checks,
        [approval_validation, command_manifest, dry_run_diff, release_checklist],
    )
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/verify_dhatu_canonical_write_release.py",
        "verificationStatus": "READY" if safe else "BLOCKED",
        "checkedFiles": build_checked_files(manifest),
        "consistencyChecks": checks,
        "blockingReasons": blocking_reasons,
        "safeToProceed": safe,
        "nextRequiredAction": next_required_action(safe),
    }


def write_release_verification(verification: Dict[str, Any], path: Any = DEFAULT_VERIFICATION_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(verification, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(verification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "verificationStatus": verification["verificationStatus"],
        "safeToProceed": verification["safeToProceed"],
        "blockingReasonCount": len(verification["blockingReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify canonical dhatu write release package.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", default=str(DEFAULT_VERIFICATION_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        verification = build_release_verification(args.manifest)
        write_release_verification(verification, args.output)
        print(json.dumps(build_summary(verification), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write release verification failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
