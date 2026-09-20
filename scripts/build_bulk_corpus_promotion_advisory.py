import json
from pathlib import Path

from build_bulk_corpus_promotion_readiness import (
    build_bulk_corpus_promotion_readiness,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_promotion_advisory(data):
    readiness = build_bulk_corpus_promotion_readiness(data)

    ready = (
        readiness.get("valid") is True
        and readiness.get("promotionStatus") == "promotion-ready"
        and readiness.get("promotionConfidence", 0) == 100
        and readiness.get("canonicalWriteAllowed") is False
        and readiness.get("promotionAllowed") is False
    )

    advisory_packets = []
    recommendation = "hold"

    if ready:
        recommendation = "manual-review-ready"
        advisory_packets.extend([
            {
                "packetId": "advisory-001",
                "kind": "readiness",
                "message": "Promotion readiness is complete.",
                "severity": "info",
                "previewOnly": True,
            },
            {
                "packetId": "advisory-002",
                "kind": "safety",
                "message": "Canonical write remains locked.",
                "severity": "guard",
                "previewOnly": True,
            },
            {
                "packetId": "advisory-003",
                "kind": "recommendation",
                "message": "Manual promotion review may begin.",
                "severity": "review",
                "previewOnly": True,
            },
        ])
    else:
        advisory_packets.append({
            "packetId": "advisory-001",
            "kind": "blocker",
            "message": "Promotion readiness is blocked.",
            "severity": "blocker",
            "previewOnly": True,
        })

    return {
        "valid": ready,
        "advisoryStatus": "advisory-ready" if ready else "advisory-blocked",
        "recommendation": recommendation,
        "advisoryPacketCount": len(advisory_packets),
        "advisoryPackets": advisory_packets,
        "promotionConfidence": readiness.get("promotionConfidence", 0),
        "acceptedRecordCount": readiness.get("acceptedRecordCount", 0),
        "rejectedRecordCount": readiness.get("rejectedRecordCount", 0),
        "readiness": readiness,
        "previewOnly": True,
        "readOnly": True,
        "advisoryExecutionAllowed": False,
        "promotionExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
    }


def main():
    result = build_bulk_corpus_promotion_advisory(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())