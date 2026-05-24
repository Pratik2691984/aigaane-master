from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHONETICS_DIR = PROJECT_ROOT / "ui" / "tabs" / "sanskrit" / "phonetics"

MAHESHVARA_PATH = PHONETICS_DIR / "maheshvara-sutras.js"
SHIVA_MAP_PATH = PHONETICS_DIR / "shiva-sutra-map.js"
PRATYAHARA_PATH = PHONETICS_DIR / "pratyahara-engine.js"


def test_maheshvara_sutra_registry_exists():
    assert MAHESHVARA_PATH.exists()


def test_maheshvara_sutra_registry_has_fourteen_sutras():
    source = MAHESHVARA_PATH.read_text(encoding="utf-8")

    assert "export const MAHESHVARA_SUTRAS" in source
    assert "index: 14" in source
    assert "हल्" in source


def test_shiva_sutra_map_exports_lookup_helpers():
    source = SHIVA_MAP_PATH.read_text(encoding="utf-8")

    assert "export function flattenMaheshvaraSounds" in source
    assert "export function mapSoundToSutraIndex" in source
    assert "export function lookupMaheshvaraSound" in source


def test_pratyahara_engine_exports_expected_helpers():
    source = PRATYAHARA_PATH.read_text(encoding="utf-8")

    assert "export function expandPratyahara" in source
    assert "export function getShivaSutraSequence" in source
    assert "Deterministic structural pratyāhāra expansion only" in source


def test_pratyahara_engine_uses_marker_boundary_logic():
    source = PRATYAHARA_PATH.read_text(encoding="utf-8")

    assert "marker: true" in source
    assert "entry.sound === marker && entry.marker" in source
    assert ".filter((entry) => !entry.marker)" in source