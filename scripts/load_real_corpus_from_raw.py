#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
RAW_CORPUS_ROOT = ROOT / "raw" / "sanskrit"
RAW_LEGACY_ROOT = ROOT / "raw" / "corpus"
RAW_MANIFEST = RAW_CORPUS_ROOT / "manifest.v1.json"
STAGING_MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

EXPECTED_SCHEMA = "sanskrit-bulk-corpus-staging.v1"
MAX_RECORDS = 2000
ALLOWED_TYPES = {"dhatu", "sutra", "stotra"}


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _normalize_record(record: Dict[str, Any], source_file: str) -> Dict[str, Any]:
    return {
        "id": str(record.get("id") or record.get("root_id") or "").strip(),
        "type": str(record.get("type") or "").strip(),
        "text": str(
            record.get("text")
            or record.get("devanagari")
            or record.get("root")
            or record.get("canonicalForm")
            or ""
        ).strip(),
        "source": str(record.get("source") or source_file).strip(),
        "gana": str(record.get("gana") or record.get("gana_id") or "").strip() or None,
        "notes": str(record.get("notes") or record.get("artha") or "").strip() or None,
    }


def _load_batch_file(path: Path) -> Dict[str, Any]:
    payload = _read_json(path)
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    batch_id = str(payload.get("batchId") or path.stem).strip()
    records = []

    for record in payload.get("records", []):
        if not isinstance(record, dict):
            continue
        normalized = _normalize_record(record, rel)
        if normalized["type"] not in ALLOWED_TYPES:
            corpus_type = str(payload.get("corpusType") or "").strip()
            if corpus_type in ALLOWED_TYPES:
                normalized["type"] = corpus_type
        item = {key: value for key, value in normalized.items() if value}
        if item.get("id") and item.get("type") in ALLOWED_TYPES and item.get("text") and item.get("source"):
            records.append(item)

    return {
        "batchId": batch_id,
        "source": rel,
        "lineage": batch_id,
        "corpusType": payload.get("corpusType"),
        "records": records,
    }


def discover_raw_corpus_batches() -> List[Path]:
    paths: List[Path] = []
    roots = [RAW_CORPUS_ROOT]
    if RAW_CORPUS_ROOT.exists() and not any(RAW_CORPUS_ROOT.rglob("*.json")):
        roots.append(RAW_LEGACY_ROOT)
    elif not RAW_CORPUS_ROOT.exists():
        roots = [RAW_LEGACY_ROOT]

    for root in roots:
        for subdir in ("dhatu", "sutra", "stotra"):
            batch_dir = root / subdir
            if batch_dir.exists():
                paths.extend(sorted(batch_dir.glob("*.json")))
    return list(dict.fromkeys(paths))


def load_real_corpus_from_raw(dry_run: bool = True) -> Dict[str, Any]:
    batches: List[Dict[str, Any]] = []
    type_counts = {"dhatu": 0, "sutra": 0, "stotra": 0}
    errors: List[str] = []

    for batch_path in discover_raw_corpus_batches():
        try:
            batch = _load_batch_file(batch_path)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{batch_path.name}:loadError:{exc}")
            continue

        if not batch["records"]:
            errors.append(f"{batch['batchId']}:empty")
            continue

        batches.append(batch)
        for record in batch["records"]:
            record_type = record.get("type")
            if record_type in type_counts:
                type_counts[record_type] += 1

    record_count = sum(type_counts.values())
    seen_ids = set()
    duplicate_ids = []

    for batch in batches:
        for record in batch["records"]:
            record_id = record["id"]
            if record_id in seen_ids and record_id not in duplicate_ids:
                duplicate_ids.append(record_id)
            seen_ids.add(record_id)

    if duplicate_ids:
        errors.append("duplicateRecordIds")

    if record_count > MAX_RECORDS:
        errors.append("recordLimitExceeded")

    raw_manifest = _read_json(RAW_MANIFEST) if RAW_MANIFEST.exists() else {}
    manifest = {
        "schemaVersion": EXPECTED_SCHEMA,
        "status": "staging-ready" if not errors else "staging-invalid",
        "mode": "preview-only",
        "canonicalWriteAllowed": False,
        "maxRecords": MAX_RECORDS,
        "batches": batches,
        "metadata": {
            "createdFor": "Phase 11 Real Corpus Loading",
            "readOnly": True,
            "phase": "11",
            "rawManifest": str(RAW_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "targets": raw_manifest.get("targets", {}),
            "typeCounts": type_counts,
            "recordCount": record_count,
            "seedDhatuCount": raw_manifest.get("seedDhatuCount"),
        },
    }

    valid = not errors and record_count > 0

    if not dry_run and valid:
        _write_json(STAGING_MANIFEST, manifest)

    return {
        "valid": valid,
        "phase": "11",
        "dryRun": dry_run,
        "written": not dry_run and valid,
        "stagingManifest": str(STAGING_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "batchCount": len(batches),
        "recordCount": record_count,
        "typeCounts": type_counts,
        "duplicateIds": duplicate_ids,
        "errors": errors,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Load real corpus from raw/ into corpus-staging manifest.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write bulk_corpus_manifest.v1.json (default is dry-run preview).",
    )
    args = parser.parse_args()
    result = load_real_corpus_from_raw(dry_run=not args.write)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())