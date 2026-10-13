import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.kernel_api import app


class TestLexicon(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_lookup_rama(self):
        r = self.client.get("/api/v3/lexicon/lookup", params={"q": "rāma"})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertTrue(data["found"])
        self.assertGreater(data["count"], 0)

    def test_lookup_bhavati(self):
        r = self.client.get("/api/v3/lexicon/lookup", params={"q": "bhavati"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()["found"])

    def test_lookup_unknown_word(self):
        r = self.client.get("/api/v3/lexicon/lookup", params={"q": "xyzzy"})
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertFalse(data["found"])
        self.assertEqual(data["count"], 0)

    def test_lookup_surface_form(self):
        r = self.client.get("/api/v3/lexicon/lookup", params={"q": "rāmaḥ"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertFalse(r.json()["found"])

    def test_exists_rama(self):
        r = self.client.get("/api/v3/lexicon/exists", params={"q": "rāma"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertTrue(r.json()["exists"])

    def test_exists_xyzzy(self):
        r = self.client.get("/api/v3/lexicon/exists", params={"q": "xyzzy"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertFalse(r.json()["exists"])

    def test_stats(self):
        r = self.client.get("/api/v3/lexicon/stats")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertGreater(r.json()["dhatu_count"], 1000)


if __name__ == "__main__":
    unittest.main()