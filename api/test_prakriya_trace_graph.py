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


BASE_EXECUTION = """
import { executePrakriya } from './ui/tabs/sanskrit/prakriya/prakriya-composition-engine.js';
import {
  attachPrakriyaOverlay,
  buildPrakriyaTraceGraph,
  serializePrakriyaTraceGraph,
} from './ui/tabs/sanskrit/prakriya/prakriya-trace-graph.js';
const execution = executePrakriya({
  nounInputs: [{ stem: 'राम', stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }],
  verbInput: { dhatu: 'gam', lakara: 'laṭ', pada: 'parasmaipada', purusha: 'prathama', vacana: 'eka' },
  enableTrace: true,
  enableReversePreview: true,
});
"""


class PrakriyaTraceGraphTests(unittest.TestCase):
    def test_graph_construction(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            console.log(JSON.stringify({ nodes: graph.nodes.length, edges: graph.edges.length, status: graph.status }));
            """))
        self.assertEqual(result["status"], "ready")
        self.assertGreater(result["nodes"], 0)
        self.assertGreater(result["edges"], 0)

    def test_generated_pada_nodes(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            console.log(JSON.stringify(graph.nodes.map((node) => node.type)));
            """))
        self.assertIn("subantaGeneration", result)
        self.assertIn("tinantaGeneration", result)

    def test_sentence_assembly_node(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            const assembly = graph.nodes.find((node) => node.type === 'padaAssembly');
            const sentence = graph.nodes.find((node) => node.type === 'sentenceComposition');
            console.log(JSON.stringify({ assembly, sentence }));
            """))
        self.assertEqual(result["assembly"]["output"], "रामः gacchati")
        self.assertEqual(result["sentence"]["output"], "रामः gacchati")

    def test_sandhi_transition_nodes(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            console.log(JSON.stringify({
              sandhiNodes: graph.nodes.filter((node) => node.type === 'sandhiExecution').length,
              sandhiEdges: graph.edges.filter((edge) => edge.type === 'appliesSandhi').length,
            }));
            """))
        self.assertEqual(result["sandhiNodes"], 1)
        self.assertEqual(result["sandhiEdges"], 1)

    def test_serialization_stability(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            const first = serializePrakriyaTraceGraph(graph);
            const second = serializePrakriyaTraceGraph(graph);
            console.log(JSON.stringify({ stable: first === second, parsed: JSON.parse(first).schemaVersion }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["parsed"], "prakriya-trace-graph.v1")

    def test_overlay_attachment_does_not_mutate_original(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const graph = buildPrakriyaTraceGraph(execution);
            const before = JSON.stringify(graph);
            const attached = attachPrakriyaOverlay(graph, { sourceLayer: 'karaka', nodes: [{ id: 'k1' }] });
            const after = JSON.stringify(graph);
            console.log(JSON.stringify({
              same: before === after,
              originalOverlays: graph.overlays.length,
              attachedOverlays: attached.overlays.length,
              overlayCount: attached.diagnostics.overlayCount,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertEqual(result["originalOverlays"], 0)
        self.assertEqual(result["attachedOverlays"], 1)
        self.assertEqual(result["overlayCount"], 1)

    def test_runtime_isolation(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const before = JSON.stringify(execution);
            const graph = buildPrakriyaTraceGraph(execution);
            const after = JSON.stringify(execution);
            console.log(JSON.stringify({ same: before === after, nodeCount: graph.diagnostics.nodeCount }));
            """))
        self.assertTrue(result["same"])
        self.assertGreater(result["nodeCount"], 0)

    def test_stability(self):
        result = run_node_json(textwrap.dedent(BASE_EXECUTION + """
            const first = buildPrakriyaTraceGraph(execution);
            const second = buildPrakriyaTraceGraph(execution);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_partial_input_safety(self):
        result = run_node_json(textwrap.dedent("""
            import { buildPrakriyaTraceGraph } from './ui/tabs/sanskrit/prakriya/prakriya-trace-graph.js';
            const outputs = [
              buildPrakriyaTraceGraph(),
              buildPrakriyaTraceGraph({}),
              buildPrakriyaTraceGraph({ trace: [null, 'bad'], generatedPadas: [null, 'bad'], sandhiTransitions: [null, 'bad'] }),
              buildPrakriyaTraceGraph({ sentenceAssembly: {}, diagnostics: { warnings: ['warn'] } }),
            ];
            console.log(JSON.stringify(outputs.map((item) => item.status)));
            """))
        self.assertEqual(result, ["ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()
