"""One-shot local patch for Node 38G.1 write-hook test. Does not touch corpus or 38H."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "api" / "test_large_scale_ingestion.py"

OLD = '''        self.assertIn("Placeholder-safe", combined)
        self.assertNotIn("AIGAANE_ENABLE_CANONICAL_DHATU_WRITE", combined)
        self.assertNotIn("promote_ready_dhatu_to_canonical", combined)
'''

NEW = '''        self.assertIn("Placeholder-safe", combined)
        try:
            from api.sanskrit_ui_write_hook_scan import executable_canonical_write_bindings
        except ImportError:
            from sanskrit_ui_write_hook_scan import executable_canonical_write_bindings
        bindings = executable_canonical_write_bindings(combined)
        self.assertEqual(bindings, [])
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "executable_canonical_write_bindings(combined)" in text and "test_semantic_platform_status_ui_has_no_canonical_write_hooks" in text:
        print("already patched")
        return 0
    if OLD not in text:
        print("target block not found; no write")
        return 1
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"patched {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
