from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "ui" / "tabs" / "sanskrit" / "trace"


class RuleTraceStaticTests(unittest.TestCase):
    def test_rule_trace_files_exist(self):
        self.assertTrue((TRACE / "rule-trace-map.js").exists())
        self.assertTrue((TRACE / "rule-trace-engine.js").exists())
        self.assertTrue((TRACE / "rule-trace-renderer.js").exists())

    def test_rule_trace_map_exports(self):
        content = (TRACE / "rule-trace-map.js").read_text(encoding="utf-8")
        self.assertIn("export const RULE_TRACE_NODES", content)
        self.assertIn("export const RULE_TRACE_EDGES", content)
        self.assertIn("export const RULE_TRACE_SAFETY_NOTE", content)

    def test_rule_trace_engine_exports(self):
        content = (TRACE / "rule-trace-engine.js").read_text(encoding="utf-8")
        self.assertIn("export function buildRuleTraceGraph", content)
        self.assertIn("export function inspectRuleTrace", content)

    def test_rule_trace_renderer_exports(self):
        content = (TRACE / "rule-trace-renderer.js").read_text(encoding="utf-8")
        self.assertIn("export function renderRuleTraceList", content)

    def test_controller_imports_rule_trace(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "controller.js").read_text(encoding="utf-8")
        self.assertIn(
            'import { inspectRuleTrace } from "./trace/rule-trace-engine.js";',
            content,
        )

    def test_view_contains_rule_trace_panel(self):
        content = (ROOT / "ui" / "tabs" / "sanskrit" / "view.html").read_text(encoding="utf-8")
        self.assertIn("rule-trace-panel", content)

    def test_rule_trace_engine_contains_safety_phrase(self):
        content = (TRACE / "rule-trace-engine.js").read_text(encoding="utf-8")
        self.assertIn(
            "no authoritative Paninian interpretation or grammatical correctness claim",
            content,
        )


if __name__ == "__main__":
    unittest.main()
