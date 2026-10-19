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


class VakyaDependencyOverlayTests(unittest.TestCase):
    def test_finite_verb_anchor_detection(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const overlay = buildVakyaDependencyOverlay({
              morphologyTransitions: {
                entries: [{ token: 'gacchati', index: 2, morphologyType: 'tiṅanta' }],
              },
            });
            console.log(JSON.stringify(overlay));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["diagnostics"]["anchorCount"], 1)
        self.assertEqual(result["anchors"][0]["anchorType"], "finite-verb")
        self.assertEqual(result["anchors"][0]["token"], "gacchati")

    def test_karaka_to_verb_dependency_mapping(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const karakas = ['karta', 'karma', 'karana', 'sampradana', 'apadana', 'adhikarana'];
            const overlay = buildVakyaDependencyOverlay({
              morphologyTransitions: {
                entries: [{ token: 'gacchati', index: 6, morphologyType: 'finite-verb' }],
              },
              karakaOverlay: {
                nodes: karakas.map((karaka, index) => ({
                  id: `karaka_${karaka}`,
                  token: `token_${index}`,
                  index,
                  karaka,
                  vibhakti: 'explicit',
                })),
              },
            });
            console.log(JSON.stringify(overlay.edges.map((edge) => edge.relation)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(
            result,
            [
                "kartaToVerb",
                "karmaToVerb",
                "karanaToVerb",
                "sampradanaToVerb",
                "apadanaToVerb",
                "adhikaranaToVerb",
            ],
        )

    def test_no_anchor_safety(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const overlay = buildVakyaDependencyOverlay({
              karakaOverlay: {
                nodes: [{ id: 'karaka_karta', token: 'rāmaḥ', index: 0, karaka: 'karta', vibhakti: 'prathama' }],
              },
            });
            console.log(JSON.stringify(overlay));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["diagnostics"]["anchorCount"], 0)
        self.assertEqual(result["diagnostics"]["edgeCount"], 0)
        self.assertEqual(result["nodes"][0]["role"], "unresolvedCandidate")
        self.assertTrue(result["diagnostics"]["warnings"])

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const input = {
              tokens: [{ token: 'rāmaḥ', index: 0 }],
              morphologyTransitions: { entries: [{ token: 'gacchati', index: 1, marker: 'finite-verb' }] },
              karakaOverlay: { nodes: [{ id: 'k1', token: 'rāmaḥ', index: 0, karaka: 'karta' }] },
              semanticOverlays: { nodes: [{ id: 's1' }] },
              derivationGraph: { nodes: [{ id: 'd1' }] },
              ruleTraceChain: { nodes: [{ id: 'r1' }] },
            };
            const before = JSON.stringify(input);
            const overlay = buildVakyaDependencyOverlay(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, edgeCount: overlay.edges.length }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["edgeCount"], 1)

    def test_overlay_stability(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const input = {
              morphologyTransitions: { entries: [{ token: 'paśyati', index: 2, tags: ['tinganta'] }] },
              karakaOverlay: { nodes: [{ id: 'k2', token: 'phalam', index: 1, karaka: 'karma' }] },
            };
            const first = buildVakyaDependencyOverlay(input);
            const second = buildVakyaDependencyOverlay(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { buildVakyaDependencyOverlay } from './ui/tabs/sanskrit/vakya/vakya-dependency-engine.js';
            const overlays = [
              buildVakyaDependencyOverlay(),
              buildVakyaDependencyOverlay({}),
              buildVakyaDependencyOverlay({
                tokens: [null, 'bad'],
                morphologyTransitions: { entries: [null, 'bad'] },
                karakaOverlay: { nodes: [null, 'bad', { token: 'x', karaka: 'karta' }] },
              }),
            ];
            console.log(JSON.stringify(overlays.map((overlay) => overlay.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
