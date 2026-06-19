import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_engine():
    path = ROOT / "api" / "engines" / "corpus_pipeline.py"
    spec = importlib.util.spec_from_file_location("corpus_pipeline", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["corpus_pipeline"] = module
    spec.loader.exec_module(module)
    return module


class Phase11CorpusSystemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run(["python", "scripts/build_real_corpus_raw_batches.py"], cwd=ROOT, check=True)
        cls.engine = load_engine()
        cls.status = cls.engine.run_phase11_pipeline()

    def test_pipeline_valid(self):
        self.assertTrue(self.status["valid"])
        self.assertEqual(self.status["phase"], "11")

    def test_source_registry(self):
        manifest = json.loads((ROOT / "data" / "sanskrit" / "corpus-sources" / "source_manifest.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["phase"], "11A")
        self.assertGreaterEqual(len(manifest["sources"]), 3)

    def test_normalized_records(self):
        payload = json.loads((ROOT / "data" / "sanskrit" / "corpus-staging" / "normalized_records.v1.json").read_text(encoding="utf-8"))
        self.assertGreater(payload["recordCount"], 0)
        sample = payload["records"][0]
        self.assertIn("recordId", sample)
        self.assertIn("normalized", sample)

    def test_canonical_registry_read_only(self):
        dhatu = json.loads((ROOT / "data" / "sanskrit" / "canonical" / "dhatu" / "dhatu_registry.v1.json").read_text(encoding="utf-8"))
        self.assertTrue(dhatu["readOnly"])
        self.assertGreater(dhatu["recordCount"], 0)

    def test_corpus_index(self):
        index = json.loads((ROOT / "data" / "sanskrit" / "index" / "corpus_index.v1.json").read_text(encoding="utf-8"))
        self.assertGreater(index["recordCount"], 0)
        self.assertIn("lookup", index)
        self.assertIn("prefixIndex", index)

    def test_derivation_hooks(self):
        hooks = json.loads((ROOT / "data" / "sanskrit" / "corpus-staging" / "derivation_hooks.v1.json").read_text(encoding="utf-8"))
        self.assertGreater(hooks["hookCount"], 0)
        self.assertIn("sandhi", hooks["hooks"][0])

    def test_search_api(self):
        from sanskrit_corpus_api import get_corpus_by_type, search_corpus

        search = search_corpus(query="भू", corpus_type="dhatu", limit=5)
        self.assertTrue(search["valid"])
        dhatu = get_corpus_by_type("dhatu", limit=5)
        self.assertTrue(dhatu["valid"])
        self.assertGreaterEqual(dhatu["count"], 1)

    def test_corpus_browser_js(self):
        result = subprocess.run(
            ["node", "-e", """
const { buildCorpusBrowserState } = require("./ui/tabs/sanskrit/corpus/corpus-browser-engine.js");
const { renderCorpusBrowserPanel } = require("./ui/tabs/sanskrit/corpus/corpus-browser-renderer.js");
const state = buildCorpusBrowserState({ recordCount: 2000 }, "Search");
const panel = renderCorpusBrowserPanel(state, { valid: true, count: 1, results: [{ recordId: "01.0001", type: "dhatu", text: "भू" }] });
console.log(JSON.stringify({ section: state.section, hasBody: Boolean(panel.body) }));
"""],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["section"], "Search")
        self.assertTrue(data["hasBody"])


if __name__ == "__main__":
    unittest.main()