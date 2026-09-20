import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_semantic_query import (
    build_query_index,
    combined_query,
    load_query_context,
    query_by_action_type,
    query_by_gana,
    query_by_karmatva,
    query_by_pada,
    query_by_root,
    query_by_rule_trigger,
    query_by_semantic_domain,
    query_by_tag,
    query_by_trace_completeness,
    normalize_query_value,
    summarize_query_index,
)


FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


class DhatuSemanticQueryTests(unittest.TestCase):
    def setUp(self):
        self.context = load_query_context()
        self.index = build_query_index(
            self.context["records"],
            semantic_overlay=self.context["semanticOverlay"],
            prakriya_refs=self.context["prakriyaRefs"],
        )

    def test_query_context_loads_successfully(self):
        self.assertGreaterEqual(len(self.context["records"]), 10)
        self.assertIn("records", self.context["semanticOverlay"])
        self.assertIn("records", self.context["prakriyaRefs"])

    def test_query_index_builds_over_canonical_registry(self):
        self.assertGreaterEqual(len(self.index["items"]), 10)

    def test_semantic_domain_existence_returns_bhu(self):
        self.assertEqual(self._ids(query_by_semantic_domain(self.index, "existence")), ["01.0001"])

    def test_semantic_domain_growth_returns_edh(self):
        self.assertEqual(self._ids(query_by_semantic_domain(self.index, "growth")), ["01.0002"])

    def test_query_by_gana_id_returns_bhvadi_records(self):
        ids = self._ids(query_by_gana(self.index, "01"))

        self.assertIn("01.0001", ids)
        self.assertIn("01.0002", ids)

    def test_query_by_gana_slug_returns_bhvadi_records(self):
        ids = self._ids(query_by_gana(self.index, "bhvadi"))

        self.assertIn("01.0001", ids)
        self.assertIn("01.0002", ids)

    def test_query_by_pada_parasmaipada_returns_expected_records(self):
        ids = self._ids(query_by_pada(self.index, "parasmaipada"))

        self.assertIn("01.0001", ids)
        self.assertIn("02.0001", ids)

    def test_query_by_karmatva_akarmaka_returns_expected_records(self):
        ids = self._ids(query_by_karmatva(self.index, "akarmaka"))

        self.assertIn("04.0001", ids)
        self.assertTrue(ids)

    def test_query_by_rule_trigger_returns_records_where_trigger_exists(self):
        self.assertEqual(self._ids(query_by_rule_trigger(self.index, "1.3.78")), ["01.0001"])

    def test_query_by_trace_completeness_stub_returns_records_with_stub_traces(self):
        ids = self._ids(query_by_trace_completeness(self.index, "stub"))

        self.assertIn("01.0001", ids)
        self.assertIn("04.0001", ids)

    def test_query_by_action_type_state_change_returns_bhu(self):
        self.assertEqual(self._ids(query_by_action_type(self.index, "state-change")), ["01.0001"])

    def test_query_by_root_bhu_returns_seed_record(self):
        root = self.index["items"][0]["root"]

        self.assertEqual(self._ids(query_by_root(self.index, root)), ["01.0001"])

    def test_query_by_tag_bhvadi_returns_tagged_records(self):
        ids = self._ids(query_by_tag(self.index, "bhvadi"))

        self.assertIn("01.0001", ids)
        self.assertIn("01.0002", ids)

    def test_combined_query_semantic_domain_and_gana_returns_intersection(self):
        results = combined_query(self.index, {"semanticDomain": "existence", "gana": "01"})

        self.assertEqual(self._ids(results), ["01.0001"])

    def test_combined_query_impossible_combination_returns_empty_list(self):
        results = combined_query(self.index, {"semanticDomain": "existence", "gana": "10"})

        self.assertEqual(results, [])

    def test_summarize_query_index_returns_counts(self):
        summary = summarize_query_index(self.index)

        self.assertGreaterEqual(summary["recordCount"], 10)
        self.assertGreaterEqual(summary["domainCount"], 10)
        self.assertGreaterEqual(summary["ganaCount"], 9)

    def test_query_results_are_sorted_by_dhatu_id(self):
        ids = self._ids(query_by_pada(self.index, "parasmaipada"))

        self.assertEqual(ids, sorted(ids))

    def test_normalize_query_value_is_case_insensitive_and_trimmed(self):
        self.assertEqual(normalize_query_value(" Bhvadi "), "bhvadi")

    def test_query_functions_do_not_mutate_input(self):
        original = copy.deepcopy(self.index)

        query_by_semantic_domain(self.index, "existence")
        query_by_gana(self.index, "01")
        combined_query(self.index, {"pada": "parasmaipada"})

        self.assertEqual(self.index, original)

    def test_no_runtime_grammar_engines_are_imported(self):
        import_lines = [
            line.strip()
            for line in Path(__file__).read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def _ids(self, results):
        return [item["dhatuId"] for item in results]


if __name__ == "__main__":
    unittest.main()
