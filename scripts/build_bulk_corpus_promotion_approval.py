import json
from pathlib import Path

from build_bulk_corpus_promotion_advisory import (
    build_bulk_corpus_promotion_advisory,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_promotion_approval(data):
    advisory = build_bulk_corpus_promotion_advisory(data)

    approved = (
        advisory.get("valid") is True
        and advisory.get("advisoryStatus") == "advisory-ready"
        and advisory.get("recommendation") == "manual-review-ready"
        and advisory.get("canonicalWriteAllowed") is False
        and advisory.get("promotionAllowed") is False
    )

    approval_ledger = []

    if approved:
        approval_ledger.extend([
            {
                "approvalId": "approval-001",
                "kind": "advisory",
                "status": "accepted",
                "message": "Promotion advisory accepted for manual review.",
                "previewOnly": True,
            },
            {
                "approvalId": "approval-002",
                "kind": "safety",
                "status": "locked",
                "message": "Canonical write remains disabled.",
                "previewOnly": True,
            },
            {
                "approvalId": "approval-003",
                "kind": "promotion",
                "status": "not-executed",
                "message": "Promotion execution is not allowed in this layer.",
                "previewOnly": True,
            },
        ])
    else:
        approval_ledger.append({
            "approvalId": "approval-001",
            "kind": "blocker",
            "status": "blocked",
            "message": "Promotion approval is blocked.",
            "previewOnly": True,
        })

    return {
        "valid": approved,
        "approvalStatus": "approval-ready" if approved else "approval-blocked",
        "approvalLedgerCount": len(approval_ledger),
        "approvalLedger": approval_ledger,
        "recommendation": advisory.get("recommendation", "hold"),
        "advisoryStatus": advisory.get("advisoryStatus", "advisory-blocked"),
        "acceptedRecordCount": advisory.get("acceptedRecordCount", 0),
        "rejectedRecordCount": advisory.get("rejectedRecordCount", 0),
        "advisory": advisory,
        "previewOnly": True,
        "readOnly": True,
        "approvalExecutionAllowed": False,
        "advisoryExecutionAllowed": False,
        "promotionExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }


def main():
    result = build_bulk_corpus_promotion_approval(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())