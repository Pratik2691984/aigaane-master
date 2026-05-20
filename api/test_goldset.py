import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_registry import load_all_dhatus


ROOT = Path(__file__).resolve().parents[1]
GOLDSET_ROOT = ROOT / "data" / "sanskrit" / "goldset"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
GOLDSET_FILES = [
    "README.md",
    "CHANGELOG.md",
    "goldset_metadata.v1.json",
    "dhatu_goldset.v1.json",
    "expected_records.v1.json",
    "expected_prakriya_refs.v1.json",
    "semantic_enrichment.v1.json",
]
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.semantic_query_engine",
    "engines.trace_graph",
}


class SanskritGoldsetTests(unittest.TestCase):
    def setUp(self):
        self.metadata = self._load_json("goldset_metadata.v1.json")
        self.goldset = self._load_json("dhatu_goldset.v1.json")
        self.expected_records = self._load_json("expected_records.v1.json")
        self.expected_prakriya_refs = self._load_json("expected_prakriya_refs.v1.json")
        self.semantic_enrichment = self._load_json("semantic_enrichment.v1.json")
        self.registry_by_id = {record["id"]: record for record in load_all_dhatus(DHATU_ROOT)}

    def test_goldset_files_exist(self):
        for filename in GOLDSET_FILES:
            self.assertTrue((GOLDSET_ROOT / filename).exists(), filename)

    def test_metadata_version_exists(self):
        self.assertEqual(self.metadata["goldsetVersion"], "1.0.0")
        self.assertEqual(self.metadata["schemaVersion"], "dhatu.schema.v2")
        self.assertEqual(self.metadata["recordCount"], len(self.metadata["records"]))
        self.assertGreaterEqual(self.metadata["recordCount"], 10)
        self.assertEqual(self.semantic_enrichment["goldsetVersion"], "1.0.0")
        self.assertEqual(self.semantic_enrichment["semanticVersion"], "1.0.0")

    def test_dhatu_goldset_ids_are_unique(self):
        ids = [entry["id"] for entry in self.goldset["records"]]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, self.metadata["records"])

    def test_every_goldset_id_exists_in_canonical_dhatu_registry(self):
        for dhatu_id in self.metadata["records"]:
            self.assertIn(dhatu_id, self.registry_by_id)

    def test_expected_records_contains_every_goldset_id(self):
        for dhatu_id in self.metadata["records"]:
            self.assertIn(dhatu_id, self.expected_records["records"])

    def test_expected_record_equals_canonical_registry_record_exactly(self):
        for dhatu_id in self.metadata["records"]:
            self.assertEqual(self.expected_records["records"][dhatu_id], self.registry_by_id[dhatu_id])

    def test_expected_prakriya_refs_is_valid_json_and_may_be_empty(self):
        self.assertEqual(self.expected_prakriya_refs["goldsetVersion"], "1.0.0")
        self.assertIn("records", self.expected_prakriya_refs)
        self.assertIsInstance(self.expected_prakriya_refs["records"], dict)

    def test_no_runtime_engines_are_imported_or_modified(self):
        import_lines = [
            line.strip()
            for line in Path(__file__).read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def _load_json(self, filename):
        with (GOLDSET_ROOT / filename).open("r", encoding="utf-8") as handle:
            return json.load(handle)


if __name__ == "__main__":
    unittest.main()
