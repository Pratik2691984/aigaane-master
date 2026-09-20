import json
from pathlib import Path

from build_bulk_corpus_admission import build_bulk_corpus_admission


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_promotion_readiness(data):
    admission = build_bulk_corpus_admission(data)

    accepted_count = int(admission.get("acceptedRecordCount", 0))
    rejected_count = int(admission.get("rejectedRecordCount", 0))

    promotion_confidence = 100 if (
        admission.get("valid") is True
        and admission.get("admissionStatus") == "admission-ready"
        and accepted_count > 0
        and rejected_count == 0
        and admission.get("canonicalWriteAllowed") is False
    ) else 0

    ready = promotion_confidence == 100

    advisory = []
    blockers = []

    if ready:
        advisory.append("admissionReady")
        advisory.append("promotionPreviewReady")
        advisory.append("canonicalWriteLocked")
    else:
        blockers.append("admissionNotReady")

    return {
        "valid": ready,
        "promotionStatus": "promotion-ready" if ready else "promotion-blocked",
        "promotionConfidence": promotion_confidence,
        "acceptedRecordCount": accepted_count,
        "rejectedRecordCount": rejected_count,
        "advisory": advisory,
        "blockers": blockers,
        "admission": admission,
        "previewOnly": True,
        "readOnly": True,
        "promotionReadinessAllowed": True,
        "promotionExecutionAllowed": False,
        "admissionExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = build_bulk_corpus_promotion_readiness(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())