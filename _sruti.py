"""
22-Śruti Microtonal Acoustic Model for Aigaane Gāndharvaveda (Studio III).
Implements exact integer frequency ratios, cent calculations, and MIDI pitch-bend offsets.
"""
import math
from typing import Dict, Any, List, Tuple

# Base reference Sa = 240.0 Hz (Standard Madhyama-grāma / Gandharva baseline) or 261.63 Hz (Middle C4)
DEFAULT_SA_HZ = 240.0

# Canonical 22 Śruti Definition Table
# Index, Śruti Name, Svara, Ratio (Num/Den), Paninian / Bharata Shastra Reference
SRUTI_CANONICAL: List[Dict[str, Any]] = [
    {"index": 1, "name": "Kṣiti", "svara": "Ṣaḍja (S)", "ratio_num": 1, "ratio_den": 1, "svara_symbol": "S"},
    {"index": 2, "name": "Tīvrā", "svara": "Komal Ṛṣabha (r1)", "ratio_num": 256, "ratio_den": 243, "svara_symbol": "r1"},
    {"index": 3, "name": "Kumudvatī", "svara": "Komal Ṛṣabha (r2)", "ratio_num": 16, "ratio_den": 15, "svara_symbol": "r2"},
    {"index": 4, "name": "Mandā", "svara": "Śuddha Ṛṣabha (R1)", "ratio_num": 10, "ratio_den": 9, "svara_symbol": "R1"},
    {"index": 5, "name": "Chandovatī", "svara": "Śuddha Ṛṣabha (R2)", "ratio_num": 9, "ratio_den": 8, "svara_symbol": "R2"},
    {"index": 6, "name": "Dayāvatī", "svara": "Komal Gāndhāra (g1)", "ratio_num": 32, "ratio_den": 27, "svara_symbol": "g1"},
    {"index": 7, "name": "Rañjanī", "svara": "Komal Gāndhāra (g2)", "ratio_num": 6, "ratio_den": 5, "svara_symbol": "g2"},
    {"index": 8, "name": "Raktikā", "svara": "Śuddha Gāndhāra (G1)", "ratio_num": 5, "ratio_den": 4, "svara_symbol": "G1"},
    {"index": 9, "name": "Raudrī", "svara": "Śuddha Gāndhāra (G2)", "ratio_num": 81, "ratio_den": 64, "svara_symbol": "G2"},
    {"index": 10, "name": "Krodhā", "svara": "Śuddha Madhyama (M1)", "ratio_num": 4, "ratio_den": 3, "svara_symbol": "M1"},
    {"index": 11, "name": "Vajrikā", "svara": "Tīvra Madhyama (M2)", "ratio_num": 27, "ratio_den": 20, "svara_symbol": "M2"},
    {"index": 12, "name": "Prasāriṇī", "svara": "Tīvratara Madhyama (M3)", "ratio_num": 45, "ratio_den": 32, "svara_symbol": "M3"},
    {"index": 13, "name": "Prīti", "svara": "Tīvratama Madhyama (M4)", "ratio_num": 729, "ratio_den": 512, "svara_symbol": "M4"},
    {"index": 14, "name": "Mārjanī", "svara": "Pañcama (P)", "ratio_num": 3, "ratio_den": 2, "svara_symbol": "P"},
    {"index": 15, "name": "Kṣiti (D)", "svara": "Komal Dhaivata (d1)", "ratio_num": 128, "ratio_den": 81, "svara_symbol": "d1"},
    {"index": 16, "name": "Raktā", "svara": "Komal Dhaivata (d2)", "ratio_num": 8, "ratio_den": 5, "svara_symbol": "d2"},
    {"index": 17, "name": "Sandīpanī", "svara": "Śuddha Dhaivata (D1)", "ratio_num": 5, "ratio_den": 3, "svara_symbol": "D1"},
    {"index": 18, "name": "Ālāpinī", "svara": "Śuddha Dhaivata (D2)", "ratio_num": 27, "ratio_den": 16, "svara_symbol": "D2"},
    {"index": 19, "name": "Madantī", "svara": "Komal Niṣāda (n1)", "ratio_num": 16, "ratio_den": 9, "svara_symbol": "n1"},
    {"index": 20, "name": "Rohiṇī", "svara": "Komal Niṣāda (n2)", "ratio_num": 9, "ratio_den": 5, "svara_symbol": "n2"},
    {"index": 21, "name": "Ramyā", "svara": "Śuddha Niṣāda (N1)", "ratio_num": 15, "ratio_den": 8, "svara_symbol": "N1"},
    {"index": 22, "name": "Ugrā", "svara": "Śuddha Niṣāda (N2)", "ratio_num": 243, "ratio_den": 128, "svara_symbol": "N2"},
]


def ratio_to_cents(num: int, den: int) -> float:
    """Computes exact cents: 1200 * log2(num / den)."""
    return round(1200.0 * math.log2(num / den), 2)


def get_sruti_table(sa_hz: float = DEFAULT_SA_HZ) -> List[Dict[str, Any]]:
    """Generates the full 22-Śruti acoustic table with Hz and cents."""
    table = []
    for entry in SRUTI_CANONICAL:
        num = entry["ratio_num"]
        den = entry["ratio_den"]
        freq = round(sa_hz * (num / den), 3)
        cents = ratio_to_cents(num, den)
        
        # Microtonal offset relative to 12-TET semitones
        twelve_tet_semitone = round(cents / 100.0)
        twelve_tet_cents = twelve_tet_semitone * 100.0
        deviation_cents = round(cents - twelve_tet_cents, 2)

        table.append({
            "index": entry["index"],
            "name": entry["name"],
            "svara": entry["svara"],
            "svara_symbol": entry["svara_symbol"],
            "ratio": f"{num}/{den}",
            "frequency_hz": freq,
            "cents": cents,
            "tet_deviation_cents": deviation_cents
        })
    return table


def lookup_svara(symbol: str, sa_hz: float = DEFAULT_SA_HZ) -> Dict[str, Any]:
    """Look up an individual svara symbol (e.g. 'S', 'g1', 'G1', 'M1', 'P')."""
    sym = symbol.strip()
    table = get_sruti_table(sa_hz)
    # 1. Exact case-sensitive match on symbol first (crucial: 'g1' != 'G1')
    for item in table:
        if item["svara_symbol"] == sym:
            return item
    # 2. Case-insensitive match on name or fallback symbol
    for item in table:
        if item["name"].lower() == sym.lower() or item["svara_symbol"].lower() == sym.lower():
            return item
    return {}


import io
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage


def cents_to_midi_pitch_bend(cents_deviation: float, semitone_range: float = 2.0) -> int:
    """
    Converts cents deviation (-100 to +100) to standard 14-bit MIDI pitch bend (0 to 16383).
    8192 is center (0 deviation).
    """
    max_cents = semitone_range * 100.0
    clamped = max(-max_cents, min(max_cents, cents_deviation))
    normalized = clamped / max_cents
    bend_val = int(round(8192 + normalized * 8191))
    return max(0, min(16383, bend_val))


def generate_sruti_midi(svara_sequence: List[str], sa_midi_note: int = 60, sa_hz: float = DEFAULT_SA_HZ, tempo_bpm: int = 80) -> bytes:
    """
    Generates a Type 1 Standard MIDI file with two synchronous tracks:
    - Track 0: Melody sequence with exact 22-Śruti pitch-bend modulation
    - Track 1: Continuous 4-string Tanpura drone (Pa - Sa - Sa - Sa)
    """
    mid = MidiFile(type=1)

    # --- Track 0: Melody ---
    melody_track = MidiTrack()
    mid.tracks.append(melody_track)
    tempo = mido.bpm2tempo(tempo_bpm)
    melody_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    melody_track.append(MetaMessage('track_name', name='22-Sruti Melody', time=0))

    ticks_per_beat = mid.ticks_per_beat
    note_duration = ticks_per_beat

    for sym in svara_sequence:
        svara_info = lookup_svara(sym, sa_hz=sa_hz)
        if not svara_info:
            continue
        cents = svara_info["cents"]
        semitone_offset = int(round(cents / 100.0))
        target_note = sa_midi_note + semitone_offset
        cents_deviation = svara_info["tet_deviation_cents"]
        bend_val = cents_to_midi_pitch_bend(cents_deviation)

        melody_track.append(Message('pitchwheel', pitch=bend_val - 8192, channel=0, time=0))
        melody_track.append(Message('note_on', note=target_note, velocity=88, channel=0, time=0))
        melody_track.append(Message('note_off', note=target_note, velocity=0, channel=0, time=note_duration))

    melody_track.append(Message('pitchwheel', pitch=0, channel=0, time=0))

    # --- Track 1: Tanpura Drone ---
    tanpura_track = MidiTrack()
    mid.tracks.append(tanpura_track)
    tanpura_track.append(MetaMessage('track_name', name='Tanpura Drone', time=0))
    tanpura_track.append(Message('program_change', program=104, channel=1, time=0))  # Sitar / Tanpura timbre

    # Tanpura tuning pattern: Pa (Mandra), Sa (Madhya), Sa (Madhya), Sa (Kharja/Lower)
    drone_notes = [sa_midi_note + 7 - 12, sa_midi_note, sa_midi_note, sa_midi_note - 12]
    total_beats = max(len(svara_sequence), 4)

    for i in range(total_beats):
        note = drone_notes[i % 4]
        tanpura_track.append(Message('note_on', note=note, velocity=52, channel=1, time=0))
        tanpura_track.append(Message('note_off', note=note, velocity=0, channel=1, time=ticks_per_beat))

    bio = io.BytesIO()
    mid.save(file=bio)
    return bio.getvalue()

