import copy
import json
import sys
import unittest
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.sutra_registry import SUTRA_ROOT, SutraRegistryValidator


class SutraRegistryPipelineTests(unittest.TestCase):
    def setUp(self):
        self.validator = SutraRegistryValidator()
        self.entries = self.validator.load_sample_sutras()

    def test_schema_exists(self):
        schema_path = SUTRA_ROOT / "schema" / "sutra_entry_schema.json"

        self.assertTrue(schema_path.exists())
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.assertIn("sutra_id", schema["required"])
        self.assertIn("vowel_sandhi", schema["properties"]["domain"]["enum"])

    def test_sample_sutras_load(self):
        sutra_ids = {entry["sutra_id"] for entry in self.entries}

        self.assertEqual(len(self.entries), 7)
        self.assertEqual(
            sutra_ids,
            {"6.1.101", "6.1.87", "6.1.77", "8.3.15", "8.3.34", "8.4.40", "8.2.39"},
        )

    def test_all_seven_sutras_validate(self):
        normalized = self.validator.validate_registry(self.entries)

        self.assertEqual(len(normalized), 7)

    def test_duplicate_sutra_id_rejected(self):
        entries = copy.deepcopy(self.entries)
        entries[1]["sutra_id"] = entries[0]["sutra_id"]

        with self.assertRaises(ValueError):
            self.validator.validate_registry(entries)

    def test_invalid_domain_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        entry["domain"] = "phonology"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_invalid_status_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        entry["status"] = "approved"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_invalid_source_type_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        entry["source_type"] = "web"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_nfc_normalization_preservation(self):
        entry = copy.deepcopy(self.entries[1])
        entry["sutra_text_iast"] = "a\u0304dgun\u0323ah\u0323"

        normalized = self.validator.validate_entry(entry)

        self.assertEqual(normalized["sutra_text_iast"], unicodedata.normalize("NFC", entry["sutra_text_iast"]))

    def test_utf8_sanskrit_preservation(self):
        normalized = self.validator.validate_registry(self.entries)
        sutra_texts = [entry["sutra_text_devanagari"] for entry in normalized]

        self.assertIn("\u0906\u0926\u094d\u0917\u0941\u0923\u0903", sutra_texts)
        self.assertIn("\u0938\u094d\u0924\u094b\u0903 \u0936\u094d\u091a\u0941\u0928\u093e \u0936\u094d\u091a\u0941\u0903", sutra_texts)

    def test_chapter_pada_integrity(self):
        entry = copy.deepcopy(self.entries[0])
        entry["chapter"] = 7

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

        entry = copy.deepcopy(self.entries[0])
        entry["pada"] = 2

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

        entry = copy.deepcopy(self.entries[0])
        entry["sutra_number"] = "102"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_registry_validation_summary(self):
        normalized = self.validator.validate_registry(self.entries)
        domains = {entry["domain"] for entry in normalized}
        canonical_count = sum(1 for entry in normalized if entry["status"] == "canonical")

        self.assertEqual(len(normalized), 7)
        self.assertEqual(canonical_count, 7)
        self.assertEqual(domains, {"vowel_sandhi", "visarga_sandhi", "consonant_sandhi"})


if __name__ == "__main__":
    unittest.main()
