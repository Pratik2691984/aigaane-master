"""
tests/test_subanta.py
Automated Unit Tests for Subanta Nominal Declensions (Ajanta & Halanta)
"""
import pytest
from engine.morphology.subanta import inflect_stem, decline_halanta

class TestSubantaEngine:
    def test_a_masc_rama(self):
        res_prathama_eka = inflect_stem("राम", "prathama", "eka")
        res_dvitiya_bahu = inflect_stem("राम", "dvitiya", "bahu")
        res_trtiya_eka = inflect_stem("राम", "trtiya", "eka")
        res_saptami_bahu = inflect_stem("राम", "saptami", "bahu")
        
        assert res_prathama_eka["form"] == "रामः"
        assert res_dvitiya_bahu["form"] == "रामान्"
        assert res_trtiya_eka["form"] == "रामेण"
        assert res_saptami_bahu["form"] == "रामेषु"

    def test_aa_fem_ramaa(self):
        res_prathama_eka = inflect_stem("रमा", "prathama", "eka")
        res_dvitiya_bahu = inflect_stem("रमा", "dvitiya", "bahu")
        res_trtiya_eka = inflect_stem("रमा", "trtiya", "eka")
        res_saptami_bahu = inflect_stem("रमा", "saptami", "bahu")

        assert res_prathama_eka["form"] == "रमा"
        assert res_dvitiya_bahu["form"] == "रमाः"
        assert res_trtiya_eka["form"] == "रमया"
        assert res_saptami_bahu["form"] == "रमासु"

    def test_i_masc_hari(self):
        res_prathama_eka = inflect_stem("हरि", "prathama", "eka")
        res_dvitiya_bahu = inflect_stem("हरि", "dvitiya", "bahu")
        res_trtiya_eka = inflect_stem("हरि", "trtiya", "eka")
        res_saptami_eka = inflect_stem("हरि", "saptami", "eka")

        assert res_prathama_eka["form"] == "हरिः"
        assert res_dvitiya_bahu["form"] == "हरीन्"
        assert res_trtiya_eka["form"] == "हरिणा"
        assert res_saptami_eka["form"] == "हरौ"

    def test_u_masc_guru(self):
        res_prathama_eka = inflect_stem("गुरु", "prathama", "eka")
        res_dvitiya_bahu = inflect_stem("गुरु", "dvitiya", "bahu")
        res_trtiya_eka = inflect_stem("गुरु", "trtiya", "eka")
        res_saptami_eka = inflect_stem("गुरु", "saptami", "eka")

        assert res_prathama_eka["form"] == "गुरुः"
        assert res_dvitiya_bahu["form"] == "गुरून्"
        assert res_trtiya_eka["form"] == "गुरुणा"
        assert res_saptami_eka["form"] == "गुरौ"

    def test_halanta_marut(self):
        table = decline_halanta("marut")
        assert table["prathama"][0] == "मरुत्"
        assert table["dvitiya"][2] == "मरुतः"
        assert table["trtiya"][1] == "मरुद्भ्याम्"
        assert table["saptami"][2] == "मरुत्सु"

    def test_halanta_rajan(self):
        table = decline_halanta("rajan")
        assert table["prathama"][0] == "राजा"
        assert table["dvitiya"][2] == "राज्ञः"
        assert table["trtiya"][0] == "राज्ञा"
        assert table["sasthi"][2] == "राज्ञाम्"

    def test_halanta_manas(self):
        table = decline_halanta("manas")
        assert table["prathama"][0] == "मनः"
        assert table["prathama"][2] == "मनांसि"
        assert table["trtiya"][2] == "मनोभिः"
        assert table["saptami"][0] == "मनसि"
