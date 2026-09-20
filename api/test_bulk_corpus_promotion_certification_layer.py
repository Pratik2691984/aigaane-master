import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_bulk_corpus_promotion_certification import (
    EXPECTED_TOTAL,
    build_certification_record,
)


class TestBulkCorpusPromotionCertificationLayer(unittest.TestCase):
    def setUp(self):
        self.valid_manifest = {
            "metadata": {"recordCount": EXPECTED_TOTAL},
            "status": "staging-ready",
        }

    def test_certification_invariants(self):
        cert = build_certification_record(self.valid_manifest)
        invariants = cert["invariants"]

        self.assertTrue(invariants["approval-ready"])
        self.assertTrue(invariants["manual-review-ready"])
        self.assertEqual(invariants["acceptedRecords"], 2000)
        self.assertEqual(invariants["rejectedRecords"], 0)
        self.assertFalse(invariants["canonicalWriteEnabled"])
        self.assertFalse(invariants["promotionExecutionEnabled"])
        self.assertFalse(invariants["importExecutionEnabled"])
        self.assertTrue(invariants["unsafeWriteRefused"])

    def test_strict_zero_mutation_guarantees(self):
        cert = build_certification_record(self.valid_manifest)
        guarantees = cert["guarantees"]

        self.assertTrue(guarantees["noMutationPaths"])
        self.assertTrue(guarantees["noCanonicalWrites"])
        self.assertTrue(guarantees["noImports"])
        self.assertTrue(guarantees["noPromotions"])

    def test_record_count_mismatch_raises(self):
        bad_manifest = {"metadata": {"recordCount": 1999}}
        with self.assertRaises(ValueError):
            build_certification_record(bad_manifest)

    def test_safety_flags_remain_locked(self):
        cert = build_certification_record(self.valid_manifest)
        self.assertTrue(cert["previewOnly"])
        self.assertTrue(cert["readOnly"])
        self.assertFalse(cert["canonicalWriteAllowed"])
        self.assertFalse(cert["promotionAllowed"])
        self.assertFalse(cert["importAllowed"])
        self.assertFalse(cert["executionAllowed"])
        self.assertFalse(cert["certificationExecutionAllowed"])


if __name__ == "__main__":
    unittest.main()
