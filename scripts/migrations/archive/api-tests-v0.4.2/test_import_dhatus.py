import csv
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "import_dhatus.py"
SCHEMA_PATH = ROOT / "data" / "sanskrit" / "schemas" / "dhatu.schema.v2.json"
SEED_DHATU_DIR = ROOT / "data" / "sanskrit" / "dhatus"

spec = importlib.util.spec_from_file_location("import_dhatus", SCRIPT_PATH)
import_dhatus = importlib.util.module_from_spec(spec)
sys.modules["import_dhatus"] = import_dhatus
spec.loader.exec_module(import_dhatus)


class ImportDhatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dhatu-import-"))
        self.output_dir = self.tmp / "dhatus"
        shutil.copytree(SEED_DHATU_DIR, self.output_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_csv_sample_dry_run_parses_successfully(self):
        csv_path = self._write_csv([self._row("01.0101", root="गम्", canonical="गच्छति")])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH)

        self.assertEqual(result.parsed, 1)
        self.assertEqual(result.valid, 1)
        self.assertFalse(result.written_files)

    def test_jsonl_sample_dry_run_parses_successfully(self):
        jsonl_path = self.tmp / "raw.jsonl"
        jsonl_path.write_text(json.dumps(self._row("01.0102", root="पठ्", canonical="पठति"), ensure_ascii=False) + "\n", encoding="utf-8")

        result = import_dhatus.import_dhatus(jsonl_path, self.output_dir, SCHEMA_PATH)

        self.assertEqual(result.parsed, 1)
        self.assertEqual(result.valid, 1)
        self.assertFalse(result.errors)

    def test_nine_form_csv_matrix_converts_to_three_by_three(self):
        matrix = import_dhatus.parse_matrix("a,b,c,d,e,f,g,h,i")

        self.assertEqual(matrix, [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]])

    def test_malformed_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            import_dhatus.parse_matrix("a,b,c")

    def test_invalid_id_is_rejected(self):
        csv_path = self._write_csv([self._row("bad-id")])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH)

        self.assertEqual(result.valid, 0)
        self.assertEqual(len(result.errors), 1)

    def test_derivation_base_ending_in_ting_suffix_is_rejected(self):
        row = self._row("01.0103")
        row["sananta_base"] = "भवति"
        csv_path = self._write_csv([row])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH)

        self.assertEqual(result.valid, 0)
        self.assertIn("stem-only", result.errors[0].message)

    def test_duplicate_id_is_skipped_without_force(self):
        csv_path = self._write_csv([self._row("01.0001", root="गम्", canonical="गच्छति")])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH, write=True)
        payload = self._read_gana()

        self.assertEqual(result.skipped_duplicates, 1)
        self.assertFalse(result.written_files)
        self.assertNotEqual(payload["records"][0]["identity"]["root"], "गम्")

    def test_duplicate_id_is_replaced_with_force(self):
        csv_path = self._write_csv([self._row("01.0001", root="गम्", canonical="गच्छति")])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH, write=True, force=True)
        payload = self._read_gana()
        replaced = [record for record in payload["records"] if record["id"] == "01.0001"][0]

        self.assertEqual(result.replaced_duplicates, 1)
        self.assertEqual(replaced["identity"]["root"], "गम्")

    def test_write_mode_updates_gana_file_atomically(self):
        csv_path = self._write_csv([self._row("01.0104", root="नी", canonical="नयति")])

        result = import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH, write=True)
        payload = self._read_gana()

        self.assertTrue(result.written_files)
        self.assertFalse((self.output_dir / "01_bhvadi.json.tmp").exists())
        self.assertIn("01.0104", {record["id"] for record in payload["records"]})

    def test_index_json_is_rebuilt_correctly(self):
        csv_path = self._write_csv([self._row("01.0105", root="भज्", canonical="भजति")])

        import_dhatus.import_dhatus(csv_path, self.output_dir, SCHEMA_PATH, write=True)
        index = json.loads((self.output_dir / "index.json").read_text(encoding="utf-8"))

        self.assertEqual(index["records"]["01.0105"]["root"], "भज्")
        self.assertEqual(index["records"]["01.0105"]["canonicalForm"], "भजति")
        self.assertEqual(index["records"]["01.0105"]["gana"]["slug"], "bhvadi")

    def test_no_runtime_grammar_engines_are_imported_or_modified(self):
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertNotIn("engines.morphology", source)
        self.assertNotIn("engines.sandhi", source)
        self.assertNotIn("engines.vyakarana", source)
        self.assertNotIn("derivation_replay", source)
        self.assertNotIn("replay_analytics", source)

    def _row(self, dhatu_id, root="भू", canonical="भवति"):
        return {
            "id": dhatu_id,
            "upadesha": root,
            "root": root,
            "romanized": "bhu",
            "canonicalForm": canonical,
            "gana_id": "01",
            "itStatus": "seṭ",
            "karmatva": "akarmaka",
            "defaultPada": "parasmaipada",
            "semantics_sanskrit": "भाव",
            "semantics_english": "being",
            "lat_kartari_parasmaipada": "भवति,भवतः,भवन्ति,भवसि,भवथः,भवथ,भवामि,भवावः,भवामः",
            "lot_kartari_parasmaipada": "",
            "lat_kartari_atmanepada": "",
            "lot_kartari_atmanepada": "",
            "lat_bhavaKarmani_atmanepada": "",
            "sananta_base": "बुभूष",
            "nijanta_base": "भावि",
            "yanganta_base": "बोभूय",
            "upasarga_list": "प्र;सम्",
            "ruleTriggers": "1.3.78",
        }

    def _write_csv(self, rows):
        path = self.tmp / "raw.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _read_gana(self):
        return json.loads((self.output_dir / "01_bhvadi.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
