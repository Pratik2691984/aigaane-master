import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


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


class SutraDependencyResolverTests(unittest.TestCase):
    def test_dependency_registry_includes_required_stages(self):
        result = run_node_json(textwrap.dedent("""
            import { groupSutraDependenciesByStage } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-map.js';
            const groups = groupSutraDependenciesByStage();
            console.log(JSON.stringify(Object.fromEntries(
              Object.entries(groups).map(([stage, items]) => [stage, items.length])
            )));
            """))
        self.assertGreaterEqual(result["sandhiExecution"], 5)
        self.assertGreaterEqual(result["subantaGeneration"], 5)
        self.assertGreaterEqual(result["tinantaGeneration"], 4)
        self.assertGreaterEqual(result["padaAssembly"], 1)
        self.assertGreaterEqual(result["sentenceComposition"], 1)

    def test_dependency_index_groups_by_rule_id(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyIndex } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-map.js';
            const index = buildSutraDependencyIndex();
            console.log(JSON.stringify({
              hasSandhi: Boolean(index.sandhi_a_i_to_e?.length),
              dep: index.sandhi_a_i_to_e?.[0]?.dependsOn,
            }));
            """))
        self.assertTrue(result["hasSandhi"])
        self.assertEqual(result["dep"], "symbolic_ac")

    def test_rule_dependency_resolution(self):
        result = run_node_json(textwrap.dedent("""
            import { resolveRuleDependencies } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const resolution = resolveRuleDependencies('sandhi_a_i_to_e');
            console.log(JSON.stringify(resolution));
            """))
        self.assertEqual(result["dependencies"][0]["dependsOn"], "symbolic_ac")
        self.assertFalse(result["diagnostics"]["warnings"])

    def test_missing_dependency_safety(self):
        result = run_node_json(textwrap.dedent("""
            import { resolveRuleDependencies } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            console.log(JSON.stringify(resolveRuleDependencies('unknown_rule')));
            """))
        self.assertEqual(result["dependencies"], [])
        self.assertTrue(result["diagnostics"]["warnings"])

    def test_dependency_graph_construction(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyGraph } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const graph = buildSutraDependencyGraph({
              rulefire: { firedRules: [{ ruleId: 'sandhi_a_i_to_e' }, { ruleId: 'tinanta_gam_lat_prathama_eka' }] },
              sutraReferenceOverlay: { overlay: { nodes: [{ id: 'symbolic_ac' }] } },
            });
            console.log(JSON.stringify(graph));
            """))
        self.assertEqual(result["status"], "ready")
        self.assertGreaterEqual(result["diagnostics"]["nodeCount"], 4)
        self.assertGreaterEqual(result["diagnostics"]["edgeCount"], 2)

    def test_runtime_isolation(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyGraph } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const input = { rulefire: { firedRules: [{ ruleId: 'sandhi_a_i_to_e' }] } };
            const before = JSON.stringify(input);
            const graph = buildSutraDependencyGraph(input);
            console.log(JSON.stringify({ same: before === JSON.stringify(input), nodeCount: graph.nodes.length }));
            """))
        self.assertTrue(result["same"])
        self.assertGreater(result["nodeCount"], 0)

    def test_graph_attachment_does_not_mutate_original(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyGraph, attachSutraDependenciesToGraph } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const graph = { nodes: [{ id: 'base', type: 'input' }], edges: [], metadata: {} };
            const dep = buildSutraDependencyGraph({ rulefire: { firedRules: [{ ruleId: 'sandhi_a_i_to_e' }] } });
            const before = JSON.stringify(graph);
            const attached = attachSutraDependenciesToGraph(graph, dep);
            console.log(JSON.stringify({
              same: before === JSON.stringify(graph),
              attached: attached.metadata.dependenciesAttached,
              baseNodes: graph.nodes.length,
              attachedNodes: attached.nodes.length,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertTrue(result["attached"])
        self.assertGreater(result["attachedNodes"], result["baseNodes"])

    def test_stability(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyGraph } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const input = { rulefire: { firedRules: [{ ruleId: 'prakriya_emit_sentence' }] } };
            const first = buildSutraDependencyGraph(input);
            const second = buildSutraDependencyGraph(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_backend_compatibility(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "agnim ile"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("prakriya_graph", payload)
        self.assertIn("sutra_dependency", payload)
        self.assertTrue(payload["prakriya_graph"]["metadata"]["dependenciesAttached"])
        self.assertEqual(payload["sutra_dependency"]["status"], "ready")

    def test_partial_input_safety(self):
        result = run_node_json(textwrap.dedent("""
            import { buildSutraDependencyGraph } from './ui/tabs/sanskrit/sutra-dependency/sutra-dependency-engine.js';
            const outputs = [
              buildSutraDependencyGraph(),
              buildSutraDependencyGraph(null),
              buildSutraDependencyGraph({ rulefire: 'bad' }),
              buildSutraDependencyGraph({ rulefire: { firedRules: [{ ruleId: 'unknown' }] }, ruleTraceOverlay: 'bad', enabledStages: ['unsupported'] }),
            ];
            console.log(JSON.stringify(outputs.map((item) => ({
              status: item.status,
              nodes: item.nodes.length,
              edges: item.edges.length,
              warnings: item.diagnostics.warnings.length,
            }))));
            """))
        self.assertEqual([item["status"] for item in result], ["ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()

