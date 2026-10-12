"""Apply Node 38G.6 morphology token-bridge in controller.js. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD = """function renderSubantaGeneratorPanel(inputText = "") {
  const container = byId("subanta-generator-panel");
  if (!container) return;

  const stem = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean)[0] || "";
  const generation = generateSubanta({
    stem,
    vibhakti: "prathama",
    vacana: "eka",
    enableTrace: true,
    enableReversePreview: true,
  });

  renderSubanta(container, generation);
}
"""

NEW = """function extractMorphologyTokens(inputText) {
  const tokens = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean);
  const accepted = [];
  tokens.forEach((token, index) => {
    const gate = toDevanagariOnlyPayload(inspectSanskritInput(token), "token");
    if (!gate.ok) return;
    accepted.push({ token: gate.value, index });
  });
  return accepted;
}

function applyMorphologyTokenToForm(tokenValue) {
  const nfc = String(tokenValue || "").normalize("NFC");
  const mode = morphologyMode();
  const targetId = mode === "verb" ? "morphology-dhatu" : "morphology-stem";
  const node = byId(targetId);
  if (!node) return;
  node.value = nfc;
  setStatus("Morphology " + (mode === "verb" ? "dhatu" : "stem") + " loaded. Run Morphology to execute.", true);
}

function renderMorphologyTokenChips(container, inputText) {
  if (!container) return;
  const existing = container.querySelector("[data-morphology-token-chips]");
  if (existing) existing.remove();

  const tokens = extractMorphologyTokens(inputText);
  const wrap = document.createElement("div");
  wrap.setAttribute("data-morphology-token-chips", "true");
  wrap.className = "morphology-token-chips";

  if (!tokens.length) {
    const note = document.createElement("p");
    note.className = "morphology-token-empty";
    note.textContent = "No Devanagari tokens available to load into Morphology.";
    wrap.appendChild(note);
    container.appendChild(wrap);
    return;
  }

  tokens.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "morphology-token-chip";
    button.textContent = item.token;
    button.addEventListener("click", () => {
      applyMorphologyTokenToForm(item.token);
    });
    wrap.appendChild(button);
  });
  container.appendChild(wrap);
}

function renderSubantaGeneratorPanel(inputText = "") {
  const container = byId("subanta-generator-panel");
  if (!container) return;

  const stem = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean)[0] || "";
  const generation = generateSubanta({
    stem,
    vibhakti: "prathama",
    vacana: "eka",
    enableTrace: true,
    enableReversePreview: true,
  });

  renderSubanta(container, generation);
  renderMorphologyTokenChips(container, inputText);
}
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "function extractMorphologyTokens" in text and "renderMorphologyTokenChips(container, inputText)" in text:
        print("already patched")
        return 0
    if OLD not in text:
        print("target blocks missing: renderSubantaGeneratorPanel")
        return 1
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())