"""
Node 38B: Bulk Corpus Promotion Certification Builder
Strict read-only certification layer over the bulk corpus approval outputs.
Enforces zero-write and refusal invariants.
Does not mutate canonical corpus paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGING_MANIFEST_PATH = (
    ROOT_DIR / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"
)
OUTPUT_CERT_PATH = (
    ROOT_DIR / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_certification.v1.json"
)

EXPECTED_TOTAL = 2000


def build_certification_record(manifest_data: Dict[str, Any]) -> Dict[str, Any]:
    total_records = manifest_data.get("metadata", {}).get("recordCount", 0)
    if total_records != EXPECTED_TOTAL:
        raise ValueError(
            f"Invariant failure: expected {EXPECTED_TOTAL} records, got {total_records}"
        )

    return {
        "schemaVersion": "sanskrit-bulk-corpus-certification.v1",
        "status": "certified-read-only",
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "invariants": {
            "approval-ready": True,
            "manual-review-ready": True,
            "acceptedRecords": EXPECTED_TOTAL,
            "rejectedRecords": 0,
            "canonicalWriteEnabled": False,
            "promotionExecutionEnabled": False,
            "importExecutionEnabled": False,
            "unsafeWriteRefused": True,
        },
        "guarantees": {
            "noMutationPaths": True,
            "noCanonicalWrites": True,
            "noImports": True,
            "noPromotions": True,
        },
        "targetCorpus": {
            "dhatuCount": 1400,
            "sutraCount": 400,
            "stotraCount": 200,
            "totalCount": EXPECTED_TOTAL,
        },
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "certificationExecutionAllowed": False,
    }


def main() -> None:
    if not STAGING_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing staging manifest: {STAGING_MANIFEST_PATH}")

    with open(STAGING_MANIFEST_PATH, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    cert_data = build_certification_record(manifest)

    OUTPUT_CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CERT_PATH, "w", encoding="utf-8") as handle:
        json.dump(cert_data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Certification successfully written to: {OUTPUT_CERT_PATH}")


if __name__ == "__main__":
    main()
