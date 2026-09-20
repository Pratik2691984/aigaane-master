import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.ambiguity import AmbiguityCandidate, make_ambiguous, make_unambiguous
from kernel_api import MorphologyResponse, SandhiAnalyzeResponse


DERIVATION_STEP = {
    "sutra": "phase1_test",
    "sutra_name": "Phase 1 ambiguity test",
    "operation": "candidate_enumeration",
    "input_state": "input",
    "output_state": "output",
    "engine_node": "Node 6 Ambiguity",
}


class AmbiguityPipelineTests(unittest.TestCase):
    def test_unambiguous_payload_shape(self):
        payload = make_unambiguous()
        self.assertFalse(payload.is_ambiguous)
        self.assertEqual(payload.candidates, [])
        self.assertEqual(payload.strategy, "unambiguous")
        self.assertIsNone(payload.selected_candidate_id)

    def test_ambiguous_payload_shape(self):
        candidate = AmbiguityCandidate(
            candidate_id="sandhi-1",
            final_output="\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f",
            source_engine="Node 2A Vowel Sandhi",
            reason="Supported enumerated derivation.",
            derivation_path=[DERIVATION_STEP],
        )
        payload = make_ambiguous([candidate])
        self.assertTrue(payload.is_ambiguous)
        self.assertEqual(payload.strategy, "enumeration_only")
        self.assertEqual(payload.candidates[0].candidate_id, "sandhi-1")

    def test_candidate_serialization(self):
        candidate = AmbiguityCandidate(
            candidate_id="morphology-1",
            final_output="\u092d\u0935\u0924\u093f",
            source_engine="Node 3 Morphology",
            confidence=None,
            reason="Candidate retained without ranking.",
            derivation_path=[DERIVATION_STEP],
        )
        self.assertEqual(
            candidate.model_dump(),
            {
                "candidate_id": "morphology-1",
                "final_output": "\u092d\u0935\u0924\u093f",
                "source_engine": "Node 3 Morphology",
                "confidence": None,
                "reason": "Candidate retained without ranking.",
                "derivation_path": [DERIVATION_STEP],
            },
        )

    def test_no_default_selected_candidate(self):
        payload = make_ambiguous(
            [
                {
                    "candidate_id": "candidate-1",
                    "final_output": "output",
                    "source_engine": "test_engine",
                    "reason": "Enumerated test candidate.",
                    "derivation_path": [],
                }
            ]
        )
        self.assertIsNone(payload.selected_candidate_id)

    def test_existing_sandhi_response_can_include_ambiguity_null(self):
        response = SandhiAnalyzeResponse(
            merged="\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f",
            sutra="6.1.101",
            sutra_name="\u0905\u0915\u0903 \u0938\u0935\u0930\u094d\u0923\u0947 \u0926\u0940\u0930\u094d\u0918\u0903",
            type="vowel_sandhi",
            trace=[
                {
                    "layer": "orthographic_input",
                    "word1": "\u0930\u093e\u092e",
                    "word2": "\u0905\u0938\u094d\u0924\u093f",
                }
            ],
            ambiguity=None,
        )
        self.assertIsNone(response.ambiguity)

    def test_existing_morphology_response_can_include_ambiguity_null(self):
        response = MorphologyResponse(
            type="tinganta",
            input={"dhatu": "\u092d\u0942", "lakara": "lat", "person": "3", "number": "1"},
            form="\u092d\u0935\u0924\u093f",
            metadata={},
            rule={"engine": "table_driven_lat_conjugation"},
            ambiguity=None,
        )
        self.assertIsNone(response.ambiguity)


if __name__ == "__main__":
    unittest.main()
