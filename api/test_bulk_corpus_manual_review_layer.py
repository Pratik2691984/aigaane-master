import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_manual_review import build_manual_review_record


def _ready_assurance():
    return {
        "schemaVersion": "sanskrit-bulk-corpus-certification-assurance.v1",
        "status": "assurance-ready",
        "assured": True,
        "hardStop": True,
        "authorization": {"certificationIsAuthorization": False},
        "nextGate": "MANUAL REVIEW / CERTIFIED",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
    }


class TestBulkCorpusManualReviewLayer(unittest.TestCase):
    def test_default_is_pending_not_attested(self):
        record = build_manual_review_record(_ready_assurance(), attested=False)
        self.assertEqual(record["status"], "manual-review-pending")
        self.assertFalse(record["attested"])
        self.assertTrue(record["hardStop"])
        self.assertFalse(record["authorization"]["manualReviewIsAuthorization"])
        self.assertFalse(record["authorization"]["manualReviewIsExecutionAuthorization"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])

    def test_attested_still_holds_writes(self):
        record = build_manual_review_record(_ready_assurance(), attested=True)
        self.assertEqual(record["status"], "manual-review-attested")
        self.assertTrue(record["attested"])
        self.assertTrue(record["hardStop"])
        self.assertEqual(record["nextGate"], "POST-ATTESTATION HOLD")
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["executionAllowed"])
        self.assertFalse(record["authorization"]["manualReviewIsExecutionAuthorization"])

    def test_unassured_packet_blocks(self):
        packet = _ready_assurance()
        packet["assured"] = False
        packet["status"] = "assurance-blocked"
        record = build_manual_review_record(packet, attested=True)
        self.assertEqual(record["status"], "manual-review-blocked")
        self.assertFalse(record["attested"])
        self.assertIn("assurance-not-ready", record["failures"])

    def test_repo_38c_packet_is_pending(self):
        path = (
            ROOT
            / "data"
            / "sanskrit"
            / "corpus-staging"
            / "bulk_corpus_certification_assurance.v1.json"
        )
        if not path.exists():
            self.skipTest("38C packet not on disk")
        packet = json.loads(path.read_text(encoding="utf-8"))
        record = build_manual_review_record(packet, attested=False)
        self.assertEqual(record["status"], "manual-review-pending", record["failures"])
        self.assertFalse(record["attested"])


if __name__ == "__main__":
    unittest.main()
