from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHIKSHA_ENGINE_PATH = PROJECT_ROOT / "ui" / "tabs" / "sanskrit" / "phonetics" / "shiksha-engine.js"


def test_shiksha_engine_exists():
    assert SHIKSHA_ENGINE_PATH.exists()


def test_shiksha_engine_exports_expected_functions():
    source = SHIKSHA_ENGINE_PATH.read_text(encoding="utf-8")

    assert "export function classifyShikshaCharacter" in source
    assert "export function analyzeShikshaText" in source


def test_shiksha_engine_has_deterministic_safety_note():
    source = SHIKSHA_ENGINE_PATH.read_text(encoding="utf-8")

    assert "deterministic character classification only" in source
    assert "no audio validation" in source
    assert "Vedic accent verification" in source


def test_shiksha_engine_uses_phoneme_map_read_only():
    source = SHIKSHA_ENGINE_PATH.read_text(encoding="utf-8")

    assert 'import { SHIKSHA_PHONEME_MAP } from "./phoneme-map.js";' in source
    assert "SHIKSHA_PHONEME_MAP[value]" in source