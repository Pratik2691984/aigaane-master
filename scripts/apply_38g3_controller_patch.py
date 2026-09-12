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

OLD_FETCH = """      body: JSON.stringify({ input_text: inputText }),\n"""

NEW_FETCH = """      body: JSON.stringify(toAnalyzePayload(inspectedInput)),\n"""

OLD_SANDHI = """  try {\n    const data = await postJson(\"/api/v3/sandhi\", {\n      word1: fieldValue(\"sandhi-word1\"),\n      word2: fieldValue(\"sandhi-word2\"),\n    });\n"""

NEW_SANDHI = """  try {\n    const word1Gate = toDevanagariOnlyPayload(inspectSanskritInput(fieldValue(\"sandhi-word1\")), \"word1\");\n    const word2Gate = toDevanagariOnlyPayload(inspectSanskritInput(fieldValue(\"sandhi-word2\")), \"word2\");\n    if (!word1Gate.ok || !word2Gate.ok) {\n      setStatus(\"Devanagari input required for Sandhi and Morphology execution.\", true);\n      return;\n    }\n    const data = await postJson(\"/api/v3/sandhi\", {\n      word1: word1Gate.value,\n      word2: word2Gate.value,\n    });\n"""

OLD_MORPH = """  try {\n    const request = morphologyRequest();\n    const data = await postJson(request.url, request.body);\n"""

NEW_MORPH = """  try {\n    const request = morphologyRequest();\n    const gatedField = request.body.dhatu != null ? \"dhatu\" : \"stem\";\n    const gatedValue = request.body[gatedField];\n    const gate = toDevanagariOnlyPayload(inspectSanskritInput(gatedValue), gatedField);\n    if (!gate.ok) {\n      setStatus(\"Devanagari input required for Sandhi and Morphology execution.\", true);\n      return;\n    }\n    request.body[gatedField] = gate.value;\n    const data = await postJson(request.url, request.body);\n"""


def main() -> int:
    text = TARGET.read_text(encoding=\"utf-8\")
    if \"toDevanagariOnlyPayload\" in text and \"toAnalyzePayload(inspectedInput)\" in text:
        print(\"already patched\")
        return 0
    missing = []
    for label, block in (
        (\"import\", OLD_IMPORT),
        (\"analyze\", OLD_ANALYZE),
        (\"fetch\", OLD_FETCH),
        (\"sandhi\", OLD_SANDHI),
        (\"morph\", OLD_MORPH),
    ):
        if block not in text:
            missing.append(label)
    if missing:
        print(\"target blocks missing: \" + \",\".join(missing))
        return 1
    text = text.replace(OLD_IMPORT, NEW_IMPORT, 1)
    text = text.replace(OLD_ANALYZE, NEW_ANALYZE, 1)
    text = text.replace(OLD_FETCH, NEW_FETCH, 1)
    text = text.replace(OLD_SANDHI, NEW_SANDHI, 1)
    text = text.replace(OLD_MORPH, NEW_MORPH, 1)
    TARGET.write_text(text, encoding=\"utf-8\")
    print(f\"patched {TARGET}\")
    return 0


if __name__ == \"__main__\":
    raise SystemExit(main())
