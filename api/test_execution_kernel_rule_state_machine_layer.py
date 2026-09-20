import json
import subprocess
import unittest

FILE = "ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-state-machine.js"

class RuleStateMachineTests(unittest.TestCase):
    def run_json(self, script):
        r = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(["node", "--check", FILE], check=True)

    def test_state_machine_builds_blocked_states(self):
        data = self.run_json("""
const { createRuleStateMachine } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-state-machine.js");
console.log(JSON.stringify(createRuleStateMachine({rules:[{id:"r1"},{id:"r2"}]})));
""")
        self.assertEqual(data["schemaVersion"], "sanskrit-rule-state-machine.v1")
        self.assertEqual(len(data["states"]), 2)
        self.assertFalse(data["capabilities"]["transition"])
        self.assertFalse(data["capabilities"]["execute"])
        self.assertTrue(data["diagnostics"]["transitionBlocked"])

    def test_states_remain_unauthorized_and_unexecuted(self):
        data = self.run_json("""
const { createRuleStateMachine } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-state-machine.js");
console.log(JSON.stringify(createRuleStateMachine({rules:[{id:"r1"}]})));
""")
        state = data["states"][0]
        self.assertFalse(state["authorized"])
        self.assertFalse(state["executed"])
        self.assertFalse(state["mutated"])
        self.assertFalse(state["transitionAllowed"])

    def test_diagnostics(self):
        data = self.run_json("""
const { createRuleStateMachine, getRuleStateMachineDiagnostics } = require("./ui/tabs/sanskrit/execution-kernel/execution-kernel-rule-state-machine.js");
console.log(JSON.stringify(getRuleStateMachineDiagnostics(createRuleStateMachine({rules:[{id:"r1"}]}))));
""")
        self.assertTrue(data["ready"])
        self.assertEqual(data["stateCount"], 1)
        self.assertTrue(data["transitionBlocked"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationFree"])

if __name__ == "__main__":
    unittest.main()