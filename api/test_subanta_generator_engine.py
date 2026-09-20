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


class SubantaGeneratorEngineTests(unittest.TestCase):
    def test_masculine_a_stem_generation(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const base = { stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vacana: 'eka' };
            const cases = {
              prathama: generateSubanta({ ...base, vibhakti: 'prathama' }),
              dvitiya: generateSubanta({ ...base, vibhakti: 'dvitiya' }),
              sasthi: generateSubanta({ ...base, vibhakti: 'sasthi' }),
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["prathama"]["generatedForm"], "रामः")
        self.assertEqual(result["dvitiya"]["generatedForm"], "रामम्")
        self.assertEqual(result["sasthi"]["generatedForm"], "रामस्य")

    def test_neuter_a_stem_generation(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const base = { stem: 'फल', stemClass: 'a-stem', linga: 'neuter', vacana: 'eka' };
            const cases = {
              prathama: generateSubanta({ ...base, vibhakti: 'prathama' }),
              dvitiya: generateSubanta({ ...base, vibhakti: 'dvitiya' }),
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["prathama"]["generatedForm"], "फलम्")
        self.assertEqual(result["dvitiya"]["generatedForm"], "फलम्")

    def test_feminine_aa_stem_generation(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const base = { stem: 'सीता', stemClass: 'ā-stem', linga: 'feminine', vacana: 'eka' };
            const cases = {
              prathama: generateSubanta({ ...base, vibhakti: 'prathama' }),
              trtiya: generateSubanta({ ...base, vibhakti: 'trtiya' }),
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["prathama"]["generatedForm"], "सीता")
        self.assertEqual(result["trtiya"]["generatedForm"], "सीतया")

    def test_deterministic_suffix_application(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const input = { stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'trtiya', vacana: 'eka' };
            const first = generateSubanta(input);
            const second = generateSubanta(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), form: first.generatedForm }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["form"], "रामेण")

    def test_reverse_preview_stability(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const input = { stem: 'सीता', stemClass: 'ā-stem', linga: 'feminine', vibhakti: 'trtiya', vacana: 'eka' };
            const before = JSON.stringify(input);
            const first = generateSubanta(input).reversePreview;
            const second = generateSubanta(input).reversePreview;
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, stable: JSON.stringify(first) === JSON.stringify(second), first }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"][0]["reconstructedStem"], "सीता")

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const input = {
              stem: 'राम',
              stemClass: 'a-stem',
              linga: 'masculine',
              vibhakti: 'prathama',
              vacana: 'eka',
              metadata: { source: 'test' },
            };
            const before = JSON.stringify(input);
            const output = generateSubanta(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, form: output.generatedForm }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["form"], "रामः")

    def test_unsupported_combination_safety(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const output = generateSubanta({
              stem: 'हरि',
              stemClass: 'i-stem',
              linga: 'masculine',
              vibhakti: 'prathama',
              vacana: 'eka',
            });
            console.log(JSON.stringify(output));
            """
        )
        result = run_node_json(source)
        self.assertFalse(result["matched"])
        self.assertFalse(result["diagnostics"]["supported"])
        self.assertEqual(result["generatedForm"], "")
        self.assertGreaterEqual(len(result["diagnostics"]["warnings"]), 1)

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { generateSubanta } from './ui/tabs/sanskrit/subanta/subanta-generator-engine.js';
            const outputs = [
              generateSubanta(),
              generateSubanta(null),
              generateSubanta({}),
              generateSubanta({ stem: '' }),
              generateSubanta({ stem: 'राम', linga: 'unexpected', vibhakti: '', vacana: '' }),
              generateSubanta({ stem: 'राम', vibhakti: 'prathama', vacana: 'बहु' }),
            ];
            console.log(JSON.stringify(outputs.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
