import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-audit-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-audit-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-audit-renderer.js"
)


class RuntimeAuditLayerTests(unittest.TestCase):

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

    def test_audit_is_review_only(self):
        data = self.run_json("""
const {
createRuntimeAuditRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-audit-engine.js"
);

console.log(JSON.stringify(
createRuntimeAuditRecord({
replayId:"r1",
replayMode:"inspection-only",
replayAllowed:true,
sourceHash:"h1",
targetHash:"h2",
stepCount:1,
warnings:["blocked"]
})
));
""")
        self.assertEqual(data["auditStatus"], "review-only")
        self.assertEqual(data["state"], "REVIEW_ONLY")
        self.assertFalse(data["replayAllowed"])

    def test_audit_findings_present(self):
        data = self.run_json("""
const {
deriveRuntimeAuditFindings
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-audit-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeAuditFindings({
stepCount:1,
warnings:["blocked"]
})
));
""")
        self.assertIn("execution-blocked", data)
        self.assertIn("mutation-blocked", data)
        self.assertIn("canonical-write-blocked", data)
        self.assertIn("runtime-transition-detected", data)
        self.assertIn("warnings-present", data)

    def test_audit_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeAuditRecord,
inspectRuntimeAuditRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-audit-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeAuditRecord(
createRuntimeAuditRecord({
stepCount:1,
warnings:["blocked"]
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
        self.assertFalse(data["replayAllowed"])

    def test_renderer_escapes_html(self):
        data = self.run_json("""
const {
renderRuntimeAuditPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-audit-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeAuditPanel({
auditStatus:"<review>",
replayMode:"<script>",
sourceHash:"h1",
targetHash:"h2",
stepCount:1,
findings:["<finding>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;review&gt;", data["body"])
        self.assertIn("&lt;script&gt;", data["body"])
        self.assertIn("&lt;finding&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<script>", data["body"])


if __name__ == "__main__":
    unittest.main()