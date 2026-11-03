import pytest
import _sruti

def test_sruti_table_has_all_22_intervals():
    table = _sruti.get_sruti_table()
    assert len(table) == 22, "Must contain exactly 22 canonical śrutis."
    assert table[0]["svara_symbol"] == "S"
    assert table[0]["frequency_hz"] == 240.0
    assert table[0]["cents"] == 0.0

def test_pancama_perfect_fifth():
    # Pañcama (index 14) ratio must be 3/2 (701.96 cents)
    p = _sruti.lookup_svara("P")
    assert p["ratio"] == "3/2"
    assert abs(p["cents"] - 701.96) < 0.1
    assert p["frequency_hz"] == 360.0

def test_suddha_madhyama_perfect_fourth():
    # Śuddha Madhyama (index 10) ratio must be 4/3 (498.04 cents)
    m1 = _sruti.lookup_svara("M1")
    assert m1["ratio"] == "4/3"
    assert abs(m1["cents"] - 498.04) < 0.1

def test_pramana_sruti_difference():
    # Pramāṇa śruti is difference between R2 (9/8) and R1 (10/9) = 81/80 ~ 21.51 cents
    r1 = _sruti.lookup_svara("R1")
    r2 = _sruti.lookup_svara("R2")
    diff = r2["cents"] - r1["cents"]
    assert abs(diff - 21.51) < 0.1


def test_sruti_midi_binary_generation():
    # Kalyāṇī / Yaman svara sequence
    seq = ["S", "R2", "G2", "M2", "P", "D2", "N2"]
    data = _sruti.generate_sruti_midi(seq, sa_midi_note=60)
    assert len(data) > 0
    assert data[:4] == b"MThd", "Valid MIDI file must start with MThd header"
