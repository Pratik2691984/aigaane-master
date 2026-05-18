// Sanskrit Tab - deterministic linguistic analysis UI.

let mountNode = null;
let analyzeButton = null;
let inputNode = null;

const DEFAULT_PAYLOAD = {
  input_text: "agnim ile purohitam yajnasya devam rtvijam hotaram ratnadhatamam",
};

function byId(id) {
  return mountNode?.querySelector(`#${id}`);
}

function setStatus(message, isError = false) {
  const status = byId("sanskrit-status");
  if (!status) return;
  status.textContent = message;
  status.classList.toggle("error", isError);
}

function clearChildren(node) {
  if (!node) return;
  while (node.firstChild) node.removeChild(node.firstChild);
}

function text(value, fallback = "-") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function setText(id, value, fallback = "-") {
  const node = byId(id);
  if (node) node.textContent = text(value, fallback);
}

function appendListItems(node, items, formatter) {
  clearChildren(node);
  if (!node) return;

  const values = Array.isArray(items) ? items : [];
  if (values.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No entries";
    node.appendChild(empty);
    return;
  }

  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter ? formatter(item) : text(item);
    node.appendChild(li);
  });
}

function renderPadas(padas) {
  const container = byId("padas-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(padas) ? padas : [];
  values.forEach((pada) => {
    const row = document.createElement("article");
    row.className = "pada-row";
    const label = document.createElement("strong");
    const content = document.createElement("span");
    const meta = document.createElement("small");
    label.textContent = text(pada.label);
    content.textContent = text(pada.text);
    meta.textContent = `${text(pada.meter)} · ${text(pada.matra_count, 0)} mātrā · ${text(pada.guru_laghu_pattern)}`;
    row.append(label, content, meta);
    container.appendChild(row);
  });
}

function renderSyllables(syllables) {
  const container = byId("phonological-syllables-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(syllables) ? syllables : [];
  values.forEach((syllable) => {
    const chip = document.createElement("span");
    const weightClass = text(syllable.weight).toLowerCase();
    const weightSymbol = weightClass === "guru" ? "G" : "L";
    chip.className = `syllable-chip ${weightClass}`;
    chip.textContent = `${text(syllable.text)}(${weightSymbol}:${text(syllable.matra_count, 0)})`;
    chip.title = `${text(syllable.weight)} syllable, cluster ${text(syllable.cluster_start)}-${text(syllable.cluster_end)}`;
    container.appendChild(chip);
  });
}

function renderGraph(graph) {
  const container = byId("prakriya-graph-output");
  clearChildren(container);
  if (!container) return;

  const nodes = Array.isArray(graph?.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph?.edges) ? graph.edges : [];

  nodes.forEach((node) => {
    const row = document.createElement("div");
    row.className = "graph-node";
    const outgoing = edges.filter((edge) => edge.from === node.id).map((edge) => edge.to).join(", ");
    row.textContent = `${text(node.label)}${outgoing ? ` -> ${outgoing}` : ""}`;
    container.appendChild(row);
  });
}

function renderLexical(entries) {
  const container = byId("lexical-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(entries) ? entries : [];
  values.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "lexical-row";
    const token = document.createElement("strong");
    const gloss = document.createElement("span");
    const lemma = document.createElement("small");
    token.textContent = text(entry.token);
    gloss.textContent = text(entry.gloss);
    lemma.textContent = text(entry.lemma);
    row.append(token, gloss, lemma);
    container.appendChild(row);
  });
}

function renderExperimental(payload) {
  const container = byId("experimental-payload-output");
  clearChildren(container);
  if (!container) return;

  const cells = Array.isArray(payload?.field_map) ? payload.field_map : [];
  cells.forEach((cell) => {
    const square = document.createElement("span");
    square.className = "symbolic-cell";
    square.textContent = text(cell.symbol);
    square.title = `structural index ${text(cell.index)}; weight ${text(cell.weight)}`;
    container.appendChild(square);
  });
}

function renderPayload(payload) {
  setText("overall-stanza-meter", payload.overall_stanza_meter);
  setText("total-matra-count", payload.total_matra_count, 0);
  setText("diagnostic-count", payload.parser_diagnostics?.length, 0);
  setText("transliteration-output", payload.transliteration);

  appendListItems(byId("sandhi-output"), payload.sandhi, (item) => `${text(item.rule)}: ${text(item.before)} -> ${text(item.after)}`);
  renderPadas(payload.padas);
  renderSyllables(payload.phonological_syllables);
  appendListItems(byId("derivation-history-output"), payload.derivation_history, (step) => `${text(step.stage)}: ${text(step.input)} -> ${text(step.output)} (${text(step.rule)})`);
  renderGraph(payload.prakriya_graph);
  renderLexical(payload.lexical_lookup);
  appendListItems(byId("parser-diagnostics-output"), payload.parser_diagnostics, (item) => `${text(item.level)}: ${text(item.message)}`);
  renderExperimental(payload.experimental_payload);
}

async function analyzeCurrentInput() {
  if (!inputNode) return;
  const inputText = inputNode.value.trim();
  if (!inputText) {
    setStatus("Enter Sanskrit text to analyze.", true);
    return;
  }

  setStatus("Analyzing...");
  analyzeButton.disabled = true;

  try {
    const response = await fetch("/api/v3/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_text: inputText }),
    });

    if (!response.ok) throw new Error(`Analysis failed with HTTP ${response.status}`);
    const payload = await response.json();
    renderPayload(payload);
    setStatus("Analysis complete");
  } catch (error) {
    console.error("[Sanskrit] Analysis error:", error);
    setStatus("Analysis unavailable", true);
  } finally {
    analyzeButton.disabled = false;
  }
}

export function init(node) {
  mountNode = node;
  analyzeButton = byId("analyze-sanskrit");
  inputNode = byId("sanskrit-input");

  analyzeButton?.addEventListener("click", analyzeCurrentInput);
  inputNode?.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      analyzeCurrentInput();
    }
  });

  renderPayload({
    overall_stanza_meter: "-",
    total_matra_count: 0,
    parser_diagnostics: [],
    transliteration: "-",
    sandhi: [],
    padas: [],
    phonological_syllables: [],
    derivation_history: [],
    prakriya_graph: { nodes: [], edges: [] },
    lexical_lookup: [],
    experimental_payload: { field_map: [] },
  });

  if (inputNode && !inputNode.value.trim()) inputNode.value = DEFAULT_PAYLOAD.input_text;
  analyzeCurrentInput();
}

export function render() {
  // The Sanskrit tab is driven by its own linguistic API payload, not shared scalar controls.
}

export function destroy() {
  analyzeButton?.removeEventListener("click", analyzeCurrentInput);
  mountNode = null;
  analyzeButton = null;
  inputNode = null;
}
