import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_post_attestation_hold import (
    build_post_attestation_hold_record,
)


def _pending():
    return {
        "schemaVersion": "sanskrit-bulk-corpus-manual-review.v1",
        "status": "manual-review-pending",
        "attested": False,
        "hardStop": True,
        "authorization": {"manualReviewIsExecutionAuthorization": False},
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
    }


def _attested():
    packet = _pending()
    packet["status"] = "manual-review-attested"
    packet["attested"] = True
    return packet


class TestBulkCorpusPostAttestationHoldLayer(unittest.TestCase):
    def test_pending_waits_and_does_not_complete(self):
        record = build_post_attestation_hold_record(_pending())
        self.assertEqual(record["status"], "hold-waiting-attestation")
        self.assertTrue(record["waitingAttestation"])
        self.assertFalse(record["holdCompleted"])
        self.assertFalse(record["autoPromote"])
        self.assertFalse(record["canonicalWriteAllowed"])

    def test_attested_enters_hold_not_authorization(self):
        record = build_post_attestation_hold_record(_attested())
        self.assertEqual(record["status"], "hold-active")
        self.assertTrue(record["holdActive"])
        self.assertFalse(record["holdCompleted"])
        self.assertFalse(record["autoPromote"])
        self.assertFalse(record["authorization"]["attestationIsAuthorization"])
        self.assertFalse(record["authorization"]["holdIsAuthorization"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["executionAllowed"])
        self.assertEqual(record["nextGate"], "38F FINAL GOVERNANCE DECISION")

    def test_write_flag_on_review_blocks_hold(self):
        packet = _attested()
        packet["canonicalWriteAllowed"] = True
        record = build_post_attestation_hold_record(packet)
        self.assertEqual(record["status"], "hold-blocked")
        self.assertFalse(record["canonicalWriteAllowed"])

    def test_repo_38d_packet_waits(self):
        path = (
            ROOT
            / "data"
            / "sanskrit"
            / "corpus-staging"
            / "bulk_corpus_manual_review.v1.json"
        )
        if not path.exists():
            self.skipTest("38D packet not on disk")
        packet = json.loads(path.read_text(encoding="utf-8"))
        record = build_post_attestation_hold_record(packet)
        self.assertEqual(record["status"], "hold-waiting-attestation", record["failures"])
        self.assertFalse(record["holdCompleted"])


if __name__ == "__main__":
    unittest.main()
