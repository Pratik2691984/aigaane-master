import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engines.dhatu_semantic_overlay import (
    build_semantic_domain_index,
    find_dhatus_by_semantic_domain,
    get_semantics_for_dhatu,
    list_semantic_domains,
    load_semantic_overlay,
    validate_semantic_overlay,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDSET_ROOT = ROOT / "data" / "sanskrit" / "goldset"
OVERLAY_PATH = GOLDSET_ROOT / "semantic_enrichment.v1.json"
GOLDSET_PATH = GOLDSET_ROOT / "goldset_metadata.v1.json"
FORBIDDEN_KEY_NAMES = {"bija", "chakra", "mantra", "deity", "sonicProfile", "vector49d", "mandala"}
FORBIDDEN_RUNTIME_IMPORTS = {
    "engines.morphology",
    "engines.sandhi",
    "engines.vyakarana",
    "engines.derivation_replay_exporter",
    "engines.replay_analytics_engine",
    "engines.trace_graph",
}


class DhatuSemanticOverlayTests(unittest.TestCase):
    def setUp(self):
        self.overlay = load_semantic_overlay(OVERLAY_PATH)
        with GOLDSET_PATH.open("r", encoding="utf-8") as handle:
            self.goldset_ids = json.load(handle)["records"]

    def test_semantic_enrichment_loads(self):
        self.assertEqual(self.overlay["goldsetVersion"], "1.0.0")
        self.assertEqual(self.overlay["semanticVersion"], "1.0.0")

    def test_every_goldset_id_has_semantic_enrichment(self):
        validate_semantic_overlay(self.overlay, self.goldset_ids)
        for dhatu_id in self.goldset_ids:
            self.assertIn(dhatu_id, self.overlay["records"])

    def test_no_forbidden_symbolic_or_sonic_keys_exist(self):
        serialized = json.dumps(self.overlay, ensure_ascii=False)

        for key in FORBIDDEN_KEY_NAMES:
            self.assertNotIn(f'"{key}"', serialized)

    def test_semantic_domain_index_contains_expected_domains(self):
        domains = set(list_semantic_domains(self.overlay))

        for domain in {"existence", "growth", "consumption", "offering", "obstruction", "exchange"}:
            self.assertIn(domain, domains)

    def test_find_existence_domain_returns_bhu(self):
        self.assertEqual(find_dhatus_by_semantic_domain(self.overlay, "existence"), ["01.0001"])

    def test_find_growth_domain_returns_edh(self):
        self.assertEqual(find_dhatus_by_semantic_domain(self.overlay, "growth"), ["01.0002"])

    def test_get_semantics_for_dhatu_returns_correct_root(self):
        self.assertEqual(
            get_semantics_for_dhatu(self.overlay, "01.0001")["root"],
            self.overlay["records"]["01.0001"]["root"],
        )
        self.assertIsNone(get_semantics_for_dhatu(self.overlay, "99.9999"))

    def test_validation_fails_if_goldset_id_is_missing(self):
        payload = copy.deepcopy(self.overlay)
        payload["records"].pop(self.goldset_ids[0])

        with self.assertRaises(ValueError):
            validate_semantic_overlay(payload, self.goldset_ids)

    def test_validation_fails_if_forbidden_keys_are_present(self):
        payload = copy.deepcopy(self.overlay)
        payload["records"]["01.0001"]["mantra"] = "forbidden"

        with self.assertRaises(ValueError):
            validate_semantic_overlay(payload, self.goldset_ids)

    def test_build_semantic_domain_index_is_stable(self):
        index = build_semantic_domain_index(self.overlay)

        self.assertEqual(index["existence"], ["01.0001"])
        self.assertEqual(index["growth"], ["01.0002"])

    def test_no_runtime_grammar_engines_are_imported(self):
        import_lines = [
            line.strip()
            for line in Path(__file__).read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

        for forbidden_import in FORBIDDEN_RUNTIME_IMPORTS:
            self.assertFalse(any(forbidden_import in line for line in import_lines), forbidden_import)


if __name__ == "__main__":
    unittest.main()
