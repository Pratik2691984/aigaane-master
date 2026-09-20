import csv
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.scholarly_export_engine import ScholarlyExportEngine


class ScholarlyExportEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ScholarlyExportEngine()
        self.payload = {
            "input_text": "rama asti",
            "timeline": [
                {"step_id": "s_0001", "operation": "sandhi", "output_state": {"sutra": "6.1.101", "merged": "ramasti"}, "semantic": {"semanticTag": "combination"}},
            ],
            "ambiguity_branches": [{"branch_id": "a", "status": "selected"}],
            "provenanceScore": {"score": 0.92, "grade": "canonical"},
            "semanticAttributions": [{"stepId": "s_0001", "semanticTag": "combination"}],
        }

    def test_exports_all_scholarly_formats(self):
        result = self.engine.export(self.payload)

        self.assertEqual(set(result.keys()), {"jsonld", "markdown", "csv", "teiXml"})
        self.assertEqual(json.loads(result["jsonld"])["@type"], "aigaane:DerivationExport")
        self.assertIn("# Aigaane Derivation Report", result["markdown"])
        self.assertIn("<TEI>", result["teiXml"])

    def test_csv_trace_table_contains_steps(self):
        rows = list(csv.DictReader(io.StringIO(self.engine.export_csv(self.payload))))

        self.assertEqual(rows[0]["step_id"], "s_0001")
        self.assertEqual(rows[0]["sutra"], "6.1.101")
        self.assertEqual(rows[0]["semantic_tags"], "combination")

    def test_rejects_non_dict_input(self):
        with self.assertRaises(ValueError):
            self.engine.export([])


if __name__ == "__main__":
    unittest.main()
