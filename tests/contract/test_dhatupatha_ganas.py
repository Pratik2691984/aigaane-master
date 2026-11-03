import pytest
from engine import parse

def test_gana_2_adadi_luk():
    # ad (eat) -> atti (luk-śap 2.4.72)
    doc_ad = parse("atti")
    assert doc_ad is not None
    tok_ad = doc_ad["tokens"][0]
    assert tok_ad["stem"] == "ad"
    assert tok_ad["pos"] == "tinanta"
    assert tok_ad["purusa"] == "prathama"
    assert tok_ad["vacana"] == "ekavacana"

    # as (be) -> santi (bahuvacana via śnasor allopaḥ 6.4.111)
    doc_as = parse("santi")
    assert doc_as is not None
    tok_as = doc_as["tokens"][0]
    assert tok_as["stem"] == "as"
    assert tok_as["vacana"] == "bahuvacana"

def test_gana_3_juhotyadi_slu():
    # hu (sacrifice) -> juhoti (ślu 6.1.10)
    doc_hu = parse("juhoti")
    assert doc_hu is not None
    tok_hu = doc_hu["tokens"][0]
    assert tok_hu["stem"] == "hu"
    assert tok_hu["purusa"] == "prathama"

    # dā (give) -> dadāti
    doc_da = parse("dadāti")
    assert doc_da is not None
    assert doc_da["tokens"][0]["stem"] == "dā"

def test_gana_5_svadi_snu():
    # su -> sunoti (śnu 3.1.73)
    doc_su = parse("sunoti")
    assert doc_su is not None
    assert doc_su["tokens"][0]["stem"] == "su"

    # āp -> āpnuvanti
    doc_ap = parse("āpnuvanti")
    assert doc_ap is not None
    assert doc_ap["tokens"][0]["stem"] == "āp"
    assert doc_ap["tokens"][0]["vacana"] == "bahuvacana"

def test_gana_6_tudadi_sa():
    # tud -> tudati (śa 3.1.77)
    doc_tud = parse("tudati")
    assert doc_tud is not None
    assert doc_tud["tokens"][0]["stem"] == "tud"

    # likh -> likhanti
    doc_likh = parse("likhanti")
    assert doc_likh is not None
    assert doc_likh["tokens"][0]["stem"] == "likh"

def test_gana_7_rudhadi_snam():
    # rudh -> ruṇaddhi (śnam 3.1.78)
    doc_rudh = parse("ruṇaddhi")
    assert doc_rudh is not None
    assert doc_rudh["tokens"][0]["stem"] == "rudh"

def test_gana_8_tanadi_u():
    # kṛ -> karoti (u 3.1.79)
    doc_kr = parse("karoti")
    assert doc_kr is not None
    assert doc_kr["tokens"][0]["stem"] == "kṛ"

    # kṛ -> kurvanti
    doc_kur = parse("kurvanti")
    assert doc_kur is not None
    assert doc_kur["tokens"][0]["stem"] == "kṛ"
    assert doc_kur["tokens"][0]["vacana"] == "bahuvacana"

def test_gana_9_kryadi_sna():
    # jñā -> jānāti (śnā 3.1.81 + jñājanor jā 7.3.79)
    doc_jna = parse("jānāti")
    assert doc_jna is not None
    assert doc_jna["tokens"][0]["stem"] == "jñā"

def test_gana_10_curadi_nic():
    # cur -> corayati (ṇic 3.1.25)
    doc_cur = parse("corayati")
    assert doc_cur is not None
    assert doc_cur["tokens"][0]["stem"] == "cur"
