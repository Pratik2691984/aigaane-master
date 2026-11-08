"""
Regression tests for Studio III MIDI export.

Validates:
  - endpoint returns a base64-encoded, structurally valid Type-1 MIDI file
  - exactly 3 tracks (Conductor, Vina/Melody, Tanpura)
  - conductor track contains tempo + time signature meta events
  - verse_title default is UTF-8-clean (no "Â·" mojibake)
"""
import base64
import io
import struct

import mido
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _parse_midi_header(raw: bytes) -> dict:
    """
    Parse the 14-byte MIDI file header.

    Layout:
      0..4   "MThd"
      4..8   header length (big-endian uint32, always 6)
      8..10  format (big-endian uint16)
      10..12 ntrks  (big-endian uint16)
      12..14 division (big-endian uint16)
    """
    assert len(raw) >= 14, f"file too short for MIDI header: {len(raw)} bytes"
    assert raw[:4] == b"MThd", f"missing 'MThd' magic, got {raw[:4]!r}"
    hdr_len = struct.unpack(">I", raw[4:8])[0]
    assert hdr_len == 6, f"unexpected MThd length {hdr_len}"
    fmt, ntrks, division = struct.unpack(">HHH", raw[8:14])
    return {"format": fmt, "ntrks": ntrks, "division": division}


def test_midi_export_returns_valid_type1_midi(client):
    body = {
        "swaras": ["S", "R1", "G1", "m1", "P", "d1", "n1", "S"],
        "tempo_bpm": 120,
    }
    r = client.post("/api/v3/studio3/midi/export", json=body)
    assert r.status_code == 200, r.text

    payload = r.json()
    assert payload["encoding"] == "base64"
    assert payload["size_bytes"] > 0
    assert payload["download_filename"].endswith(".mid")

    raw = base64.b64decode(payload["midi_base64"])

    # --- header checks (no hardcoded MTrk offset) ---
    hdr = _parse_midi_header(raw)
    assert hdr["format"] == 1, f"expected Type-1, got {hdr['format']}"
    assert hdr["ntrks"] == 3, f"expected 3 tracks, got {hdr['ntrks']}"
    assert hdr["division"] > 0, "division must be positive"

    # --- full parse via mido ---
    mid = mido.MidiFile(file=io.BytesIO(raw))
    assert mid.type == 1, "must be Type-1 multi-track"
    assert len(mid.tracks) == 3, f"expected 3 tracks, got {len(mid.tracks)}"

    # conductor track contains tempo + time signature
    conductor = mid.tracks[0]
    assert any(m.type == "set_tempo" for m in conductor), "no set_tempo in conductor"
    assert any(m.type == "time_signature" for m in conductor), "no time_signature in conductor"

    # melody track should carry note events
    melody = mid.tracks[1]
    assert any(m.type == "note_on" for m in melody), "no note_on in melody track"


def test_midi_export_without_tanpura_has_two_tracks(client):
    body = {"swaras": ["S", "P"], "include_tanpura": False}
    r = client.post("/api/v3/studio3/midi/export", json=body)
    assert r.status_code == 200, r.text

    raw = base64.b64decode(r.json()["midi_base64"])
    hdr = _parse_midi_header(raw)
    assert hdr["format"] == 1
    assert hdr["ntrks"] == 2, f"header says {hdr['ntrks']} tracks, expected 2"

    mid = mido.MidiFile(file=io.BytesIO(raw))
    assert len(mid.tracks) == 2


def test_verse_title_is_valid_utf8(client):
    body = {"swaras": ["S", "P"]}
    r = client.post("/api/v3/studio3/midi/export", json=body)
    assert r.status_code == 200, r.text

    title = r.json()["verse_title"]
    # Latin-1 mojibake for U+00B7 would appear as "Â·"
    assert "\u00c2" not in title, f"mojibake detected: {title!r}"
    assert title == "Aigaane \u00b7 Gandharvaveda", f"unexpected title: {title!r}"


def test_export_rejects_empty_swaras(client):
    r = client.post("/api/v3/studio3/midi/export", json={"swaras": []})
    assert r.status_code == 422, "empty swaras list should be rejected by validation"


def test_export_rejects_out_of_range_midi_note(client):
    r = client.post(
        "/api/v3/studio3/midi/export",
        json={"swaras": ["S"], "sa_midi_note": 200},
    )
    assert r.status_code == 422, "sa_midi_note > 127 should be rejected"


def test_probe_reports_sruti_ok(client):
    r = client.get("/api/v3/studio3/probe")
    assert r.status_code == 200
    data = r.json()
    assert data["sruti_ok"] is True
    assert data["has_generate_sruti_midi"] is True