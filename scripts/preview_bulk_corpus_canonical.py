import json
from pathlib import Path

from build_bulk_corpus_certification import build_bulk_corpus_certification


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def preview_bulk_corpus_canonical(data):
    certification = build_bulk_corpus_certification(data)

    ready = (
        certification.get("valid") is True
        and certification.get("certificationStatus") == "certification-ready"
        and certification.get("canonicalWriteAllowed") is False
        and certification.get("promotionAllowed") is False
    )

    canonical_ledger = []

    if ready:
        canonical_ledger.extend([
            {
                "canonicalId": "canonical-001",
                "kind": "certification",
                "status": "verified",
                "message": "Certification verified for canonical preview.",
                "previewOnly": True,
            },
            {
                "canonicalId": "canonical-002",
                "kind": "safety",
                "status": "locked",
                "message": "Canonical write execution remains disabled.",
                "previewOnly": True,
            },
            {
                "canonicalId": "canonical-003",
                "kind": "preview",
                "status": "not-executed",
                "message": "Canonical promotion is preview-only in Phase 11.",
                "previewOnly": True,
            },
        ])
    else:
        canonical_ledger.append({
            "canonicalId": "canonical-001",
            "kind": "blocker",
            "status": "blocked",
            "message": "Canonical preview is blocked.",
            "previewOnly": True,
        })

    return {
        "valid": ready,
        "canonicalStatus": "canonical-preview-ready" if ready else "canonical-preview-blocked",
        "canonicalLedgerCount": len(canonical_ledger),
        "canonicalLedger": canonical_ledger,
        "acceptedRecordCount": certification.get("acceptedRecordCount", 0),
        "rejectedRecordCount": certification.get("rejectedRecordCount", 0),
        "certificationStatus": certification.get("certificationStatus", "certification-blocked"),
        "recommendation": certification.get("recommendation", "hold"),
        "certification": certification,
        "previewOnly": True,
        "readOnly": True,
        "canonicalExecutionAllowed": False,
        "certificationExecutionAllowed": False,
        "promotionExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }


def main():
    result = preview_bulk_corpus_canonical(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())