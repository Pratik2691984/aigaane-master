import wave
import numpy as np
from aigaane.raga import svara_ratio

DEFAULT_SAMPLE_RATE = 44100
DEFAULT_AMPLITUDE   = 0.8
DEFAULT_ATTACK_MS   = 15
DEFAULT_RELEASE_MS  = 30

def generate_tone(freq_hz, duration_s, sample_rate=DEFAULT_SAMPLE_RATE, amplitude=DEFAULT_AMPLITUDE, attack_ms=DEFAULT_ATTACK_MS, release_ms=DEFAULT_RELEASE_MS):
    n_total = int(duration_s * sample_rate)
    n_attack = int((attack_ms / 1000.0) * sample_rate)
    n_release = int((release_ms / 1000.0) * sample_rate)
    
    if n_attack + n_release > n_total:
        scale = n_total / (n_attack + n_release)
        n_attack = int(n_attack * scale)
        n_release = int(n_release * scale)
        
    t = np.arange(n_total, dtype=np.float64) / sample_rate
    
    # 1. ADDITIVE HARMONICS (Makes it sound like an instrument, not a beep)
    # We blend the fundamental frequency with its 2nd and 3rd harmonics
    wave_data = (
        np.sin(2 * np.pi * freq_hz * t) * 1.0 + 
        np.sin(2 * np.pi * freq_hz * 2 * t) * 0.3 + 
        np.sin(2 * np.pi * freq_hz * 3 * t) * 0.1
    )
    
    # 2. TREMOLO / VIBRATO (Slight volume pulsing, like a plucked string)
    # 5 Hz tremolo rate
    tremolo = 0.8 + 0.2 * np.sin(2 * np.pi * 5 * t)
    wave_data = wave_data * tremolo
    
    # 3. ENVELOPE (Smooth fade in/out to prevent clicking)
    envelope = np.ones(n_total, dtype=np.float64)
    if n_attack > 0:
        envelope[:n_attack] = np.linspace(0.0, 1.0, n_attack, endpoint=False)
    if n_release > 0:
        envelope[n_total - n_release:] = np.linspace(1.0, 0.0, n_release, endpoint=True)
        
    # Normalize volume to prevent clipping
    wave_data = wave_data / 1.4 
    
    return wave_data * envelope * amplitude

def render_to_pcm(cells, raga_name, reference_hz, sample_rate=DEFAULT_SAMPLE_RATE, amplitude=DEFAULT_AMPLITUDE):
    if not cells:
        return np.array([], dtype=np.float32)
        
    last_cell = cells[-1]
    total_duration = last_cell['start_s'] + last_cell['duration_s']
    total_samples = int(np.ceil(total_duration * sample_rate))
    buffer = np.zeros(total_samples, dtype=np.float32)
    
    for cell in cells:
        start_s = cell['start_s']
        dur_s = cell['duration_s']
        freq = reference_hz * svara_ratio(raga_name, cell['svara'])
        
        start_sample = int(round(start_s * sample_rate))
        end_sample = start_sample + int(round(dur_s * sample_rate))
        
        tone = generate_tone(freq, dur_s, sample_rate, amplitude)
        
        # Mixing the tone into the buffer
        buffer[start_sample:end_sample] += tone.astype(np.float32)
        
    return buffer

def pcm_to_wav(pcm, path, sample_rate=DEFAULT_SAMPLE_RATE):
    peak = np.max(np.abs(pcm)) if len(pcm) > 0 else 0
    if peak > 1.0:
        pcm = pcm / peak
        
    int16_pcm = np.clip(pcm * 32767, -32768, 32767).astype(np.int16)
    
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_pcm.tobytes())

def render_to_wav(cells, raga_name, reference_hz, path, sample_rate=DEFAULT_SAMPLE_RATE):
    pcm = render_to_pcm(cells, raga_name, reference_hz, sample_rate)
    pcm_to_wav(pcm, path, sample_rate)