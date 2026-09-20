import copy
import json
import sys
import unittest
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.lexical_registry import LEXICON_ROOT, LexicalRegistryValidator


class LexicalRegistryPipelineTests(unittest.TestCase):
    def setUp(self):
        self.validator = LexicalRegistryValidator()
        self.entries = self.validator.load_sample_entries()

    def test_schema_file_exists(self):
        schema_path = LEXICON_ROOT / "schema" / "lexical_entry_schema.json"

        self.assertTrue(schema_path.exists())
        with schema_path.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
        self.assertIn("lexical_id", schema["required"])
        self.assertEqual(schema["properties"]["normalization"]["properties"]["unicode"]["const"], "NFC")

    def test_sample_entries_load(self):
        lemmas = {entry["lemma_devanagari"] for entry in self.entries}

        self.assertEqual(len(self.entries), 7)
        self.assertTrue({"\u0930\u093e\u092e", "\u0939\u0930\u093f", "\u0928\u0926\u0940", "\u092b\u0932", "\u092d\u0942", "\u092a\u0920\u094d", "\u0917\u092e\u094d"}.issubset(lemmas))

    def test_all_sample_entries_validate(self):
        normalized = self.validator.validate_registry(self.entries)

        self.assertEqual(len(normalized), 7)

    def test_duplicate_lexical_id_rejected(self):
        entries = copy.deepcopy(self.entries)
        entries[1]["lexical_id"] = entries[0]["lexical_id"]

        with self.assertRaises(ValueError):
            self.validator.validate_registry(entries)

    def test_missing_source_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        del entry["source"]

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_invalid_category_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        entry["category"] = "adjective"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_invalid_status_rejected(self):
        entry = copy.deepcopy(self.entries[0])
        entry["status"] = "approved"

        with self.assertRaises(ValueError):
            self.validator.validate_entry(entry)

    def test_nfc_normalization_applied(self):
        entry = copy.deepcopy(self.entries[0])
        entry["lemma_iast"] = "ra\u0304ma"

        normalized = self.validator.validate_entry(entry)

        self.assertEqual(normalized["lemma_iast"], "r\u0101ma")
        self.assertEqual(unicodedata.normalize("NFC", normalized["lemma_iast"]), normalized["lemma_iast"])

    def test_utf8_sanskrit_preserved(self):
        normalized = self.validator.validate_registry(self.entries)
        devanagari_forms = [entry["lemma_devanagari"] for entry in normalized]

        self.assertIn("\u0930\u093e\u092e", devanagari_forms)
        self.assertIn("\u092a\u0920\u094d", devanagari_forms)


if __name__ == "__main__":
    unittest.main()
