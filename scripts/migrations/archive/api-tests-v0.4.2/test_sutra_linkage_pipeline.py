import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.sutra_linker import SutraTraceLinker


class SutraLinkagePipelineTests(unittest.TestCase):
    def setUp(self):
        self.linker = SutraTraceLinker()

    def test_registry_loads(self):
        registry = self.linker.load_registry()

        self.assertEqual(len(registry), 7)
        self.assertIn("8.4.40", registry)

    def test_resolve_existing_sutra(self):
        sutra = self.linker.resolve_sutra("8.4.40")

        self.assertIsNotNone(sutra)
        self.assertEqual(sutra["sutra_text_devanagari"], "\u0938\u094d\u0924\u094b\u0903 \u0936\u094d\u091a\u0941\u0928\u093e \u0936\u094d\u091a\u0941\u0903")
        self.assertEqual(sutra["domain"], "consonant_sandhi")

    def test_unresolved_sutra_returns_none(self):
        self.assertIsNone(self.linker.resolve_sutra("1.1.1"))

    def test_trace_step_gains_sutra_ref(self):
        step = {
            "sutra": "8.4.40",
            "operation": "dental_to_palatal_assimilation",
            "input_state": "\u0924\u0924\u094d + \u091a",
            "output_state": "\u0924\u091a\u094d\u091a",
        }

        linked = self.linker.link_trace_step(step)

        self.assertEqual(linked["sutra"], "8.4.40")
        self.assertEqual(linked["sutra_ref"]["sutra_id"], "8.4.40")

    def test_unresolved_step_gets_null_sutra_ref(self):
        linked = self.linker.link_trace_step({"sutra": "1.1.1", "operation": "unknown"})

        self.assertIsNone(linked["sutra_ref"])

    def test_original_trace_object_unchanged(self):
        trace = [{"sutra": "8.4.40", "operation": "dental_to_palatal_assimilation"}]
        original = copy.deepcopy(trace)

        linked = self.linker.link_trace(trace)
        linked[0]["sutra_ref"]["notes"] = "changed"

        self.assertEqual(trace, original)
        self.assertNotIn("sutra_ref", trace[0])

    def test_utf8_sanskrit_preserved(self):
        linked = self.linker.link_trace_step({"sutra": "6.1.87"})

        self.assertEqual(linked["sutra_ref"]["sutra_text_devanagari"], "\u0906\u0926\u094d\u0917\u0941\u0923\u0903")
        self.assertEqual(linked["sutra_ref"]["sutra_text_iast"], "\u0101dgu\u1e47a\u1e25")

    def test_multiple_step_trace_linking(self):
        trace = [
            {"sutra": "6.1.87", "operation": "guna_substitution"},
            {"sutra": "8.4.40", "operation": "dental_to_palatal_assimilation"},
            {"sutra": "1.1.1", "operation": "unresolved"},
        ]

        linked = self.linker.link_trace(trace)

        self.assertEqual(len(linked), 3)
        self.assertEqual(linked[0]["sutra_ref"]["sutra_id"], "6.1.87")
        self.assertEqual(linked[1]["sutra_ref"]["sutra_id"], "8.4.40")
        self.assertIsNone(linked[2]["sutra_ref"])

    def test_missing_sutra_field_safe_handling(self):
        linked = self.linker.link_trace_step({"operation": "missing_sutra"})

        self.assertEqual(linked["operation"], "missing_sutra")
        self.assertIsNone(linked["sutra_ref"])


if __name__ == "__main__":
    unittest.main()
