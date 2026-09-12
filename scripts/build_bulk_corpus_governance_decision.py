"""
Node 38F: Final Governance Decision
Consumes 38E hold. Default PENDING. CLEARED_FOR_AUTHORIZATION is not
write, import, promotion, or execution authorization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
HOLD_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_post_attestation_hold.v1.json"
)
OUTPUT_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_governance_decision.v1.json"
)

EXPECTED_HOLD_SCHEMA = "sanskrit-bulk-corpus-post-attestation-hold.v1"
VALID_DECISIONS = (None, "blocked", "cleared-for-authorization")


def _hold_failures(hold: Dict[str, Any]) -> List[str]:
    found: List[str] = []
    if hold.get("schemaVersion") != EXPECTED_HOLD_SCHEMA:
        found.append("hold-schema-mismatch")
    if hold.get("hardStop") is not True:
        found.append("hold-hardStop-missing")
    if hold.get("autoPromote") is not False:
        found.append("hold-autoPromote-true")
    if hold.get("holdCompleted") is True:
        found.append("hold-already-completed")
    auth = hold.get("authorization") or {}
    if auth.get("holdIsAuthorization") is not False:
        found.append("hold-treated-as-authorization")
    for key in (
        "canonicalWriteAllowed",
        "promotionAllowed",
        "importAllowed",
        "executionAllowed",
    ):
        if hold.get(key) is not False:
            found.append(f"hold-{key}-exposed")
    return found


def build_governance_decision_record(
    hold: Dict[str, Any],
    *,
    decision: Optional[str] = None,
) -> Dict[str, Any]:
    failures = _hold_failures(hold)
    hold_status = hold.get("status")

    if decision not in VALID_DECISIONS:
        failures.append("invalid-decision")
        decision = None

    if failures or hold_status == "hold-blocked":
        status = "governance-decision-blocked"
        resolved = None
    elif decision == "blocked":
        status = "governance-decision-blocked"
        resolved = "blocked"
    elif decision == "cleared-for-authorization":
        if hold_status != "hold-active":
            status = "governance-decision-blocked"
            resolved = None
            failures.append("clearance-requires-hold-active")
        else:
            status = "governance-decision-cleared-for-authorization"
            resolved = "cleared-for-authorization"
    else:
        status = "governance-decision-pending"
        resolved = None

    return {
        "schemaVersion": "sanskrit-bulk-corpus-governance-decision.v1",
        "status": status,
        "decision": resolved,
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "hardStop": True,
        "sourceHold": {
            "status": hold.get("status"),
            "holdActive": hold.get("holdActive"),
            "waitingAttestation": hold.get("waitingAttestation"),
            "holdCompleted": hold.get("holdCompleted"),
        },
        "failures": failures,
        "authorization": {
            "governanceDecisionIsAuthorization": False,
            "clearedForAuthorizationIsWrite": False,
            "clearedForAuthorizationIsImport": False,
            "clearedForAuthorizationIsExecution": False,
            "canonicalWrite": False,
            "promotion": False,
            "import": False,
            "execution": False,
        },
        "nextGate": "38G PROMOTION AUTHORIZATION",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "governanceExecutionAllowed": False,
        "holdExecutionAllowed": False,
    }


def main() -> int:
    if not HOLD_PATH.exists():
        raise FileNotFoundError(f"Missing 38E packet: {HOLD_PATH}")
    with HOLD_PATH.open("r", encoding="utf-8") as handle:
        hold = json.load(handle)
    record = build_governance_decision_record(hold, decision=None)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        json.dumps(
            {
                "written": str(OUTPUT_PATH),
                "status": record["status"],
                "decision": record["decision"],
            },
            indent=2,
        )
    )
    return 0 if record["status"] != "governance-decision-blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
