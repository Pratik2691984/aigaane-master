import pytest
import base64
from httpx import AsyncClient, ASGITransport
from api.main import app

@pytest.mark.asyncio
async def test_studio_pipeline_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "text": "parvato vahnimān dhūmavattvāt",
            "raga_svaras": ["S", "R2", "G2", "M1", "P", "D2", "N2", "S"],
            "sa_hz": 240.0,
            "tempo_bpm": 80
        }
        res = await ac.post("/api/v1/pipeline", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert "pipeline_id" in data
        assert data["studio_ii_verification"]["is_valid_inference"] is True
        assert data["studio_i_analysis"]["schema_version"] == "0.2.0"
        
        # Verify acoustics & MIDI
        acoustics = data["studio_iii_acoustics"]
        assert "midi_base64" in acoustics
        midi_raw = base64.b64decode(acoustics["midi_base64"])
        assert midi_raw[:4] == b"MThd"
