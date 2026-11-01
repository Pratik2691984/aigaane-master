import pytest
from engine import parse

def test_marut_nominative_and_instrumental():
    # Prathama ekavacana: marut
    doc1 = parse("marut")
    assert doc1 is not None
    assert doc1["tokens"][0]["stem"] == "marut"
    assert doc1["tokens"][0]["vibhakti"] == "prathama"
    assert doc1["tokens"][0]["vacana"] == "ekavacana"
    assert doc1["tokens"][0]["linga"] == "pullinga"

    # Trtiya ekavacana: marutā
    doc2 = parse("marutā")
    assert doc2 is not None
    assert doc2["tokens"][0]["stem"] == "marut"
    assert doc2["tokens"][0]["vibhakti"] == "trtiya"
    assert doc2["tokens"][0]["vacana"] == "ekavacana"

    # Saptami bahuvacana: marutsu
    doc3 = parse("marutsu")
    assert doc3 is not None
    assert doc3["tokens"][0]["stem"] == "marut"
    assert doc3["tokens"][0]["vibhakti"] == "saptami"
    assert doc3["tokens"][0]["vacana"] == "bahuvacana"

def test_vac_coh_kuh_velar_shift():
    # Prathama ekavacana: vāk (coḥ kuḥ 8.2.30)
    doc1 = parse("vāk")
    assert doc1 is not None
    assert doc1["tokens"][0]["stem"] == "vāc"
    assert doc1["tokens"][0]["pos"] == "subhanta"
    assert doc1["tokens"][0]["linga"] == "strilinga"

    # Dvitiya ekavacana: vācam
    doc2 = parse("vācam")
    assert doc2 is not None
    assert doc2["tokens"][0]["stem"] == "vāc"
    assert doc2["tokens"][0]["vibhakti"] == "dvitiya"

    # Saptami bahuvacana: vākṣu (coḥ kuḥ + ādeśapratyayayoḥ)
    doc3 = parse("vākṣu")
    assert doc3 is not None
    assert doc3["tokens"][0]["stem"] == "vāc"
    assert doc3["tokens"][0]["vibhakti"] == "saptami"
    assert doc3["tokens"][0]["vacana"] == "bahuvacana"
