"""
Node 38E: Post-Attestation Hold / Review Closure
Consumes 38D. Attestation never auto-promotes. Hold stays closed
until an explicit later governance decision (38F).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
REVIEW_PATH = (
    ROOT_DIR / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manual_review.v1.json"
)
OUTPUT_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_post_attestation_hold.v1.json"
)

EXPECTED_REVIEW_SCHEMA = "sanskrit-bulk-corpus-manual-review.v1"


def _review_failures(review: Dict[str, Any]) -> List[str]:
    found: List[str] = []
    if review.get("schemaVersion") != EXPECTED_REVIEW_SCHEMA:
        found.append("review-schema-mismatch")
    if review.get("hardStop") is not True:
        found.append("review-hardStop-missing")
    auth = review.get("authorization") or {}
    if auth.get("manualReviewIsExecutionAuthorization") is not False:
        found.append("review-treated-as-execution")
    for key in (
        "canonicalWriteAllowed",
        "promotionAllowed",
        "importAllowed",
        "executionAllowed",
    ):
        if review.get(key) is not False:
            found.append(f"review-{key}-exposed")
    return found


def build_post_attestation_hold_record(review: Dict[str, Any]) -> Dict[str, Any]:
    failures = _review_failures(review)
    status_in = review.get("status")
    attested = review.get("attested") is True

    if failures or status_in == "manual-review-blocked":
        status = "hold-blocked"
        hold_active = False
        waiting = False
    elif status_in == "manual-review-attested" and attested:
        status = "hold-active"
        hold_active = True
        waiting = False
    elif status_in == "manual-review-pending":
        status = "hold-waiting-attestation"
        hold_active = True
        waiting = True
    else:
        status = "hold-blocked"
        hold_active = False
        waiting = False

    return {
        "schemaVersion": "sanskrit-bulk-corpus-post-attestation-hold.v1",
        "status": status,
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "hardStop": True,
        "holdActive": hold_active,
        "waitingAttestation": waiting,
        "holdCompleted": False,
        "autoPromote": False,
        "sourceReview": {
            "status": review.get("status"),
            "attested": review.get("attested"),
        },
        "failures": failures,
        "authorization": {
            "holdIsAuthorization": False,
            "attestationIsAuthorization": False,
            "manualReviewIsExecutionAuthorization": False,
            "canonicalWrite": False,
            "promotion": False,
            "import": False,
            "execution": False,
        },
        "nextGate": "38F FINAL GOVERNANCE DECISION",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "holdExecutionAllowed": False,
        "manualReviewExecutionAllowed": False,
    }


def main() -> int:
    if not REVIEW_PATH.exists():
        raise FileNotFoundError(f"Missing 38D packet: {REVIEW_PATH}")
    with REVIEW_PATH.open("r", encoding="utf-8") as handle:
        review = json.load(handle)
    record = build_post_attestation_hold_record(review)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        json.dumps(
            {
                "written": str(OUTPUT_PATH),
                "status": record["status"],
                "holdCompleted": record["holdCompleted"],
                "autoPromote": record["autoPromote"],
            },
            indent=2,
        )
    )
    return 0 if record["status"] != "hold-blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
