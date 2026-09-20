import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_governance_decision import (
    build_governance_decision_record,
)


def _valid_hold(status="hold-waiting-attestation"):
    return {
        "schemaVersion": "sanskrit-bulk-corpus-post-attestation-hold.v1",
        "status": status,
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "holdActive": True,
        "waitingAttestation": status == "hold-waiting-attestation",
        "holdCompleted": False,
        "autoPromote": False,
        "hardStop": True,
        "authorization": {
            "holdIsAuthorization": False,
            "attestationIsAuthorization": False,
        },
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
    }


class TestBulkCorpusGovernanceDecisionLayer(unittest.TestCase):
    def test_default_pending_state(self):
        record = build_governance_decision_record(_valid_hold(), decision=None)
        self.assertEqual(record["status"], "governance-decision-pending")
        self.assertIsNone(record["decision"])
        self.assertTrue(record["hardStop"])
        self.assertFalse(record["authorization"]["governanceDecisionIsAuthorization"])
        self.assertFalse(record["authorization"]["governanceDecisionIsExecutionAuthorization"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])

    def test_explicit_blocked_state(self):
        record = build_governance_decision_record(_valid_hold(), decision="blocked")
        self.assertEqual(record["status"], "governance-blocked")
        self.assertEqual(record["decision"], "blocked")
        self.assertTrue(record["hardStop"])
        self.assertFalse(record["executionAllowed"])
        self.assertFalse(record["canonicalWriteAllowed"])

    def test_cleared_for_authorization_is_still_non_authorizing(self):
        record = build_governance_decision_record(
            _valid_hold(), decision="cleared-for-authorization"
        )
        self.assertEqual(record["status"], "governance-cleared-for-authorization")
        self.assertTrue(record["hardStop"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])
        auth = record["authorization"]
        self.assertFalse(auth["governanceDecisionIsAuthorization"])
        self.assertFalse(auth["governanceDecisionIsExecutionAuthorization"])
        self.assertFalse(auth["governanceClearanceIsWriteAuthorization"])
        self.assertFalse(auth["governanceClearanceIsPromotionAuthorization"])
        self.assertFalse(auth["governanceClearanceIsImportAuthorization"])
        self.assertFalse(auth["governanceClearanceIsExecutionAuthorization"])
        self.assertEqual(record["nextGate"], "38G PROMOTION AUTHORIZATION")

    def test_unsafe_or_blocked_38e_cannot_clear(self):
        leaked = _valid_hold()
        leaked["promotionAllowed"] = True
        record = build_governance_decision_record(
            leaked, decision="cleared-for-authorization"
        )
        self.assertEqual(record["status"], "governance-blocked")
        self.assertIsNone(record["decision"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["executionAllowed"])

        blocked = _valid_hold()
        blocked["status"] = "hold-blocked"
        record = build_governance_decision_record(
            blocked, decision="cleared-for-authorization"
        )
        self.assertEqual(record["status"], "governance-blocked")
        self.assertFalse(record["executionAllowed"])

    def test_repo_38e_packet_defaults_pending(self):
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
        self.assertEqual(record["status"], "governance-decision-pending", record["failures"])
        self.assertIsNone(record["decision"])


if __name__ == "__main__":
    unittest.main()
