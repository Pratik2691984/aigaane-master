import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_MANIFEST = ROOT / "raw" / "corpus" / "manifest.v1.json"
STAGING_MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"
PIPELINE_REPORT = ROOT / "data" / "sanskrit" / "corpus-staging" / "real_corpus_pipeline_report.v1.json"


class RealCorpusLoadingTests(unittest.TestCase):

    def test_build_raw_batches_meets_targets(self):
        result = subprocess.run(
            ["python", "scripts/build_real_corpus_raw_batches.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["counts"]["dhatu"], 1400)
        self.assertEqual(data["counts"]["sutra"], 400)
        self.assertEqual(data["counts"]["stotra"], 200)
        self.assertEqual(data["counts"]["total"], 2000)
        self.assertGreater(data["seedDhatuCount"], 0)

        manifest = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["phase"], "11")
        self.assertEqual(manifest["counts"]["total"], 2000)

    def test_load_real_corpus_from_raw_preview(self):
        subprocess.run(
            ["python", "scripts/build_real_corpus_raw_batches.py"],
            check=True,
        )
        result = subprocess.run(
            ["python", "scripts/load_real_corpus_from_raw.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertTrue(data["dryRun"])
        self.assertFalse(data["written"])
        self.assertEqual(data["recordCount"], 2000)
        self.assertEqual(data["typeCounts"]["dhatu"], 1400)
        self.assertEqual(data["typeCounts"]["sutra"], 400)
        self.assertEqual(data["typeCounts"]["stotra"], 200)

    def test_pipeline_end_to_end(self):
        result = subprocess.run(
            ["python", "scripts/run_real_corpus_loading_pipeline.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["phase"], "11")
        self.assertEqual(
            data["pipeline"],
            [
                "raw",
                "corpus-staging",
                "validation",
                "provenance",
                "preview",
                "approval",
                "certification",
                "canonical",
            ],
        )
        self.assertEqual(data["recordCount"], 2000)
        self.assertEqual(data["canonicalStatus"], "canonical-preview-ready")

        manifest = json.loads(STAGING_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["metadata"]["phase"], "11")
        self.assertEqual(manifest["metadata"]["recordCount"], 2000)
        self.assertFalse(manifest["canonicalWriteAllowed"])
        self.assertEqual(manifest["mode"], "preview-only")

        report = json.loads(PIPELINE_REPORT.read_text(encoding="utf-8"))
        self.assertTrue(report["valid"])


if __name__ == "__main__":
    unittest.main()