import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.vyakarana import analyze_sanskrit


ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "tests" / "chandas_corpus" / "suite.json"


def weight_string(pada):
    return pada["guru_laghu_pattern"].replace(" ", "")


class ChandasCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))

    def test_frozen_chandas_corpus(self):
        for case in self.suite["cases"]:
            with self.subTest(case=case["id"]):
                payload = analyze_sanskrit(case["input_text"])
                expected = case["expected"]
                padas = payload["padas"]

                self.assertIn(expected["meter_substring"], payload["overall_stanza_meter"])
                self.assertEqual(len(padas), expected["pada_count"])
                self.assertEqual([pada["syllable_count"] for pada in padas], expected["dimensions"])
                self.assertEqual([weight_string(pada) for pada in padas], expected["weight_strings"])
                self.assertEqual([pada["matra_count"] for pada in padas], expected["pada_matra_totals"])
                self.assertEqual(payload["total_matra_count"], expected["total_matra_count"])


if __name__ == "__main__":
    unittest.main()
