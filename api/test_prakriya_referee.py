import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.prakriya_referee import (
    build_prakriya_ref_id,
    load_referee_context,
    resolve_prakriya_query,
    validate_referee_query,
)


ROOT = Path(__file__).resolve().parents[1]
PRAKRIYA_REFS_PATH = ROOT / "data" / "sanskrit" / "goldset" / "expected_prakriya_refs.v1.json"
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


class PrakriyaRefereeTests(unittest.TestCase):
    def setUp(self):
        self.context = load_referee_context()

    def test_valid_bhu_lat_kartari_parasmaipada_3s_returns_target_form(self):
        query = self._query("01.0001", "parasmaipada")
        result = resolve_prakriya_query(self.context, query)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["targetForm"], self.context["registryRecords"]["01.0001"]["forms"]["kartari"]["lat"]["parasmaipada"][0][0])

    def test_valid_edh_lat_kartari_atmanepada_3s_returns_target_form(self):
        query = self._query("01.0002", "atmanepada")
        result = resolve_prakriya_query(self.context, query)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["targetForm"], self.context["registryRecords"]["01.0002"]["forms"]["kartari"]["lat"]["atmanepada"][0][0])

    def test_missing_dhatu_id_returns_missing_record(self):
        result = resolve_prakriya_query(self.context, self._query("99.9999", "parasmaipada"))

        self.assertEqual(result["status"], "missing-record")
        self.assertFalse(result["registryRecordFound"])

    def test_unsupported_lakara_returns_missing_form(self):
        query = self._query("01.0001", "parasmaipada")
        query["lakara"] = "lun"
        result = resolve_prakriya_query(self.context, query)

        self.assertEqual(result["status"], "missing-form")
        self.assertFalse(result["confidence"]["formFound"])

    def test_invalid_matrix_index_is_rejected(self):
        query = self._query("01.0001", "parasmaipada")
        query["personRow"] = 3

        with self.assertRaises(ValueError):
            validate_referee_query(query)

    def test_result_includes_semantic_domains_when_overlay_exists(self):
        result = resolve_prakriya_query(self.context, self._query("01.0001", "parasmaipada"))

        self.assertTrue(result["semanticOverlayFound"])
        self.assertIn("existence", result["semanticDomains"])

    def test_result_marks_goldset_record_true_for_goldset_ids(self):
        result = resolve_prakriya_query(self.context, self._query("01.0001", "parasmaipada"))

        self.assertTrue(result["goldsetRecord"])
        self.assertTrue(result["confidence"]["goldsetBacked"])

    def test_generated_prakriya_ref_is_stable_and_deterministic(self):
        query = self._query("01.0001", "parasmaipada")

        self.assertEqual(
            build_prakriya_ref_id(query),
            "PR_01_0001_LAT_KARTARI_PARASMAI_3S",
        )
        self.assertEqual(build_prakriya_ref_id(query), build_prakriya_ref_id(dict(query)))

    def test_expected_prakriya_refs_loads_and_validates(self):
        with PRAKRIYA_REFS_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertEqual(payload["goldsetVersion"], "1.0.0")
        self.assertEqual(payload["traceVersion"], "0.2.0")
        self.assertIn("PR_01_0001_LAT_KARTARI_PARASMAI_3S", payload["records"])
        for ref_id, ref in payload["records"].items():
            self.assertTrue(ref_id.startswith("PR_"))
            self.assertTrue(ref["canonicalized"])
            self.assertEqual(ref["traceVersion"], "0.2.0")
            self.assertIn("dhatuId", ref)
            self.assertIn("targetForm", ref)
            self.assertIn("traceCompleteness", ref)
            self.assertIn("sutraTrace", ref)

    def test_no_runtime_grammar_engines_are_imported(self):
        import_lines = [
            line.strip()
            for line in Path(__file__).read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def _query(self, dhatu_id, pada):
        return {
            "dhatuId": dhatu_id,
            "lakara": "lat",
            "pada": pada,
            "prayoga": "kartari",
            "personRow": 0,
            "numberCol": 0,
        }


if __name__ == "__main__":
    unittest.main()
