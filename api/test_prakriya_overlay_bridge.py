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


BASE_SOURCE = """
import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
import { buildPrakriyaTraceGraph } from './ui/tabs/sanskrit/prakriya/prakriya-trace-graph.js';
import {
  attachAllOverlays,
  attachOverlayToEdge,
  attachOverlayToNode,
} from './ui/tabs/sanskrit/prakriya/prakriya-overlay-bridge.js';
const execution = executePrakriya({
  nounInputs: [{ stem: 'rama', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
  verbInput: { dhatu: 'gam', lakara: 'lat', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
  enableTrace: true,
  enableReversePreview: true,
});
const graph = buildPrakriyaTraceGraph(execution);
"""


class PrakriyaOverlayBridgeTests(unittest.TestCase):
    def test_attach_overlay_to_node_does_not_mutate_original_graph(self):
        result = run_node_json(textwrap.dedent(BASE_SOURCE + """
            const before = JSON.stringify(graph);
            const attached = attachOverlayToNode(graph, graph.nodes[0].id, 'karaka', { id: 'k1' });
            console.log(JSON.stringify({
              same: before === JSON.stringify(graph),
              original: graph.nodes[0].overlays || null,
              attached: attached.nodes[0].overlays.karaka.id,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertIsNone(result["original"])
        self.assertEqual(result["attached"], "k1")

    def test_attach_overlay_to_edge_does_not_mutate_original_graph(self):
        result = run_node_json(textwrap.dedent(BASE_SOURCE + """
            const before = JSON.stringify(graph);
            const attached = attachOverlayToEdge(graph, graph.edges[0].id, 'vakya', { id: 'v1' });
            console.log(JSON.stringify({
              same: before === JSON.stringify(graph),
              original: graph.edges[0].overlays || null,
              attached: attached.edges[0].overlays.vakya.id,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertIsNone(result["original"])
        self.assertEqual(result["attached"], "v1")

    def test_attach_all_overlays_returns_metadata(self):
        result = run_node_json(textwrap.dedent(BASE_SOURCE + """
            const unified = attachAllOverlays(graph, execution, {
              inputText: 'rama gacchati',
              morphologyTransitions: {
                entries: [
                  { token: 'rama', index: 0, vibhakti: 'prathama' },
                  { token: 'gacchati', index: 1, marker: 'finite-verb' },
                ],
              },
            });
            console.log(JSON.stringify({
              attached: unified.metadata.overlaysAttached,
              overlayCount: unified.diagnostics.overlayCount,
            }));
            """))
        self.assertEqual(
            result["attached"],
            ["karaka", "vakya", "chandas", "sandarbha", "semantic", "rule-trace"],
        )
        self.assertGreater(result["overlayCount"], 0)

    def test_unsupported_missing_graph_does_not_crash(self):
        result = run_node_json(textwrap.dedent("""
            import { attachAllOverlays } from './ui/tabs/sanskrit/prakriya/prakriya-overlay-bridge.js';
            const outputs = [
              attachAllOverlays(),
              attachAllOverlays(null, null),
              attachAllOverlays('bad', 'bad'),
            ];
            console.log(JSON.stringify(outputs.map((item) => ({
              status: item.status,
              nodes: item.nodes.length,
              overlaysAttached: item.metadata.overlaysAttached,
            }))));
            """))
        self.assertEqual([item["status"] for item in result], ["ready", "ready", "ready"])
        self.assertEqual([item["nodes"] for item in result], [0, 0, 0])

    def test_same_input_returns_identical_unified_graph(self):
        result = run_node_json(textwrap.dedent(BASE_SOURCE + """
            const options = {
              inputText: 'rama gacchati',
              morphologyTransitions: {
                entries: [
                  { token: 'rama', index: 0, vibhakti: 'prathama' },
                  { token: 'gacchati', index: 1, marker: 'finite-verb' },
                ],
              },
            };
            const first = attachAllOverlays(graph, execution, options);
            const second = attachAllOverlays(graph, execution, options);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_renderer_compatible_nodes_preserve_overlays_object(self):
        result = run_node_json(textwrap.dedent(BASE_SOURCE + """
            const unified = attachAllOverlays(graph, execution, {
              inputText: 'rama gacchati',
              morphologyTransitions: {
                entries: [
                  { token: 'rama', index: 0, vibhakti: 'prathama' },
                  { token: 'gacchati', index: 1, marker: 'finite-verb' },
                ],
              },
            });
            const node = unified.nodes.find((item) => item.overlays && Object.keys(item.overlays).length);
            console.log(JSON.stringify({
              hasNode: Boolean(node),
              isObject: Boolean(node && node.overlays && !Array.isArray(node.overlays)),
              types: node ? Object.keys(node.overlays).sort() : [],
            }));
            """))
        self.assertTrue(result["hasNode"])
        self.assertTrue(result["isObject"])
        self.assertGreater(len(result["types"]), 0)


if __name__ == "__main__":
    unittest.main()

