import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.mark.asyncio
async def test_gandharva_phrase_deterministic_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "verse_text": "dharmakṣetre kurukṣetre",
            "syllables": ["dhar", "mak", "ṣe", "tre", "ku", "ru", "kṣe", "tre"],
            "weights": ["G", "L", "G", "G", "L", "L", "G", "G"],
            "target_raga": "Bhairav"
        }
        res = await ac.post("/api/v1/gandharva/phrase", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["target_raga"] == "Bhairav"
        assert len(data["swara_sequence"]) == 8
        assert data["confidence"] <= 0.75
        assert all(t["swara"] in {"S", "r", "G", "M", "P", "d", "N", "S'"} for t in data["swara_sequence"])


@pytest.mark.asyncio
async def test_gandharva_phrase_rejects_non_sanskrit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "verse_text": "plain english without diacritics",
            "syllables": ["plain", "eng", "lish"],
            "weights": ["G", "L", "G"],
            "target_raga": "Bhairav"
        }
        res = await ac.post("/api/v1/gandharva/phrase", json=payload)
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_gandharva_phrase_rejects_mismatched_counts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "verse_text": "dharmakṣetre",
            "syllables": ["dhar", "mak", "ṣe", "tre"],
            "weights": ["G", "L"],
            "target_raga": "Bhairav"
        }
        res = await ac.post("/api/v1/gandharva/phrase", json=payload)
        assert res.status_code == 422
