"""
Node 38G: Controlled Post-Governance Authorization Gate
Consumes 38F. Fail-closed. Does not write, promote, import, or execute.
Authorization is not execution.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
GOVERNANCE_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_governance_decision.v1.json"
)
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
    / "bulk_corpus_authorization_gate.v1.json"
)

EXPECTED_GOV_SCHEMA = "sanskrit-bulk-corpus-governance-decision.v1"
CLEARED = "governance-cleared-for-authorization"
PENDING = "governance-decision-pending"
BLOCKED = "governance-blocked"
EXPECTED_HOLD_SCHEMA = "sanskrit-bulk-corpus-post-attestation-hold.v1"
VALID_HOLD_STATUSES = ("hold-waiting-attestation", "hold-active")


def _failures(governance: Dict[str, Any], hold: Optional[Dict[str, Any]]) -> List[str]:
    found: List[str] = []
    if governance.get("schemaVersion") != EXPECTED_GOV_SCHEMA:
        found.append("governance-schema-mismatch")
    status = governance.get("status")
    decision = governance.get("decision")
    if status not in (PENDING, BLOCKED, CLEARED):
        found.append("unknown-governance-status")
    if status == PENDING:
        found.append("governance-pending")
    if status == BLOCKED or decision == "blocked":
        found.append("governance-blocked")
    if status == CLEARED and decision != "cleared-for-authorization":
        found.append("cleared-decision-mismatch")
    for key in (
        "canonicalWriteAllowed",
        "promotionAllowed",
        "importAllowed",
        "executionAllowed",
    ):
        if governance.get(key) is True:
            found.append(f"governance-{key}-leaked")
    auth = governance.get("authorization") or {}
    if auth.get("governanceDecisionIsAuthorization") is True:
        found.append("governance-claimed-authorization")
    if auth.get("governanceDecisionIsExecutionAuthorization") is True:
        found.append("governance-claimed-execution")
    if hold is None:
        found.append("hold-missing")
    else:
        if hold.get("schemaVersion") != EXPECTED_HOLD_SCHEMA:
            found.append("hold-schema-mismatch")
        hold_status = hold.get("status")
        if hold_status is None:
            found.append("hold-status-missing")
        elif hold_status == "hold-blocked":
            found.append("hold-blocked")
        elif hold_status not in VALID_HOLD_STATUSES:
            found.append("hold-status-unknown")
        if hold.get("autoPromote") is True:
            found.append("hold-autoPromote")
        if hold.get("canonicalWriteAllowed") is True:
            found.append("hold-canonicalWrite-leaked")
    return found


def build_authorization_gate_record(
    governance: Dict[str, Any],
    hold: Optional[Dict[str, Any]] = None,
    *,
    prerequisites: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    failures = _failures(governance, hold)
    prereq = dict(prerequisites or {})
    if "holdNotBlocked" in prereq and prereq["holdNotBlocked"] is not True:
        failures.append("prerequisite-holdNotBlocked")
    if "reviewComplete" in prereq and prereq["reviewComplete"] is not True:
        failures.append("prerequisite-reviewComplete")

    cleared = (
        governance.get("status") == CLEARED
        and governance.get("decision") == "cleared-for-authorization"
    )
    authorized = cleared and len(failures) == 0
    return {
        "schemaVersion": "sanskrit-bulk-corpus-authorization-gate.v1",
        "status": "authorization-ready" if authorized else "authorization-blocked",
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "authorized": authorized,
        "authorization": authorized,
        "hardStop": True,
        "sourceGovernance": {
            "status": governance.get("status"),
            "decision": governance.get("decision"),
        },
        "sourceHold": {
            "status": None if hold is None else hold.get("status"),
        },
        "failures": failures,
        "nextGate": "38H PROMOTION PREFLIGHT",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "authorizationExecutionAllowed": False,
        "authorizationIsWrite": False,
        "authorizationIsImport": False,
        "authorizationIsPromotion": False,
        "authorizationIsExecution": False,
    }


def main() -> int:
    if not GOVERNANCE_PATH.exists():
        raise FileNotFoundError(f"Missing 38F packet: {GOVERNANCE_PATH}")
    with GOVERNANCE_PATH.open("r", encoding="utf-8") as handle:
        governance = json.load(handle)
    hold = None
    if HOLD_PATH.exists():
        with HOLD_PATH.open("r", encoding="utf-8") as handle:
            hold = json.load(handle)
    record = build_authorization_gate_record(governance, hold)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"written": str(OUTPUT_PATH), "status": record["status"], "authorized": record["authorized"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
