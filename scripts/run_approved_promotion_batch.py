#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from promote_verified_dhatus import load_promotion, run_promotion


DEFAULT_MANIFEST = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_batches.v1.json"
DEFAULT_PREFERENCES = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_preferences.v1.json"
DEFAULT_ATTRIBUTION = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
DEFAULT_RECENSIONS = ROOT / "data" / "sanskrit" / "ingestion" / "recensions.v1.json"
DEFAULT_EDITORIAL = ROOT / "data" / "sanskrit" / "ingestion" / "editorial_resolutions.v1.json"
DEFAULT_REPORT_DIR = ROOT / "data" / "sanskrit" / "ingestion" / "reports"
VALID_BATCH_STATUSES = {"planned", "active", "completed", "paused"}
VALID_PROMOTION_STATUSES = {"approved", "deferred", "rejected"}


def load_promotion_batch_manifest(path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest_path = _resolve_path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_promotion_batch_manifest(payload)


def validate_promotion_batch_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Promotion batch manifest must be a JSON object.")
    for field in ("batchVersion", "policy", "batches"):
        if field not in payload:
            raise ValueError(f"Promotion batch manifest missing field: {field}.")
    policy = _require_dict(payload["policy"], "policy")
    if policy.get("defaultMode") != "dry-run":
        raise ValueError("Promotion batch defaultMode must be dry-run.")
    if policy.get("requiresWriteFlag") is not True:
        raise ValueError("Promotion batch policy must require --write.")
    if policy.get("requiresApprovedPromotion") is not True:
        raise ValueError("Promotion batch policy must require approved promotions.")
    if policy.get("requiresCanonicalPreference") is not True:
        raise ValueError("Promotion batch policy must require canonical preferences.")
    if policy.get("requiresSourceAttribution") is not True:
        raise ValueError("Promotion batch policy must require source attribution.")
    if policy.get("autoPromote") is not False:
        raise ValueError("Promotion batch policy must not auto-promote.")
    if not isinstance(payload["batches"], list):
        raise ValueError("Promotion batches must be a list.")
    for batch in payload["batches"]:
        _validate_batch(batch)
    return payload


def find_promotion_batch(payload: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
    for batch in payload.get("batches", []):
        if batch.get("batchId") == batch_id:
            return batch
    raise ValueError(f"Unknown promotion batch: {batch_id}.")


def collect_approved_candidates(
    batch: Dict[str, Any],
    verified_promotions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    allowed_statuses = set(batch.get("allowedStatuses", []))
    if allowed_statuses != {"approved"}:
        raise ValueError("Promotion batch may only allow approved status.")
    return [
        record
        for record in verified_promotions.get("records", [])
        if record.get("status") == "approved"
    ]


def validate_candidate_governance(
    candidate: Dict[str, Any],
    preferences: Dict[str, Any],
    attribution: Dict[str, Any],
    recensions: Dict[str, Any],
    editorial: Dict[str, Any],
) -> List[str]:
    candidate_id = candidate.get("id")
    errors: List[str] = []
    if candidate.get("status") != "approved":
        errors.append(f"{candidate_id}: promotion status is not approved.")

    record_attribution = attribution.get("recordAttributions", {}).get(candidate_id)
    if not record_attribution:
        errors.append(f"{candidate_id}: missing source attribution.")

    preference = preferences.get("candidatePreferences", {}).get(candidate_id)
    if not preference:
        errors.append(f"{candidate_id}: missing canonical preference.")
    elif preference.get("preferenceStatus") != "canonical":
        errors.append(f"{candidate_id}: canonical preference is not canonical.")

    unresolved = recensions.get("unresolvedReadings", {}).get(candidate_id)
    if unresolved and unresolved.get("status") in {"deferred", "needs-review", "rejected"}:
        errors.append(f"{candidate_id}: recension layer marks candidate unresolved/{unresolved.get('status')}.")

    recommendation = editorial.get("recommendations", {}).get(candidate_id)
    if recommendation and recommendation.get("status") in {"defer", "reject", "needs-review"}:
        errors.append(f"{candidate_id}: editorial recommendation is {recommendation.get('status')}.")

    return errors


def run_approved_promotion_batch(
    batch_id: str,
    write: bool = False,
    force: bool = False,
    manifest: Any = DEFAULT_MANIFEST,
    report_dir: Any = DEFAULT_REPORT_DIR,
    preferences_path: Any = DEFAULT_PREFERENCES,
    attribution_path: Any = DEFAULT_ATTRIBUTION,
    recensions_path: Any = DEFAULT_RECENSIONS,
    editorial_path: Any = DEFAULT_EDITORIAL,
) -> Dict[str, Any]:
    manifest_payload = load_promotion_batch_manifest(manifest)
    batch = find_promotion_batch(manifest_payload, batch_id)
    verified_promotions = load_promotion(batch["sourcePromotionFile"])
    preferences = _load_json(preferences_path)
    attribution = _load_json(attribution_path)
    recensions = _load_json(recensions_path)
    editorial = _load_json(editorial_path)

    approved = collect_approved_candidates(batch, verified_promotions)
    deferred = [record for record in verified_promotions.get("records", []) if record.get("status") == "deferred"]
    rejected = [record for record in verified_promotions.get("records", []) if record.get("status") == "rejected"]
    errors: List[str] = []
    for candidate in approved:
        errors.extend(validate_candidate_governance(candidate, preferences, attribution, recensions, editorial))

    promoted = 0
    if write and approved and not errors:
        promotion_report = run_promotion(
            batch["sourcePromotionFile"],
            write=True,
            force=force,
            report_dir=report_dir,
        )
        promoted = promotion_report.get("promoted", 0)
        errors.extend(promotion_report.get("errors", []))

    report = build_promotion_batch_report(
        batch_id=batch_id,
        mode="write" if write else "dry-run",
        approved_candidates=len(approved),
        promoted=promoted,
        skipped_deferred=len(deferred),
        skipped_rejected=len(rejected),
        errors=errors,
        canonical_mutation=bool(write and promoted),
    )
    if write:
        write_promotion_batch_report(report, report_dir)
    return report


def build_promotion_batch_report(
    batch_id: str,
    mode: str,
    approved_candidates: int,
    promoted: int,
    skipped_deferred: int,
    skipped_rejected: int,
    errors: List[str],
    canonical_mutation: bool,
) -> Dict[str, Any]:
    return {
        "reportVersion": "1.0.0",
        "batchId": batch_id,
        "mode": mode,
        "approvedCandidates": approved_candidates,
        "promoted": promoted,
        "skippedDeferred": skipped_deferred,
        "skippedRejected": skipped_rejected,
        "errors": list(errors),
        "canonicalMutation": canonical_mutation,
    }


def write_promotion_batch_report(report: Dict[str, Any], report_dir: Any = DEFAULT_REPORT_DIR) -> Path:
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{report['batchId']}.report.json"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run approved dhatu promotion batches.")
    parser.add_argument("--batch", required=True)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--dry-run", action="store_true", help="Validate without canonical writes. Default unless --write is passed.")
    parser.add_argument("--write", action="store_true", help="Execute approved canonical writes through the existing promotion path.")
    parser.add_argument("--force", action="store_true", help="Forward duplicate replacement to importer. Discouraged.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = run_approved_promotion_batch(
            args.batch,
            write=args.write,
            force=args.force,
            manifest=args.manifest,
            report_dir=args.report_dir,
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1 if report["errors"] else 0
    except Exception as exc:
        print(f"Approved promotion batch failed: {exc}", file=sys.stderr)
        return 1


def _validate_batch(batch: Dict[str, Any]) -> None:
    for field in ("batchId", "sourcePromotionFile", "sourceRawFile", "status", "allowedStatuses", "notes"):
        if field not in batch:
            raise ValueError(f"Promotion batch missing field: {field}.")
    if batch["status"] not in VALID_BATCH_STATUSES:
        raise ValueError(f"Invalid promotion batch status: {batch['status']}.")
    if not isinstance(batch["allowedStatuses"], list):
        raise ValueError("Promotion batch allowedStatuses must be a list.")
    if set(batch["allowedStatuses"]) - VALID_PROMOTION_STATUSES:
        raise ValueError("Promotion batch has invalid allowedStatuses.")


def _load_json(path: Any) -> Dict[str, Any]:
    resolved = _resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
