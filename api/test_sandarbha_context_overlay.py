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


class SandarbhaContextOverlayTests(unittest.TestCase):
    def test_local_dependency_neighborhood(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlay = buildSandarbhaContextOverlay({
              vakyaDependencyOverlay: {
                edges: [{ source: 'vakya.node.0.rama.karta', target: 'vakya.anchor.1.gacchati', relation: 'kartaToVerb' }],
              },
            });
            console.log(JSON.stringify(overlay));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["diagnostics"]["neighborhoodCount"], 1)
        self.assertEqual(result["neighborhoods"][0]["relation"], "localDependencyNeighborhood")

    def test_karaka_continuity(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlay = buildSandarbhaContextOverlay({
              karakaOverlay: {
                nodes: [
                  { id: 'k1', token: 'rāmaḥ', index: 0, karaka: 'karta' },
                  { id: 'k2', token: 'sītā', index: 1, karaka: 'karta' },
                ],
              },
            });
            console.log(JSON.stringify(overlay.candidates.map((item) => item.candidateType)));
            """
        )
        result = run_node_json(source)
        self.assertIn("karakaContinuity", result)

    def test_morphology_continuity(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlay = buildSandarbhaContextOverlay({
              morphologyTransitions: {
                entries: [
                  { token: 'rāmaḥ', index: 0, vibhakti: 'prathama', linga: 'pum', vacana: 'eka' },
                  { token: 'devaḥ', index: 1, vibhakti: 'prathama', linga: 'pum', vacana: 'eka' },
                ],
              },
            });
            console.log(JSON.stringify(overlay.candidates.map((item) => item.candidateType)));
            """
        )
        result = run_node_json(source)
        self.assertIn("morphologyContinuity", result)

    def test_no_semantic_guessing(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlay = buildSandarbhaContextOverlay({
              tokens: [{ token: 'saḥ', index: 0 }],
              semanticOverlays: { graph: { nodes: [{ id: 'cluster_motion' }] } },
            });
            console.log(JSON.stringify(overlay));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["diagnostics"]["edgeCount"], 0)
        self.assertFalse(any(item["relation"] == "semanticAdjacency" for item in result["edges"]))
        self.assertFalse(any(item["candidateType"] == "antecedentResolution" for item in result["candidates"]))

    def test_pronoun_candidate_safety(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlay = buildSandarbhaContextOverlay({
              tokens: [{ token: 'saḥ', index: 0, pos: 'pronoun' }],
            });
            console.log(JSON.stringify(overlay));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result["candidates"][0]["candidateType"], "pronounAntecedentCandidate")
        self.assertEqual(result["diagnostics"]["unresolvedCount"], 1)
        self.assertFalse(any(item["candidateType"] == "antecedentResolution" for item in result["candidates"]))

    def test_runtime_isolation_no_input_mutation(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const input = {
              tokens: [{ token: 'saḥ', index: 0, pos: 'pronoun' }],
              morphologyTransitions: { entries: [{ token: 'rāmaḥ', index: 1, vibhakti: 'prathama' }] },
              karakaOverlay: { nodes: [{ id: 'k1', token: 'rāmaḥ', index: 1, karaka: 'karta' }] },
              vakyaDependencyOverlay: { edges: [{ source: 'k1', target: 'v1', relation: 'kartaToVerb' }] },
              semanticOverlays: { graph: { edges: [{ source: 'cluster_guidance', target: 'cluster_motion' }] } },
              derivationGraph: { graph: { nodes: [{ id: 'd1', lineage: ['x'] }, { id: 'd2', lineage: ['x'] }] } },
              ruleTraceChain: { nodes: [{ id: 'r1' }] },
            };
            const before = JSON.stringify(input);
            const overlay = buildSandarbhaContextOverlay(input);
            const after = JSON.stringify(input);
            console.log(JSON.stringify({ same: before === after, edgeCount: overlay.edges.length }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["same"])
        self.assertGreaterEqual(result["edgeCount"], 1)

    def test_overlay_stability(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const input = {
              karakaOverlay: {
                nodes: [
                  { id: 'k1', token: 'rāmaḥ', index: 0, karaka: 'karta' },
                  { id: 'k2', token: 'sītā', index: 1, karaka: 'karta' },
                ],
              },
            };
            const first = buildSandarbhaContextOverlay(input);
            const second = buildSandarbhaContextOverlay(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """
        )
        result = run_node_json(source)
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        source = textwrap.dedent(
            """
            import { buildSandarbhaContextOverlay } from './ui/tabs/sanskrit/sandarbha/sandarbha-context-engine.js';
            const overlays = [
              buildSandarbhaContextOverlay(),
              buildSandarbhaContextOverlay({}),
              buildSandarbhaContextOverlay({
                tokens: [null, 'bad'],
                morphologyTransitions: { entries: [null, 'bad'] },
                karakaOverlay: { nodes: [null, 'bad'] },
                vakyaDependencyOverlay: { edges: [null, 'bad'] },
              }),
            ];
            console.log(JSON.stringify(overlays.map((item) => item.status)));
            """
        )
        result = run_node_json(source)
        self.assertEqual(result, ["ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
