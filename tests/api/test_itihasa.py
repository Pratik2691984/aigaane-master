import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.asyncio
async def test_search_all_corpus():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/itihasa/search")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 5
        assert len(data["results"]) >= 5


@pytest.mark.asyncio
async def test_search_by_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/itihasa/search?q=karma")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        assert any("karmaṇyevādhikāraste" in r["transliteration"] for r in data["results"])


@pytest.mark.asyncio
async def test_search_by_meter_filter():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/itihasa/search?meter=triṣṭubh")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 4
        assert all(r["meter"] == "triṣṭubh" for r in data["results"])
