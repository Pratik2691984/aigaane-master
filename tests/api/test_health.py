"""
Contract verification for GET /health endpoint.
"""

def test_health_status_and_versions(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["engine_version"] == "0.8.8"
    assert data["schema_version"] == "0.2.0"
    assert data["tests_passing"] >= 142
    assert "engine_module" in data

def test_health_warnings_present(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["warnings"], list)
    assert len(data["warnings"]) >= 1

def test_health_pillar_status_coverage(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    pillars = data["pillar_status"]
    assert "pillar_1_llm" in pillars
    assert "pillar_2_paninian_grammar" in pillars
    assert "pillar_3_multistudio_runtime" in pillars
    assert "pillar_4_governance" in pillars
