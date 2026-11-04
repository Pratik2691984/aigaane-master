"""
API Contract Verification for POST /api/v1/route
"""

def test_route_nyaya_argumentation(client):
    parse_res = client.post("/api/v1/parse", json={"text": "parvato vahnimān dhūmavattvāt"})
    assert parse_res.status_code == 200
    doc = parse_res.json()

    route_res = client.post("/api/v1/route", json={"doc": doc})
    assert route_res.status_code == 200
    decision = route_res.json()
    assert decision["studio"] == "Studio_II"
    assert decision["intent_class"] == "logical_argumentation"
    assert decision.get("nyaya_verifier_mode") == "deterministic"
    assert "nyaya_syllogism" in decision
    syllogism = decision["nyaya_syllogism"]
    assert len(syllogism["steps"]) == 5
    assert syllogism["steps"][0]["step"] == "pratijna"
    assert syllogism["steps"][0]["verifier_status"] == "verified"

def test_route_chhandas_prosody(client):
    parse_res = client.post("/api/v1/parse", json={"text": "gāyatrī"})
    assert parse_res.status_code == 200
    doc = parse_res.json()

    route_res = client.post("/api/v1/route", json={"doc": doc})
    assert route_res.status_code == 200
    decision = route_res.json()
    assert decision["studio"] == "Studio_III"
    assert decision["intent_class"] == "chhandas_meter_validation"

def test_route_default_studio(client):
    parse_res = client.post("/api/v1/parse", json={"text": "himālayaḥ"})
    assert parse_res.status_code == 200
    doc = parse_res.json()

    route_res = client.post("/api/v1/route", json={"doc": doc})
    assert route_res.status_code == 200
    decision = route_res.json()
    assert decision["studio"] == "Studio_I"