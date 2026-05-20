#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from preview_dhatu_batch_promotion import (
    DEFAULT_PREVIEW_PATH,
    build_promotion_preview,
    write_promotion_preview,
)
from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_PLAN_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_plan.v1.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
GOLDSET_ROOT = ROOT / "data" / "sanskrit" / "goldset"
CANONICAL_ID_RE = re.compile(r"^(?P<gana>[0-9]{2})\.(?P<order>[0-9]{4})$")


def load_promotion_preview(path: Any = DEFAULT_PREVIEW_PATH) -> Dict[str, Any]:
    preview_path = Path(path)
    with preview_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("mode") != "dry-run-preview":
        raise ValueError("Promotion preview must be a dry-run preview.")
    if payload.get("canonicalMutation") is not False:
        raise ValueError("Promotion preview must not allow canonical mutation.")
    if "previewRecords" not in payload or not isinstance(payload["previewRecords"], list):
        raise ValueError("Promotion preview missing previewRecords.")
    return payload


def build_canonical_promotion_plan(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(manifest_path)
    preview = build_promotion_preview(manifest_path)
    write_promotion_preview(preview)
    persisted_preview = load_promotion_preview(DEFAULT_PREVIEW_PATH)
    canonical = load_canonical_registry()
    records = sorted(
        persisted_preview["previewRecords"],
        key=lambda record: (record["gana"], record["iast"], record["root_id"]),
    )
    duplicate_roots = duplicate_root_ids(records)
    proposed_ids = propose_canonical_ids(records, canonical["ids"])
    planned_records = [
        build_planned_record(
            record,
            proposed_ids[record["root_id"]],
            persisted_preview,
            canonical,
            duplicate_roots,
        )
        for record in records
    ]
    status_counts = count_statuses(planned_records)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/plan_dhatu_canonical_promotion.py",
        "sourcePreviewFile": "data/sanskrit/ingestion/promotion_preview.v1.json",
        "manifestVersion": manifest["manifestVersion"],
        "totalRecords": len(planned_records),
        "readyCount": status_counts.get("ready", 0),
        "needsReviewCount": status_counts.get("needs_review", 0),
        "blockedCount": status_counts.get("blocked", 0),
        "plannedRecords": planned_records,
        "conflictSummary": build_conflict_summary(planned_records),
        "safetyChecks": {
            "stagedValidationPassed": True,
            "promotionPreviewRegenerated": True,
            "canonicalRegistryMutation": False,
            "goldsetMutation": False,
            "batchMutation": False,
            "deterministicOrdering": True,
            "safeToRegenerate": True,
        },
    }


def load_canonical_registry(dhatu_root: Any = DHATU_ROOT) -> Dict[str, Any]:
    root_path = Path(dhatu_root)
    ids: Set[str] = set()
    roots_by_gana: Dict[str, Set[str]] = {}
    iast_by_gana: Dict[str, Set[str]] = {}
    for path in sorted(root_path.glob("*.json")):
        if path.name == "index.json":
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for record in payload.get("records", []):
            canonical_id = str(record.get("id", "")).strip()
            identity = record.get("identity", {})
            grammar = record.get("grammar", {})
            gana = str(
                grammar.get("gana", {}).get("id")
                or payload.get("gana", {}).get("id")
                or canonical_id.split(".")[0]
            ).strip()
            if canonical_id:
                ids.add(canonical_id)
            root = normalize_text(identity.get("root", ""))
            root_iast = normalize_text(identity.get("rootIast", "")).lower()
            if root:
                roots_by_gana.setdefault(gana, set()).add(root)
            if root_iast:
                iast_by_gana.setdefault(gana, set()).add(root_iast)
    return {
        "ids": ids,
        "rootsByGana": roots_by_gana,
        "iastByGana": iast_by_gana,
    }


def propose_canonical_ids(records: Iterable[Dict[str, Any]], existing_ids: Set[str]) -> Dict[str, str]:
    next_order_by_gana: Dict[str, int] = {}
    for canonical_id in existing_ids:
        match = CANONICAL_ID_RE.match(canonical_id)
        if match:
            gana = match.group("gana")
            next_order_by_gana[gana] = max(next_order_by_gana.get(gana, 0), int(match.group("order")))
    proposals: Dict[str, str] = {}
    for record in records:
        gana = record["gana"]
        order = next_order_by_gana.get(gana, 0) + 1
        proposed_id = f"{gana}.{order:04d}"
        while proposed_id in existing_ids or proposed_id in proposals.values():
            order += 1
            proposed_id = f"{gana}.{order:04d}"
        next_order_by_gana[gana] = order
        proposals[record["root_id"]] = proposed_id
    return proposals


def build_planned_record(
    record: Dict[str, Any],
    proposed_id: str,
    preview: Dict[str, Any],
    canonical: Dict[str, Any],
    duplicate_roots: Set[str],
) -> Dict[str, Any]:
    conflicts = detect_record_conflicts(record, proposed_id, canonical, duplicate_roots)
    missing_optional = preview.get("missingOptionalMetadata", {}).get(record["root_id"], [])
    classification = classify_record(conflicts, missing_optional)
    return {
        "sourceRootId": record["root_id"],
        "proposedCanonicalId": proposed_id,
        "classification": classification,
        "devanagari": record["devanagari"],
        "iast": record["iast"],
        "gana": record["gana"],
        "pada": record["pada"],
        "artha": record["artha"],
        "source": record["source"],
        "sourceFile": record.get("sourceFile", ""),
        "conflicts": conflicts,
        "missingOptionalMetadata": missing_optional,
        "recommendedAction": "manual-review-required" if classification != "ready" else "ready-for-governed-review",
    }


def detect_record_conflicts(
    record: Dict[str, Any],
    proposed_id: str,
    canonical: Dict[str, Any],
    duplicate_roots: Set[str],
) -> List[str]:
    conflicts: List[str] = []
    gana = record["gana"]
    if proposed_id in canonical["ids"]:
        conflicts.append("proposedCanonicalId already exists")
    if record["root_id"] in duplicate_roots:
        conflicts.append("duplicate staged root_id")
    if normalize_text(record["devanagari"]) in canonical["rootsByGana"].get(gana, set()):
        conflicts.append("canonical root already exists in gana")
    if normalize_text(record["iast"]).lower() in canonical["iastByGana"].get(gana, set()):
        conflicts.append("canonical IAST root already exists in gana")
    return conflicts


def classify_record(conflicts: List[str], missing_optional: List[str]) -> str:
    if conflicts:
        return "blocked"
    if missing_optional:
        return "needs_review"
    return "ready"


def build_conflict_summary(planned_records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    by_type: Dict[str, int] = {}
    blocked_root_ids: List[str] = []
    for record in planned_records:
        if record["classification"] == "blocked":
            blocked_root_ids.append(record["sourceRootId"])
        for conflict in record["conflicts"]:
            by_type[conflict] = by_type.get(conflict, 0) + 1
    return {
        "totalConflicts": sum(by_type.values()),
        "byType": dict(sorted(by_type.items())),
        "blockedRootIds": sorted(blocked_root_ids),
    }


def duplicate_root_ids(records: Iterable[Dict[str, Any]]) -> Set[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for record in records:
        root_id = record["root_id"]
        if root_id in seen:
            duplicates.add(root_id)
        seen.add(root_id)
    return duplicates


def count_statuses(planned_records: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in planned_records:
        status = record["classification"]
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_canonical_promotion_plan(plan: Dict[str, Any], path: Any = DEFAULT_PLAN_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(plan, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(plan: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "totalRecords": plan["totalRecords"],
        "readyCount": plan["readyCount"],
        "needsReviewCount": plan["needsReviewCount"],
        "blockedCount": plan["blockedCount"],
        "conflictSummary": plan["conflictSummary"],
        "canonicalRegistryMutation": plan["safetyChecks"]["canonicalRegistryMutation"],
    }


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan canonical dhatu promotion without canonical writes.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        plan = build_canonical_promotion_plan(args.manifest)
        write_canonical_promotion_plan(plan)
        print(json.dumps(build_summary(plan), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical promotion planning failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
