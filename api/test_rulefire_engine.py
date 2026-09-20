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


class RulefireEngineTests(unittest.TestCase):
    def test_rule_registry_includes_required_categories(self):
        result = run_node_json(textwrap.dedent("""
            import { groupRulefireRulesByCategory } from './ui/tabs/sanskrit/rulefire/rulefire-map.js';
            const groups = groupRulefireRulesByCategory();
            console.log(JSON.stringify(Object.fromEntries(
              Object.entries(groups).map(([key, value]) => [key, value.length])
            )));
            """))
        self.assertGreaterEqual(result["sandhi"], 4)
        self.assertGreaterEqual(result["subanta"], 4)
        self.assertGreaterEqual(result["tinanta"], 3)
        self.assertGreaterEqual(result["prakriya"], 5)

    def test_priority_ordering_is_deterministic(self):
        result = run_node_json(textwrap.dedent("""
            import { listRulefireRules, sortRulefireRulesByPriority } from './ui/tabs/sanskrit/rulefire/rulefire-map.js';
            const ordered = sortRulefireRulesByPriority(listRulefireRules()).map((rule) => rule.priority);
            const sorted = [...ordered].sort((a, b) => a - b);
            console.log(JSON.stringify({ ordered, stable: JSON.stringify(ordered) === JSON.stringify(sorted) }));
            """))
        self.assertTrue(result["stable"])

    def test_explicit_eligibility_match_fires_rule(self):
        result = run_node_json(textwrap.dedent("""
            import { getRulefireRule } from './ui/tabs/sanskrit/rulefire/rulefire-map.js';
            import { evaluateRuleEligibility, fireRule } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const state = { morphology: { nounInputs: [{ stemClass: 'a-stem', linga: 'masculine', vibhakti: 'prathama', vacana: 'eka' }] } };
            const rule = getRulefireRule('subanta_a_masculine_prathama_eka');
            const eligibility = evaluateRuleEligibility(rule, state);
            const fired = fireRule(rule, state);
            console.log(JSON.stringify({ eligible: eligibility.eligible, fired: fired.fired, generatedForms: fired.after.generatedForms }));
            """))
        self.assertTrue(result["eligible"])
        self.assertTrue(result["fired"])
        self.assertTrue(result["generatedForms"])

    def test_unsupported_input_does_not_fire_hidden_rules(self):
        result = run_node_json(textwrap.dedent("""
            import { executeRulefire } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const output = executeRulefire({ initialState: { text: 'unsupported only' }, stages: [] });
            console.log(JSON.stringify(output));
            """))
        self.assertEqual(result["diagnostics"]["firedCount"], 0)
        self.assertEqual(result["diagnostics"]["unresolvedCount"], 1)

    def test_snapshot_isolation_no_initial_state_mutation(self):
        result = run_node_json(textwrap.dedent("""
            import { executeRulefire } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const input = {
              initialState: {
                morphology: { verbInput: { dhatu: 'gam', lakara: 'lat', purusha: 'prathama', vacana: 'eka' } },
              },
              enabledCategories: ['tinanta'],
            };
            const before = JSON.stringify(input);
            const output = executeRulefire(input);
            console.log(JSON.stringify({
              same: before === JSON.stringify(input),
              snapshots: output.snapshots.length,
              fired: output.firedRules.length,
            }));
            """))
        self.assertTrue(result["same"])
        self.assertGreater(result["snapshots"], 1)
        self.assertEqual(result["fired"], 1)

    def test_same_input_returns_identical_rulefire_output(self):
        result = run_node_json(textwrap.dedent("""
            import { executeRulefire } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const input = {
              initialState: {
                text: 'a i',
                sandhi: [{ boundary: 'a+i' }],
                morphology: { verbInput: { dhatu: 'gam', lakara: 'lat', purusha: 'prathama', vacana: 'eka' } },
              },
              enabledCategories: ['sandhi', 'tinanta'],
            };
            const first = executeRulefire(input);
            const second = executeRulefire(input);
            console.log(JSON.stringify({ stable: JSON.stringify(first) === JSON.stringify(second), first, second }));
            """))
        self.assertTrue(result["stable"])
        self.assertEqual(result["first"], result["second"])

    def test_graph_projection_has_rule_nodes_and_edges(self):
        result = run_node_json(textwrap.dedent("""
            import { executeRulefire } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const output = executeRulefire({
              initialState: {
                text: 'a i',
                sandhi: [{ boundary: 'a+i' }],
                morphology: { verbInput: { dhatu: 'gam', lakara: 'lat', purusha: 'prathama', vacana: 'eka' } },
              },
              enabledCategories: ['sandhi', 'tinanta'],
            });
            console.log(JSON.stringify({
              nodes: output.graphProjection.nodes,
              edges: output.graphProjection.edges,
            }));
            """))
        self.assertGreaterEqual(len(result["nodes"]), 2)
        self.assertGreaterEqual(len(result["edges"]), 1)
        self.assertTrue(all(node["type"] == "rulefireRule" for node in result["nodes"]))

    def test_partial_input_safety(self):
        result = run_node_json(textwrap.dedent("""
            import { executeRulefire } from './ui/tabs/sanskrit/rulefire/rulefire-engine.js';
            const outputs = [
              executeRulefire(),
              executeRulefire(null),
              executeRulefire({ initialState: 'bad' }),
              executeRulefire({ stages: [], enabledCategories: ['unknown'] }),
            ];
            console.log(JSON.stringify(outputs.map((item) => ({
              status: item.status,
              firedCount: item.diagnostics.firedCount,
              warnings: item.diagnostics.warnings.length,
            }))));
            """))
        self.assertEqual([item["status"] for item in result], ["ready", "ready", "ready", "ready"])
        self.assertTrue(all(item["warnings"] >= 1 for item in result))

    def test_backend_analyze_payload_keeps_unified_graph_and_rulefire(self):
        client = TestClient(app)
        response = client.post("/api/v3/analyze", json={"input_text": "agnim ile"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("metadata", payload["prakriya_graph"])
        self.assertEqual(payload["rulefire"]["status"], "ready")
        self.assertEqual(payload["rulefire"]["executionType"], "deterministic-rulefire")


if __name__ == "__main__":
    unittest.main()

