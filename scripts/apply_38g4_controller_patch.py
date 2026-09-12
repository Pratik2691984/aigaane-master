"""Apply Node 38G.4 controller envelope wiring. Does not touch kernel, manifest, or 38H."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_IMPORT = (
    'import { inspectSanskritInput, toAnalyzePayload, toDevanagariOnlyPayload } '
    'from "./input/sanskrit-input-engine.js";\n'
)
NEW_IMPORT = (
    'import { inspectSanskritInput, toAnalyzePayload, toDevanagariOnlyPayload } '
    'from "./input/sanskrit-input-engine.js";\n'
    'import { normalizeAnalysisEnvelope } from "./input/sanskrit-analysis-envelope.js";\n'
)

OLD_NORM = """function normalizeSanskritFallbackInput(inputText) {
  return text(inputText, "")
    .trim()
    .replace(/\\s+/g, " ")
    .toLowerCase();
}
"""
NEW_NORM = """function normalizeSanskritFallbackInput(inputText) {
  return text(inputText, "")
    .trim()
    .replace(/\\s+/g, " ");
}
"""

OLD_RENDER = """function renderPayload(payload) {
  renderFallbackAnalysisPanel(payload);
"""
NEW_RENDER = """function renderPayload(payload) {
  payload = normalizeAnalysisEnvelope(payload);
  renderFallbackAnalysisPanel(payload);
"""

OLD_PANEL = """  const isFallback = payload?.pipelineStatus?.mode === "local-fallback";

  if (panel) panel.classList.toggle("hidden", !isFallback);
  if (!isFallback) return;

  if (badge) badge.textContent = "Local fallback";
  if (explanation) {
    explanation.textContent = text(
      payload?.pipelineStatus?.backendUnavailableExplanation,
      "The backend analysis route was unavailable, so a deterministic local fallback was rendered.",
    );
  }

  clearChildren(stages);
  const stageValues = Array.isArray(payload?.pipelineStatus?.stages) ? payload.pipelineStatus.stages : [];
"""
NEW_PANEL = """  const fallbackMeta = payload?.client_fallback || payload;
  const isFallback = fallbackMeta?.pipelineStatus?.mode === "local-fallback";

  if (panel) panel.classList.toggle("hidden", !isFallback);
  if (!isFallback) return;

  if (badge) badge.textContent = "Local fallback";
  if (explanation) {
    explanation.textContent = text(
      fallbackMeta?.pipelineStatus?.backendUnavailableExplanation,
      "The backend analysis route was unavailable, so a deterministic local fallback was rendered.",
    );
  }

  clearChildren(stages);
  const stageValues = Array.isArray(fallbackMeta?.pipelineStatus?.stages) ? fallbackMeta.pipelineStatus.stages : [];
"""

OLD_TOKENS = """  const tokenValues = Array.isArray(payload?.tokenization?.tokens) ? payload.tokenization.tokens : [];
"""
NEW_TOKENS = """  const tokenValues = Array.isArray(fallbackMeta?.tokenization?.tokens) ? fallbackMeta.tokenization.tokens : [];
"""

OLD_SAFETY = """  if (safety) safety.textContent = text(payload?.safety_note);
"""
NEW_SAFETY = """  if (safety) safety.textContent = text(fallbackMeta?.safety_note);
"""

OLD_RETURN = "  return {\n    input_text: inputText,\n    normalized_input: normalizedInput,\n    pipelineStatus: {"
NEW_RETURN = "  return normalizeAnalysisEnvelope({\n    input_text: inputText,\n    normalized_input: normalizedInput,\n    pipelineStatus: {"

OLD_END = """    experimental_payload: {
      field_map: tokens.map((tokenValue, index) => ({
        symbol: tokenValue.slice(0, 1) || "-",
        token: tokenValue,
        index,
      })),
    },
  };
}
"""
NEW_END = """    experimental_payload: {
      field_map: tokens.map((tokenValue, index) => ({
        symbol: tokenValue.slice(0, 1) || "-",
        token: tokenValue,
        index,
      })),
    },
  });
}
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "normalizeAnalysisEnvelope(payload)" in text and "client_fallback || payload" in text:
        print("already patched")
        return 0
    missing = []
    blocks = {
        "import": OLD_IMPORT,
        "norm": OLD_NORM,
        "render": OLD_RENDER,
        "panel": OLD_PANEL,
        "tokens": OLD_TOKENS,
        "safety": OLD_SAFETY,
        "return": OLD_RETURN,
        "end": OLD_END,
    }
    for label, block in blocks.items():
        if block not in text:
            missing.append(label)
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_IMPORT, NEW_IMPORT, 1)
    text = text.replace(OLD_NORM, NEW_NORM, 1)
    text = text.replace(OLD_RENDER, NEW_RENDER, 1)
    text = text.replace(OLD_PANEL, NEW_PANEL, 1)
    text = text.replace(OLD_TOKENS, NEW_TOKENS, 1)
    text = text.replace(OLD_SAFETY, NEW_SAFETY, 1)
    text = text.replace(OLD_RETURN, NEW_RETURN, 1)
    text = text.replace(OLD_END, NEW_END, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())