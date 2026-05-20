#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "sanskrit" / "ingestion" / "large_scale_manifest.v1.json"
DEFAULT_REPORT_DIR = ROOT / "data" / "sanskrit" / "ingestion" / "reports"
RAW_BATCH_ROOT = ROOT / "raw" / "dhatupatha_batches"
GANA_ID_RE = re.compile(r"^[0-9]{2}$")
VALID_BATCH_STATUSES = {"planned", "ready", "paused", "completed"}
REQUIRED_STAGED_FIELDS = {"root_id", "devanagari", "iast", "gana", "pada", "artha", "source", "status"}


def load_large_scale_manifest(path: Any) -> Dict[str, Any]:
    manifest_path = _resolve_path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_large_scale_manifest(payload)


def validate_large_scale_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Large-scale manifest must be a JSON object.")
    for field in ("manifestVersion", "policy", "ganaBatches"):
        if field not in payload:
            raise ValueError(f"Large-scale manifest missing field: {field}.")

    policy = _require_dict(payload["policy"], "policy")
    if policy.get("mode") != "local-only":
        raise ValueError("Large-scale ingestion mode must be local-only.")
    if policy.get("networkScraping") is not False:
        raise ValueError("Large-scale ingestion must disable network scraping.")
    if policy.get("defaultOperation") != "dry-run":
        raise ValueError("Large-scale ingestion default operation must be dry-run.")
    if policy.get("allowDirectCanonicalWrite") is not False:
        raise ValueError("Large-scale ingestion must not allow direct canonical writes.")

    batches = payload["ganaBatches"]
    if not isinstance(batches, list):
        raise ValueError("ganaBatches must be a list.")
    if len(batches) != 10:
        raise ValueError("Large-scale manifest must contain exactly 10 gana batches.")

    seen_ids = set()
    seen_slugs = set()
    for batch in batches:
        _validate_gana_batch(batch)
        gana_id = batch["ganaId"]
        slug = batch["slug"]
        if gana_id in seen_ids:
            raise ValueError(f"Duplicate ganaId: {gana_id}.")
        if slug in seen_slugs:
            raise ValueError(f"Duplicate slug: {slug}.")
        seen_ids.add(gana_id)
        seen_slugs.add(slug)
    expected_ids = {f"{value:02d}" for value in range(1, 11)}
    if seen_ids != expected_ids:
        raise ValueError("Large-scale manifest must include gana ids 01 through 10.")
    _validate_batch_file_coverage(payload)
    _validate_global_staged_records(payload)
    return payload


def list_gana_batches(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [dict(batch) for batch in payload.get("ganaBatches", [])]


def find_gana_batch(payload: Dict[str, Any], gana_id_or_slug: str) -> Dict[str, Any]:
    for batch in payload.get("ganaBatches", []):
        if batch.get("ganaId") == gana_id_or_slug or batch.get("slug") == gana_id_or_slug:
            return dict(batch)
    raise ValueError(f"Unknown gana batch: {gana_id_or_slug}.")


def discover_staged_batch_files(root_dir: Any = RAW_BATCH_ROOT) -> List[str]:
    root_path = _resolve_path(root_dir)
    if not root_path.exists():
        return []
    return [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in sorted(root_path.rglob("*.json"))
    ]


def list_manifest_batch_files(payload: Dict[str, Any]) -> List[str]:
    batch_files: List[str] = []
    for batch in payload.get("ganaBatches", []):
        for batch_file in batch.get("batchFiles", []):
            batch_files.append(str(batch_file).replace("\\", "/"))
    return sorted(batch_files)


def scan_raw_batch_directory(raw_dir: Any) -> List[Dict[str, str]]:
    raw_path = _resolve_path(raw_dir)
    if not raw_path.exists():
        raise ValueError(f"Raw batch directory does not exist: {raw_dir}.")
    records: List[Dict[str, str]] = []
    for csv_path in sorted(raw_path.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                record = {key: (value or "").strip() for key, value in row.items()}
                record["sourceFile"] = str(csv_path.relative_to(ROOT)).replace("\\", "/")
                records.append(record)
    for json_path in sorted(raw_path.glob("*.json")):
        records.extend(_load_json_batch_records(json_path))
    return records


def scan_all_staged_batch_files(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    return {
        batch_file: _load_json_batch_records(_resolve_path(batch_file))
        for batch_file in list_manifest_batch_files(payload)
    }


def detect_duplicate_ids(records: List[Dict[str, Any]]) -> List[str]:
    seen = set()
    duplicates = set()
    for record in records:
        record_id = record.get("root_id") or record.get("id")
        if not record_id:
            continue
        if record_id in seen:
            duplicates.add(record_id)
        seen.add(record_id)
    return sorted(duplicates)


def detect_cross_batch_collisions(batch_records: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
    owners: Dict[str, List[str]] = {}
    for batch_id, records in batch_records.items():
        for record in records:
            record_id = record.get("root_id") or record.get("id")
            if record_id:
                owners.setdefault(record_id, []).append(batch_id)
    return {
        record_id: sorted(set(batch_ids))
        for record_id, batch_ids in sorted(owners.items())
        if len(set(batch_ids)) > 1
    }


def validate_batch_readiness(batch: Dict[str, Any]) -> Dict[str, Any]:
    records = scan_raw_batch_directory(batch["rawDir"])
    duplicate_ids = detect_duplicate_ids(records)
    errors = [f"Duplicate id in batch: {record_id}." for record_id in duplicate_ids]
    for record in records:
        errors.extend(_validate_staged_record(record, batch))
    ready = batch.get("status") == "ready" and not errors and bool(records)
    return {
        "ganaId": batch["ganaId"],
        "slug": batch["slug"],
        "recordCount": len(records),
        "ready": ready,
        "errors": errors,
        "warnings": [] if records else ["No raw records staged."],
    }


def build_large_scale_readiness_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    validate_large_scale_manifest(payload)
    batch_results = [validate_batch_readiness(batch) for batch in payload["ganaBatches"]]
    batch_records = scan_all_staged_batch_files(payload)
    global_collisions = detect_cross_batch_collisions(batch_records)
    errors = [
        error
        for result in batch_results
        for error in result["errors"]
    ]
    errors.extend(
        f"Global root_id collision: {record_id} in {', '.join(batch_files)}."
        for record_id, batch_files in global_collisions.items()
    )
    warnings = [
        f"{result['ganaId']}: {warning}"
        for result in batch_results
        for warning in result["warnings"]
    ]
    return {
        "reportVersion": "1.0.0",
        "manifestVersion": payload["manifestVersion"],
        "mode": "readiness-check",
        "ganaCount": len(payload["ganaBatches"]),
        "readyBatches": len([result for result in batch_results if result["ready"]]),
        "plannedBatches": len([batch for batch in payload["ganaBatches"] if batch.get("status") == "planned"]),
        "stagedBatchFiles": len(batch_records),
        "stagedRecords": sum(len(records) for records in batch_records.values()),
        "errors": errors,
        "warnings": warnings,
    }


def write_large_scale_report(report: Dict[str, Any], report_dir: Any = DEFAULT_REPORT_DIR) -> Path:
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "large_scale_ingestion_readiness.report.json"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate large-scale local Dhātupāṭha ingestion readiness.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--gana")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        payload = load_large_scale_manifest(args.manifest)
        if args.gana:
            batch = find_gana_batch(payload, args.gana)
            report = validate_batch_readiness(batch)
        else:
            report = build_large_scale_readiness_report(payload)
        if args.report:
            write_large_scale_report(report, args.report_dir)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1 if report.get("errors") else 0
    except Exception as exc:
        print(f"Large-scale ingestion validation failed: {exc}", file=__import__("sys").stderr)
        return 1


def _validate_gana_batch(batch: Dict[str, Any]) -> None:
    for field in ("ganaId", "slug", "rawDir", "status", "targetScale", "notes"):
        if field not in batch:
            raise ValueError(f"Gana batch missing field: {field}.")
    if not GANA_ID_RE.match(batch["ganaId"]):
        raise ValueError(f"Invalid ganaId: {batch['ganaId']}.")
    if batch["status"] not in VALID_BATCH_STATUSES:
        raise ValueError(f"Invalid batch status: {batch['status']}.")
    raw_dir = str(batch["rawDir"]).replace("\\", "/")
    if raw_dir.startswith(("http://", "https://")):
        raise ValueError(f"Network source is not allowed: {raw_dir}.")
    if not raw_dir.startswith("raw/dhatupatha_batches/"):
        raise ValueError(f"rawDir must stay under raw/dhatupatha_batches: {raw_dir}.")
    if "data/sanskrit/dhatus" in raw_dir:
        raise ValueError("Large-scale batches must not target canonical dhatu registry.")
    raw_path = _resolve_path(raw_dir)
    if not raw_path.exists():
        raise ValueError(f"rawDir does not exist: {raw_dir}.")
    for batch_file in batch.get("batchFiles", []):
        normalized_file = str(batch_file).replace("\\", "/")
        batch_file_path = _resolve_path(normalized_file)
        if normalized_file.startswith(("http://", "https://")):
            raise ValueError(f"Network source is not allowed: {normalized_file}.")
        if not normalized_file.startswith(f"{raw_dir}/"):
            raise ValueError(f"batchFile must stay under rawDir: {normalized_file}.")
        if "data/sanskrit/dhatus" in normalized_file:
            raise ValueError("Large-scale batch files must not target canonical dhatu registry.")
        if not batch_file_path.exists():
            raise ValueError(f"batchFile does not exist: {normalized_file}.")
        if batch_file_path.suffix != ".json":
            raise ValueError(f"batchFile must be JSON: {normalized_file}.")
        _validate_json_batch_file(batch_file_path, batch)


def _validate_batch_file_coverage(payload: Dict[str, Any]) -> None:
    manifest_files = set(list_manifest_batch_files(payload))
    discovered_files = set(discover_staged_batch_files())
    if manifest_files != discovered_files:
        missing = sorted(discovered_files - manifest_files)
        stale = sorted(manifest_files - discovered_files)
        if missing:
            raise ValueError(f"Discovered batch files missing from manifest: {', '.join(missing)}.")
        if stale:
            raise ValueError(f"Manifest batch files not discovered on disk: {', '.join(stale)}.")
    expected_count = payload.get("batchFileCount")
    if expected_count is not None and expected_count != len(discovered_files):
        raise ValueError("Manifest batchFileCount does not match discovered batch files.")


def _validate_global_staged_records(payload: Dict[str, Any]) -> None:
    collisions = detect_cross_batch_collisions(scan_all_staged_batch_files(payload))
    if collisions:
        collision_text = ", ".join(sorted(collisions))
        raise ValueError(f"Global root_id collisions detected: {collision_text}.")


def _load_json_batch_records(json_path: Path) -> List[Dict[str, str]]:
    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        records = payload["records"]
    else:
        raise ValueError(f"JSON batch must contain a records list: {json_path}.")
    normalized = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"JSON batch record must be an object: {json_path}.")
        item = {key: str(value).strip() for key, value in record.items()}
        item["sourceFile"] = _display_path(json_path)
        normalized.append(item)
    return normalized


def _validate_json_batch_file(json_path: Path, batch: Dict[str, Any]) -> None:
    records = _load_json_batch_records(json_path)
    if not records:
        raise ValueError(f"JSON batch must not be empty: {json_path}.")
    duplicate_ids = detect_duplicate_ids(records)
    if duplicate_ids:
        raise ValueError(f"Duplicate root_id values in {json_path}: {', '.join(duplicate_ids)}.")
    errors: List[str] = []
    for record in records:
        errors.extend(_validate_staged_record(record, batch))
    if errors:
        raise ValueError(f"Invalid staged records in {json_path}: {'; '.join(errors)}")


def _validate_staged_record(record: Dict[str, Any], batch: Dict[str, Any]) -> List[str]:
    record_id = record.get("root_id") or record.get("id") or "<missing>"
    errors: List[str] = []
    missing = sorted(REQUIRED_STAGED_FIELDS - set(record.keys()))
    if missing:
        errors.append(f"{record_id}: missing required fields: {', '.join(missing)}.")
    if record.get("status") != "staged":
        errors.append(f"{record_id}: status must be staged.")
    if record.get("gana") != batch.get("ganaId"):
        errors.append(f"{record_id}: record gana does not match folder gana {batch.get('ganaId')}.")
    source = str(record.get("source", ""))
    if source.startswith(("http://", "https://")):
        errors.append(f"{record_id}: network source is not allowed.")
    return errors


def _resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
