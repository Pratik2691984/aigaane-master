import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.prakriya_referee import load_referee_context, resolve_prakriya_query
from engines.sutra_trace_canonicalizer import (
    build_step_id,
    canonicalize_step,
    canonicalize_trace,
    canonicalize_trace_map,
    compare_canonical_traces,
    summarize_trace,
    validate_step_id,
    validate_sutra_id,
)


FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


class SutraTraceCanonicalizerTests(unittest.TestCase):
    def test_canonicalize_step_adds_step_id_when_missing(self):
        step = canonicalize_step({"seq": 1, "sutra": "1.3.1"}, 1)

        self.assertEqual(step["stepId"], "STEP_001")
        self.assertTrue(validate_step_id(step["stepId"]))

    def test_canonicalize_trace_sorts_steps_by_seq(self):
        trace = self._trace(
            [
                {"seq": 2, "sutra": "3.1.68", "role": "stem"},
                {"seq": 1, "sutra": "1.3.1", "role": "dhatu-samjna"},
            ]
        )

        canonical = canonicalize_trace(trace)

        self.assertEqual([step["seq"] for step in canonical["sutraTrace"]], [1, 2])

    def test_invalid_sutra_id_fails_validation(self):
        self.assertFalse(validate_sutra_id("bad"))
        with self.assertRaises(ValueError):
            canonicalize_step({"seq": 1, "sutra": "bad"}, 1)

    def test_valid_sutra_id_passes_validation(self):
        self.assertTrue(validate_sutra_id("1.3.1"))

    def test_canonicalized_trace_gets_trace_version(self):
        canonical = canonicalize_trace(self._trace([]))

        self.assertTrue(canonical["canonicalized"])
        self.assertEqual(canonical["traceVersion"], "0.2.0")

    def test_missing_confidence_defaults_to_stub(self):
        step = canonicalize_step({"seq": 1, "sutra": "1.3.1"}, 1)

        self.assertEqual(step["confidence"], "stub")

    def test_missing_notes_defaults_to_empty_list(self):
        step = canonicalize_step({"seq": 1, "sutra": "1.3.1"}, 1)

        self.assertEqual(step["notes"], [])

    def test_compare_canonical_traces_returns_no_differences_for_equivalent_traces(self):
        a = self._trace([{"seq": 1, "sutra": "1.3.1", "role": "dhatu-samjna"}])
        b = self._trace([{"stepId": "STEP_001", "seq": 1, "sutra": "1.3.1", "role": "dhatu-samjna"}])

        result = compare_canonical_traces(a, b)

        self.assertTrue(result["equal"])
        self.assertEqual(result["differences"], [])

    def test_compare_canonical_traces_detects_changed_sutra_or_role(self):
        a = self._trace([{"seq": 1, "sutra": "1.3.1", "role": "dhatu-samjna"}])
        b = self._trace([{"seq": 1, "sutra": "3.1.68", "role": "stem"}])

        result = compare_canonical_traces(a, b)
        fields = {diff["field"] for diff in result["differences"]}

        self.assertFalse(result["equal"])
        self.assertIn("sutra", fields)
        self.assertIn("role", fields)

    def test_canonicalize_trace_map_canonicalizes_all_records(self):
        trace_map = {"goldsetVersion": "1.0.0", "records": {"PR_X": self._trace([])}}

        canonical = canonicalize_trace_map(trace_map)

        self.assertEqual(canonical["traceVersion"], "0.2.0")
        self.assertTrue(canonical["records"]["PR_X"]["canonicalized"])

    def test_summarize_trace_returns_counts_and_completeness(self):
        summary = summarize_trace(self._trace([{"seq": 1, "sutra": "1.3.1"}, {"seq": 2, "sutra": "1.3.1"}]))

        self.assertEqual(summary["traceId"], "PR_TEST")
        self.assertEqual(summary["stepCount"], 2)
        self.assertEqual(summary["sutraCount"], 1)
        self.assertEqual(summary["completeness"], "stub")

    def test_prakriya_referee_still_returns_ok_for_bhu(self):
        result = resolve_prakriya_query(load_referee_context(), self._query("01.0001", "parasmaipada"))

        self.assertEqual(result["status"], "ok")

    def test_prakriya_referee_result_contains_canonicalized_trace_metadata(self):
        result = resolve_prakriya_query(load_referee_context(), self._query("01.0001", "parasmaipada"))

        self.assertTrue(result["canonicalized"])
        self.assertEqual(result["traceVersion"], "0.2.0")
        self.assertEqual(result["canonicalTrace"]["traceVersion"], "0.2.0")

    def test_no_runtime_grammar_engines_are_imported(self):
        import_lines = [
            line.strip()
            for line in Path(__file__).read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)

    def test_build_step_id_rejects_invalid_index(self):
        with self.assertRaises(ValueError):
            build_step_id(0)

    def _trace(self, steps):
        return {
            "traceId": "PR_TEST",
            "dhatuId": "01.0001",
            "targetForm": "bhavati",
            "traceCompleteness": "stub",
            "sutraTrace": steps,
        }

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
