"""Test the neural success path explicitly by mocking _engine.phrase."""
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from api.main import app
from aigaane.neural.schemas import SwaraSequence, SwaraToken


@pytest.mark.asyncio
async def test_gandharva_phrase_neural_success():
    """Verify neural_used=True and response structure when Gemini engine succeeds."""
    mock_seq = SwaraSequence(
        sequence=[
            SwaraToken(swara="S"),
            SwaraToken(swara="r", meend_target="G"),
            SwaraToken(swara="G"),
            SwaraToken(swara="M"),
        ],
        confidence=0.62,
        rationale="Bhairav opening with komal Re glide",
    )

    with patch("api.routes.gandharva._engine") as mock_engine:
        mock_engine.phrase.return_value = mock_seq

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "verse_text": "dharmakṣetre kurukṣetre",
                "syllables": ["dhar", "mak", "ṣe", "tre"],
                "weights": ["G", "L", "G", "G"],
                "target_raga": "Bhairav"
            }
            res = await ac.post("/api/v1/gandharva/phrase", json=payload)

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["neural_used"] is True
    assert data["confidence"] == 0.62
    assert len(data["swara_sequence"]) == 4
    assert data["swara_sequence"][1]["swara"] == "r"
    assert data["swara_sequence"][1]["meend_target"] == "G"
