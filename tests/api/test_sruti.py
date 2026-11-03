import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app

@pytest.mark.asyncio
async def test_get_sruti_matrix_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/sruti")
        assert res.status_code == 200
        data = res.json()
        assert data["total_srutis"] == 22
        assert len(data["intervals"]) == 22
        assert data["intervals"][0]["svara_symbol"] == "S"
        assert data["intervals"][13]["svara_symbol"] == "P"
        assert data["intervals"][13]["ratio"] == "3/2"

@pytest.mark.asyncio
async def test_lookup_individual_svara():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/sruti/G1")
        assert res.status_code == 200
        data = res.json()
        assert data["svara_symbol"] == "G1"
        assert data["ratio"] == "5/4"
        assert abs(data["cents"] - 386.31) < 0.1


@pytest.mark.asyncio
async def test_export_sruti_midi_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "svaras": ["S", "R1", "g2", "M1", "P", "d1", "n2"],
            "sa_hz": 240.0,
            "tempo_bpm": 80
        }
        res = await ac.post("/api/v1/sruti/midi/export", json=payload)
        assert res.status_code == 200
        assert res.headers["content-type"] == "audio/midi"
        assert res.content[:4] == b"MThd"
