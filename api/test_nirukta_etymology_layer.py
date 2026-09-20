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


class NiruktaEtymologyLayerTests(unittest.TestCase):
    def test_nirukta_registry_contains_seed_entries(self):
        result = run_node_json(textwrap.dedent("""
            import { listNiruktaEntries } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-map.js';
            const lemmas = listNiruktaEntries().map((entry) => entry.lemma).sort();
            console.log(JSON.stringify(lemmas));
            """))
        for lemma in ["gam", "bhu", "ni", "rama", "phala", "sita", "pra", "pari", "sam", "vi", "aa"]:
            self.assertIn(lemma, result)

    def test_known_lemma_lookup_returns_deterministic_entry(self):
        result = run_node_json(textwrap.dedent("""
            import { getNiruktaEntry } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-map.js';
            console.log(JSON.stringify(getNiruktaEntry('gam')));
            """))
        self.assertEqual(result["semanticFamily"], "motion")
        self.assertEqual(result["confidence"], "deterministic-placeholder")

    def test_semantic_family_grouping(self):
        result = run_node_json(textwrap.dedent("""
            import { findNiruktaBySemanticFamily } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-map.js';
            console.log(JSON.stringify({
              motion: findNiruktaBySemanticFamily('motion').length,
              being: findNiruktaBySemanticFamily('being').length,
              guidance: findNiruktaBySemanticFamily('guidance').length,
              nominal: findNiruktaBySemanticFamily('nominal-family').length,
            }));
            """))
        self.assertEqual(result, {"motion": 1, "being": 1, "guidance": 1, "nominal": 3})

    def test_overlay_construction_matches_known_generated_padas(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const overlay = buildNiruktaOverlay({
              prakriyaExecution: {
                inputs: {
                  nounInputs: [{ stem: 'rama', iast: 'rama' }],
                  verbInput: { dhatu: 'gam' },
                },
                generatedPadas: [
                  { id: 'pada.subanta.0', sourceType: 'subanta', generatedForm: 'ramah' },
                  { id: 'pada.tinanta.0', sourceType: 'tinanta', generatedForm: 'gacchati' },
                ],
              },
              rulefire: { firedRules: [{ ruleId: 'tinanta_gam_lat_prathama_eka' }] },
              sutraDependency: { nodes: [{ referenceId: 'tinanta_lat_parasmaipada_selection' }] },
              traceGraph: { nodes: [{ id: 'n1', label: 'gacchati', type: 'tinantaGeneration' }] },
            });
            console.log(JSON.stringify(overlay));
            """))
        self.assertEqual(result["diagnostics"]["candidateCount"], 2)
        self.assertEqual(result["diagnostics"]["unresolvedCount"], 0)

    def test_unknown_form_remains_unresolved(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const overlay = buildNiruktaOverlay({ generatedPadas: [{ id: 'x', sourceType: 'subanta', generatedForm: 'unknownform' }] });
            console.log(JSON.stringify(overlay));
            """))
        self.assertEqual(result["diagnostics"]["candidateCount"], 0)
        self.assertEqual(result["diagnostics"]["unresolvedCount"], 1)

    def test_runtime_isolation(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const input = {
              prakriyaExecution: {
                inputs: { verbInput: { dhatu: 'gam' } },
                generatedPadas: [{ sourceType: 'tinanta', generatedForm: 'gacchati' }],
              },
            };
            const before = JSON.stringify(input);
            const overlay = buildNiruktaOverlay(input);
            console.log(JSON.stringify({ same: before === JSON.stringify(input), candidates: overlay.candidates.length }));
            """))
        self.assertTrue(result["same"])
        self.assertEqual(result["candidates"], 1)

    def test_graph_attachment_does_not_mutate_original(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay, attachNiruktaToGraph } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const graph = { nodes: [{ id: 'base', type: 'input' }], edges: [], metadata: {} };
            const overlay = buildNiruktaOverlay({
              prakriyaExecution: {
                inputs: { verbInput: { dhatu: 'gam' } },
                generatedPadas: [{ sourceType: 'tinanta', generatedForm: 'gacchati' }],
              },
            });
            const before = JSON.stringify(graph);
            const attached = attachNiruktaToGraph(graph, overlay);
            console.log(JSON.stringify({
              same: before === JSON.stringify(graph),
              attached: attached.metadata.niruktaAttached,
              baseNodes: graph.nodes.length,
              attachedNodes: attached.nodes.length,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertTrue(result["attached"])
        self.assertGreater(result["attachedNodes"], result["baseNodes"])

    def test_stability(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const input = {
              prakriyaExecution: {
                inputs: { verbInput: { dhatu: 'ni' } },
                generatedPadas: [{ sourceType: 'tinanta', generatedForm: 'nayati' }],
              },
            };
            const first = buildNiruktaOverlay(input);
            const second = buildNiruktaOverlay(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_backend_payload_includes_nirukta(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "agnim ile"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("nirukta", payload)
        self.assertTrue(payload["prakriya_graph"]["metadata"]["niruktaAttached"])
        self.assertEqual(payload["nirukta"]["status"], "ready")

    def test_partial_input_safety(self):
        result = run_node_json(textwrap.dedent("""
            import { buildNiruktaOverlay } from './ui/tabs/sanskrit/nirukta/nirukta-etymology-engine.js';
            const outputs = [
              buildNiruktaOverlay(),
              buildNiruktaOverlay(null),
              buildNiruktaOverlay({ generatedPadas: [null, 'bad'] }),
              buildNiruktaOverlay({ rulefire: {}, sutraDependency: 'bad', semanticOverlay: null }),
            ];
            console.log(JSON.stringify(outputs.map((item) => ({
              status: item.status,
              candidates: item.candidates.length,
              unresolved: item.unresolved.length,
              warnings: item.diagnostics.warnings.length,
            }))));
            """))
        self.assertEqual([item["status"] for item in result], ["ready", "ready", "ready", "ready"])


if __name__ == "__main__":
    unittest.main()

