"""
tests/test_subanta.py
Validation of the 4 core Subanta paradigms:
- Rama (a_masc)
- Ramaa (aa_fem)
- Hari (i_masc)
- Guru (u_masc)
"""
import unittest
from engine.morphology.subanta import inflect_stem

class TestSubantaEngine(unittest.TestCase):

    def test_a_masc_rama(self):
        # 1.1 Ramah
        res = inflect_stem("राम", "nominative", "singular")
        self.assertEqual(res["form"], "रामः")
        self.assertIn("8.3.15", res["sutras"])

        # 3.1 Ramena (natva 8.4.2)
        res = inflect_stem("राम", "trtiya", "eka")
        self.assertEqual(res["form"], "रामेण")

        # 6.3 Ramanam (natva 8.4.2)
        res = inflect_stem("राम", "sasthi", "bahu")
        self.assertEqual(res["form"], "रामाणाम्")

    def test_aa_fem_ramaa(self):
        # 1.1 Rama
        res = inflect_stem("रमा", "prathama", "eka", "aa_fem")
        self.assertEqual(res["form"], "रमा")

        # 4.1 Ramayai (7.3.112)
        res = inflect_stem("रमा", "caturthi", "eka", "aa_fem")
        self.assertEqual(res["form"], "रमायै")

        # 6.1 Ramayah
        res = inflect_stem("रमा", "sasthi", "eka", "aa_fem")
        self.assertEqual(res["form"], "रमायाः")

        # Cognate test: Lata -> Latayah
        res = inflect_stem("लता", "sasthi", "eka", "aa_fem")
        self.assertEqual(res["form"], "लतायाः")

    def test_i_masc_hari(self):
        # 1.1 Harih
        res = inflect_stem("हरि", "1", "1")
        self.assertEqual(res["form"], "हरिः")

        # 1.3 Harayah (guna 7.3.109 + ay 6.1.78)
        res = inflect_stem("हरि", "prathama", "bahu")
        self.assertEqual(res["form"], "हरयः")

        # 6.1 Hareh
        res = inflect_stem("हरि", "sasthi", "eka")
        self.assertEqual(res["form"], "हरेः")

        # 7.1 Harau
        res = inflect_stem("हरि", "saptami", "eka")
        self.assertEqual(res["form"], "हरौ")

    def test_u_masc_guru(self):
        # 1.1 Guruh
        res = inflect_stem("गुरु", "prathama", "eka")
        self.assertEqual(res["form"], "गुरुः")

        # 1.3 Guravah (guna 7.3.109 + av 6.1.78)
        res = inflect_stem("गुरु", "prathama", "bahu")
        self.assertEqual(res["form"], "गुरवः")

        # 4.1 Gurave
        res = inflect_stem("गुरु", "caturthi", "eka")
        self.assertEqual(res["form"], "गुरवे")

        # 7.1 Gurau
        res = inflect_stem("गुरु", "saptami", "eka")
        self.assertEqual(res["form"], "गुरौ")

if __name__ == "__main__":
    unittest.main()