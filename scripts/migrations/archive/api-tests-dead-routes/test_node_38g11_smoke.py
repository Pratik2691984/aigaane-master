"""Node 38G.11 static Sanskrit-tab contract smoke tests. Read-only."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"
ENGINE = ROOT / "ui" / "tabs" / "sanskrit" / "corpus" / "corpus-browser-engine.js"
KERNEL = ROOT / "api" / "kernel_api.py"
VYAKARANA = ROOT / "api" / "engines" / "vyakarana.py"
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

FORBIDDEN_CHIP_CALLS = ("fetch(", "runSandhi(", "runMorphology(", "morphologyRequest(")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_function(source: str, name: str) -> str:
    token = f"function {name}("
    start = source.find(token)
    if start < 0:
        raise AssertionError(f"missing function {name}")
    brace = source.find("{", start)
    depth = 0
    i = brace
    while i < len(source):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start : i + 1]
        i += 1
    raise AssertionError(f"unclosed function {name}")


class Node38G11SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = _read(CONTROLLER)
        cls.engine = _read(ENGINE)

    def test_chip_handlers_do_not_auto_post(self) -> None:
        sandhi = _extract_function(self.controller, "applySandhiPairToForm")
        morph = _extract_function(self.controller, "applyMorphologyTokenToForm")
        pair_click = _extract_function(self.controller, "renderSandhiPairChips")
        morph_click = _extract_function(self.controller, "renderMorphologyTokenChips")
        for block, label in (
            (sandhi, "applySandhiPairToForm"),
            (morph, "applyMorphologyTokenToForm"),
            (pair_click, "renderSandhiPairChips"),
            (morph_click, "renderMorphologyTokenChips"),
        ):
            for needle in FORBIDDEN_CHIP_CALLS:
                self.assertNotIn(needle, block, f"{label} must not call {needle}")

    def test_corpus_engine_exports_nfc_filter_sort(self) -> None:
        for name in ("nfcCorpusText", "matchesCorpusQuery", "sortCorpusResults"):
            self.assertIn(f"function {name}", self.engine)
        self.assertIn("nfcCorpusText,", self.engine)
        self.assertIn("matchesCorpusQuery,", self.engine)
        self.assertIn("sortCorpusResults", self.engine)
        self.assertIn("previewOnly: true", self.engine)
        self.assertIn("canonicalWriteAllowed: false", self.engine)

    def test_controller_has_no_bhu_empty_search_default(self) -> None:
        self.assertNotIn('query || "भू"', self.controller)
        self.assertIn("nfcCorpusText", self.controller)

    def test_absent_badges_and_trace_partition(self) -> None:
        for badge in (
            "derivation_path: absent",
            "derivation_history: absent",
            "sutra: absent",
            "chandas: absent",
        ):
            self.assertIn(badge, self.controller)
        self.assertNotIn("payload.steps", self.controller)
        self.assertNotIn("data.steps", self.controller)
        timeline = _extract_function(self.controller, "renderDerivationTimeline")
        self.assertIn("input_state", timeline)
        self.assertIn("output_state", timeline)
        self.assertNotIn("derivation_history", timeline)

    def test_kernel_and_vyakarana_present_unmodified_by_this_node(self) -> None:
        self.assertTrue(KERNEL.is_file())
        self.assertTrue(VYAKARANA.is_file())
        kernel = _read(KERNEL)
        self.assertIn("validate_devanagari_only", kernel)
        self.assertIn('/api/v3/analyze', kernel)
        self.assertIn('/api/v3/sandhi', kernel)
        ast.parse(kernel)
        ast.parse(_read(VYAKARANA))

    def test_staging_manifest_preview_only(self) -> None:
        self.assertTrue(MANIFEST.is_file())
        data = json.loads(_read(MANIFEST))
        self.assertNotEqual(data.get("previewOnly"), False)
        self.assertNotEqual(data.get("canonicalWriteAllowed"), True)
        promoted = data.get("promotedCount", data.get("promoted_count", 0))
        self.assertEqual(int(promoted or 0), 0)


if __name__ == "__main__":
    unittest.main()