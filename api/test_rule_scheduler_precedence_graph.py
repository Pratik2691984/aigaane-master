import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRECEDENCE_MAP = ROOT / "ui" / "tabs" / "sanskrit" / "rule-scheduler" / "rule-precedence-map.js"
SCHEDULER_ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "rule-scheduler" / "rule-scheduler-engine.js"


class TestRuleSchedulerPrecedenceGraph(unittest.TestCase):
    def test_rule_scheduler_files_are_syntax_valid(self):
        for path in (PRECEDENCE_MAP, SCHEDULER_ENGINE):
            result = subprocess.run(
                ["node", "--check", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_precedence_graph_export_is_runtime_safe_and_normalized(self):
        script = """
const scheduler = require("./ui/tabs/sanskrit/rule-scheduler/rule-scheduler-engine.js");
const result = scheduler.buildRulePrecedenceGraphExport();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "sanskrit-rule-precedence.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contracts"]["deterministic"])
        self.assertTrue(payload["contracts"]["inspectionOnly"])
        self.assertTrue(payload["contracts"]["nonPerformative"])
        self.assertTrue(payload["contracts"]["runtimeIsolated"])
        self.assertTrue(payload["contracts"]["immutableSafe"])
        self.assertTrue(payload["contracts"]["replaySafe"])
        self.assertTrue(payload["contracts"]["staticPreviewCompatible"])
        self.assertEqual(payload["relationCount"], 5)

        self.assertTrue(payload["diagnostics"]["normalized"])
        self.assertTrue(payload["diagnostics"]["deterministic"])
        self.assertTrue(payload["diagnostics"]["runtimeSafe"])
        self.assertTrue(payload["diagnostics"]["replaySafe"])
        self.assertTrue(payload["diagnostics"]["mutationFree"])
        self.assertTrue(payload["diagnostics"]["schedulerOnly"])

        for relation in payload["relations"]:
            self.assertIsInstance(relation["id"], str)
            self.assertIsInstance(relation["type"], str)
            self.assertTrue(relation["sutra"] is None or isinstance(relation["sutra"], str))
            self.assertIsInstance(relation["label"], str)
            self.assertIsInstance(relation["summary"], str)
            self.assertIsInstance(relation["priority"], (int, float))
            self.assertIsInstance(relation["diagnostics"], list)

    def test_scheduler_orders_rules_deterministically_by_precedence_priority(self):
        script = """
const scheduler = require("./ui/tabs/sanskrit/rule-scheduler/rule-scheduler-engine.js");
const result = scheduler.scheduleRulesByPrecedence([
  { id: "rule.low", precedencePriority: 10 },
  { id: "rule.high", precedencePriority: 100 },
  { id: "rule.same-a", precedencePriority: 50 },
  { id: "rule.same-b", precedencePriority: 50 }
]);
console.log(JSON.stringify(result.map((rule) => rule.id)));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        ordered_ids = json.loads(result.stdout)

        self.assertEqual(
            ordered_ids,
            ["rule.high", "rule.same-a", "rule.same-b", "rule.low"],
        )

    def test_rule_scheduler_diagnostics_contracts_are_satisfied(self):
        script = """
const scheduler = require("./ui/tabs/sanskrit/rule-scheduler/rule-scheduler-engine.js");
const result = scheduler.getRuleSchedulerDiagnostics();
console.log(JSON.stringify(result));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["schemaVersion"], "sanskrit-rule-precedence.v1")
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["contractsSatisfied"])
        self.assertEqual(payload["relationCount"], 5)


if __name__ == "__main__":
    unittest.main()