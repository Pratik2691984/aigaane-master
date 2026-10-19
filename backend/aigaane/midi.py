import math
import mido
from aigaane.raga import RAGAS, svara_ratio

def assign_timings(cells: list[dict], akshara_duration_s: float = 0.5) -> list[dict]:
    timed = []
    for i, cell in enumerate(cells):
        weight = cell.get('weight')
        if weight == 'G':
            duration_s = akshara_duration_s
        elif weight == 'L':
            duration_s = akshara_duration_s / 2.0
        else:
            raise ValueError(f"Unknown weight '{weight}' in cell index {i}")
        start_s = i * akshara_duration_s
        timed.append({**cell, 'start_s': start_s, 'duration_s': duration_s})
    return timed

def svara_to_hz(raga_name: str, svara: str, reference_hz: float) -> float:
    return reference_hz * svara_ratio(raga_name, svara)

def hz_to_midi_note(hz: float) -> int:
    return round(69 + 12 * math.log2(hz / 440.0))

def render_to_midi(cells: list[dict], raga_name: str, reference_hz: float, akshara_duration_s: float = 0.5, tempo_bpm: int = 120, ticks_per_beat: int = 480) -> mido.MidiFile:
    if raga_name not in RAGAS:
        raise KeyError(f"Unknown raga: {raga_name}")
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo_bpm), time=0))
    ticks_per_sec = ticks_per_beat * (tempo_bpm / 60.0)
    
    events = []
    for i, cell in enumerate(cells):
        # Fallback to index-based timing if start_s/duration_s are missing
        start_s = cell.get('start_s')
        if start_s is None:
            start_s = i * akshara_duration_s
            
        dur_s = cell.get('duration_s')
        if dur_s is None:
            dur_s = akshara_duration_s if cell.get('weight') == 'G' else akshara_duration_s / 2.0

        start_tick = round(start_s * ticks_per_sec)
        end_tick = round((start_s + dur_s) * ticks_per_sec)
        
        hz = svara_to_hz(raga_name, cell['svara'], reference_hz)
        note = hz_to_midi_note(hz)
        
        events.append((start_tick, 'on', note))
        events.append((end_tick, 'off', note))
        
    # Sort by tick, then put 'on' before 'off' at the same tick
    events.sort(key=lambda x: (x[0], 1 if x[1] == 'on' else 2))
    
    current_tick = 0
    for tick, ev_type, note in events:
        delta = tick - current_tick
        current_tick = tick
        if ev_type == 'on':
            track.append(mido.Message('note_on', note=note, velocity=64, time=delta))
        else:
            track.append(mido.Message('note_off', note=note, velocity=0, time=delta))
            
    return mid

def save_midi(midi_file: mido.MidiFile, path: str) -> None:
    midi_file.save(path)
