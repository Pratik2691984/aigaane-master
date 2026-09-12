"""Apply Node 38G.3 controller call sites. Does not touch kernel, manifest, or 38H."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_IMPORT = 'import { inspectTransliteration } from "./phonetics/transliteration-engine.js";\n'
NEW_IMPORT = (
    'import { inspectTransliteration } from "./phonetics/transliteration-engine.js";\n'
    'import { inspectSanskritInput, toAnalyzePayload, toDevanagariOnlyPayload } from "./input/sanskrit-input-engine.js";\n'
)

OLD_ANALYZE = """  const inputText = inputNode.value.trim();\n\n  if (!inputText) {\n"""

NEW_ANALYZE = """  const inspectedInput = inspectSanskritInput(inputNode.value);\n  const inputText = inspectedInput.nfc || inspectedInput.trimmed;\n\n  if (!inputText || inspectedInput.script === \"empty\") {\n"""
