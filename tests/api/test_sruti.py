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
