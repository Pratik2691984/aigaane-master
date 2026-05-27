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


class KarakaOverlayTests(unittest.TestCase):
    def test_deterministic_mapping(self):
        source = textwrap.dedent(
            """
            import { getKarakaByVibhakti } from './ui/tabs/sanskrit/karaka/karaka-relation-map.js';
            const pairs = {
              prathama: 'karta',
              dvitiya: 'karma',
              trtiya: 'karana',
              caturthi: 'sampradana',
              pancami: 'apadana',
              saptami: 'adhikarana',
            };
            const result = Object.fromEntries(
              Object.entries(pairs).map(([vibhakti]) => [vibhakti, getKarakaByVibhakti(vibhakti)?.id || null])
            );
            console.log(JSON.stringify(result));
            """
        )
        result = run_node_json(source)
        self.assertEqual(
            result,
            {
                "prathama": "karta",
                "dvitiya": "karma",
                "trtiya": "karana",
                "caturthi": "sampradana",
                "pancami": "apadana",
                "saptami": "adhikarana",
            },
        )

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { buildKarakaOverlay } from './ui/tabs/sanskrit/karaka/karaka-overlay-engine.js';
            const input = {
              morphologyTransitions: {
                entries: [
                  { token: 'rāmaḥ', index: 0, vibhakti: 'prathama' },
                  { token: 'vanam', index: 1, vibhakti: 'dvitiya' },
                ],
              },
              semanticOverlays: { nodes: [{ id: 'semantic_1' }] },
              derivationGraph: { nodes: [{ id: 'derivation_1' }] },
              ruleTraceChain: { nodes: [{ id: 'trace_1' }] },
            };
            const before = JSON.stringify(input);
            const overlay = buildKarakaOverlay(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, overlay }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertEqual(result["overlay"]["diagnostics"]["matchedCount"], 2)

    def test_overlay_stability(self):
        source = textwrap.dedent(
            """
            import { buildKarakaOverlay } from './ui/tabs/sanskrit/karaka/karaka-overlay-engine.js';
            const input = {
              morphologyTransitions: {
                entries: [
                  { token: 'rāmeṇa', index: 2, vibhakti: 'trtiya' },
                  { token: 'grāme', index: 3, vibhakti: 'saptami' },
                ],
              },
            };
            const first = buildKarakaOverlay(input);
            const second = buildKarakaOverlay(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { buildKarakaOverlay } from './ui/tabs/sanskrit/karaka/karaka-overlay-engine.js';
            const cases = [
              buildKarakaOverlay(),
              buildKarakaOverlay({}),
              buildKarakaOverlay({ morphologyTransitions: [{ token: 'x' }, null, 'bad'] }),
            ];
            console.log(JSON.stringify(cases.map((item) => ({
              status: item.status,
              inspectedCount: item.diagnostics.inspectedCount,
              warnings: item.diagnostics.warnings.length,
            }))));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result[0]["status"], "ready")
        self.assertEqual(result[1]["status"], "ready")
        self.assertEqual(result[2]["status"], "ready")
        self.assertEqual(result[2]["inspectedCount"], 3)
        self.assertGreaterEqual(result[2]["warnings"], 2)


if __name__ == "__main__":
    unittest.main()
