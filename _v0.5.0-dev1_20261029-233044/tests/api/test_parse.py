"""
API Contract Verification for POST /api/v1/parse
"""

def test_parse_golden_sandhi(client):
    res = client.post("/api/v1/parse", json={"text": "himālayaḥ"})
    assert res.status_code == 200
    data = res.json()
    assert data["schema_version"] == "0.2.0"
    assert data["surface"] == "himālayaḥ"
    assert len(data["tokens"]) == 2
    assert data["sandhi_splits"][0]["rule"] == "savarna_dirgha"

def test_parse_devanagari(client):
    res = client.post("/api/v1/parse", json={"text": "रामो गच्छति"})
    assert res.status_code == 200
    data = res.json()
    assert data["script_original"] == "devanagari"
    assert len(data["tokens"]) == 2

def test_parse_generative_sentence(client):
    res = client.post("/api/v1/parse", json={"text": "rāmasya bhavati"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["tokens"]) == 2
    assert data["tokens"][0]["stem"] == "rāma"
    assert data["tokens"][1]["dhatu"] == "bhū"

def test_parse_generative_compound(client):
    res = client.post("/api/v1/parse", json={"text": "devaputraḥ"})
    assert res.status_code == 200
    data = res.json()
    assert "samasa_tree" in data
    assert data["samasa_tree"]["type"] == "tatpurusha"

def test_parse_unparseable_input(client):
    res = client.post("/api/v1/parse", json={"text": "xyz987_invalid_token"})
    assert res.status_code == 422
