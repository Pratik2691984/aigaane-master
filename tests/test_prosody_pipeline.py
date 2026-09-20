"""
tests/test_prosody_pipeline.py
Automated Unit Tests for Sanskrit Phonology, Akṣara Weight, and Multi-Meter Metrics
"""
import pytest
from engine.prosody.chandas import (
    tokenize_aksaras, 
    classify_syllables, 
    scan_anustubh, 
    scan_varnavrtta_pada
)

def test_aksara_tokenization():
    text = "धर्मक्षेत्रे"  # धर्मक्षेत्रे
    tokens = tokenize_aksaras(text)
    assert len(tokens) == 4
    assert tokens[0].text == "ध"
    assert tokens[1].text == "र्म"
    assert tokens[2].text == "क्षे"
    assert tokens[3].text == "त्रे"

def test_samyoga_guru_assignment():
    text = "सत्यम्"  # सत्यम्
    tokens = tokenize_aksaras(text)
    syls = classify_syllables(tokens, padanta_guru=False)
    assert syls[0]["weight"] == "G"
    assert syls[1]["weight"] == "G"

def test_gita_first_verse_validity():
    verse = """धर्मक्षेत्रे कुरुक्षेत्रे
समवेतऺ युयुत्सवः
मामकाः पाण्डवाश्चैव
किमकुर्वत सञ्जय"""
    report = scan_anustubh(verse)
    assert report["valid"] is True
    assert report["chandas"] == "anuṣṭubh"
    assert report["variant"] == "pathyā"
    assert len(report["padas"]) == 4

def test_broken_verse_diagnostics():
    broken_verse = """धर्मक्षेत्रे वीरक्षेत्रे
समवेतऺ युयुत्सवः
मामकाः पाण्डवाश्चैव
किमकुर्वत सञ्जय"""
    report = scan_anustubh(broken_verse)
    assert report["valid"] is False
    assert any(d["rule"] == "pathyā-5-L" for d in report["diagnostics"])

def test_indravajra_canonical_scan():
    # Canonical 11-akṣara Indravajrā (अर्थो हि कन्या परकीय एव)
    # Weights: GGLLGLLGLGG
    pada_text = "अर्थो हि कन्या परकीय एव"
    res, diags = scan_varnavrtta_pada(pada_text, 1, "indravajra", padanta_guru=True)
    assert res["total_syllables"] == 11
    assert res["weight_pattern"] == "GGLGGLLGLGG"
    assert res["valid"] is True
    assert len(diags) == 0
