import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-publication-registry.js"
)

class RuntimePublicationRegistryTests(unittest.TestCase):

    def run_json(self,script):
        r=subprocess.run(
            ["node","-e",script],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(r.stdout)

    def test_syntax(self):
        subprocess.run(["node","--check",FILE],check=True)

    def test_registry(self):
        data=self.run_json("""
const {
createRuntimePublicationRegistry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-registry.js"
);
console.log(JSON.stringify(createRuntimePublicationRegistry({
entries:[{id:"r1"},{id:"r2"}]
})));
""")
        self.assertEqual(len(data["entries"]),2)
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_registry_entry_blocks_writes(self):
        data=self.run_json("""
const {
normalizeRegistryEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-registry.js"
);
console.log(JSON.stringify(normalizeRegistryEntry({id:"r1"},0)));
""")
        self.assertTrue(data["registered"])
        self.assertFalse(data["canonicalWriteEnabled"])
        self.assertTrue(data["diagnostics"]["canonicalWriteBlocked"])

    def test_diagnostics(self):
        data=self.run_json("""
const {
createRuntimePublicationRegistry,
getRuntimePublicationRegistryDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-publication-registry.js"
);
console.log(JSON.stringify(
getRuntimePublicationRegistryDiagnostics(
createRuntimePublicationRegistry({})
)
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["canonicalWriteBlocked"])

if __name__=="__main__":
    unittest.main()