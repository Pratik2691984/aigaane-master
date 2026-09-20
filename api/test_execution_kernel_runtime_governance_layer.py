import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-governance-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-governance-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-governance-renderer.js"
)


class RuntimeGovernanceLayerTests(unittest.TestCase):

    def run_json(self, script):
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(result.stdout)

    def test_syntax(self):
        subprocess.run(["node", "--check", MAP_FILE], check=True)
        subprocess.run(["node", "--check", ENGINE_FILE], check=True)
        subprocess.run(["node", "--check", RENDERER_FILE], check=True)

    def test_governance_approves_inspection_only(self):
        data = self.run_json("""
const {
createRuntimeGovernanceDecision
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-governance-engine.js"
);

console.log(JSON.stringify(
createRuntimeGovernanceDecision({
auditId:"a1",
auditStatus:"review-only",
findings:["runtime-transition-detected"],
warnings:["review required"]
})
));
""")
        self.assertEqual(data["governanceStatus"], "inspection-approved")
        self.assertEqual(data["decision"], "approve-inspection-only")
        self.assertEqual(data["state"], "APPROVED_FOR_INSPECTION")
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_governance_controls_present(self):
        data = self.run_json("""
const {
deriveRuntimeGovernanceControls
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-governance-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeGovernanceControls({
findings:[
"runtime-transition-detected",
"warnings-present"
]
})
));
""")
        self.assertIn("execution-denied", data)
        self.assertIn("mutation-denied", data)
        self.assertIn("publication-denied", data)
        self.assertIn("rollback-denied", data)
        self.assertIn("canonical-write-denied", data)
        self.assertIn("inspection-only-approved", data)
        self.assertIn("runtime-transition-review-required", data)
        self.assertIn("warning-review-required", data)

    def test_governance_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeGovernanceDecision,
inspectRuntimeGovernanceDecision
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-governance-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeGovernanceDecision(
createRuntimeGovernanceDecision({
findings:["runtime-transition-detected"],
warnings:["review"]
})
)
));
""")
        self.assertTrue(data["readOnly"])
        self.assertTrue(data["executionBlocked"])
        self.assertTrue(data["mutationBlocked"])
        self.assertTrue(data["publicationBlocked"])
        self.assertTrue(data["rollbackBlocked"])
        self.assertTrue(data["canonicalWriteBlocked"])
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeGovernancePanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-governance-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeGovernancePanel({
governanceStatus:"<approved>",
decision:"<inspect>",
findingCount:1,
warningCount:1,
controls:["<control>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;approved&gt;", data["body"])
        self.assertIn("&lt;inspect&gt;", data["body"])
        self.assertIn("&lt;control&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<approved>", data["body"])


if __name__ == "__main__":
    unittest.main()