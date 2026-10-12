import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_registry import (
    find_dhatu_by_id,
    find_dhatus_by_root,
    load_all_dhatus,
    load_dhatu_file,
    validate_dhatu_record,
    validate_lakara_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
DHATU_FILE = ROOT / "data" / "sanskrit" / "dhatus" / "01_bhvadi.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
INDEX_FILE = DHATU_ROOT / "index.json"
DHATU_ID_RE = re.compile(r"^[0-9]{2}\.[0-9]{4}$")
SUTRA_ID_RE = re.compile(r"^[1-8]\.[1-4]\.[0-9]+$")
OBVIOUS_TIN_ENDINGS = ("ति", "ते", "सि", "से")


class DhatuRegistryTests(unittest.TestCase):
    def setUp(self):
        self.records = load_dhatu_file(DHATU_FILE)
        self.records_by_id = {record["id"]: record for record in self.records}

    def test_bhvadi_file_loads_as_json(self):
        with DHATU_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertEqual(payload["gana"]["id"], "01")
        self.assertGreaterEqual(len(payload["records"]), 2)

    def test_every_record_id_matches_gana_number_format(self):
        for record in self.records:
            self.assertRegex(record["id"], DHATU_ID_RE)

    def test_gana_id_matches_file_prefix(self):
        for record in self.records:
            self.assertEqual(record["grammar"]["gana"]["id"], "01")
            validate_dhatu_record(record, expected_gana_id="01")

    def test_every_form_matrix_is_3_by_3(self):
        for record in self.records:
            for matrix in self._matrices(record["forms"]):
                self.assertEqual(validate_lakara_matrix(matrix), matrix)
                self.assertEqual(len(matrix), 3)
                self.assertTrue(all(len(row) == 3 for row in matrix))

    def test_pada_rule_triggers_are_sutra_shaped(self):
        for record in self.records:
            for sutra_id in record["padaProfile"].get("ruleTriggers", []):
                self.assertRegex(sutra_id, SUTRA_ID_RE)

    def test_derivation_bases_are_stem_only(self):
        for record in self.records:
            for derivation in record["derivations"]:
                base = derivation["base"]
                self.assertFalse(base.endswith(OBVIOUS_TIN_ENDINGS), base)

    def test_index_maps_seed_ids_to_root_canonical_form_and_gana_slug(self):
        with INDEX_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertIn("01.0001", payload["records"])
        self.assertIn("01.0002", payload["records"])
        for dhatu_id in ("01.0001", "01.0002"):
            indexed = payload["records"][dhatu_id]
            canonical = self.records_by_id[dhatu_id]
            self.assertEqual(indexed["root"], canonical["identity"]["root"])
            self.assertEqual(indexed["canonicalForm"], canonical["identity"]["canonicalForm"])
            self.assertEqual(indexed["gana"]["slug"], canonical["grammar"]["gana"]["slug"])

    def test_read_only_helpers_find_records(self):
        all_records = load_all_dhatus(DHATU_ROOT)
        all_records_by_id = {record["id"]: record for record in all_records}

        self.assertGreaterEqual(len(all_records), 2)
        self.assertIn("02.0001", all_records_by_id)
        self.assertIn("03.0001", all_records_by_id)
        self.assertIn("04.0001", all_records_by_id)
        self.assertEqual(
            find_dhatu_by_id(all_records, "01.0002")["identity"]["root"],
            self.records_by_id["01.0002"]["identity"]["root"],
        )
        self.assertEqual(
            find_dhatus_by_root(all_records, self.records_by_id["01.0001"]["identity"]["root"])[0]["identity"]["canonicalForm"],
            self.records_by_id["01.0001"]["identity"]["canonicalForm"],
        )
        self.assertIsNone(find_dhatu_by_id(all_records, "01.9999"))

    def _matrices(self, value):
        matrices = []
        if isinstance(value, dict):
            for child in value.values():
                matrices.extend(self._matrices(child))
        elif isinstance(value, list):
            if len(value) == 3 and all(isinstance(row, list) for row in value):
                matrices.append(value)
            else:
                for child in value:
                    matrices.extend(self._matrices(child))
        return matrices


if __name__ == "__main__":
    unittest.main()
