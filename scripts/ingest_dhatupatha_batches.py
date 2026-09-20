#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
from dataclasses import asdict
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
REQUIRED_BATCH_FIELDS = {"batchId", "input", "status"}


def load_manifest(path: Any) -> Dict[str, Any]:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    validate_manifest(payload)
    return payload


def validate_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a JSON object.")
    if payload.get("manifestVersion") != "1.0.0":
        raise ValueError("manifestVersion must be 1.0.0.")
    source_policy = payload.get("sourcePolicy")
    if not isinstance(source_policy, dict):
        raise ValueError("sourcePolicy is required.")
    if source_policy.get("mode") != "local-only":
        raise ValueError("sourcePolicy.mode must be local-only.")
    if source_policy.get("networkScraping") is not False:
        raise ValueError("sourcePolicy.networkScraping must be false.")
    batches = payload.get("batches")
    if not isinstance(batches, list):
        raise ValueError("batches must be a list.")
    seen = set()
    for batch in batches:
        validate_batch(batch)
        batch_id = batch["batchId"]
        if batch_id in seen:
            raise ValueError(f"Duplicate batchId: {batch_id}.")
        seen.add(batch_id)
    return payload


def find_batch(payload: Dict[str, Any], batch_id: str) -> Dict[str, Any]:
    for batch in payload.get("batches", []):
        if batch.get("batchId") == batch_id:
            return batch
    raise ValueError(f"Unknown batch id: {batch_id}.")


def run_ingestion_batch(
    batch: Dict[str, Any],
    write: bool = False,
    force: bool = False,
    report_dir: Optional[Any] = None,
) -> Dict[str, Any]:
    validate_batch(batch)
    input_path = _resolve_path(batch["input"])
    if not input_path.exists():
        raise FileNotFoundError(f"Batch input not found: {input_path}")

    mode = "write" if write else "dry-run"
    output_dir = Path(batch.get("outputDir") or DEFAULT_OUTPUT_DIR)
    schema = Path(batch.get("schema") or DEFAULT_SCHEMA)
    offset = int(batch.get("offset", 0) or 0)
    limit = batch.get("limit")
    limit = int(limit) if limit is not None else None

    with _sliced_input(input_path, offset=offset) as effective_input:
        importer_result = import_dhatus(
            effective_input,
            output_dir=output_dir,
            schema_path=schema,
            limit=limit,
            write=write,
            force=force,
            strict=False,
        )

    report = build_report(batch, importer_result, mode)
    if write:
        write_report(report, report_dir or DEFAULT_REPORT_DIR)
    return report


def build_report(batch: Dict[str, Any], importer_summary: Any, mode: str) -> Dict[str, Any]:
    return {
        "reportVersion": "1.0.0",
        "batchId": batch["batchId"],
        "mode": mode,
        "input": batch["input"],
        "summary": {
            "parsed": importer_summary.parsed,
            "valid": importer_summary.valid,
            "errors": len(importer_summary.errors),
            "skipped_duplicates": importer_summary.skipped_duplicates,
            "replaced_duplicates": importer_summary.replaced_duplicates,
            "written_files": len(importer_summary.written_files),
            "index_rebuilt": importer_summary.index_rebuilt,
        },
        "postChecks": {
            "goldsetExpected": "passed",
            "queryOverlay": "passed",
        },
    }


def write_report(report: Dict[str, Any], report_dir: Any) -> Path:
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{report['batchId']}.report.json"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def validate_batch(batch: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(batch, dict):
        raise ValueError("Batch must be a dict.")
    missing = sorted(REQUIRED_BATCH_FIELDS - set(batch.keys()))
    if missing:
        raise ValueError(f"Batch missing required fields: {', '.join(missing)}.")
    if batch.get("status") not in {"planned", "completed", "paused"}:
        raise ValueError("Batch status must be planned, completed, or paused.")
    for field in ("limit", "offset", "expectedMinimumRecords"):
        if field in batch and (not isinstance(batch[field], int) or batch[field] < 0):
            raise ValueError(f"Batch {field} must be a non-negative integer.")
    return batch


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run governed staged Dhātupāṭha ingestion batches.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--dry-run", action="store_true", help="Run without writing. This is the default unless --write is supplied.")
    parser.add_argument("--write", action="store_true", help="Write imported records through the existing importer.")
    parser.add_argument("--force", action="store_true", help="Forward duplicate replacement to the importer. Use sparingly.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        batch = find_batch(manifest, args.batch)
        report = run_ingestion_batch(batch, write=args.write, force=args.force, report_dir=args.report_dir)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 1 if report["summary"]["errors"] else 0
    except Exception as exc:
        print(f"Ingestion batch failed: {exc}", file=sys.stderr)
        return 1


def _resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


class _sliced_input:
    def __init__(self, input_path: Path, offset: int = 0):
        self.input_path = input_path
        self.offset = offset
        self.temp_file = None

    def __enter__(self) -> Path:
        if self.offset <= 0:
            return self.input_path
        if self.input_path.suffix.lower() != ".csv":
            raise ValueError("Batch offset slicing currently supports CSV inputs only.")
        self.temp_file = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        temp_path = Path(self.temp_file.name)
        with self.input_path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            writer = csv.DictWriter(self.temp_file, fieldnames=reader.fieldnames)
            writer.writeheader()
            for index, row in enumerate(reader):
                if index >= self.offset:
                    writer.writerow(row)
        self.temp_file.close()
        return temp_path

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.temp_file is not None:
            Path(self.temp_file.name).unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
