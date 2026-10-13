import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.kernel_api import app


class TestSandhiSplit(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_split_ramashca(self):
        r = self.client.post(
            "/api/v3/sandhi/split",
            json={"text": "rāmaśca"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertGreater(data["count"], 0)
        first = data["splits"][0]
        self.assertEqual(first["first"], "rāma")
        self.assertEqual(first["second"], "śca")

    def test_split_tacchrutva(self):
        r = self.client.post(
            "/api/v3/sandhi/split",
            json={"text": "tacchrutvā"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        first = data["splits"][0]
        self.assertEqual(first["first"], "tat")

    def test_split_devanagari_input(self):
        r = self.client.post(
            "/api/v3/sandhi/split",
            json={"text": "रामश्च", "script": "devanagari"},
        )
        self.assertEqual(r.status_code, 200, r.text)
        data = r.json()
        self.assertGreater(data["count"], 0)

    def test_split_short_input_returns_422(self):
        r = self.client.post(
            "/api/v3/sandhi/split",
            json={"text": "a"},
        )
        self.assertEqual(r.status_code, 422)

    def test_split_unknown_script_returns_422(self):
        r = self.client.post(
            "/api/v3/sandhi/split",
            json={"text": "rāmaśca", "script": "klingon"},
        )
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()