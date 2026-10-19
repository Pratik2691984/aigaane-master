import os
import tempfile
import wave
import numpy as np
import pytest

from aigaane.chandas import scan_iast
from aigaane.tala import align_to_tala
from aigaane.raga import assign_svaras
from aigaane.midi import assign_timings
from aigaane.synth import (
    generate_tone, render_to_pcm, pcm_to_wav, render_to_wav,
    DEFAULT_SAMPLE_RATE
)

REF_HZ = 146.83

# ---- generate_tone ----

def test_tone_length():
    t = generate_tone(146.83, 0.5, sample_rate=44100)
    assert len(t) == 22050

def test_tone_envelope_starts_and_ends_at_zero():
    t = generate_tone(146.83, 0.5, attack_ms=15, release_ms=30, sample_rate=44100)
    assert abs(t[0]) < 1e-6
    assert abs(t[-1]) < 1e-6

def test_tone_frequency_dominates_spectrum():
    t = generate_tone(146.83, 1.0, sample_rate=44100)
    spectrum = np.abs(np.fft.rfft(t))
    freqs = np.fft.rfftfreq(len(t), 1.0 / 44100)
    peak_freq = freqs[np.argmax(spectrum)]
    assert abs(peak_freq - 146.83) < 1.0

# ---- render_to_pcm ----

def test_pcm_length_single_pada():
    weights = scan_iast("dharmakṣetre kurukṣetre")
    svaras = assign_svaras(align_to_tala(weights, "adi"), "mayamalavagowla")
    timed = assign_timings(svaras, akshara_duration_s=0.5)
    pcm = render_to_pcm(timed, "mayamalavagowla", REF_HZ, sample_rate=44100)
    # 8 syllables * 0.5s = 4.0s total
    assert len(pcm) == 4 * 44100

def test_pcm_silence_in_laghu_gap():
    weights = scan_iast("dharmakṣetre kurukṣetre")
    svaras = assign_svaras(align_to_tala(weights, "adi"), "mayamalavagowla")
    timed = assign_timings(svaras, 0.5)
    pcm = render_to_pcm(timed, "mayamalavagowla", REF_HZ, sample_rate=44100)
    # The 5th note (index 4) is L (duration 0.25s). 
    # It starts at 2.0s (sample 88200) and ends at 2.25s (sample 99225).
    # The gap is from 99225 to the start of the next note at 2.5s (sample 110250).
    gap = pcm[99500:110000]
    assert np.max(np.abs(gap)) < 0.01

def test_pcm_exact_ji_frequency_not_quantized():
    # P = 1.5 * 146.83 = 220.245 Hz
    cells = [{"weight": "G", "svara": "P", "start_s": 0.0, "duration_s": 2.0}]
    pcm = render_to_pcm(cells, "mayamalavagowla", REF_HZ, sample_rate=44100)
    
    # Analyze the middle 1 second to avoid envelope ramps
    body = pcm[44100:88200]
    spectrum = np.abs(np.fft.rfft(body))
    freqs = np.fft.rfftfreq(len(body), 1.0 / 44100)
    peak_freq = freqs[np.argmax(spectrum)]
    
    # This proves we did NOT quantize to 220.0 Hz
    assert abs(peak_freq - 220.245) < 0.5

# ---- pcm_to_wav ----

def test_wav_file_created():
    pcm = np.zeros(44100, dtype=np.float32)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        pcm_to_wav(pcm, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 44
    finally:
        os.unlink(path)

def test_wav_header_correct():
    pcm = np.zeros(44100, dtype=np.float32)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        pcm_to_wav(pcm, path, sample_rate=44100)
        with wave.open(path, "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 44100
            assert wf.getnframes() == 44100
    finally:
        os.unlink(path)

# ---- End-to-End ----

def test_render_to_wav_end_to_end():
    weights = scan_iast("dharmakṣetre kurukṣetre")
    svaras = assign_svaras(align_to_tala(weights, "adi"), "mayamalavagowla")
    timed = assign_timings(svaras, 0.5)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        render_to_wav(timed, "mayamalavagowla", REF_HZ, path)
        with wave.open(path, "rb") as wf:
            assert wf.getnframes() == 4 * 44100
            assert wf.getframerate() == 44100
    finally:
        os.unlink(path)
