import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_certification_assurance import (
    EXPECTED_TOTAL,
    build_assurance_record,
)


def _valid_packet():
    return {
        "schemaVersion": "sanskrit-bulk-corpus-certification.v1",
        "status": "certified-read-only",
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "invariants": {
            "approval-ready": True,
            "manual-review-ready": True,
            "acceptedRecords": EXPECTED_TOTAL,
            "rejectedRecords": 0,
            "canonicalWriteEnabled": False,
            "promotionExecutionEnabled": False,
            "importExecutionEnabled": False,
            "unsafeWriteRefused": True,
        },
        "guarantees": {
            "noMutationPaths": True,
            "noCanonicalWrites": True,
            "noImports": True,
            "noPromotions": True,
        },
        "targetCorpus": {
            "dhatuCount": 1400,
            "sutraCount": 400,
            "stotraCount": 200,
            "totalCount": EXPECTED_TOTAL,
        },
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "certificationExecutionAllowed": False,
    }


class TestBulkCorpusCertificationAssuranceLayer(unittest.TestCase):
    def test_valid_packet_is_assured_and_hard_stopped(self):
        record = build_assurance_record(_valid_packet())
        self.assertTrue(record["assured"])
        self.assertEqual(record["status"], "assurance-ready")
        self.assertTrue(record["hardStop"])
        self.assertEqual(record["failures"], [])
        self.assertFalse(record["authorization"]["certificationIsAuthorization"])
        self.assertFalse(record["canonicalWriteAllowed"])
        self.assertFalse(record["promotionAllowed"])
        self.assertFalse(record["importAllowed"])
        self.assertFalse(record["executionAllowed"])
        self.assertFalse(record["assuranceExecutionAllowed"])

    def test_write_flag_blocks_assurance(self):
        packet = _valid_packet()
        packet["canonicalWriteAllowed"] = True
        record = build_assurance_record(packet)
        self.assertFalse(record["assured"])
        self.assertEqual(record["status"], "assurance-blocked")
        self.assertIn("canonicalWriteAllowed-not-false", record["failures"])
        self.assertFalse(record["canonicalWriteAllowed"])

    def test_count_mismatch_blocks_assurance(self):
        packet = _valid_packet()
        packet["invariants"]["acceptedRecords"] = 1999
        record = build_assurance_record(packet)
        self.assertFalse(record["assured"])
        self.assertIn("acceptedRecords-mismatch", record["failures"])

    def test_repo_38b_packet_assures(self):
        path = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_certification.v1.json"
        if not path.exists():
            self.skipTest("38B packet not on disk")
        packet = json.loads(path.read_text(encoding="utf-8"))
        record = build_assurance_record(packet)
        self.assertTrue(record["assured"], record["failures"])


if __name__ == "__main__":
    unittest.main()
