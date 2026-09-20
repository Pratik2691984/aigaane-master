#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_CLOSEOUT_INDEX_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_closeout_index.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Closeout index source must be a JSON object.")
    return payload


def manifest_path(manifest: Dict[str, Any], key: str, fallback: str) -> str:
    value = manifest.get(key, fallback)
    if not isinstance(value, str):
        return fallback
    return value


def file_entry(name: str, path: str, required: bool = True) -> Dict[str, Any]:
    resolved = resolve_path(path)
    return {
        "name": name,
        "path": path,
        "exists": resolved.exists(),
        "required": required,
    }


def build_artifact_index(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = [
        ("manifest", "largeScaleManifestFile", "data/sanskrit/ingestion/large_scale_manifest.v1.json"),
        ("promotionPreview", "promotionPreviewFile", "data/sanskrit/ingestion/promotion_preview.v1.json"),
        ("canonicalPromotionPlan", "canonicalPromotionPlanFile", "data/sanskrit/ingestion/canonical_promotion_plan.v1.json"),
        ("reviewDecisions", "reviewDecisionsFile", "data/sanskrit/ingestion/review_decisions.v1.json"),
        (
            "reviewedCanonicalPromotionPlan",
            "reviewedCanonicalPromotionPlanFile",
            "data/sanskrit/ingestion/canonical_promotion_plan.reviewed.v1.json",
        ),
        ("promotionReadinessLock", "promotionReadinessLockFile", "data/sanskrit/ingestion/promotion_readiness_lock.v1.json"),
        ("canonicalPromotionAudit", "canonicalPromotionAuditFile", "data/sanskrit/ingestion/canonical_promotion_audit.v1.json"),
        (
            "promotionEvidenceReport",
            "dhatuPromotionEvidenceReportFile",
            "data/sanskrit/ingestion/dhatu_promotion_evidence_report.v1.json",
        ),
        (
            "canonicalWriteAuthorization",
            "canonicalWriteAuthorizationFile",
            "data/sanskrit/ingestion/canonical_write_authorization.v1.json",
        ),
        ("canonicalWriteApproval", "canonicalWriteApprovalFile", "data/sanskrit/ingestion/canonical_write_approval.v1.json"),
        (
            "canonicalWriteApprovalValidation",
            "canonicalWriteApprovalValidationFile",
            "data/sanskrit/ingestion/canonical_write_approval_validation.v1.json",
        ),
        (
            "canonicalWriteCommandManifest",
            "canonicalWriteCommandManifestFile",
            "data/sanskrit/ingestion/canonical_write_command_manifest.v1.json",
        ),
        ("canonicalWriteDryRunDiff", "canonicalWriteDryRunDiffFile", "data/sanskrit/ingestion/canonical_write_dry_run_diff.v1.json"),
        (
            "canonicalWriteReleaseChecklist",
            "canonicalWriteReleaseChecklistFile",
            "data/sanskrit/ingestion/canonical_write_release_checklist.v1.json",
        ),
        (
            "canonicalWriteApprovalPackage",
            "canonicalWriteApprovalPackageFile",
            "data/sanskrit/ingestion/canonical_write_approval_package.v1.md",
        ),
        (
            "canonicalWriteReleaseVerification",
            "canonicalWriteReleaseVerificationFile",
            "data/sanskrit/ingestion/canonical_write_release_verification.v1.json",
        ),
        (
            "canonicalWritePreflightSnapshot",
            "canonicalWritePreflightSnapshotFile",
            "data/sanskrit/ingestion/canonical_write_preflight_snapshot.v1.json",
        ),
        (
            "canonicalWritePostAuditVerification",
            "canonicalWritePostAuditVerificationFile",
            "data/sanskrit/ingestion/canonical_write_post_audit_verification.v1.json",
        ),
        ("canonicalWriteRunbook", "canonicalWriteRunbookFile", "data/sanskrit/ingestion/canonical_write_runbook.v1.md"),
    ]
    return [file_entry(name, manifest_path(manifest, key, fallback)) for name, key, fallback in entries]


def status_from_sources(
    approval_validation: Dict[str, Any],
    command_manifest: Dict[str, Any],
    release_verification: Dict[str, Any],
    post_audit_verification: Dict[str, Any],
) -> str:
    if (
        approval_validation.get("approvalValid") is True
        and command_manifest.get("commandStatus") == "READY_FOR_MANUAL_EXECUTION"
        and release_verification.get("safeToProceed") is True
        and post_audit_verification.get("verificationStatus") != "BLOCKED_NO_PRODUCTION_WRITE"
    ):
        return "READY_FOR_CLOSEOUT_REVIEW"
    return "BLOCKED_NO_PRODUCTION_WRITE"


def build_closeout_index(manifest_path_value: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(resolve_path(manifest_path_value))
    artifact_index = build_artifact_index(manifest)
    approval_validation = load_json(manifest_path(manifest, "canonicalWriteApprovalValidationFile", "data/sanskrit/ingestion/canonical_write_approval_validation.v1.json"))
    command_manifest = load_json(manifest_path(manifest, "canonicalWriteCommandManifestFile", "data/sanskrit/ingestion/canonical_write_command_manifest.v1.json"))
    release_verification = load_json(manifest_path(manifest, "canonicalWriteReleaseVerificationFile", "data/sanskrit/ingestion/canonical_write_release_verification.v1.json"))
    post_audit_verification = load_json(manifest_path(manifest, "canonicalWritePostAuditVerificationFile", "data/sanskrit/ingestion/canonical_write_post_audit_verification.v1.json"))
    missing_required = [entry["path"] for entry in artifact_index if entry["required"] and not entry["exists"]]
    closeout_status = status_from_sources(
        approval_validation,
        command_manifest,
        release_verification,
        post_audit_verification,
    )
    if missing_required:
        closeout_status = "BLOCKED_MISSING_ARTIFACTS"

    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/index_dhatu_canonical_promotion_closeout.py",
        "closeoutStatus": closeout_status,
        "sourceFiles": {
            "manifest": str(resolve_path(manifest_path_value).relative_to(ROOT)),
            "approvalValidation": manifest_path(manifest, "canonicalWriteApprovalValidationFile", "data/sanskrit/ingestion/canonical_write_approval_validation.v1.json"),
            "commandManifest": manifest_path(manifest, "canonicalWriteCommandManifestFile", "data/sanskrit/ingestion/canonical_write_command_manifest.v1.json"),
            "releaseVerification": manifest_path(manifest, "canonicalWriteReleaseVerificationFile", "data/sanskrit/ingestion/canonical_write_release_verification.v1.json"),
            "postAuditVerification": manifest_path(manifest, "canonicalWritePostAuditVerificationFile", "data/sanskrit/ingestion/canonical_write_post_audit_verification.v1.json"),
            "runbook": manifest_path(manifest, "canonicalWriteRunbookFile", "data/sanskrit/ingestion/canonical_write_runbook.v1.md"),
        },
        "artifactIndex": artifact_index,
        "safetySummary": {
            "approvalValid": approval_validation.get("approvalValid") is True,
            "commandStatus": command_manifest.get("commandStatus"),
            "releaseVerificationStatus": release_verification.get("verificationStatus"),
            "safeToProceed": release_verification.get("safeToProceed") is True,
            "postAuditVerificationStatus": post_audit_verification.get("verificationStatus"),
            "productionRegistryMutationDetected": post_audit_verification.get("productionRegistryMutationDetected") is True,
        },
        "blockingReasons": missing_required
        + list(release_verification.get("blockingReasons", []))
        + list(post_audit_verification.get("blockingReasons", [])),
        "recommendedNextAction": "Keep production canonical write blocked until human approval, release verification, preflight snapshot, and post-write audit gates are ready.",
    }


def write_closeout_index(index: Dict[str, Any], output_path: Any = DEFAULT_CLOSEOUT_INDEX_PATH) -> Path:
    path = resolve_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index canonical promotion closeout artifacts.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to large-scale manifest JSON.")
    parser.add_argument("--output", default=str(DEFAULT_CLOSEOUT_INDEX_PATH), help="Path to write closeout index JSON.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    index = build_closeout_index(args.manifest)
    write_closeout_index(index, args.output)
    print(json.dumps({"closeoutStatus": index["closeoutStatus"], "artifactCount": len(index["artifactIndex"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
