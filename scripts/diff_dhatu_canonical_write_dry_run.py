#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from validate_large_scale_ingestion import ROOT


DEFAULT_COMMAND_MANIFEST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_command_manifest.v1.json"
)
DEFAULT_APPROVAL_VALIDATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_validation.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_PROMOTION_PREVIEW_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_preview.v1.json"
DEFAULT_PROMOTION_PLAN_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_plan.v1.json"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"


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
        raise ValueError(f"Dry-run diff source must be a JSON object: {display_path(resolved)}")
    return payload


def records_by_source_id(records: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    return {
        str(record.get(key)): record
        for record in records
        if record.get(key)
    }


def duplicate_values(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def build_registry_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "canonicalId": record["proposedCanonicalId"],
        "sourceRootId": record["sourceRootId"],
        "canonicalRecord": {
            "canonicalForm": record["devanagari"],
            "gana": {"id": record["gana"]},
            "gloss": record["artha"],
            "promotion": {
                "source": record.get("source", ""),
                "sourceFile": record.get("sourceFile", ""),
                "sourceRootId": record["sourceRootId"],
            },
            "root": record["devanagari"],
            "rootIast": record["iast"],
        },
    }


def build_records_to_add(
    approved_ids: List[str],
    promotion_plan: Dict[str, Any],
    promotion_preview: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], List[str]]:
    planned_by_source = records_by_source_id(promotion_plan.get("plannedRecords", []), "sourceRootId")
    preview_by_source = records_by_source_id(promotion_preview.get("previewRecords", []), "root_id")
    missing_staged = sorted(source_id for source_id in approved_ids if source_id not in preview_by_source)
    records_to_add = [
        build_registry_record(planned_by_source[source_id])
        for source_id in sorted(approved_ids)
        if source_id in planned_by_source and source_id in preview_by_source
    ]
    missing_plan = sorted(source_id for source_id in approved_ids if source_id not in planned_by_source)
    return records_to_add, sorted(set(missing_staged + missing_plan))


def detect_duplicate_ids(records_to_add: List[Dict[str, Any]], registry: Dict[str, Any]) -> List[str]:
    existing_ids = set(registry.get("records", {}).keys())
    proposed_ids = [record["canonicalId"] for record in records_to_add]
    duplicates = set(duplicate_values(proposed_ids))
    duplicates.update(proposed_id for proposed_id in proposed_ids if proposed_id in existing_ids)
    return sorted(duplicates)


def build_contract_checks(
    command_ready: bool,
    approval_validation: Dict[str, Any],
    approved_ids: List[str],
    readiness_lock: Dict[str, Any],
    duplicate_ids: List[str],
    missing_staged_records: List[str],
) -> Dict[str, Any]:
    ready_ids = set(readiness_lock.get("readyRecordIds", []))
    approved_set = set(approved_ids)
    approved_not_ready = sorted(approved_set - ready_ids)
    return {
        "commandManifestReady": command_ready,
        "approvalValidationValid": approval_validation.get("approvalValid") is True,
        "approvedIdsInReadinessLock": not approved_not_ready,
        "noDuplicateIds": not duplicate_ids,
        "approvedRecordsExistInStaging": not missing_staged_records,
        "dryRunOnly": True,
        "canonicalRegistryMutation": False,
        "passed": (
            command_ready
            and approval_validation.get("approvalValid") is True
            and not approved_not_ready
            and not duplicate_ids
            and not missing_staged_records
        ),
        "violations": {
            "approvedIdsNotInReadinessLock": approved_not_ready,
            "duplicateIds": duplicate_ids,
            "missingStagedRecords": missing_staged_records,
        },
    }


def build_refusal_reasons(
    command_manifest: Dict[str, Any],
    approval_validation: Dict[str, Any],
    duplicate_ids: List[str],
    missing_staged_records: List[str],
) -> List[str]:
    reasons: List[str] = []
    if command_manifest.get("commandStatus") != "READY_FOR_MANUAL_EXECUTION":
        reasons.append("Command manifest is not READY_FOR_MANUAL_EXECUTION.")
    reasons.extend(command_manifest.get("refusalReasons", []))
    if approval_validation.get("approvalValid") is not True:
        reasons.append("Approval validation is not valid.")
    reasons.extend(approval_validation.get("refusalReasons", []))
    if duplicate_ids:
        reasons.append("Duplicate canonical ids would be created.")
    if missing_staged_records:
        reasons.append("Approved records are missing from staged preview or promotion plan.")
    return list(dict.fromkeys(reasons))


def build_dry_run_diff(
    command_manifest_path: Any = DEFAULT_COMMAND_MANIFEST_PATH,
    approval_validation_path: Any = DEFAULT_APPROVAL_VALIDATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> Dict[str, Any]:
    command_manifest = load_json(command_manifest_path)
    approval_validation = load_json(approval_validation_path)
    readiness_lock = load_json(DEFAULT_READINESS_LOCK_PATH)
    promotion_preview = load_json(DEFAULT_PROMOTION_PREVIEW_PATH)
    promotion_plan = load_json(DEFAULT_PROMOTION_PLAN_PATH)
    registry = load_json(canonical_registry_path)
    before_count = len(registry.get("records", {}))
    command_ready = command_manifest.get("commandStatus") == "READY_FOR_MANUAL_EXECUTION"
    approved_ids = sorted(approval_validation.get("approvedRecordIds", []))
    candidate_records, missing_staged_records = build_records_to_add(approved_ids, promotion_plan, promotion_preview)
    duplicate_ids = detect_duplicate_ids(candidate_records, registry)
    contract_checks = build_contract_checks(
        command_ready,
        approval_validation,
        approved_ids,
        readiness_lock,
        duplicate_ids,
        missing_staged_records,
    )
    records_to_add = candidate_records if contract_checks["passed"] else []
    records_blocked = sorted(
        set(command_manifest.get("blockedRecordIds", []))
        | set(approval_validation.get("rejectedRecordIds", []))
        | set(missing_staged_records)
    )
    refusal_reasons = build_refusal_reasons(
        command_manifest,
        approval_validation,
        duplicate_ids,
        missing_staged_records,
    )
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/diff_dhatu_canonical_write_dry_run.py",
        "dryRunOnly": True,
        "commandStatus": command_manifest.get("commandStatus"),
        "canonicalRegistryPath": display_path(canonical_registry_path),
        "beforeCount": before_count,
        "afterCountIfApplied": before_count + len(records_to_add),
        "recordsToAdd": records_to_add,
        "recordsBlocked": records_blocked,
        "duplicateIds": duplicate_ids,
        "missingStagedRecords": missing_staged_records,
        "contractChecks": contract_checks,
        "refusalReasons": refusal_reasons,
    }


def write_dry_run_diff(diff: Dict[str, Any], path: Any = DEFAULT_DRY_RUN_DIFF_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(diff, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(diff: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "commandStatus": diff["commandStatus"],
        "dryRunOnly": diff["dryRunOnly"],
        "recordsToAddCount": len(diff["recordsToAdd"]),
        "recordsBlockedCount": len(diff["recordsBlocked"]),
        "refusalCount": len(diff["refusalReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a dry-run diff for canonical dhatu writes.")
    parser.add_argument("--command-manifest", default=str(DEFAULT_COMMAND_MANIFEST_PATH))
    parser.add_argument("--approval-validation-file", default=str(DEFAULT_APPROVAL_VALIDATION_PATH))
    parser.add_argument("--canonical-registry", default=str(DEFAULT_CANONICAL_REGISTRY_PATH))
    parser.add_argument("--output", default=str(DEFAULT_DRY_RUN_DIFF_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        diff = build_dry_run_diff(args.command_manifest, args.approval_validation_file, args.canonical_registry)
        write_dry_run_diff(diff, args.output)
        print(json.dumps(build_summary(diff), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write dry-run diff failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
