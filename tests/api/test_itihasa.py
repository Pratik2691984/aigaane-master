import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app

@pytest.mark.asyncio
async def test_itihasa_search_by_keyword():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/itihasa/search", json={"query": "karma"})
        assert res.status_code == 200
        data = res.json()
        assert data["total_matches"] >= 1
        assert any("karma" in m["keywords"] for m in data["matches"])

@pytest.mark.asyncio
async def test_itihasa_search_by_source_filter():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/itihasa/search", json={"query": "", "source": "Rāmāyaṇa"})
        assert res.status_code == 200
        data = res.json()
        assert data["total_matches"] >= 1
        assert "Vālmīki Rāmāyaṇa" in data["matches"][0]["source"]
