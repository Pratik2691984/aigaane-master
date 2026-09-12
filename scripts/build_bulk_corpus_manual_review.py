"""
Node 38D: Bulk Corpus Manual Review / Human Attestation Gate
Consumes the 38C assurance packet. Does not authorize write, import,
promotion, or execution. Default emit is PENDING (not attested).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSURANCE_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_certification_assurance.v1.json"
)
OUTPUT_PATH = (
    ROOT_DIR / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manual_review.v1.json"
)

EXPECTED_ASSURANCE_SCHEMA = "sanskrit-bulk-corpus-certification-assurance.v1"


def _assurance_failures(assurance: Dict[str, Any]) -> List[str]:
    found: List[str] = []
    if assurance.get("schemaVersion") != EXPECTED_ASSURANCE_SCHEMA:
        found.append("assurance-schema-mismatch")
    if assurance.get("status") != "assurance-ready":
        found.append("assurance-not-ready")
    if assurance.get("assured") is not True:
        found.append("assurance-not-assured")
    if assurance.get("hardStop") is not True:
        found.append("hardStop-missing")
    auth = assurance.get("authorization") or {}
    if auth.get("certificationIsAuthorization") is not False:
        found.append("certification-treated-as-authorization")
    for key in (
        "canonicalWriteAllowed",
        "promotionAllowed",
        "importAllowed",
        "executionAllowed",
    ):
        if assurance.get(key) is not False:
            found.append(f"assurance-{key}-exposed")
    return found


def build_manual_review_record(
    assurance: Dict[str, Any],
    *,
    attested: bool = False,
) -> Dict[str, Any]:
    failures = _assurance_failures(assurance)
    gate_open = len(failures) == 0
    if not gate_open:
        status = "manual-review-blocked"
        attested_flag = False
    elif attested:
        status = "manual-review-attested"
        attested_flag = True
    else:
        status = "manual-review-pending"
        attested_flag = False

    return {
        "schemaVersion": "sanskrit-bulk-corpus-manual-review.v1",
        "status": status,
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "hardStop": True,
        "attested": attested_flag,
        "reviewer": None if not attested_flag else "human",
        "sourceAssurance": {
            "status": assurance.get("status"),
            "assured": assurance.get("assured"),
            "nextGate": assurance.get("nextGate"),
        },
        "failures": failures,
        "authorization": {
            "manualReviewIsAuthorization": False,
            "manualReviewIsExecutionAuthorization": False,
            "certificationIsAuthorization": False,
            "canonicalWrite": False,
            "promotion": False,
            "import": False,
            "execution": False,
        },
        "nextGate": "POST-ATTESTATION HOLD",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "manualReviewExecutionAllowed": False,
        "assuranceExecutionAllowed": False,
        "certificationExecutionAllowed": False,
    }


def main() -> int:
    if not ASSURANCE_PATH.exists():
        raise FileNotFoundError(f"Missing 38C packet: {ASSURANCE_PATH}")
    with ASSURANCE_PATH.open("r", encoding="utf-8") as handle:
        assurance = json.load(handle)
    record = build_manual_review_record(assurance, attested=False)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        json.dumps(
            {
                "written": str(OUTPUT_PATH),
                "status": record["status"],
                "attested": record["attested"],
            },
            indent=2,
        )
    )
    return 0 if record["status"] != "manual-review-blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
