#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from apply_dhatu_review_decisions import build_reviewed_promotion_plan
from lock_dhatu_promotion_readiness import (
    DEFAULT_READINESS_LOCK_PATH,
    build_promotion_readiness_lock,
    load_reviewed_promotion_plan,
)
from plan_dhatu_canonical_promotion import build_canonical_promotion_plan
from preview_dhatu_batch_promotion import build_promotion_preview
from validate_large_scale_ingestion import (
    DEFAULT_MANIFEST,
    ROOT,
    load_large_scale_manifest,
    scan_all_staged_batch_files,
)


WRITE_FLAG = "AIGAANE_ENABLE_CANONICAL_DHATU_WRITE"
TEST_WRITE_FLAG = "AIGAANE_ALLOW_TEST_CANONICAL_WRITE"
DEFAULT_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"


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


def build_disabled_audit(
    lock: Dict[str, Any],
    reviewed_plan: Optional[Dict[str, Any]] = None,
    staged_records: Optional[Dict[str, Dict[str, Any]]] = None,
    canonical_registry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if staged_records is None:
        staged_records = flatten_staged_records(
            scan_all_staged_batch_files(load_large_scale_manifest(DEFAULT_MANIFEST))
        )
    registry = canonical_registry or load_canonical_registry_index(DEFAULT_CANONICAL_REGISTRY_PATH)
    contract_checks = build_contract_checks(
        lock,
        reviewed_plan or load_reviewed_promotion_plan(),
        staged_records,
        registry,
    )
    registry_count = canonical_registry_count(registry)
    return build_audit(
        lock=lock,
        canonical_write_attempted=False,
        canonical_write_enabled=False,
        write_guard_satisfied=False,
        unsafe_write_refused=False,
        canonical_registry_before_count=registry_count,
        canonical_registry_after_count=registry_count,
        contract_checks=contract_checks,
        promoted_record_ids=[],
        skipped_record_ids=all_locked_record_ids(lock),
        refusalReason=f"Set {WRITE_FLAG}=1 to enable controlled canonical dhatu writes.",
    )


def build_enabled_audit(
    lock: Dict[str, Any],
    reviewed_plan: Dict[str, Any],
    staged_records: Optional[Dict[str, Dict[str, Any]]],
    canonical_registry_before: Dict[str, Any],
    canonical_registry_after: Optional[Dict[str, Any]] = None,
    write_guard_satisfied: bool = False,
    unsafe_write_refused: bool = True,
) -> Dict[str, Any]:
    ready_ids = sorted(lock.get("readyRecordIds", []))
    after_registry = canonical_registry_after or canonical_registry_before
    promoted_ids = ready_ids if write_guard_satisfied and not unsafe_write_refused else []
    return build_audit(
        lock=lock,
        canonical_write_attempted=True,
        canonical_write_enabled=True,
        write_guard_satisfied=write_guard_satisfied,
        unsafe_write_refused=unsafe_write_refused,
        canonical_registry_before_count=canonical_registry_count(canonical_registry_before),
        canonical_registry_after_count=canonical_registry_count(after_registry),
        contract_checks=build_contract_checks(lock, reviewed_plan, staged_records, canonical_registry_before),
        promoted_record_ids=promoted_ids,
        skipped_record_ids=sorted(set(all_locked_record_ids(lock)) - set(promoted_ids)),
        refusalReason=None if write_guard_satisfied else f"Set {TEST_WRITE_FLAG}=1 to allow guarded test canonical writes.",
    )


def build_audit(
    lock: Dict[str, Any],
    canonical_write_attempted: bool,
    canonical_write_enabled: bool,
    write_guard_satisfied: bool,
    unsafe_write_refused: bool,
    canonical_registry_before_count: int,
    canonical_registry_after_count: int,
    contract_checks: Dict[str, Any],
    promoted_record_ids: List[str],
    skipped_record_ids: List[str],
    refusalReason: Optional[str],
) -> Dict[str, Any]:
    safety_checks = {
        **lock.get("safetyChecks", {}),
        "writeFlagRequired": True,
        "writeFlagName": WRITE_FLAG,
        "testWriteGuardRequired": True,
        "testWriteGuardName": TEST_WRITE_FLAG,
        "canonicalRegistryMutation": canonical_write_attempted
        and canonical_write_enabled
        and write_guard_satisfied
        and not unsafe_write_refused,
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
        "writeGuardSatisfied": write_guard_satisfied,
        "unsafeWriteRefused": unsafe_write_refused,
        "canonicalRegistryBeforeCount": canonical_registry_before_count,
        "canonicalRegistryAfterCount": canonical_registry_after_count,
        "contractChecks": contract_checks,
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


def load_canonical_registry_index(path: Any = DEFAULT_CANONICAL_REGISTRY_PATH) -> Dict[str, Any]:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("records"), dict):
        raise ValueError("Canonical registry index must contain a records object.")
    return payload


def canonical_registry_count(registry: Dict[str, Any]) -> int:
    return len(registry.get("records", {}))


def flatten_staged_records(batch_records: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    records: Dict[str, Dict[str, Any]] = {}
    for batch_file_records in batch_records.values():
        for record in batch_file_records:
            record_id = str(record.get("root_id") or record.get("id") or "").strip()
            if record_id:
                records[record_id] = record
    return records


def duplicate_values(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def reviewed_records_by_source_id(reviewed_plan: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(record.get("sourceRootId")): record
        for record in reviewed_plan.get("plannedRecords", [])
        if record.get("sourceRootId")
    }


def build_contract_checks(
    lock: Dict[str, Any],
    reviewed_plan: Dict[str, Any],
    staged_records: Optional[Dict[str, Dict[str, Any]]],
    canonical_registry: Dict[str, Any],
) -> Dict[str, Any]:
    ready_ids = sorted(lock.get("readyRecordIds", []))
    staged = staged_records or {}
    reviewed = reviewed_records_by_source_id(reviewed_plan)
    canonical_records = canonical_registry.get("records", {})
    missing_from_plan = sorted(source_id for source_id in ready_ids if source_id not in reviewed)
    missing_from_staged = sorted(source_id for source_id in ready_ids if source_id not in staged)
    not_approved = sorted(
        source_id
        for source_id in ready_ids
        if source_id in reviewed
        and (
            reviewed[source_id].get("classification") != "ready"
            or reviewed[source_id].get("reviewDecision") != "approve"
        )
    )
    not_readiness_locked = sorted(
        source_id
        for source_id, record in reviewed.items()
        if record.get("classification") == "ready" and source_id not in set(ready_ids)
    )
    unsafe_overwrites: List[Dict[str, str]] = []
    for source_id in ready_ids:
        record = reviewed.get(source_id)
        if not record:
            continue
        proposed_id = str(record.get("proposedCanonicalId", "")).strip()
        existing = canonical_records.get(proposed_id)
        existing_source_id = str(existing.get("promotion", {}).get("sourceRootId", "")).strip() if isinstance(existing, dict) else ""
        if existing and existing_source_id != source_id:
            unsafe_overwrites.append({"sourceRootId": source_id, "canonicalId": proposed_id})

    final_ids = list(canonical_records.keys())
    for source_id in ready_ids:
        record = reviewed.get(source_id)
        if not record:
            continue
        proposed_id = str(record.get("proposedCanonicalId", "")).strip()
        existing = canonical_records.get(proposed_id)
        if not existing:
            final_ids.append(proposed_id)
    duplicate_dhatu_ids = duplicate_values(final_ids)

    violations = {
        "duplicateDhatuIds": duplicate_dhatu_ids,
        "unsafeCanonicalOverwrites": unsafe_overwrites,
        "missingFromReviewedPlan": missing_from_plan,
        "missingFromStagedBatch": missing_from_staged,
        "notApprovedByReviewDecision": not_approved,
        "notInReadinessLock": not_readiness_locked,
    }
    return {
        "noDuplicateDhatuIds": not duplicate_dhatu_ids,
        "noUnsafeCanonicalOverwrite": not unsafe_overwrites,
        "promotedRecordsExistInStagedBatch": not missing_from_staged,
        "promotedRecordsApprovedByReviewDecision": not not_approved and not missing_from_plan,
        "promotedRecordsInReadinessLock": not not_readiness_locked,
        "passed": all(not value for value in violations.values()),
        "violations": violations,
    }


def build_canonical_registry_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "canonicalForm": record["devanagari"],
        "gana": {"id": record["gana"]},
        "root": record["devanagari"],
        "rootIast": record["iast"],
        "gloss": record["artha"],
        "promotion": {
            "sourceRootId": record["sourceRootId"],
            "sourceFile": record.get("sourceFile", ""),
            "source": record.get("source", ""),
            "reviewDecision": record.get("reviewDecision", ""),
        },
    }


def apply_promotions_to_registry(
    canonical_registry: Dict[str, Any],
    reviewed_plan: Dict[str, Any],
    ready_record_ids: List[str],
) -> Tuple[Dict[str, Any], List[str]]:
    promoted_registry = json.loads(json.dumps(canonical_registry))
    records = promoted_registry.setdefault("records", {})
    reviewed = reviewed_records_by_source_id(reviewed_plan)
    promoted_ids: List[str] = []
    for source_id in sorted(ready_record_ids):
        record = reviewed[source_id]
        canonical_id = record["proposedCanonicalId"]
        records[canonical_id] = build_canonical_registry_record(record)
        promoted_ids.append(source_id)
    promoted_registry["records"] = {key: records[key] for key in sorted(records)}
    return promoted_registry, promoted_ids


def write_canonical_registry_index(registry: Dict[str, Any], path: Any = DEFAULT_CANONICAL_REGISTRY_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(registry, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def write_promotion_audit(audit: Dict[str, Any], path: Any = DEFAULT_AUDIT_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(audit, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def promote_ready_dhatus(
    manifest_path: Any = DEFAULT_MANIFEST,
    audit_path: Any = DEFAULT_AUDIT_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> Dict[str, Any]:
    lock = run_promotion_prerequisites(manifest_path)
    manifest = load_large_scale_manifest(manifest_path)
    staged_records = flatten_staged_records(scan_all_staged_batch_files(manifest))
    reviewed_plan = load_reviewed_promotion_plan()
    canonical_registry = load_canonical_registry_index(canonical_registry_path)
    enabled = os.environ.get(WRITE_FLAG) == "1"
    if not enabled:
        audit = build_disabled_audit(lock, reviewed_plan, staged_records, canonical_registry)
        write_promotion_audit(audit, audit_path)
        print(f"Canonical dhatu write disabled; set {WRITE_FLAG}=1 to promote ready records.")
        return audit
    write_guard_satisfied = os.environ.get(TEST_WRITE_FLAG) == "1"
    if not write_guard_satisfied:
        audit = build_enabled_audit(lock, reviewed_plan, staged_records, canonical_registry)
        write_promotion_audit(audit, audit_path)
        print(f"Unsafe canonical dhatu write refused; set {TEST_WRITE_FLAG}=1 for guarded test writes.")
        return audit
    contract_checks = build_contract_checks(lock, reviewed_plan, staged_records, canonical_registry)
    if not contract_checks["passed"]:
        audit = build_enabled_audit(
            lock,
            reviewed_plan,
            staged_records,
            canonical_registry,
            write_guard_satisfied=True,
            unsafe_write_refused=True,
        )
        audit["contractChecks"] = contract_checks
        audit["refusalReason"] = "Canonical promotion contract checks failed."
        write_promotion_audit(audit, audit_path)
        return audit
    promoted_registry, promoted_ids = apply_promotions_to_registry(
        canonical_registry,
        reviewed_plan,
        lock.get("readyRecordIds", []),
    )
    write_canonical_registry_index(promoted_registry, canonical_registry_path)
    audit = build_enabled_audit(
        lock,
        reviewed_plan,
        staged_records,
        canonical_registry,
        canonical_registry_after=promoted_registry,
        write_guard_satisfied=True,
        unsafe_write_refused=False,
    )
    audit["promotedRecordIds"] = promoted_ids
    audit["promotedCount"] = len(promoted_ids)
    audit["skippedRecordIds"] = sorted(set(all_locked_record_ids(lock)) - set(promoted_ids))
    write_promotion_audit(audit, audit_path)
    return audit


def build_summary(audit: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "canonicalWriteAttempted": audit["canonicalWriteAttempted"],
        "canonicalWriteEnabled": audit["canonicalWriteEnabled"],
        "writeGuardSatisfied": audit["writeGuardSatisfied"],
        "unsafeWriteRefused": audit["unsafeWriteRefused"],
        "promotedCount": audit["promotedCount"],
        "skippedCount": len(audit["skippedRecordIds"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote ready dhatu records only when canonical writes are enabled.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT_PATH))
    parser.add_argument("--canonical-registry", default=str(DEFAULT_CANONICAL_REGISTRY_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        audit = promote_ready_dhatus(args.manifest, args.audit, args.canonical_registry)
        print(json.dumps(build_summary(audit), ensure_ascii=False, sort_keys=True))
        return 1 if audit.get("unsafeWriteRefused") else 0
    except Exception as exc:
        print(f"Ready dhatu canonical promotion failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
