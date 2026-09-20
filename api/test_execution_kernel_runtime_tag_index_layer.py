import json
import subprocess
import unittest

FILE=(
"ui/tabs/sanskrit/execution-kernel/"
"execution-kernel-runtime-tag-index.js"
)

class RuntimeTagIndexTests(unittest.TestCase):

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
        subprocess.run(
            ["node","--check",FILE],
            check=True
        )

    def test_index_entries(self):
        data=self.run_json("""
const {
createRuntimeTagIndex
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-index.js"
);

console.log(JSON.stringify(
createRuntimeTagIndex({
entries:[
{id:"t1"},
{id:"t2"}
]
})
));
""")
        self.assertEqual(len(data["entries"]),2)
        self.assertFalse(data["capabilities"]["execute"])
        self.assertFalse(data["capabilities"]["canonicalWrite"])

    def test_entry_blocks_mutation_and_canonical_write(self):
        data=self.run_json("""
const {
normalizeTagIndexEntry
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-index.js"
);

console.log(JSON.stringify(
normalizeTagIndexEntry({id:"t1"},0)
));
""")
        self.assertFalse(data["mutationEnabled"])
        self.assertFalse(data["canonicalWriteEnabled"])
        self.assertTrue(data["diagnostics"]["canonicalWriteBlocked"])

    def test_diagnostics(self):
        data=self.run_json("""
const {
createRuntimeTagIndex,
getRuntimeTagIndexDiagnostics
}=require(
"./ui/tabs/sanskrit/execution-kernel/execution-kernel-runtime-tag-index.js"
);

console.log(JSON.stringify(
getRuntimeTagIndexDiagnostics(
createRuntimeTagIndex({})
)
));
""")
        self.assertTrue(data["ready"])
        self.assertTrue(data["canonicalWriteBlocked"])

if __name__=="__main__":
    unittest.main()