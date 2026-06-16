import json
import subprocess
import unittest

MAP_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-certification-map.js"
)

ENGINE_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-certification-engine.js"
)

RENDERER_FILE = (
    "ui/tabs/sanskrit/execution-kernel/"
    "execution-kernel-runtime-certification-renderer.js"
)


class RuntimeCertificationLayerTests(unittest.TestCase):

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

    def test_certification_inspection_only(self):
        data = self.run_json("""
const {
createRuntimeCertificationRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-certification-engine.js"
);

console.log(JSON.stringify(
createRuntimeCertificationRecord({
governanceId:"g1",
governanceStatus:"inspection-approved",
decision:"approve-inspection-only",
controls:["runtime-transition-review-required"],
warnings:["review required"],
findingCount:1
})
));
""")
        self.assertEqual(data["certificationStatus"], "certified-for-inspection")
        self.assertEqual(data["certificate"], "controlled-runtime-inspection-only")
        self.assertEqual(data["state"], "CERTIFIED_FOR_INSPECTION")
        self.assertFalse(data["executionAllowed"])
        self.assertFalse(data["canonicalWriteAllowed"])

    def test_certification_attestations_present(self):
        data = self.run_json("""
const {
deriveRuntimeCertificationAttestations
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-certification-engine.js"
);

console.log(JSON.stringify(
deriveRuntimeCertificationAttestations({
controls:[
"runtime-transition-review-required",
"warning-review-required"
]
})
));
""")
        self.assertIn("inspection-path-certified", data)
        self.assertIn("execution-denial-certified", data)
        self.assertIn("mutation-denial-certified", data)
        self.assertIn("publication-denial-certified", data)
        self.assertIn("rollback-denial-certified", data)
        self.assertIn("canonical-write-denial-certified", data)
        self.assertIn("runtime-transition-review-certified", data)
        self.assertIn("warning-review-certified", data)

    def test_certification_is_read_only(self):
        data = self.run_json("""
const {
createRuntimeCertificationRecord,
inspectRuntimeCertificationRecord
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-certification-engine.js"
);

console.log(JSON.stringify(
inspectRuntimeCertificationRecord(
createRuntimeCertificationRecord({
controls:["runtime-transition-review-required"],
warnings:["review"],
findingCount:1
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
renderRuntimeCertificationPanel
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-certification-renderer.js"
);

console.log(JSON.stringify(
renderRuntimeCertificationPanel({
certificationStatus:"<certified>",
certificate:"<certificate>",
governanceStatus:"<approved>",
decision:"<inspect>",
controlCount:1,
findingCount:1,
warningCount:1,
attestations:["<attestation>"],
warnings:["<warning>"]
})
));
""")
        self.assertIn("&lt;certified&gt;", data["body"])
        self.assertIn("&lt;certificate&gt;", data["body"])
        self.assertIn("&lt;approved&gt;", data["body"])
        self.assertIn("&lt;inspect&gt;", data["body"])
        self.assertIn("&lt;attestation&gt;", data["body"])
        self.assertIn("&lt;warning&gt;", data["body"])
        self.assertNotIn("<certified>", data["body"])


if __name__ == "__main__":
    unittest.main()