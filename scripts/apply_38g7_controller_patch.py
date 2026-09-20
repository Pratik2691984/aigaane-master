"""Apply Node 38G.7 Prakriya input + live graph badge. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_STATE = "let inputNode = null;\n"
NEW_STATE = "let inputNode = null;\nlet latestAnalyzeEnvelope = null;\n"

OLD_RENDER = """function renderPayload(payload) {
  payload = normalizeAnalysisEnvelope(payload);
  renderFallbackAnalysisPanel(payload);
"""
NEW_RENDER = """function renderPayload(payload) {
  payload = normalizeAnalysisEnvelope(payload);
  latestAnalyzeEnvelope = payload;
  renderFallbackAnalysisPanel(payload);
"""

OLD_INPUT = """function buildPrakriyaCompositionInput(inputText = "") {
  const firstToken = String(inputText || "")
    .split(/\\s+/)
    .filter(Boolean)[0] || "";
  const nounInput = firstToken === "फल"
    ? { stem: "फल", stemClass: "a-stem", linga: "neuter", vibhakti: "prathama", vacana: "eka" }
    : firstToken === "सीता"
      ? { stem: "सीता", stemClass: "ā-stem", linga: "feminine", vibhakti: "prathama", vacana: "eka" }
      : { stem: "राम", stemClass: "a-stem", linga: "masculine", vibhakti: "prathama", vacana: "eka" };
  const verbInput = firstToken === "भू" || firstToken === "bhū"
    ? { dhatu: "bhū", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" }
    : firstToken === "नी" || firstToken === "nī"
      ? { dhatu: "nī", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" }
      : { dhatu: "gam", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka" };

  return {
    nounInputs: [nounInput],
    verbInput,
    enableSandhi: true,
    enableTrace: true,
    enableReversePreview: true,
  };
}
"""

NEW_INPUT = """function resolvePrakriyaSourceToken(inputText = "") {
  const candidates = [
    fieldValue("morphology-stem"),
    fieldValue("morphology-dhatu"),
    String(inputText || "").split(/\\s+/).filter(Boolean)[0] || "",
  ];
  for (const candidate of candidates) {
    const gate = toDevanagariOnlyPayload(inspectSanskritInput(candidate), "token");
    if (gate.ok) return gate.value;
  }
  return "";
}

function buildPrakriyaCompositionInput(inputText = "") {
  const firstToken = resolvePrakriyaSourceToken(inputText);
  let nounInput;
  let verbInput;
  let heuristic = false;

  if (firstToken === "फल") {
    nounInput = { stem: "फल", stemClass: "a-stem", linga: "neuter", vibhakti: "prathama", vacana: "eka", heuristic: false };
  } else if (firstToken === "सीता") {
    nounInput = { stem: "सीता", stemClass: "ā-stem", linga: "feminine", vibhakti: "prathama", vacana: "eka", heuristic: false };
  } else {
    heuristic = true;
    nounInput = { stem: firstToken, stemClass: "unclassified", linga: "", vibhakti: "prathama", vacana: "eka", heuristic: true };
  }

  if (firstToken === "भू" || firstToken === "bhū") {
    verbInput = { dhatu: "bhū", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka", heuristic: false };
  } else if (firstToken === "नी" || firstToken === "nī") {
    verbInput = { dhatu: "nī", lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka", heuristic: false };
  } else {
    heuristic = true;
    verbInput = { dhatu: firstToken, lakara: "laṭ", pada: "parasmaipada", purusha: "prathama", vacana: "eka", heuristic: true };
  }

  return {
    nounInputs: [nounInput],
    verbInput,
    enableSandhi: true,
    enableTrace: true,
    enableReversePreview: true,
    heuristic,
    previewMode: "static-preview",
  };
}
"""

OLD_TRACE = """function renderPrakriyaTraceGraphPanel(inputText = "") {
  const container = byId("prakriya-trace-graph-panel");
  const rulefireContainer = byId("rulefire-panel");
  const sutraDependencyContainer = byId("sutra-dependency-panel");
  const niruktaContainer = byId("nirukta-etymology-panel");
  if (!container && !rulefireContainer && !sutraDependencyContainer && !niruktaContainer) return;

  const execution = executePrakriya(buildPrakriyaCompositionInput(inputText));
"""

NEW_TRACE = """function renderPrakriyaLiveGraphBadge(container) {
  if (!container) return;
  const existing = container.querySelector("[data-prakriya-graph-status]");
  if (existing) existing.remove();
  const nodes = latestAnalyzeEnvelope?.prakriya_graph?.nodes;
  const live = Array.isArray(nodes) && nodes.length > 0;
  const badge = document.createElement("p");
  badge.setAttribute("data-prakriya-graph-status", "true");
  badge.className = live ? "prakriya-graph-live" : "prakriya-graph-absent";
  badge.textContent = live
    ? "prakriya_graph: live (" + nodes.length + " nodes)"
    : "prakriya_graph: absent";
  container.insertBefore(badge, container.firstChild);
}

function renderPrakriyaTraceGraphPanel(inputText = "") {
  const container = byId("prakriya-trace-graph-panel");
  const rulefireContainer = byId("rulefire-panel");
  const sutraDependencyContainer = byId("sutra-dependency-panel");
  const niruktaContainer = byId("nirukta-etymology-panel");
  if (!container && !rulefireContainer && !sutraDependencyContainer && !niruktaContainer) return;

  renderPrakriyaLiveGraphBadge(container);
  const execution = executePrakriya(buildPrakriyaCompositionInput(inputText));
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "function resolvePrakriyaSourceToken" in text and "prakriya_graph: absent" in text:
        print("already patched")
        return 0
    missing = []
    for label, block in (
        ("state", OLD_STATE),
        ("render", OLD_RENDER),
        ("input", OLD_INPUT),
        ("trace", OLD_TRACE),
    ):
        if block not in text:
            missing.append(label)
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_STATE, NEW_STATE, 1)
    text = text.replace(OLD_RENDER, NEW_RENDER, 1)
    text = text.replace(OLD_INPUT, NEW_INPUT, 1)
    text = text.replace(OLD_TRACE, NEW_TRACE, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())