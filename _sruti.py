def _safe_midi_ascii(val: str) -> str:
    mapping = {'ā':'a','Ā':'A','ī':'i','Ī':'I','ū':'u','Ū':'U','ṛ':'ri','Ṛ':'Ri','ṝ':'ri','ḷ':'li','ḹ':'li','ṃ':'m','ḥ':'h','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ś':'s','ṣ':'sh'}
    s = str(val)
    for k, v in mapping.items():
        s = s.replace(k, v)
    return s.encode('ascii', errors='replace').decode('ascii')

"""
22-Sruti Microtonal Acoustic Model for Aigaane Gandharvaveda (Studio III).
Implements exact integer frequency ratios, cent calculations, and MIDI pitch-bend offsets.
"""
import math
from typing import Dict, Any, List, Tuple

# Base reference Sa = 240.0 Hz (Standard Madhyama-grāma / Gandharva baseline) or 261.63 Hz (Middle C4)
DEFAULT_SA_HZ = 240.0

# Canonical 22 Sruti Definition Table
# Index, Sruti Name, Svara, Ratio (Num/Den), Paninian / Bharata Shastra Reference
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
    """Generates the full 22-Sruti acoustic table with Hz and cents."""
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

def _sanitize_midi_text(text: str) -> str:
    """Converts Sanskrit IAST diacritics to clean Latin-1 compatible ASCII for MIDI meta events."""
    replacements = {
        'ā': 'a', 'Ā': 'A', 'ī': 'i', 'Ī': 'I', 'ū': 'u', 'Ū': 'U',
        'ṛ': 'ri', 'Ṛ': 'Ri', 'ṝ': 'ri', 'ḷ': 'li', 'ḹ': 'li',
        'ṃ': 'm', 'ḥ': 'h', 'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd',
        'ṇ': 'n', 'ś': 's', 'ṣ': 'sh'
    }
    res = text
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res.encode('latin-1', errors='replace').decode('latin-1')

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


def generate_sruti_midi(
    svara_sequence: List[Union[str, Dict[str, Any]]],
    sa_midi_note: int = 60,
    sa_hz: float = DEFAULT_SA_HZ,
    tempo_bpm: int = 80,
    include_tanpura: bool = True,
    verse_title: str = "Aigaane · Gandharvaveda"
) -> bytes:
    """
    Generates a Standard Type-1 Multi-Track MIDI binary with:
    - Track 0: Conductor (Tempo, 4/4 Time Signature, Track Title & Metadata)
    - Track 1: Sarasvati Vina / Melody with 22-Sruti Microtonal Pitch Bends
    - Track 2: Continuous 4-String Tanpura Drone (Pa - Sa - Sa - Sa_kharja)
    """
    mid = MidiFile(type=1)

    # ----------------------------------------------------
    # TRACK 0: Conductor Track (Master Tempo & Time Signature)
    # ----------------------------------------------------
    conductor = MidiTrack()
    mid.tracks.append(conductor)

    tempo = mido.bpm2tempo(tempo_bpm)
    conductor.append(MetaMessage('track_name', name=_safe_midi_ascii(f"{verse_title} (Conductor)"), time=0))
    conductor.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    conductor.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    conductor.append(MetaMessage('end_of_track', time=0))

    # ----------------------------------------------------
    # TRACK 1: Vina Melodic Pluck Sequence (Channel 0)
    # ----------------------------------------------------
    melody_track = MidiTrack()
    mid.tracks.append(melody_track)
    melody_track.append(MetaMessage('track_name', name="Sarasvati Vina (Melody)", time=0))
    melody_track.append(Message('program_change', channel=0, program=104, time=0))  # 104 = Sitar / Vina

    ticks_per_beat = mid.ticks_per_beat
    total_ticks = 0

    for item in svara_sequence:
        if isinstance(item, dict):
            sym = item.get("swara") or item.get("symbol") or "S"
            weight = item.get("weight", "L")
            dur_beats = 2.0 if weight == "G" else 1.0
            velocity = 95 if weight == "G" else 75
        else:
            sym = str(item)
            dur_beats = 1.0
            velocity = 84

        dur_ticks = int(round(dur_beats * ticks_per_beat))
        svara_info = lookup_svara(sym, sa_hz=sa_hz)
        if not svara_info:
            continue

        cents = svara_info["cents"]
        semitone_offset = int(round(cents / 100.0))
        target_note = sa_midi_note + semitone_offset
        cents_deviation = svara_info["tet_deviation_cents"]

        # Calculate 14-bit pitch bend offset (-8192 to +8191)
        bend_val = cents_to_midi_pitch_bend(cents_deviation)

        # 1. Pitch bend (delta time = 0)
        melody_track.append(Message('pitchwheel', channel=0, pitch=bend_val - 8192, time=0))
        # 2. Note-on
        melody_track.append(Message('note_on', channel=0, note=target_note, velocity=velocity, time=0))
        # 3. Note-off after syllable duration
        melody_track.append(Message('note_off', channel=0, note=target_note, velocity=0, time=dur_ticks))
        total_ticks += dur_ticks

    # Pitch wheel neutral reset
    melody_track.append(Message('pitchwheel', channel=0, pitch=0, time=0))
    melody_track.append(MetaMessage('end_of_track', time=0))

    # ----------------------------------------------------
    # TRACK 2: Continuous 4-String Tanpura Drone (Channel 1)
    # Pa (3/2) -> Madhya Sa -> Madhya Sa -> Mandra Sa
    # ----------------------------------------------------
    if include_tanpura and total_ticks > 0:
        tanpura_track = MidiTrack()
        mid.tracks.append(tanpura_track)
        tanpura_track.append(MetaMessage('track_name', name="Tanpura Drone (Accompaniment)", time=0))
        tanpura_track.append(Message('program_change', channel=1, program=104, time=0))

        # 4 strings relative to Sa: Pa (+7 st), Sa (+0 st), Sa (+0 st), Mandra Sa (-12 st)
        drone_notes = [sa_midi_note + 7, sa_midi_note, sa_midi_note, sa_midi_note - 12]
        pluck_spacing_ticks = int(round(1.2 * (ticks_per_beat * (tempo_bpm / 60.0))))
        string_decay_ticks = int(round(3.5 * (ticks_per_beat * (tempo_bpm / 60.0))))

        current_tick = 0
        str_idx = 0
        while current_tick < (total_ticks + 2 * ticks_per_beat):
            note = drone_notes[str_idx % 4]
            # Note-on on Channel 1
            tanpura_track.append(Message('note_on', channel=1, note=note, velocity=48, time=0))
            # Note-off scheduled
            tanpura_track.append(Message('note_off', channel=1, note=note, velocity=0, time=min(string_decay_ticks, pluck_spacing_ticks)))
            
            delta_advance = max(0, pluck_spacing_ticks - min(string_decay_ticks, pluck_spacing_ticks))
            if delta_advance > 0:
                # Add delay before next pluck
                tanpura_track.append(Message('control_change', channel=1, control=0, value=0, time=delta_advance))
            
            current_tick += pluck_spacing_ticks
            str_idx += 1

        tanpura_track.append(MetaMessage('end_of_track', time=0))

    bio = io.BytesIO()
    mid.save(file=bio)
    return bio.getvalue()

