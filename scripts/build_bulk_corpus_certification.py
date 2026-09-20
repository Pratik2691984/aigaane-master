import json
from pathlib import Path

from build_bulk_corpus_promotion_approval import build_bulk_corpus_promotion_approval


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_certification(data):
    approval = build_bulk_corpus_promotion_approval(data)

    certified = (
        approval.get("valid") is True
        and approval.get("approvalStatus") == "approval-ready"
        and approval.get("recommendation") == "manual-review-ready"
        and approval.get("canonicalWriteAllowed") is False
        and approval.get("promotionAllowed") is False
    )

    certification_ledger = []

    if certified:
        certification_ledger.extend([
            {
                "certificationId": "certification-001",
                "kind": "approval",
                "status": "verified",
                "message": "Promotion approval verified for certification.",
                "previewOnly": True,
            },
            {
                "certificationId": "certification-002",
                "kind": "safety",
                "status": "locked",
                "message": "Canonical write remains disabled.",
                "previewOnly": True,
            },
            {
                "certificationId": "certification-003",
                "kind": "evidence",
                "status": "immutable",
                "message": "Certification evidence is preview-only and read-only.",
                "previewOnly": True,
            },
        ])
    else:
        certification_ledger.append({
            "certificationId": "certification-001",
            "kind": "blocker",
            "status": "blocked",
            "message": "Corpus certification is blocked.",
            "previewOnly": True,
        })

    return {
        "valid": certified,
        "certificationStatus": "certification-ready" if certified else "certification-blocked",
        "certificationLedgerCount": len(certification_ledger),
        "certificationLedger": certification_ledger,
        "acceptedRecordCount": approval.get("acceptedRecordCount", 0),
        "rejectedRecordCount": approval.get("rejectedRecordCount", 0),
        "approvalStatus": approval.get("approvalStatus", "approval-blocked"),
        "recommendation": approval.get("recommendation", "hold"),
        "approval": approval,
        "previewOnly": True,
        "readOnly": True,
        "certificationExecutionAllowed": False,
        "approvalExecutionAllowed": False,
        "promotionExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }


def main():
    result = build_bulk_corpus_certification(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())