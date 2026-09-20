#!/usr/bin/env python
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List


ROOT = Path(__file__).resolve().parents[1]
PIPELINE_REPORT = ROOT / "data" / "sanskrit" / "corpus-staging" / "real_corpus_pipeline_report.v1.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _summarize_stage_result(result: Dict[str, Any]) -> Dict[str, Any]:
    summary = {
        "valid": bool(result.get("valid")),
    }
    for key in (
        "recordCount",
        "batchCount",
        "typeCounts",
        "acceptedRecordCount",
        "approvalStatus",
        "certificationStatus",
        "canonicalStatus",
        "errors",
        "warnings",
    ):
        if key in result:
            summary[key] = result[key]
    return summary


def _stage(name: str, runner: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    result = runner()
    return {
        "stage": name,
        "valid": bool(result.get("valid")),
        "summary": _summarize_stage_result(result),
    }


def run_real_corpus_loading_pipeline(write_manifest: bool = True) -> Dict[str, Any]:
    build_raw = _load_module(
        "build_real_corpus_raw_batches",
        ROOT / "scripts" / "build_real_corpus_raw_batches.py",
    )
    load_raw = _load_module(
        "load_real_corpus_from_raw",
        ROOT / "scripts" / "load_real_corpus_from_raw.py",
    )
    validate_staging = _load_module(
        "validate_bulk_corpus_staging",
        ROOT / "scripts" / "validate_bulk_corpus_staging.py",
    )
    validate_records = _load_module(
        "validate_bulk_corpus_records",
        ROOT / "scripts" / "validate_bulk_corpus_records.py",
    )
    audit_provenance = _load_module(
        "audit_bulk_corpus_provenance",
        ROOT / "scripts" / "audit_bulk_corpus_provenance.py",
    )
    preview_import = _load_module(
        "preview_bulk_corpus_import",
        ROOT / "scripts" / "preview_bulk_corpus_import.py",
    )
    build_approval = _load_module(
        "build_bulk_corpus_promotion_approval",
        ROOT / "scripts" / "build_bulk_corpus_promotion_approval.py",
    )
    build_certification = _load_module(
        "build_bulk_corpus_certification",
        ROOT / "scripts" / "build_bulk_corpus_certification.py",
    )
    preview_canonical = _load_module(
        "preview_bulk_corpus_canonical",
        ROOT / "scripts" / "preview_bulk_corpus_canonical.py",
    )

    manifest_path = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

    def _load_manifest() -> Dict[str, Any]:
        with manifest_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    stages: List[Dict[str, Any]] = []

    stages.append(_stage("raw", build_raw.build_real_corpus_raw_batches))
    stages.append(_stage(
        "corpus-staging",
        lambda: load_raw.load_real_corpus_from_raw(dry_run=not write_manifest),
    ))

    manifest = _load_manifest()

    stages.append(_stage("validation", lambda: validate_records.validate_bulk_corpus_records(manifest)))
    stages.append(_stage("provenance", lambda: audit_provenance.audit_bulk_corpus_provenance(manifest)))
    stages.append(_stage("preview", lambda: preview_import.preview_bulk_corpus_import(manifest)))
    stages.append(_stage("approval", lambda: build_approval.build_bulk_corpus_promotion_approval(manifest)))
    stages.append(_stage("certification", lambda: build_certification.build_bulk_corpus_certification(manifest)))
    stages.append(_stage("canonical", lambda: preview_canonical.preview_bulk_corpus_canonical(manifest)))

    valid = all(stage["valid"] for stage in stages)
    final = stages[-1].get("summary", {}) if stages else {}

    report = {
        "valid": valid,
        "phase": "11",
        "title": "Real Corpus Loading Pipeline",
        "pipeline": [stage["stage"] for stage in stages],
        "stages": stages,
        "recordCount": manifest.get("metadata", {}).get("recordCount"),
        "typeCounts": manifest.get("metadata", {}).get("typeCounts"),
        "acceptedRecordCount": final.get("acceptedRecordCount"),
        "canonicalStatus": final.get("canonicalStatus"),
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }

    if write_manifest:
        PIPELINE_REPORT.parent.mkdir(parents=True, exist_ok=True)
        with PIPELINE_REPORT.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 11 real corpus loading pipeline.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview staging load without writing bulk_corpus_manifest.v1.json.",
    )
    args = parser.parse_args()
    result = run_real_corpus_loading_pipeline(write_manifest=not args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())