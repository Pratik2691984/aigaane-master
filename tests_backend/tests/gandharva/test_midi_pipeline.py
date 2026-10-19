import os
import tempfile
import mido
import pytest
from aigaane.chandas import scan_iast
from aigaane.tala import align_to_tala
from aigaane.raga import assign_svaras
from aigaane.midi import assign_timings, render_to_midi, save_midi

REF_HZ = 146.83

def test_timings_grid():
    timed = assign_timings(align_to_tala(list("GGGGLGGG"), "adi"), 0.5)
    assert [c["start_s"] for c in timed] == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
def test_timings_L_half():
    timed = assign_timings(align_to_tala(list("GGGGLGGG"), "adi"), 0.5)
    assert timed[4]["duration_s"] == 0.25
def test_timings_bad_weight():
    with pytest.raises(ValueError):
        assign_timings([{"weight": "X"}], 0.5)

def test_render_pitches():
    svaras = assign_svaras(align_to_tala(list("GGGGLGGG"), "adi"), "mayamalavagowla")
    mid = render_to_midi(svaras, "mayamalavagowla", REF_HZ)
    ons = [m.note for tr in mid.tracks for m in tr if m.type == "note_on" and m.velocity > 0]
    assert ons == [50, 51, 54, 55, 57, 58, 61, 50]

def test_render_timing():
    svaras = assign_svaras(align_to_tala(list("GGGGLGGG"), "adi"), "mayamalavagowla")
    mid = render_to_midi(svaras, "mayamalavagowla", REF_HZ)
    
    t = 0
    ons = []
    for msg in mid.tracks[0]:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            ons.append(t)
    # Check the absolute ticks directly from the in-memory track
    assert ons == [0, 480, 960, 1440, 1920, 2400, 2880, 3360]

def test_full_pipeline():
    weights = scan_iast("dharmakṣetre kurukṣetre")
    svaras = assign_svaras(align_to_tala(weights, "adi"), "mayamalavagowla")
    mid = render_to_midi(svaras, "mayamalavagowla", REF_HZ)
    ons = [m.note for tr in mid.tracks for m in tr if m.type == "note_on" and m.velocity > 0]
    assert ons == [50, 51, 54, 55, 57, 58, 61, 50]
