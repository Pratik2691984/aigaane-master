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


class ChandasProsodyOverlayTests(unittest.TestCase):
    def test_laghu_guru_classification(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const cases = {
              shortOpen: buildChandasProsodyOverlay({ text: 'अ' }).syllables[0],
              longVowel: buildChandasProsodyOverlay({ text: 'आ' }).syllables[0],
              cluster: buildChandasProsodyOverlay({ text: 'अन्त' }).syllables[0],
              anusvara: buildChandasProsodyOverlay({ text: 'अं' }).syllables[0],
              visarga: buildChandasProsodyOverlay({ text: 'अः' }).syllables[0],
            };
            console.log(JSON.stringify(cases));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["shortOpen"]["weight"], "laghu")
        self.assertEqual(result["longVowel"]["weight"], "guru")
        self.assertEqual(result["cluster"]["weight"], "guru")
        self.assertEqual(result["anusvara"]["weight"], "guru")
        self.assertEqual(result["visarga"]["weight"], "guru")

    def test_matra_counting(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const overlay = buildChandasProsodyOverlay({ text: 'अ आ अः' });
            console.log(JSON.stringify({
              matras: overlay.syllables.map((item) => item.matra),
              total: overlay.diagnostics.matraTotal,
            }));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["matras"], [1, 2, 2])
        self.assertEqual(result["total"], 5)

    def test_gana_grouping(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const overlay = buildChandasProsodyOverlay({ text: 'अ आ आ' });
            console.log(JSON.stringify(overlay.ganas[0]));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["pattern"], "laghu-guru-guru")
        self.assertEqual(result["gana"], "ya")

    def test_no_canonical_metre_guessing(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const overlay = buildChandasProsodyOverlay({ text: 'अ आ आ अ' });
            console.log(JSON.stringify(overlay.metreCandidates));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, [])

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const input = {
              text: 'अ आ',
              tokens: [{ token: 'अ', index: 0 }],
              phoneticAnalysis: { phonemes: [{ text: 'अ' }] },
              sandhiTransitions: { transitions: [{ id: 's1' }] },
              symbolicCompression: { classes: [{ id: 'ac' }] },
              phoneticTopology: { nodes: [{ id: 'kanthya' }] },
              morphologyTransitions: { nodes: [{ id: 'm1' }] },
              sandarbhaContextOverlay: { nodes: [{ id: 'c1' }] },
              derivationGraph: { nodes: [{ id: 'd1' }] },
            };
            const before = JSON.stringify(input);
            const overlay = buildChandasProsodyOverlay(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, syllableCount: overlay.diagnostics.syllableCount }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["syllableCount"], 2)

    def test_overlay_stability(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const input = { text: 'अ आ अः' };
            const first = buildChandasProsodyOverlay(input);
            const second = buildChandasProsodyOverlay(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { buildChandasProsodyOverlay } from './ui/tabs/sanskrit/chandas/chandas-prosody-engine.js';
            const overlays = [
              buildChandasProsodyOverlay(),
              buildChandasProsodyOverlay({}),
              buildChandasProsodyOverlay({
                tokens: [null, 'bad'],
                phoneticAnalysis: { phonemes: [null, 'bad'] },
                sandhiTransitions: { transitions: [null, 'bad'] },
              }),
            ];
            console.log(JSON.stringify(overlays.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
