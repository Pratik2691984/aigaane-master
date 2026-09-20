import sys
import unittest
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.derivation_session import DerivationSession


class DerivationSessionPipelineTests(unittest.TestCase):
    def test_create_empty_session(self):
        session = DerivationSession.create("तत् + च")

        UUID(session.session_id)
        self.assertTrue(session.created_at)
        self.assertEqual(session.input_text, "तत् + च")
        self.assertEqual(session.steps, [])
        self.assertEqual(session.ambiguity_branches, [])
        self.assertEqual(session.metadata, {})

    def test_add_single_step(self):
        session = DerivationSession.create("तत् + च")
        step = session.add_step(
            engine="Node 2C Consonant Sandhi",
            operation="dental_to_palatal_assimilation",
            input_state={"text": "तत् + च"},
            output_state={"text": "तच्च"},
        )

        self.assertEqual(step.step_id, "s_0001")
        self.assertEqual(step.engine, "Node 2C Consonant Sandhi")
        self.assertEqual(step.operation, "dental_to_palatal_assimilation")
        self.assertEqual(step.input_state, {"text": "तत् + च"})
        self.assertEqual(step.output_state, {"text": "तच्च"})
        self.assertIsNone(step.parent_step_id)

    def test_step_ids_increment(self):
        session = DerivationSession.create("राम अस्ति")
        first = session.add_step("engine", "normalize", {}, {})
        second = session.add_step("engine", "sandhi", {}, {})
        third = session.add_step("engine", "trace", {}, {})

        self.assertEqual(first.step_id, "s_0001")
        self.assertEqual(second.step_id, "s_0002")
        self.assertEqual(third.step_id, "s_0003")

    def test_parent_child_linkage(self):
        session = DerivationSession.create("राम अस्ति")
        parent = session.add_step("Node 5 Lexical Governance", "validate", {}, {})
        child = session.add_step(
            "Node 2A Vowel Sandhi",
            "savarna_dirgha_substitution",
            {"word1": "राम", "word2": "अस्ति"},
            {"merged": "रामास्ति"},
            parent_step_id=parent.step_id,
        )

        self.assertEqual(child.parent_step_id, "s_0001")
        self.assertIs(session.get_step(parent.step_id), parent)
        self.assertIs(session.get_step(child.step_id), child)

    def test_invalid_parent_raises_value_error(self):
        session = DerivationSession.create("राम अस्ति")

        with self.assertRaisesRegex(ValueError, "parent_step_id"):
            session.add_step("engine", "operation", {}, {}, parent_step_id="s_9999")

    def test_add_ambiguity_branch(self):
        session = DerivationSession.create("तत् + च")
        branch = {
            "is_ambiguous": True,
            "candidates": [{"candidate_id": "0", "final_output": "तच्च"}],
        }

        session.add_ambiguity_branch(branch)

        self.assertEqual(session.ambiguity_branches, [branch])
        self.assertIs(session.ambiguity_branches[0], branch)

    def test_invalid_ambiguity_branch_raises_type_error(self):
        session = DerivationSession.create("तत् + च")

        with self.assertRaisesRegex(TypeError, "dict"):
            session.add_ambiguity_branch(["not", "a", "dict"])

    def test_to_dict_shape(self):
        session = DerivationSession.create("राम अस्ति", metadata={"source": "test"})
        session.add_step("Node 5 Lexical Governance", "validate", {"text": "राम अस्ति"}, {"ok": True})
        session.add_ambiguity_branch({"is_ambiguous": False})

        payload = session.to_dict()

        self.assertEqual(
            set(payload.keys()),
            {
                "session_id",
                "created_at",
                "input_text",
                "steps",
                "ambiguity_branches",
                "metadata",
                "total_steps",
                "total_ambiguity_branches",
            },
        )
        self.assertEqual(payload["input_text"], "राम अस्ति")
        self.assertEqual(payload["total_steps"], 1)
        self.assertEqual(payload["total_ambiguity_branches"], 1)
        self.assertEqual(payload["metadata"], {"source": "test"})
        self.assertEqual(payload["steps"][0]["step_id"], "s_0001")
        self.assertIsNone(payload["steps"][0]["parent_step_id"])

    def test_derivation_path_preserved(self):
        session = DerivationSession.create("तत् + च")
        derivation_path = [
            {
                "sutra": "8.4.40",
                "sutra_name": "स्तोः श्चुना श्चुः",
                "operation": "dental_to_palatal_assimilation",
            }
        ]

        step = session.add_step(
            "Node 2C Consonant Sandhi",
            "dental_to_palatal_assimilation",
            {"text": "तत् + च"},
            {"text": "तच्च"},
            derivation_path=derivation_path,
        )

        self.assertEqual(step.derivation_path, derivation_path)
        self.assertEqual(session.to_dict()["steps"][0]["derivation_path"], derivation_path)

    def test_metadata_preserved(self):
        session = DerivationSession.create("राम अस्ति", metadata={"mode": "debug"})
        step = session.add_step(
            "Node 2A Vowel Sandhi",
            "savarna_dirgha_substitution",
            {"word1": "राम", "word2": "अस्ति"},
            {"merged": "रामास्ति"},
            metadata={"phase": "Node 7A"},
        )

        self.assertEqual(session.metadata, {"mode": "debug"})
        self.assertEqual(step.metadata, {"phase": "Node 7A"})
        self.assertEqual(session.to_dict()["metadata"], {"mode": "debug"})
        self.assertEqual(session.to_dict()["steps"][0]["metadata"], {"phase": "Node 7A"})


if __name__ == "__main__":
    unittest.main()
