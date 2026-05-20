#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from validate_large_scale_ingestion import (
    DEFAULT_MANIFEST,
    ROOT,
    load_large_scale_manifest,
    scan_all_staged_batch_files,
)


DEFAULT_PREVIEW_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_preview.v1.json"
OPTIONAL_METADATA_FIELDS = (
    "upadesha",
    "artha_en",
    "source_detail",
    "recension",
    "editorial_note",
)


def load_validated_staged_records(manifest_path: Any = DEFAULT_MANIFEST) -> List[Dict[str, str]]:
    payload = load_large_scale_manifest(manifest_path)
    records: List[Dict[str, str]] = []
    for batch_file, batch_records in scan_all_staged_batch_files(payload).items():
        for record in batch_records:
            item = dict(record)
            item["batchFile"] = batch_file
            records.append(item)
    return records


def build_promotion_preview(manifest_path: Any = DEFAULT_MANIFEST) -> Dict[str, Any]:
    manifest = load_large_scale_manifest(manifest_path)
    records = load_validated_staged_records(manifest_path)
    records_by_gana = Counter(record["gana"] for record in records)
    records_by_pada = Counter(record["pada"] for record in records)
    duplicate_candidates = detect_duplicate_canonical_candidates(records)
    missing_optional = find_missing_optional_metadata(records)

    return {
        "previewVersion": "1.0.0",
        "model": "aigaane-dhatu-promotion-preview",
        "mode": "dry-run-preview",
        "manifestVersion": manifest["manifestVersion"],
        "canonicalMutation": False,
        "goldsetMutation": False,
        "batchMutation": False,
        "totalStagedRecords": len(records),
        "recordsByGana": dict(sorted(records_by_gana.items())),
        "recordsByPada": dict(sorted(records_by_pada.items())),
        "duplicateCanonicalCandidates": duplicate_candidates,
        "missingOptionalMetadata": missing_optional,
        "previewRecords": [build_preview_record(record) for record in records],
    }


def build_preview_record(record: Dict[str, str]) -> Dict[str, str]:
    return {
        "root_id": record["root_id"],
        "candidateCanonicalId": record["root_id"],
        "devanagari": record["devanagari"],
        "iast": record["iast"],
        "gana": record["gana"],
        "pada": record["pada"],
        "artha": record["artha"],
        "source": record["source"],
        "sourceFile": record.get("sourceFile", record.get("batchFile", "")),
        "status": "preview-only",
        "recommendedAction": "manual-review-required",
    }


def detect_duplicate_canonical_candidates(records: Iterable[Dict[str, str]]) -> List[Dict[str, Any]]:
    owners: Dict[Tuple[str, str, str], List[str]] = {}
    for record in records:
        key = canonical_candidate_key(record)
        owners.setdefault(key, []).append(record["root_id"])
    duplicates = []
    for key, root_ids in sorted(owners.items()):
        unique_ids = sorted(set(root_ids))
        if len(unique_ids) > 1:
            duplicates.append(
                {
                    "gana": key[0],
                    "devanagari": key[1],
                    "iast": key[2],
                    "rootIds": unique_ids,
                }
            )
    return duplicates


def canonical_candidate_key(record: Dict[str, str]) -> Tuple[str, str, str]:
    return (
        str(record.get("gana", "")).strip(),
        str(record.get("devanagari", "")).strip(),
        str(record.get("iast", "")).strip().lower(),
    )


def find_missing_optional_metadata(
    records: Iterable[Dict[str, str]],
    optional_fields: Iterable[str] = OPTIONAL_METADATA_FIELDS,
) -> Dict[str, List[str]]:
    fields = tuple(optional_fields)
    missing: Dict[str, List[str]] = {}
    for record in records:
        missing_fields = [
            field
            for field in fields
            if not str(record.get(field, "")).strip()
        ]
        if missing_fields:
            missing[record["root_id"]] = missing_fields
    return dict(sorted(missing.items()))


def write_promotion_preview(
    preview: Dict[str, Any],
    path: Any = DEFAULT_PREVIEW_PATH,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(preview, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(preview: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "totalStagedRecords": preview["totalStagedRecords"],
        "recordsByGana": preview["recordsByGana"],
        "recordsByPada": preview["recordsByPada"],
        "duplicateCanonicalCandidates": preview["duplicateCanonicalCandidates"],
        "missingOptionalMetadata": preview["missingOptionalMetadata"],
        "canonicalMutation": preview["canonicalMutation"],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview staged dhatu promotion without canonical writes.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        preview = build_promotion_preview(args.manifest)
        write_promotion_preview(preview)
        print(json.dumps(build_summary(preview), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu promotion preview failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
