#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from apply_dhatu_review_decisions import (
    DEFAULT_REVIEWED_PLAN_PATH,
    build_reviewed_promotion_plan,
    write_reviewed_promotion_plan,
)
from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"


def load_reviewed_promotion_plan(path: Any = DEFAULT_REVIEWED_PLAN_PATH) -> Dict[str, Any]:
    reviewed_path = Path(path)
    with reviewed_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if "plannedRecords" not in payload or not isinstance(payload["plannedRecords"], list):
        raise ValueError("Reviewed promotion plan missing plannedRecords.")
    if payload.get("safetyChecks", {}).get("canonicalRegistryMutation") is not False:
        raise ValueError("Reviewed promotion plan must not mutate canonical registry.")
    return payload


def build_promotion_readiness_lock(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    load_large_scale_manifest(manifest_path)
    reviewed_plan = build_reviewed_promotion_plan(manifest_path)
    write_reviewed_promotion_plan(reviewed_plan)
    persisted = load_reviewed_promotion_plan(DEFAULT_REVIEWED_PLAN_PATH)
    ready_ids = record_ids_by_classification(persisted, "ready")
    blocked_ids = record_ids_by_classification(persisted, "blocked")
    deferred_ids = record_ids_by_classification(persisted, "needs_review")
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/lock_dhatu_promotion_readiness.py",
        "sourceReviewedPlanFile": "data/sanskrit/ingestion/canonical_promotion_plan.reviewed.v1.json",
        "totalRecords": persisted["totalRecords"],
        "readyCount": len(ready_ids),
        "needsReviewCount": len(deferred_ids),
        "blockedCount": len(blocked_ids),
        "readyRecordIds": ready_ids,
        "blockedRecordIds": blocked_ids,
        "deferredRecordIds": deferred_ids,
        "safetyChecks": {
            "stagedValidationPassed": True,
            "promotionPreviewRegenerated": True,
            "canonicalPromotionPlanRegenerated": True,
            "reviewDecisionsApplied": True,
            "canonicalRegistryMutation": False,
            "goldsetMutation": False,
            "batchMutation": False,
            "deterministicOrdering": True,
            "safeToRegenerate": True,
        },
        "canonicalWriteEnabled": False,
    }


def record_ids_by_classification(reviewed_plan: Dict[str, Any], classification: str) -> List[str]:
    return sorted(
        record["sourceRootId"]
        for record in reviewed_plan.get("plannedRecords", [])
        if record.get("classification") == classification
    )


def write_promotion_readiness_lock(lock: Dict[str, Any], path: Any = DEFAULT_READINESS_LOCK_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(lock, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(lock: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "totalRecords": lock["totalRecords"],
        "readyCount": lock["readyCount"],
        "needsReviewCount": lock["needsReviewCount"],
        "blockedCount": lock["blockedCount"],
        "canonicalWriteEnabled": lock["canonicalWriteEnabled"],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lock dhatu promotion readiness without canonical writes.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        lock = build_promotion_readiness_lock(args.manifest)
        write_promotion_readiness_lock(lock)
        print(json.dumps(build_summary(lock), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu promotion readiness lock failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
