#!/usr/bin/env python
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from plan_dhatu_canonical_promotion import (
    DEFAULT_PLAN_PATH,
    build_canonical_promotion_plan,
    build_conflict_summary,
    count_statuses,
    write_canonical_promotion_plan,
)
from preview_dhatu_batch_promotion import build_promotion_preview, write_promotion_preview
from validate_large_scale_ingestion import DEFAULT_MANIFEST, ROOT, load_large_scale_manifest


DEFAULT_REVIEW_DECISIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "review_decisions.v1.json"
DEFAULT_REVIEWED_PLAN_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_plan.reviewed.v1.json"
ALLOWED_DECISIONS = {"approve", "reject", "defer"}


def load_review_decisions(path: Any = DEFAULT_REVIEW_DECISIONS_PATH) -> Dict[str, Any]:
    decisions_path = Path(path)
    with decisions_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_review_decisions(payload)


def validate_review_decisions(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Review decisions must be a JSON object.")
    for field in ("schemaVersion", "policy", "decisions"):
        if field not in payload:
            raise ValueError(f"Review decisions missing field: {field}.")
    policy = payload["policy"]
    if not isinstance(policy, dict):
        raise ValueError("Review decisions policy must be an object.")
    if policy.get("defaultDecision") != "defer":
        raise ValueError("Review decisions must default missing decisions to defer.")
    for mutation_field in ("canonicalMutation", "goldsetMutation", "batchMutation"):
        if policy.get(mutation_field) is not False:
            raise ValueError(f"Review decisions must disable {mutation_field}.")
    decisions = payload["decisions"]
    if not isinstance(decisions, dict):
        raise ValueError("Review decisions decisions field must be an object.")
    for source_root_id, decision in decisions.items():
        if not isinstance(decision, dict):
            raise ValueError(f"Decision for {source_root_id} must be an object.")
        value = decision.get("decision")
        if value not in ALLOWED_DECISIONS:
            raise ValueError(f"Invalid review decision for {source_root_id}: {value}.")
        reviewer = str(decision.get("reviewer", "")).strip()
        if not reviewer:
            raise ValueError(f"Review decision for {source_root_id} must include reviewer.")
        if "rationale" not in decision:
            raise ValueError(f"Review decision for {source_root_id} must include rationale.")
    return payload


def load_canonical_promotion_plan(path: Any = DEFAULT_PLAN_PATH) -> Dict[str, Any]:
    plan_path = Path(path)
    with plan_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if "plannedRecords" not in payload or not isinstance(payload["plannedRecords"], list):
        raise ValueError("Canonical promotion plan missing plannedRecords.")
    return payload


def build_reviewed_promotion_plan(
    manifest_path: Any = DEFAULT_MANIFEST,
    decisions_path: Any = DEFAULT_REVIEW_DECISIONS_PATH,
) -> Dict[str, Any]:
    load_large_scale_manifest(manifest_path)
    preview = build_promotion_preview(manifest_path)
    write_promotion_preview(preview)
    plan = build_canonical_promotion_plan(manifest_path)
    write_canonical_promotion_plan(plan)
    persisted_plan = load_canonical_promotion_plan(DEFAULT_PLAN_PATH)
    decisions = load_review_decisions(decisions_path)
    return apply_review_decisions(persisted_plan, decisions)


def apply_review_decisions(plan: Dict[str, Any], decisions_payload: Dict[str, Any]) -> Dict[str, Any]:
    decisions = decisions_payload.get("decisions", {})
    reviewed_records = [
        apply_decision_to_record(record, decisions.get(record["sourceRootId"]))
        for record in plan.get("plannedRecords", [])
    ]
    counts = count_statuses(reviewed_records)
    reviewed = copy.deepcopy(plan)
    reviewed["schemaVersion"] = "1.0.0"
    reviewed["generatedBy"] = "scripts/apply_dhatu_review_decisions.py"
    reviewed["sourcePlanFile"] = "data/sanskrit/ingestion/canonical_promotion_plan.v1.json"
    reviewed["sourceReviewDecisionsFile"] = "data/sanskrit/ingestion/review_decisions.v1.json"
    reviewed["reviewDefault"] = "defer"
    reviewed["plannedRecords"] = reviewed_records
    reviewed["readyCount"] = counts.get("ready", 0)
    reviewed["needsReviewCount"] = counts.get("needs_review", 0)
    reviewed["blockedCount"] = counts.get("blocked", 0)
    reviewed["conflictSummary"] = build_conflict_summary(reviewed_records)
    reviewed["safetyChecks"] = {
        **reviewed.get("safetyChecks", {}),
        "reviewDecisionsValidated": True,
        "canonicalRegistryMutation": False,
        "goldsetMutation": False,
        "batchMutation": False,
        "deterministicOrdering": True,
        "safeToRegenerate": True,
    }
    return reviewed


def apply_decision_to_record(record: Dict[str, Any], decision_entry: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    reviewed = copy.deepcopy(record)
    original_classification = reviewed["classification"]
    decision = decision_entry.get("decision") if decision_entry else "defer"
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"Invalid review decision: {decision}.")

    if original_classification == "blocked":
        classification = "blocked"
    elif decision == "reject":
        classification = "blocked"
        conflicts = list(reviewed.get("conflicts", []))
        if "reviewer rejected" not in conflicts:
            conflicts.append("reviewer rejected")
        reviewed["conflicts"] = sorted(conflicts)
    elif original_classification == "ready":
        classification = "ready"
    elif decision == "approve":
        classification = "ready"
    else:
        classification = "needs_review"

    reviewed["classification"] = classification
    reviewed["reviewDecision"] = decision
    reviewed["reviewer"] = decision_entry.get("reviewer", "default-review-gate") if decision_entry else "default-review-gate"
    reviewed["reviewRationale"] = decision_entry.get("rationale", "Missing decision defaults to defer.") if decision_entry else "Missing decision defaults to defer."
    reviewed["recommendedAction"] = reviewed_action_for(classification)
    return reviewed


def reviewed_action_for(classification: str) -> str:
    if classification == "ready":
        return "ready-for-governed-review"
    if classification == "blocked":
        return "blocked-by-review"
    return "manual-review-required"


def write_reviewed_promotion_plan(plan: Dict[str, Any], path: Any = DEFAULT_REVIEWED_PLAN_PATH) -> Path:
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
        "reviewDefault": plan["reviewDefault"],
        "canonicalRegistryMutation": plan["safetyChecks"]["canonicalRegistryMutation"],
    }


def decision_counts(records: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        decision = record.get("reviewDecision", "defer")
        counts[decision] = counts.get(decision, 0) + 1
    return dict(sorted(counts.items()))


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply dhatu review decisions without canonical writes.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--decisions", default=str(DEFAULT_REVIEW_DECISIONS_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        reviewed = build_reviewed_promotion_plan(args.manifest, args.decisions)
        write_reviewed_promotion_plan(reviewed)
        print(json.dumps(build_summary(reviewed), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu review decision application failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
