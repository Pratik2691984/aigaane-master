#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
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
        raise ValueError(f"JSON evidence source must be an object: {display_path(resolved)}")
    return payload


def require_manifest_path(manifest: Dict[str, Any], field: str) -> str:
    value = manifest.get(field)
    if not value:
        raise ValueError(f"Large-scale manifest missing evidence source path: {field}.")
    return str(value)


def build_source_files(manifest_path: Any, manifest: Dict[str, Any]) -> Dict[str, str]:
    return {
        "largeScaleManifest": display_path(manifest_path),
        "dhatuBatchPromotionPreview": require_manifest_path(manifest, "promotionPreviewFile"),
        "dhatuCanonicalPromotionPlan": require_manifest_path(manifest, "canonicalPromotionPlanFile"),
        "dhatuReviewDecisions": require_manifest_path(manifest, "reviewDecisionsFile"),
        "promotionReadinessLock": require_manifest_path(manifest, "promotionReadinessLockFile"),
        "canonicalPromotionAudit": require_manifest_path(manifest, "canonicalPromotionAuditFile"),
    }


def release_gate_status(audit: Dict[str, Any]) -> str:
    if audit.get("canonicalWriteEnabled") is True and audit.get("writeGuardSatisfied") is True:
        return "READY_FOR_CONTROLLED_WRITE"
    return "BLOCKED"


def recommended_next_action(status: str) -> str:
    if status == "READY_FOR_CONTROLLED_WRITE":
        return "Run the controlled canonical promotion only against the explicitly approved target."
    return "Keep production canonical writes disabled; resolve guard policy and review evidence before promotion."


def count_review_decisions(decisions: Dict[str, Any], decision: str) -> int:
    return sum(
        1
        for item in decisions.get("decisions", {}).values()
        if isinstance(item, dict) and item.get("decision") == decision
    )


def build_counts(
    manifest: Dict[str, Any],
    preview: Dict[str, Any],
    plan: Dict[str, Any],
    decisions: Dict[str, Any],
    lock: Dict[str, Any],
    audit: Dict[str, Any],
) -> Dict[str, int]:
    return {
        "manifestBatchFileCount": int(manifest.get("batchFileCount", 0)),
        "previewTotalStagedRecords": int(preview.get("totalStagedRecords", 0)),
        "promotionPlanTotalRecords": int(plan.get("totalRecords", 0)),
        "promotionPlanReadyCount": int(plan.get("readyCount", 0)),
        "promotionPlanNeedsReviewCount": int(plan.get("needsReviewCount", 0)),
        "promotionPlanBlockedCount": int(plan.get("blockedCount", 0)),
        "reviewDecisionCount": len(decisions.get("decisions", {})),
        "reviewApprovedCount": count_review_decisions(decisions, "approve"),
        "readinessReadyCount": int(lock.get("readyCount", 0)),
        "readinessDeferredCount": int(lock.get("needsReviewCount", 0)),
        "readinessBlockedCount": int(lock.get("blockedCount", 0)),
        "auditPromotedCount": int(audit.get("promotedCount", 0)),
        "auditSkippedCount": len(audit.get("skippedRecordIds", [])),
        "canonicalRegistryBeforeCount": int(audit.get("canonicalRegistryBeforeCount", 0)),
        "canonicalRegistryAfterCount": int(audit.get("canonicalRegistryAfterCount", 0)),
    }


def build_guard_policy(manifest: Dict[str, Any], audit: Dict[str, Any]) -> Dict[str, Any]:
    policy = manifest.get("policy", {})
    safety = audit.get("safetyChecks", {})
    return {
        "allowDirectCanonicalWrite": policy.get("allowDirectCanonicalWrite"),
        "canonicalWriteFlag": policy.get("canonicalWriteFlag") or safety.get("writeFlagName"),
        "testCanonicalWriteGuard": policy.get("testCanonicalWriteGuard") or safety.get("testWriteGuardName"),
        "canonicalWriteEnabled": audit.get("canonicalWriteEnabled") is True,
        "writeGuardSatisfied": audit.get("writeGuardSatisfied") is True,
        "unsafeWriteRefused": audit.get("unsafeWriteRefused") is True,
        "defaultOperation": policy.get("defaultOperation"),
    }


def build_contract_summary(audit: Dict[str, Any]) -> Dict[str, Any]:
    checks = audit.get("contractChecks", {})
    return {
        "passed": checks.get("passed") is True,
        "checks": {
            "noDuplicateDhatuIds": checks.get("noDuplicateDhatuIds") is True,
            "noUnsafeCanonicalOverwrite": checks.get("noUnsafeCanonicalOverwrite") is True,
            "promotedRecordsExistInStagedBatch": checks.get("promotedRecordsExistInStagedBatch") is True,
            "promotedRecordsApprovedByReviewDecision": checks.get("promotedRecordsApprovedByReviewDecision") is True,
            "promotedRecordsInReadinessLock": checks.get("promotedRecordsInReadinessLock") is True,
        },
        "violations": checks.get("violations", {}),
    }


def build_evidence_report(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(manifest_path)
    source_files = build_source_files(manifest_path, manifest)
    preview = load_json(source_files["dhatuBatchPromotionPreview"])
    plan = load_json(source_files["dhatuCanonicalPromotionPlan"])
    decisions = load_json(source_files["dhatuReviewDecisions"])
    lock = load_json(source_files["promotionReadinessLock"])
    audit = load_json(source_files["canonicalPromotionAudit"])
    status = release_gate_status(audit)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/report_dhatu_promotion_evidence.py",
        "sourceFiles": source_files,
        "counts": build_counts(manifest, preview, plan, decisions, lock, audit),
        "readyRecordIds": sorted(lock.get("readyRecordIds", [])),
        "skippedRecordIds": sorted(audit.get("skippedRecordIds", [])),
        "guardPolicy": build_guard_policy(manifest, audit),
        "contractSummary": build_contract_summary(audit),
        "releaseGateStatus": status,
        "recommendedNextAction": recommended_next_action(status),
    }


def write_evidence_report(report: Dict[str, Any], path: Any = DEFAULT_EVIDENCE_REPORT_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "releaseGateStatus": report["releaseGateStatus"],
        "readyCount": len(report["readyRecordIds"]),
        "skippedCount": len(report["skippedRecordIds"]),
        "canonicalWriteEnabled": report["guardPolicy"]["canonicalWriteEnabled"],
        "writeGuardSatisfied": report["guardPolicy"]["writeGuardSatisfied"],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dhatu promotion evidence report before canonical writes.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output", default=str(DEFAULT_EVIDENCE_REPORT_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = build_evidence_report(args.manifest)
        write_evidence_report(report, args.output)
        print(json.dumps(build_summary(report), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu promotion evidence report failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
