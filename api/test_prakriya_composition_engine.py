import json
import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_node_json(source):
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", source],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    return json.loads(completed.stdout)


class PrakriyaCompositionEngineTests(unittest.TestCase):
    def test_subanta_tinanta_composition(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const cases = {
              rama: executePrakriya({
                nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
                verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              }).sentenceAssembly.preSandhiText,
              phala: executePrakriya({
                nounInputs: [{ stem: 'फल', stemClass: 'a-stem', linga: 'neuter', vibhakti: 'prathama', vacana: 'eka' }],
                verbInput: { dhatu: 'bhū', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              }).sentenceAssembly.preSandhiText,
              sita: executePrakriya({
                nounInputs: [{ stem: 'सीता', stemClass: 'ā-stem', linga: 'feminine', vibhakti: 'prathama', vacana: 'eka' }],
                verbInput: { dhatu: 'nī', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              }).sentenceAssembly.preSandhiText,
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["rama"], "रामः gacchati")
        self.assertEqual(result["phala"], "फलम् bhavati")
        self.assertEqual(result["sita"], "सीता nayati")

    def test_sandhi_integration(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const withSandhi = executePrakriya({
              nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
              verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              enableSandhi: true,
            });
            const withoutSandhi = executePrakriya({
              nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
              verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              enableSandhi: false,
            });
            console.log(JSON.stringify({
              transitionCount: withSandhi.sandhiTransitions.length,
              applied: withSandhi.diagnostics.sandhiAppliedCount,
              withoutCount: withoutSandhi.sandhiTransitions.length,
            }));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["transitionCount"], 1)
        self.assertEqual(result["applied"], 0)
        self.assertEqual(result["withoutCount"], 0)

    def test_trace_stability(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const input = {
              nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
              verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              enableTrace: true,
            };
            const first = executePrakriya(input).trace;
            const second = executePrakriya(input).trace;
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), stages: first.map((item) => item.stage) }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertIn("subantaGeneration", result["stages"])
        self.assertIn("tinantaGeneration", result["stages"])
        self.assertIn("sentenceComposition", result["stages"])

    def test_reverse_preview_stability(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const input = {
              nounInputs: [{ stem: 'फल', stemClass: 'a-stem', linga: 'neuter', vibhakti: 'prathama', vacana: 'eka' }],
              verbInput: { dhatu: 'bhū', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
              enableReversePreview: true,
            };
            const before = JSON.stringify(input);
            const first = executePrakriya(input).reversePreview;
            const second = executePrakriya(input).reversePreview;
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, stable: JSON.stringify(first) === JSON.stringify(second), count: first.length }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertTrue(result["stable"])
        self.assertGreaterEqual(result["count"], 2)

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const input = {
              nounInputs: [{ stem: 'सीता', stemClass: 'ā-stem', linga: 'feminine', vibhakti: 'prathama', vacana: 'eka', metadata: { i: 1 } }],
              verbInput: { dhatu: 'nī', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka', metadata: { i: 2 } },
            };
            const before = JSON.stringify(input);
            const output = executePrakriya(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, text: output.sentenceAssembly.preSandhiText }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["text"], "सीता nayati")

    def test_stability(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const input = {
              nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
              verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
            };
            const first = executePrakriya(input);
            const second = executePrakriya(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_unsupported_safety(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const output = executePrakriya({
              nounInputs: [{ stem: 'हरि', stemClass: 'i-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }, null],
              verbInput: { dhatu: 'pac', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
            });
            console.log(JSON.stringify(output.diagnostics));
            """
        )
        result = run_node_json(source)
        self.assertGreaterEqual(result["unresolvedCount"], 2)
        self.assertGreaterEqual(len(result["warnings"]), 2)

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
            const outputs = [
              executePrakriya(),
              executePrakriya(null),
              executePrakriya({}),
              executePrakriya({ nounInputs: [], verbInput: null }),
              executePrakriya({ nounInputs: [null, 'bad'], verbInput: { dhatu: '', lakara: '', pada: '', purusha: '', vacana: '' } }),
            ];
            console.log(JSON.stringify(outputs.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
