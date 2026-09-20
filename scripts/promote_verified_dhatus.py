#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from import_dhatus import import_dhatus


DEFAULT_REPORT_DIR = ROOT / "data" / "sanskrit" / "ingestion" / "reports"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "sanskrit" / "dhatus"
DEFAULT_SCHEMA = ROOT / "data" / "sanskrit" / "schemas" / "dhatu.schema.v2.json"
VALID_STATUSES = {"approved", "deferred", "rejected"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def load_promotion(path: Any) -> Dict[str, Any]:
    promotion_path = Path(path)
    with promotion_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_promotion_payload(payload)
    return payload


def validate_promotion_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Promotion payload must be a JSON object.")
    for field in ("promotionVersion", "description", "sourceBatch", "sourceFile", "records"):
        if field not in payload:
            raise ValueError(f"Promotion payload missing field: {field}.")
    if payload["promotionVersion"] != "1.0.0":
        raise ValueError("promotionVersion must be 1.0.0.")
    if not isinstance(payload["records"], list):
        raise ValueError("Promotion records must be a list.")
    seen = set()
    for record in payload["records"]:
        validate_promotion_record(record)
        if record["id"] in seen:
            raise ValueError(f"Duplicate promotion id: {record['id']}.")
        seen.add(record["id"])
    return payload


def validate_promotion_record(record: Dict[str, Any]) -> Dict[str, Any]:
    required = {"id", "root", "canonicalForm", "gana_id", "status", "sourceConfidence"}
    if not isinstance(record, dict):
        raise ValueError("Promotion record must be a dict.")
    missing = sorted(required - set(record.keys()))
    if missing:
        raise ValueError(f"Promotion record missing fields: {', '.join(missing)}.")
    if record["status"] not in VALID_STATUSES:
        raise ValueError(f"Invalid promotion status: {record['status']}.")
    if record["sourceConfidence"] not in VALID_CONFIDENCE:
        raise ValueError(f"Invalid sourceConfidence: {record['sourceConfidence']}.")
    return record


def load_source_rows(path: Any) -> Dict[str, Dict[str, str]]:
    source_path = _resolve_path(path)
    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["id"]: {key: (value or "").strip() for key, value in row.items()} for row in rows}


def select_approved_records(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [record for record in payload["records"] if record.get("status") == "approved"]


def validate_approved_against_source(payload: Dict[str, Any], source_rows: Dict[str, Dict[str, str]]) -> List[str]:
    errors = []
    for record in select_approved_records(payload):
        source = source_rows.get(record["id"])
        if source is None:
            errors.append(f"Approved id not found in source CSV: {record['id']}.")
            continue
        for field in ("id", "root", "canonicalForm", "gana_id"):
            if str(record[field]) != str(source.get(field, "")):
                errors.append(f"Approved record {record['id']} mismatch for {field}.")
    return errors


def run_promotion(
    promotion_path: Any,
    write: bool = False,
    force: bool = False,
    report_dir: Optional[Any] = None,
) -> Dict[str, Any]:
    payload = load_promotion(promotion_path)
    source_rows = load_source_rows(payload["sourceFile"])
    errors = validate_approved_against_source(payload, source_rows)
    approved = select_approved_records(payload)
    deferred = [record for record in payload["records"] if record.get("status") == "deferred"]
    rejected = [record for record in payload["records"] if record.get("status") == "rejected"]

    promoted = 0
    if approved and not errors:
        csv_path = _write_approved_temp_csv(approved, source_rows)
        try:
            result = import_dhatus(
                csv_path,
                output_dir=DEFAULT_OUTPUT_DIR,
                schema_path=DEFAULT_SCHEMA,
                write=write,
                force=force,
                strict=True,
            )
            errors.extend(error.message for error in result.errors)
            promoted = result.valid if write and not result.errors else 0
        finally:
            csv_path.unlink(missing_ok=True)

    report = build_report(payload, mode="write" if write else "dry-run", approved=len(approved), promoted=promoted, deferred=len(deferred), rejected=len(rejected), errors=errors)
    if write:
        write_report(report, report_dir or DEFAULT_REPORT_DIR)
    return report


def build_report(
    payload: Dict[str, Any],
    mode: str,
    approved: int,
    promoted: int,
    deferred: int,
    rejected: int,
    errors: List[str],
) -> Dict[str, Any]:
    return {
        "reportVersion": "1.0.0",
        "promotionVersion": payload["promotionVersion"],
        "mode": mode,
        "approved": approved,
        "promoted": promoted,
        "deferred": deferred,
        "rejected": rejected,
        "errors": list(errors),
    }


def write_report(report: Dict[str, Any], report_dir: Any) -> Path:
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"verified_promotion_{report['promotionVersion']}.json"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote reviewed dhatu rows into the canonical registry.")
    parser.add_argument("--promotion", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Validate without canonical writes. Default unless --write is passed.")
    parser.add_argument("--write", action="store_true", help="Promote approved rows through the existing importer.")
    parser.add_argument("--force", action="store_true", help="Forward duplicate replacement to importer. Discouraged.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = run_promotion(args.promotion, write=args.write, force=args.force, report_dir=args.report_dir)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1 if report["errors"] else 0
    except Exception as exc:
        print(f"Verified promotion failed: {exc}", file=sys.stderr)
        return 1


def _write_approved_temp_csv(approved: List[Dict[str, Any]], source_rows: Dict[str, Dict[str, str]]) -> Path:
    import tempfile

    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
    path = Path(temp.name)
    fieldnames = list(next(iter(source_rows.values())).keys()) if source_rows else []
    writer = csv.DictWriter(temp, fieldnames=fieldnames)
    writer.writeheader()
    for record in approved:
        writer.writerow(source_rows[record["id"]])
    temp.close()
    return path


def _resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


if __name__ == "__main__":
    raise SystemExit(main())
