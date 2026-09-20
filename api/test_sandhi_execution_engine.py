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


class SandhiExecutionEngineTests(unittest.TestCase):
    def test_vowel_sandhi_execution(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const cases = {
              aa: executeSandhi({ tokens: ['rama', 'asti'] }).transitions[0],
              ai: executeSandhi({ tokens: ['rama', 'iti'] }).transitions[0],
              au: executeSandhi({ tokens: ['rama', 'udeti'] }).transitions[0],
              ae: executeSandhi({ tokens: ['rama', 'eva'] }).transitions[0],
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["aa"]["transformedBoundary"], "ā")
        self.assertEqual(result["ai"]["transformedBoundary"], "e")
        self.assertEqual(result["au"]["transformedBoundary"], "o")
        self.assertEqual(result["ae"]["transformedBoundary"], "ai")

    def test_visarga_sandhi_execution(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const ahA = executeSandhi({ tokens: ['rāmaḥ', 'asti'] }).transitions[0];
            const ahI = executeSandhi({ tokens: ['rāmaḥ', 'iti'] }).transitions[0];
            console.log(JSON.stringify({ ahA, ahI }));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["ahA"]["category"], "visarga")
        self.assertEqual(result["ahA"]["transformedBoundary"], "o 'a")
        self.assertEqual(result["ahI"]["transformedBoundary"], "a r i")

    def test_consonant_sandhi_execution(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const cases = {
              tt: executeSandhi({ tokens: ['tat', 'tvam'] }).transitions[0],
              nd: executeSandhi({ tokens: ['san', 'dhi'] }).transitions[0],
              mp: executeSandhi({ tokens: ['sam', 'pada'] }).transitions[0],
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["tt"]["transformedBoundary"], "tt")
        self.assertEqual(result["nd"]["transformedBoundary"], "nd")
        self.assertEqual(result["mp"]["transformedBoundary"], "mp")

    def test_deterministic_ordering(self):
        source = textwrap.dedent(
            """
            import { listSandhiRules, matchSandhiRule } from './ui/tabs/sanskrit/sandhi/sandhi-rule-map.js';
            const rules = listSandhiRules();
            const priorities = rules.map((rule) => rule.priority);
            const sorted = priorities.every((priority, index) => index === 0 || priorities[index - 1] >= priority);
            const matched = matchSandhiRule('a', 'a');
            console.log(JSON.stringify({ sorted, matched }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["sorted"])
        self.assertEqual(result["matched"]["id"], "vowel.a_a.dirgha")
        self.assertEqual(result["matched"]["priority"], 100)

    def test_reverse_preview_stability(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const input = { tokens: [{ token: 'rama' }, { token: 'asti' }] };
            const before = JSON.stringify(input);
            const first = executeSandhi(input).reversePreview;
            const second = executeSandhi(input).reversePreview;
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, stable: JSON.stringify(first) === JSON.stringify(second), first }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"][0]["reconstructed"], "a+a")

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const input = {
              text: 'rama asti',
              tokens: [{ token: 'rama', meta: { index: 0 } }, { token: 'asti', meta: { index: 1 } }],
              mode: 'test',
            };
            const before = JSON.stringify(input);
            const output = executeSandhi(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, outputText: output.originalTokens.join(' ') }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["outputText"], "rama asti")

    def test_overlay_stability(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const input = { text: 'rama asti tat tvam' };
            const first = executeSandhi(input);
            const second = executeSandhi(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { executeSandhi } from './ui/tabs/sanskrit/sandhi/sandhi-execution-engine.js';
            const outputs = [
              executeSandhi(),
              executeSandhi(null),
              executeSandhi({}),
              executeSandhi({ text: '' }),
              executeSandhi({ tokens: [null, 'bad', { nope: true }, { token: '' }] }),
              executeSandhi({ tokens: [{ token: 'rama' }, { token: 'asti' }] }),
            ];
            console.log(JSON.stringify(outputs.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
