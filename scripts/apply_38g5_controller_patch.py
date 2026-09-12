"""Apply Node 38G.5 sandhi pair-bridge in controller.js. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD = """function renderSandhiExecutionPanel(inputText = "") {
  const container = byId("sandhi-execution-panel") || byId("sandhi-transition-panel");
  if (!container) return;

  const tokens = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean)
    .map((token, index) => ({ token, index }));
  const execution = executeSandhi({
    text: inputText,
    tokens,
    mode: "static-preview",
    enableTrace: true,
    enableReversePreview: true,
  });
  renderSandhiExecution(container, execution);
}
"""

NEW = """function extractSandhiTokenPairs(tokens) {
  const pairs = [];
  const list = Array.isArray(tokens) ? tokens : [];
  for (let i = 0; i < list.length - 1; i += 1) {
    const word1 = String(list[i]?.token || list[i] || "").trim();
    const word2 = String(list[i + 1]?.token || list[i + 1] || "").trim();
    if (!word1 || !word2) continue;
    const gate1 = toDevanagariOnlyPayload(inspectSanskritInput(word1), "word1");
    const gate2 = toDevanagariOnlyPayload(inspectSanskritInput(word2), "word2");
    if (!gate1.ok || !gate2.ok) continue;
    pairs.push({ word1: gate1.value, word2: gate2.value, index: i });
  }
  return pairs;
}

function applySandhiPairToForm(pair) {
  const word1Node = byId("sandhi-word1");
  const word2Node = byId("sandhi-word2");
  if (!pair || !word1Node || !word2Node) return;
  word1Node.value = String(pair.word1 || "").normalize("NFC");
  word2Node.value = String(pair.word2 || "").normalize("NFC");
  setStatus("Sandhi pair loaded. Run Sandhi to execute.", true);
}

function renderSandhiPairChips(container, tokens) {
  if (!container) return;
  const existing = container.querySelector("[data-sandhi-pair-chips]");
  if (existing) existing.remove();

  const pairs = extractSandhiTokenPairs(tokens);
  const wrap = document.createElement("div");
  wrap.setAttribute("data-sandhi-pair-chips", "true");
  wrap.className = "sandhi-pair-chips";

  if (!pairs.length) {
    const note = document.createElement("p");
    note.className = "sandhi-pair-empty";
    note.textContent = "No adjacent Devanagari token pairs available to load into Sandhi.";
    wrap.appendChild(note);
    container.appendChild(wrap);
    return;
  }

  pairs.forEach((pair) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sandhi-pair-chip";
    button.textContent = pair.word1 + " + " + pair.word2;
    button.addEventListener("click", () => {
      applySandhiPairToForm(pair);
    });
    wrap.appendChild(button);
  });
  container.appendChild(wrap);
}

function renderSandhiExecutionPanel(inputText = "") {
  const container = byId("sandhi-execution-panel") || byId("sandhi-transition-panel");
  if (!container) return;

  const tokens = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean)
    .map((token, index) => ({ token, index }));
  const execution = executeSandhi({
    text: inputText,
    tokens,
    mode: "static-preview",
    enableTrace: true,
    enableReversePreview: true,
  });
  renderSandhiExecution(container, execution);
  renderSandhiPairChips(container, tokens);
}
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "function extractSandhiTokenPairs" in text and "renderSandhiPairChips(container, tokens)" in text:
        print("already patched")
        return 0
    if OLD not in text:
        print("target blocks missing: renderSandhiExecutionPanel")
        return 1
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())