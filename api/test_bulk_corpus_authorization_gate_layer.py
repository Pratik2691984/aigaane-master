import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_authorization_gate import (
    build_authorization_gate_record,
)


def _gov(status, decision=None, **extra):
    packet = {
        "schemaVersion": "sanskrit-bulk-corpus-governance-decision.v1",
        "status": status,
        "decision": decision,
        "hardStop": True,
        "previewOnly": True,
        "readOnly": True,
        "authorization": {
            "governanceDecisionIsAuthorization": False,
            "governanceDecisionIsExecutionAuthorization": False,
        },
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
    }
    packet.update(extra)
    return packet


def _hold(status="hold-waiting-attestation"):
    return {
        "schemaVersion": "sanskrit-bulk-corpus-post-attestation-hold.v1",
        "status": status,
        "autoPromote": False,
        "canonicalWriteAllowed": False,
    }


class TestBulkCorpusAuthorizationGateLayer(unittest.TestCase):
    def test_pending_upstream_blocks_authorization(self):
        record = build_authorization_gate_record(
            _gov("governance-decision-pending", None), _hold()
        )
        self.assertFalse(record["authorized"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])

    def test_blocked_upstream_blocks_authorization(self):
        record = build_authorization_gate_record(
            _gov("governance-blocked", "blocked"), _hold()
        )
        self.assertFalse(record["authorized"])
        self.assertFalse(record["executionAllowed"])

    def test_cleared_without_prerequisite_is_not_authorized(self):
        record = build_authorization_gate_record(
            _gov("governance-cleared-for-authorization", "cleared-for-authorization"),
            _hold(),
            prerequisites={"reviewComplete": False},
        )
        self.assertFalse(record["authorized"])
        self.assertIn("prerequisite-reviewComplete", record["failures"])

    def test_valid_authorization_gate_does_not_enable_writes(self):
        record = build_authorization_gate_record(
            _gov("governance-cleared-for-authorization", "cleared-for-authorization"),
            _hold("hold-active"),
            prerequisites={"reviewComplete": True, "holdNotBlocked": True},
        )
        self.assertTrue(record["authorized"])
        self.assertEqual(record["status"], "authorization-ready")
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])
        self.assertFalse(record["authorizationIsWrite"])
        self.assertFalse(record["authorizationIsExecution"])

    def test_hold_blocked_prevents_authorization(self):
        record = build_authorization_gate_record(
            _gov("governance-cleared-for-authorization", "cleared-for-authorization"),
            _hold("hold-blocked"),
        )
        self.assertFalse(record["authorized"])
        self.assertIn("hold-blocked", record["failures"])

    def test_leaked_authorization_cannot_survive_blocked_state(self):
        first = build_authorization_gate_record(
            _gov("governance-cleared-for-authorization", "cleared-for-authorization"),
            _hold("hold-active"),
            prerequisites={"reviewComplete": True, "holdNotBlocked": True},
        )
        self.assertTrue(first["authorized"])
        second = build_authorization_gate_record(
            _gov("governance-blocked", "blocked"), _hold("hold-active")
        )
        self.assertFalse(second["authorized"])
        self.assertFalse(second["canonicalWriteAllowed"])

    def test_unknown_or_malformed_governance_fails_closed(self):
        record = build_authorization_gate_record(
            _gov("not-a-real-status", "mystery"), _hold()
        )
        self.assertFalse(record["authorized"])
        missing = _gov("governance-cleared-for-authorization", "cleared-for-authorization")
        missing.pop("status")
        record = build_authorization_gate_record(missing, _hold())
        self.assertFalse(record["authorized"])

    def test_gate_evaluation_has_no_write_side_effect(self):
        before = list((ROOT / "data" / "sanskrit").rglob("*")) if (ROOT / "data" / "sanskrit").exists() else []
        record = build_authorization_gate_record(
            _gov("governance-cleared-for-authorization", "cleared-for-authorization"),
            _hold("hold-active"),
            prerequisites={"reviewComplete": True, "holdNotBlocked": True},
        )
        after = list((ROOT / "data" / "sanskrit").rglob("*")) if (ROOT / "data" / "sanskrit").exists() else []
        self.assertTrue(record["authorized"])
        self.assertEqual({str(p) for p in before}, {str(p) for p in after})

    def test_repo_38f_packet_is_not_authorized(self):
        path = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_governance_decision.v1.json"
        if not path.exists():
            self.skipTest("38F packet not on disk")
        packet = json.loads(path.read_text(encoding="utf-8"))
        record = build_authorization_gate_record(packet)
        self.assertFalse(record["authorized"])


if __name__ == "__main__":
    unittest.main()
