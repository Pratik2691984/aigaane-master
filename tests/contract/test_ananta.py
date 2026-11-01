import pytest
from engine import parse

def test_rajan_ananta_derivations():
    # 1. Prathamā ekavacana: rājan + sU -> rājān -> rājā (8.2.7 naḥ lopaḥ)
    doc1 = parse("rājā")
    assert doc1 is not None
    assert doc1["tokens"][0]["stem"] == "rājan"
    assert doc1["tokens"][0]["vibhakti"] == "prathama"
    assert doc1["tokens"][0]["vacana"] == "ekavacana"
    assert doc1["tokens"][0]["linga"] == "pullinga"

    # 2. Tṛtīyā ekavacana: rājan + ṭā -> rājn + ā -> rājñā (6.4.134 allopo 'naḥ + 8.4.40 ścutva)
    doc2 = parse("rājñā")
    assert doc2 is not None
    assert doc2["tokens"][0]["stem"] == "rājan"
    assert doc2["tokens"][0]["vibhakti"] == "trtiya"
    assert doc2["tokens"][0]["vacana"] == "ekavacana"

    # 3. Tṛtīyā bahuvacana: rājan + bhis -> rāja + bhiḥ -> rājabhiḥ (8.2.7 naḥ lopaḥ before consonant)
    doc3 = parse("rājabhiḥ")
    assert doc3 is not None
    assert doc3["tokens"][0]["stem"] == "rājan"
    assert doc3["tokens"][0]["vibhakti"] == "trtiya"
    assert doc3["tokens"][0]["vacana"] == "bahuvacana"

def test_naman_ananta_derivations():
    # 1. Prathamā ekavacana: nāman + su -> nāman -> nāma (7.1.23 luk + 8.2.7 naḥ lopaḥ)
    doc1 = parse("nāma")
    assert doc1 is not None
    assert doc1["tokens"][0]["stem"] == "nāman"
    assert doc1["tokens"][0]["vibhakti"] == "prathama"
    assert doc1["tokens"][0]["vacana"] == "ekavacana"
    assert doc1["tokens"][0]["linga"] == "napumsakalinga"

    # 2. Prathamā bahuvacana: nāman + jas -> nāman + śi -> nāmāni (7.1.20 + 7.1.72 + 6.4.8)
    doc2 = parse("nāmāni")
    assert doc2 is not None
    assert doc2["tokens"][0]["stem"] == "nāman"
    assert doc2["tokens"][0]["vibhakti"] == "prathama"
    assert doc2["tokens"][0]["vacana"] == "bahuvacana"

    # 3. Tṛtīyā ekavacana: nāman + ṭā -> nāmnā (6.4.134 allopo 'naḥ)
    doc3 = parse("nāmnā")
    assert doc3 is not None
    assert doc3["tokens"][0]["stem"] == "nāman"
    assert doc3["tokens"][0]["vibhakti"] == "trtiya"
    assert doc3["tokens"][0]["vacana"] == "ekavacana"
