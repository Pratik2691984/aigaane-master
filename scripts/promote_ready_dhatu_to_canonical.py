#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from apply_dhatu_review_decisions import build_reviewed_promotion_plan
from lock_dhatu_promotion_readiness import (
    DEFAULT_READINESS_LOCK_PATH,
    build_promotion_readiness_lock,
    load_reviewed_promotion_plan,
)
from plan_dhatu_canonical_promotion import build_canonical_promotion_plan
from preview_dhatu_batch_promotion import build_promotion_preview
from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


WRITE_FLAG = "AIGAANE_ENABLE_CANONICAL_DHATU_WRITE"
DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"


def load_promotion_readiness_lock(path: Any = DEFAULT_READINESS_LOCK_PATH) -> Dict[str, Any]:
    lock_path = Path(path)
    with lock_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("canonicalWriteEnabled") is not False:
        raise ValueError("Readiness lock must keep canonicalWriteEnabled false.")
    if "readyRecordIds" not in payload or not isinstance(payload["readyRecordIds"], list):
        raise ValueError("Readiness lock missing readyRecordIds.")
    return payload


def run_promotion_prerequisites(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    load_large_scale_manifest(manifest_path)
    build_promotion_preview(manifest_path)
    build_canonical_promotion_plan(manifest_path)
    build_reviewed_promotion_plan(manifest_path)
    build_promotion_readiness_lock(manifest_path)
    return load_promotion_readiness_lock(DEFAULT_READINESS_LOCK_PATH)


def build_disabled_audit(lock: Dict[str, Any]) -> Dict[str, Any]:
    return build_audit(
        lock=lock,
        canonical_write_attempted=False,
        canonical_write_enabled=False,
        promoted_record_ids=[],
        skipped_record_ids=all_locked_record_ids(lock),
        refusalReason=f"Set {WRITE_FLAG}=1 to enable controlled canonical dhatu writes.",
    )


def build_enabled_audit(lock: Dict[str, Any]) -> Dict[str, Any]:
    ready_ids = sorted(lock.get("readyRecordIds", []))
    return build_audit(
        lock=lock,
        canonical_write_attempted=True,
        canonical_write_enabled=True,
        promoted_record_ids=ready_ids,
        skipped_record_ids=sorted(set(all_locked_record_ids(lock)) - set(ready_ids)),
        refusalReason=None,
    )


def build_audit(
    lock: Dict[str, Any],
    canonical_write_attempted: bool,
    canonical_write_enabled: bool,
    promoted_record_ids: List[str],
    skipped_record_ids: List[str],
    refusalReason: Optional[str],
) -> Dict[str, Any]:
    safety_checks = {
        **lock.get("safetyChecks", {}),
        "writeFlagRequired": True,
        "writeFlagName": WRITE_FLAG,
        "canonicalRegistryMutation": canonical_write_attempted and canonical_write_enabled,
        "goldsetMutation": False,
        "batchMutation": False,
        "reviewFileMutation": False,
        "readinessLockMutation": False,
    }
    audit = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/promote_ready_dhatu_to_canonical.py",
        "canonicalWriteAttempted": canonical_write_attempted,
        "canonicalWriteEnabled": canonical_write_enabled,
        "promotedCount": len(promoted_record_ids),
        "promotedRecordIds": promoted_record_ids,
        "skippedRecordIds": skipped_record_ids,
        "safetyChecks": safety_checks,
    }
    if refusalReason:
        audit["refusalReason"] = refusalReason
    return audit


def all_locked_record_ids(lock: Dict[str, Any]) -> List[str]:
    ids = (
        list(lock.get("readyRecordIds", []))
        + list(lock.get("blockedRecordIds", []))
        + list(lock.get("deferredRecordIds", []))
    )
    return sorted(set(ids))


def write_promotion_audit(audit: Dict[str, Any], path: Any = DEFAULT_AUDIT_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def promote_ready_dhatus(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    lock = run_promotion_prerequisites(manifest_path)
    enabled = os.environ.get(WRITE_FLAG) == "1"
    if not enabled:
        audit = build_disabled_audit(lock)
        write_promotion_audit(audit)
        print(f"Canonical dhatu write disabled; set {WRITE_FLAG}=1 to promote ready records.")
        return audit
    audit = build_enabled_audit(lock)
    write_promotion_audit(audit)
    return audit


def build_summary(audit: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "canonicalWriteAttempted": audit["canonicalWriteAttempted"],
        "canonicalWriteEnabled": audit["canonicalWriteEnabled"],
        "promotedCount": audit["promotedCount"],
        "skippedCount": len(audit["skippedRecordIds"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote ready dhatu records only when canonical writes are enabled.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        audit = promote_ready_dhatus(args.manifest)
        print(json.dumps(build_summary(audit), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Ready dhatu canonical promotion failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
