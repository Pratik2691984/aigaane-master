import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_registry import load_all_dhatus


ROOT = Path(__file__).resolve().parents[1]
GOLDSET_ROOT = ROOT / "data" / "sanskrit" / "goldset"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"


class SanskritGoldsetTests(unittest.TestCase):
    def setUp(self):
        self.metadata = self._load("goldset_metadata.v1.json")
        self.goldset = self._load("dhatu_goldset.v1.json")
        self.expected_records = self._load("expected_records.v1.json")
        self.expected_prakriya_refs = self._load("expected_prakriya_refs.v1.json")
        self.registry_by_id = {record["id"]: record for record in load_all_dhatus(DHATU_ROOT)}

    def test_goldset_version_exists(self):
        self.assertTrue(self.metadata.get("version"))
        self.assertTrue(self.goldset.get("version"))
        self.assertTrue(self.expected_records.get("version"))

    def test_every_goldset_id_exists_in_dhatu_registry(self):
        goldset_ids = [entry["id"] for entry in self.goldset["entries"]]

        self.assertEqual(goldset_ids, self.metadata["dhatuIds"])
        for dhatu_id in goldset_ids:
            self.assertIn(dhatu_id, self.registry_by_id)

    def test_expected_record_matches_canonical_registry_record(self):
        for dhatu_id, expected_record in self.expected_records["records"].items():
            self.assertIn(dhatu_id, self.registry_by_id)
            self.assertEqual(expected_record, self.registry_by_id[dhatu_id])

    def test_expected_prakriya_refs_may_be_empty_stub(self):
        self.assertEqual(self.expected_prakriya_refs["schema"], "aigaane.expected_prakriya_refs.v1")
        self.assertIn("refs", self.expected_prakriya_refs)
        self.assertIsInstance(self.expected_prakriya_refs["refs"], dict)

    def _load(self, filename):
        with (GOLDSET_ROOT / filename).open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
