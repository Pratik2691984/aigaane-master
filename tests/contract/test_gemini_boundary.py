"""Pillar 1 neural boundary - 8 tests verifying neural isolation invariants."""
import pytest
from aigaane.neural.schemas import SwaraSequence, SwaraToken, ChandasInput
from aigaane.neural.guards import validate_swara_sequence, validate_sanskrit_text
from aigaane.neural.confidence import cap_confidence
from aigaane.neural.gemini_swara import deterministic_fallback


def test_confidence_cap_hard_ceiling():
    assert cap_confidence(1.0) == 0.75
    assert cap_confidence(0.9) == 0.75
    assert cap_confidence(0.75) == 0.75
    assert cap_confidence(0.5) == 0.5
    assert cap_confidence(0.0) == 0.0


def test_swara_pattern_rejects_non_bhairav():
    """Shuddha Re ('R') does not exist in Bhairav."""
    with pytest.raises(ValueError):
        SwaraToken(swara="R")


def test_swara_pattern_rejects_numeric_frequencies():
    """Neural layer cannot leak frequencies, MIDI notes, or text into swara tokens."""
    for bad in ["240.0", "60", "440Hz", "C4", "komal"]:
        with pytest.raises(ValueError):
            SwaraToken(swara=bad)


def test_raga_grammar_enforced():
    """Sequence with tivra Ma (M') or shuddha Dha (D) must raise ValueError."""
    seq = SwaraSequence(
        sequence=[SwaraToken(swara="S")],
        confidence=0.5,
        rationale="valid initial",
    )
    # Manual injection of disallowed swara
    seq.sequence[0].swara = "M'"
    with pytest.raises(ValueError):
        validate_swara_sequence(seq, "Bhairav")


def test_valid_bhairav_sequence_accepted():
    seq = SwaraSequence(
        sequence=[
            SwaraToken(swara="S"),
            SwaraToken(swara="r", meend_target="G"),
            SwaraToken(swara="G"),
        ],
        confidence=0.6,
        rationale="canonical arohana opening",
    )
    result = validate_swara_sequence(seq, "Bhairav")
    assert len(result.sequence) == 3


def test_sanskrit_text_guard():
    assert validate_sanskrit_text("dharmakṣetre kurukṣetre") is True
    assert validate_sanskrit_text("धर्मक्षेत्रे कुरुक्षेत्रे") is True
    assert validate_sanskrit_text("plain english sentence") is False
    assert validate_sanskrit_text("") is False


def test_bom_sanitization():
    assert validate_sanskrit_text("\ufeffधर्मक्षेत्रे") is True


def test_deterministic_fallback_invariants():
    chandas = ChandasInput(
        verse_text="dharmakṣetre",
        syllables=["dhar", "mak", "ṣe", "tre"],
        weights=["G", "L", "G", "G"],
    )
    fallback = deterministic_fallback(chandas)
    assert fallback.confidence == 0.0
    assert len(fallback.sequence) == 4
    assert all(t.swara in {"S", "r", "G", "M", "P", "d", "N", "S'"} for t in fallback.sequence)

def test_swara_token_rejects_tivra_ma_at_construction():
    """SwaraToken regex pattern must reject non-Bhairav swaras directly at instantiation."""
    with pytest.raises(ValueError):
        SwaraToken(swara="M'")
    with pytest.raises(ValueError):
        SwaraToken(swara="D")
    with pytest.raises(ValueError):
        SwaraToken(swara="g")

