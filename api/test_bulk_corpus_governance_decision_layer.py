import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_governance_decision import (
    build_governance_decision_record,
)


def _waiting_hold():
    return {
        "schemaVersion": "sanskrit-bulk-corpus-post-attestation-hold.v1",
        "status": "hold-waiting-attestation",
        "holdActive": True,
        "waitingAttestation": True,
        "holdCompleted": False,
        "autoPromote": False,
        "hardStop": True,
        "authorization": {"holdIsAuthorization": False},
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
    }


def _active_hold():
    packet = _waiting_hold()
    packet["status"] = "hold-active"
    packet["waitingAttestation"] = False
    return packet


class TestBulkCorpusGovernanceDecisionLayer(unittest.TestCase):
    def test_default_pending_from_waiting_hold(self):
        record = build_governance_decision_record(_waiting_hold(), decision=None)
        self.assertEqual(record["status"], "governance-decision-pending")
        self.assertIsNone(record["decision"])
        self.assertTrue(record["hardStop"])
        self.assertFalse(record["authorization"]["governanceDecisionIsAuthorization"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])

    def test_clearance_requires_hold_active(self):
        record = build_governance_decision_record(
            _waiting_hold(), decision="cleared-for-authorization"
        )
        self.assertEqual(record["status"], "governance-decision-blocked")
        self.assertIn("clearance-requires-hold-active", record["failures"])
        self.assertFalse(record["canonicalWriteAllowed"])

    def test_cleared_still_not_write(self):
        record = build_governance_decision_record(
            _active_hold(), decision="cleared-for-authorization"
        )
        self.assertEqual(
            record["status"], "governance-decision-cleared-for-authorization"
        )
        self.assertEqual(record["decision"], "cleared-for-authorization")
        self.assertFalse(record["authorization"]["clearedForAuthorizationIsWrite"])
        self.assertFalse(record["authorization"]["clearedForAuthorizationIsImport"])
        self.assertFalse(record["authorization"]["clearedForAuthorizationIsExecution"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])
        self.assertTrue(record["hardStop"])
        self.assertEqual(record["nextGate"], "38G PROMOTION AUTHORIZATION")

    def test_repo_38e_packet_is_pending(self):
        path = (
            ROOT
            / "data"
            / "sanskrit"
            / "corpus-staging"
            / "bulk_corpus_post_attestation_hold.v1.json"
        )
        if not path.exists():
            self.skipTest("38E packet not on disk")
        packet = json.loads(path.read_text(encoding="utf-8"))
        record = build_governance_decision_record(packet, decision=None)
        self.assertEqual(
            record["status"], "governance-decision-pending", record["failures"]
        )
        self.assertIsNone(record["decision"])


if __name__ == "__main__":
    unittest.main()
