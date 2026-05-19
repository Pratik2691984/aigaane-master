import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kernel_api import app


class MorphologyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_meta_returns_nouns_and_dhatus(self):
        response = self.client.get("/api/v3/morphology/meta")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("nouns", payload)
        self.assertIn("dhatus", payload)
        self.assertTrue(any(item["stem"] == "\u0930\u093e\u092e" for item in payload["nouns"]))
        self.assertTrue(any(item["dhatu"] == "\u092d\u0942" for item in payload["dhatus"]))

    def test_rama_nominative_singular(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0930\u093e\u092e\u0903")

    def test_rama_accusative_singular(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0930\u093e\u092e", "case": "accusative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0930\u093e\u092e\u092e\u094d")

    def assert_hari_form(self, case, number, expected):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0939\u0930\u093f", "case": case, "number": number},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], expected)
        self.assertEqual(payload["metadata"]["declension"], "masculine_i")
        self.assertEqual(payload["metadata"]["paradigm"], "kavi_masculine")
        self.assertIn("derivation_path", payload)

    def test_hari_nominative_singular(self):
        self.assert_hari_form("nominative", "singular", "\u0939\u0930\u093f\u0903")

    def test_hari_accusative_singular(self):
        self.assert_hari_form("accusative", "singular", "\u0939\u0930\u093f\u092e\u094d")

    def test_hari_instrumental_singular(self):
        self.assert_hari_form("instrumental", "singular", "\u0939\u0930\u093f\u0923\u093e")

    def test_hari_dative_singular(self):
        self.assert_hari_form("dative", "singular", "\u0939\u0930\u092f\u0947")

    def test_hari_genitive_singular(self):
        self.assert_hari_form("genitive", "singular", "\u0939\u0930\u0947\u0903")

    def test_hari_locative_singular(self):
        self.assert_hari_form("locative", "singular", "\u0939\u0930\u094c")

    def test_hari_nominative_plural(self):
        self.assert_hari_form("nominative", "plural", "\u0939\u0930\u092f\u0903")

    def test_hari_accusative_plural(self):
        self.assert_hari_form("accusative", "plural", "\u0939\u0930\u0940\u0928\u094d")

    def assert_nadi_form(self, case, number, expected):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0928\u0926\u0940", "case": case, "number": number},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], expected)
        self.assertEqual(payload["metadata"]["declension"], "feminine_ii")
        self.assertEqual(payload["metadata"]["paradigm"], "nadi_feminine")
        self.assertEqual(payload["metadata"]["ending"], "\u012b")
        self.assertIn("derivation_path", payload)

    def test_nadi_nominative_singular(self):
        self.assert_nadi_form("nominative", "singular", "\u0928\u0926\u0940")

    def test_nadi_accusative_singular(self):
        self.assert_nadi_form("accusative", "singular", "\u0928\u0926\u0940\u092e\u094d")

    def test_nadi_instrumental_singular(self):
        self.assert_nadi_form("instrumental", "singular", "\u0928\u0926\u094d\u092f\u093e")

    def test_nadi_dative_singular(self):
        self.assert_nadi_form("dative", "singular", "\u0928\u0926\u094d\u092f\u0948")

    def test_nadi_genitive_singular(self):
        self.assert_nadi_form("genitive", "singular", "\u0928\u0926\u094d\u092f\u093e\u0903")

    def test_nadi_locative_singular(self):
        self.assert_nadi_form("locative", "singular", "\u0928\u0926\u094d\u092f\u093e\u092e\u094d")

    def test_nadi_nominative_plural(self):
        self.assert_nadi_form("nominative", "plural", "\u0928\u0926\u094d\u092f\u0903")

    def test_nadi_accusative_plural(self):
        self.assert_nadi_form("accusative", "plural", "\u0928\u0926\u0940\u0903")

    def assert_phala_form(self, case, number, expected):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u092b\u0932", "case": case, "number": number},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], expected)
        self.assertEqual(payload["metadata"]["gender"], "neuter")
        self.assertEqual(payload["metadata"]["declension"], "neuter_a")
        self.assertEqual(payload["metadata"]["paradigm"], "phala_neuter")
        self.assertIn("derivation_path", payload)

    def test_phala_nominative_singular(self):
        self.assert_phala_form("nominative", "singular", "\u092b\u0932\u092e\u094d")

    def test_phala_accusative_singular(self):
        self.assert_phala_form("accusative", "singular", "\u092b\u0932\u092e\u094d")

    def test_phala_instrumental_singular(self):
        self.assert_phala_form("instrumental", "singular", "\u092b\u0932\u0947\u0928")

    def test_phala_dative_singular(self):
        self.assert_phala_form("dative", "singular", "\u092b\u0932\u093e\u092f")

    def test_phala_genitive_singular(self):
        self.assert_phala_form("genitive", "singular", "\u092b\u0932\u0938\u094d\u092f")

    def test_phala_locative_singular(self):
        self.assert_phala_form("locative", "singular", "\u092b\u0932\u0947")

    def test_phala_nominative_plural(self):
        self.assert_phala_form("nominative", "plural", "\u092b\u0932\u093e\u0928\u093f")

    def test_phala_accusative_plural(self):
        self.assert_phala_form("accusative", "plural", "\u092b\u0932\u093e\u0928\u093f")

    def test_bhu_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092d\u0935\u0924\u093f")

    def assert_bhu_lat_form(self, person, number, expected):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": person, "number": number},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["form"], expected)
        self.assertEqual(payload["metadata"]["pada"], "parasmaipada")
        self.assertEqual(payload["metadata"]["model_stem"], "\u092d\u0935")
        self.assertIn("derivation_path", payload)

    def test_bhu_lat_3_1(self):
        self.assert_bhu_lat_form("3", "1", "\u092d\u0935\u0924\u093f")

    def test_bhu_lat_3_2(self):
        self.assert_bhu_lat_form("3", "2", "\u092d\u0935\u0924\u0903")

    def test_bhu_lat_3_3(self):
        self.assert_bhu_lat_form("3", "3", "\u092d\u0935\u0928\u094d\u0924\u093f")

    def test_bhu_lat_2_1(self):
        self.assert_bhu_lat_form("2", "1", "\u092d\u0935\u0938\u093f")

    def test_bhu_lat_2_2(self):
        self.assert_bhu_lat_form("2", "2", "\u092d\u0935\u0925\u0903")

    def test_bhu_lat_2_3(self):
        self.assert_bhu_lat_form("2", "3", "\u092d\u0935\u0925")

    def test_bhu_lat_1_1(self):
        self.assert_bhu_lat_form("1", "1", "\u092d\u0935\u093e\u092e\u093f")

    def test_bhu_lat_1_2(self):
        self.assert_bhu_lat_form("1", "2", "\u092d\u0935\u093e\u0935\u0903")

    def test_bhu_lat_1_3(self):
        self.assert_bhu_lat_form("1", "3", "\u092d\u0935\u093e\u092e\u0903")

    def test_path_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092a\u0920\u094d", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092a\u0920\u0924\u093f")

    def test_gam_lat_prathama_ekavacana(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u0917\u092e\u094d", "lakara": "la\u1e6d", "person": "3", "number": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u0917\u091a\u094d\u091b\u0924\u093f")

    def test_named_lat_prathama_ekavacana_remains_supported(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "lat", "person": "prathama", "number": "ekavacana"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["form"], "\u092d\u0935\u0924\u093f")

    def test_invalid_stem_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/noun/inflect",
            json={"stem": "\u0926\u0947\u0935", "case": "nominative", "number": "singular"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_invalid_dhatu_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u0915\u0943", "lakara": "lat", "person": "prathama", "number": "ekavacana"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_unsupported_verb_slot_returns_structured_morphology_error(self):
        response = self.client.post(
            "/api/v3/morphology/verb/conjugate",
            json={"dhatu": "\u092d\u0942", "lakara": "la\u1e6d", "person": "4", "number": "1"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "morphology_error")

    def test_existing_chandas_endpoint_still_passes(self):
        response = self.client.post("/api/v3/analyze", json={"input_text": "\u0930\u093e\u092e\u0903 \u0905\u0935\u0926\u0924\u094d"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["phonological_syllables"])

    def test_existing_sandhi_endpoint_still_passes(self):
        response = self.client.post(
            "/api/v3/sandhi",
            json={"word1": "\u0930\u093e\u092e", "word2": "\u0905\u0938\u094d\u0924\u093f"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["merged"], "\u0930\u093e\u092e\u093e\u0938\u094d\u0924\u093f")


if __name__ == "__main__":
    unittest.main()
