// Sanskrit Tab - deterministic linguistic analysis UI.

let mountNode = null;
let analyzeButton = null;
let sandhiButton = null;
let morphologyButton = null;
let inputNode = null;
let debugCreateButton = null;
let debugAppendButton = null;
let debugAmbiguityButton = null;
let currentDebugSession = null;

const DEFAULT_PAYLOAD = {
  input_text: "agnim ile purohitam yajnasya devam rtvijam hotaram ratnadhatamam",
};

function byId(id) {
  return mountNode?.querySelector(`#${id}`);
}

function all(selector) {
  return Array.from(mountNode?.querySelectorAll(selector) || []);
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

function fieldValue(id) {
  return byId(id)?.value.trim() || "";
}

function setBusy(button, isBusy) {
  if (button) button.disabled = isBusy;
}

function appendEmpty(node, message = "No entries") {
  if (!node) return;
  const empty = document.createElement("div");
  empty.className = "inspection-row";
  empty.textContent = message;
  node.appendChild(empty);
}

function appendInspectionRow(node, label, value, detail) {
  if (!node) return;
  const row = document.createElement("div");
  row.className = "inspection-row";
  const title = document.createElement("strong");
  title.textContent = label;
  const body = document.createElement("span");
  body.textContent = text(value);
  row.append(title, document.createTextNode(": "), body);
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }
  node.appendChild(row);
}

function appendDebugErrorRow(node, label, value) {
  appendInspectionRow(node, label, value);
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
    label.textContent = text(pada?.label);
    content.textContent = text(pada?.text);
    meta.textContent = `${text(pada?.meter)} · ${text(pada?.matra_count, 0)} matra · ${text(pada?.guru_laghu_pattern)}`;
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
    const weightClass = text(syllable?.weight).toLowerCase();
    const weightSymbol = weightClass === "guru" ? "G" : "L";
    chip.className = `syllable-chip ${weightClass}`;
    chip.textContent = `${text(syllable?.text)}(${weightSymbol}:${text(syllable?.matra_count, 0)})`;
    chip.title = `${text(syllable?.weight)} syllable, cluster ${text(syllable?.cluster_start)}-${text(syllable?.cluster_end)}`;
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
    const outgoing = edges.filter((edge) => edge?.from === node?.id).map((edge) => edge?.to).join(", ");
    row.textContent = `${text(node?.label)}${outgoing ? ` -> ${outgoing}` : ""}`;
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
    token.textContent = text(entry?.token);
    gloss.textContent = text(entry?.gloss);
    lemma.textContent = text(entry?.lemma);
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
    square.textContent = text(cell?.symbol);
    square.title = `structural index ${text(cell?.index)}; weight ${text(cell?.weight)}`;
    container.appendChild(square);
  });
}

function renderSandhiResult(data) {
  const container = byId("sandhi-result-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No sandhi result");
    return;
  }

  appendInspectionRow(container, "Merged", data.merged);
  appendInspectionRow(container, "Sutra", data.sutra, data.sutra_name);
  appendInspectionRow(container, "Type", data.type);

  const trace = Array.isArray(data.trace) ? data.trace : [];
  trace.forEach((step, index) => {
    const detail = Object.entries(step || {})
      .filter(([key]) => key !== "layer")
      .map(([key, value]) => `${key}: ${text(value)}`)
      .join("; ");
    appendInspectionRow(container, `Trace ${index + 1}`, step?.layer, detail);
  });
}

function renderMorphologyResult(data) {
  const container = byId("morphology-result-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No morphology result");
    return;
  }

  appendInspectionRow(container, "Form", data.form);
  appendInspectionRow(container, "Type", data.type);
  appendInspectionRow(container, "Rule Engine", data.rule?.engine);

  Object.entries(data.input || {}).forEach(([key, value]) => {
    appendInspectionRow(container, `Input ${key}`, value);
  });

  Object.entries(data.metadata || {}).forEach(([key, value]) => {
    const renderedValue = typeof value === "object" ? JSON.stringify(value) : value;
    appendInspectionRow(container, `Metadata ${key}`, renderedValue);
  });
}

function renderDerivationTimeline(path) {
  const container = byId("derivation-timeline-output");
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(path) ? path : [];
  if (steps.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No derivation path";
    container.appendChild(empty);
    return;
  }

  steps.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(step?.operation);
    body.textContent = ` ${text(step?.input_state)} -> ${text(step?.output_state)}`;
    meta.textContent = `${text(step?.sutra)} · ${text(step?.sutra_name)} · ${text(step?.engine_node)}`;
    item.append(title, body, meta);
    container.appendChild(item);
  });
}

function renderGovernancePanel(gov) {
  const container = byId("governance-output");
  clearChildren(container);
  if (!container) return;
  if (!gov) {
    appendEmpty(container, "No governance metadata");
    return;
  }

  appendInspectionRow(container, "Normalization", gov.normalization);
  appendInspectionRow(container, "Script Policy", gov.script_policy);
  appendInspectionRow(container, "Source", gov.source);
}

function renderAmbiguityPanel(ambiguity) {
  const container = byId("ambiguity-output");
  clearChildren(container);
  if (!container) return;
  if (!ambiguity) {
    appendEmpty(container, "No ambiguity payload");
    return;
  }

  appendInspectionRow(container, "Ambiguous", ambiguity.is_ambiguous ? "true" : "false");
  appendInspectionRow(container, "Strategy", ambiguity.strategy);
  appendInspectionRow(container, "Selected Candidate", ambiguity.selected_candidate_id || "none");

  const candidates = Array.isArray(ambiguity.candidates) ? ambiguity.candidates : [];
  if (candidates.length === 0) {
    appendEmpty(container, "No ambiguity candidates");
    return;
  }

  candidates.forEach((candidate) => {
    const row = document.createElement("div");
    row.className = "candidate-row";
    const title = document.createElement("strong");
    const output = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(candidate?.candidate_id);
    output.textContent = `: ${text(candidate?.final_output)}`;
    meta.textContent = `${text(candidate?.source_engine)} · ${text(candidate?.reason)} · confidence: ${text(candidate?.confidence, "null")}`;
    row.append(title, output, meta);
    container.appendChild(row);
  });
}

function renderApiError(detail) {
  const container = byId("api-error-output");
  clearChildren(container);
  if (!container) return;
  if (!detail) {
    appendEmpty(container, "No API error");
    return;
  }

  const errorDetail = detail.detail || detail;
  appendInspectionRow(container, "Code", errorDetail.code || "api_error");
  appendInspectionRow(container, "Message", errorDetail.message || errorDetail);

  const invalidCharacters = Array.isArray(errorDetail.invalid_characters) ? errorDetail.invalid_characters : [];
  if (invalidCharacters.length > 0) {
    appendInspectionRow(container, "Invalid Characters", invalidCharacters.join(", "));
  }
}

function renderDebugError(targetId, error) {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;
  if (!error) {
    appendEmpty(container, "No debug error");
    return;
  }

  const detail = error.detail || error;
  appendDebugErrorRow(container, "Code", detail.code || "debug_error");
  appendDebugErrorRow(container, "Message", detail.message || text(detail));
}

function renderDebugSession(session) {
  const container = byId("debug-session-output");
  clearChildren(container);
  if (!container) return;
  if (!session) {
    appendEmpty(container, "No debug session");
    return;
  }

  appendInspectionRow(container, "Session ID", session.session_id);
  appendInspectionRow(container, "Created At", session.created_at);
  appendInspectionRow(container, "Input Text", session.input_text);
  appendInspectionRow(container, "Total Steps", session.total_steps, `ambiguity branches: ${text(session.total_ambiguity_branches, 0)}`);
}

function renderDebugSessionSteps(steps) {
  const container = byId("debug-session-steps-output");
  clearChildren(container);
  if (!container) return;

  const values = Array.isArray(steps) ? steps : [];
  if (values.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No debug session steps";
    container.appendChild(empty);
    return;
  }

  values.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = `${text(step?.step_id)} ${text(step?.operation)}`;
    body.textContent = ` ${text(step?.input_state?.text)} -> ${text(step?.output_state?.text)}`;
    meta.textContent = `engine: ${text(step?.engine)}; parent: ${text(step?.parent_step_id, "none")}`;
    item.append(title, body, meta);
    container.appendChild(item);
  });
}

function appendDebugDerivationPath(node, path) {
  const steps = Array.isArray(path) ? path : [];
  steps.forEach((step, index) => {
    const meta = document.createElement("small");
    meta.textContent = `path ${index + 1}: ${text(step?.sutra)} ${text(step?.operation)} ${text(step?.input_state)} -> ${text(step?.output_state)}`;
    node.appendChild(meta);
  });
}

function renderDebugAmbiguity(ambiguity) {
  const container = byId("debug-ambiguity-output");
  clearChildren(container);
  if (!container) return;
  if (!ambiguity) {
    appendEmpty(container, "No ambiguity demo loaded");
    return;
  }

  const candidates = Array.isArray(ambiguity.candidates) ? ambiguity.candidates : [];
  appendInspectionRow(container, "Ambiguous", ambiguity.is_ambiguous ? "true" : "false");
  appendInspectionRow(container, "Candidate Count", candidates.length);

  candidates.forEach((candidate) => {
    const row = document.createElement("div");
    row.className = "candidate-row";
    const title = document.createElement("strong");
    const output = document.createElement("span");
    const reason = document.createElement("small");
    title.textContent = text(candidate?.candidate_id);
    output.textContent = `: ${text(candidate?.final_output)}`;
    reason.textContent = text(candidate?.reason);
    row.append(title, output, reason);
    appendDebugDerivationPath(row, candidate?.derivation_path);
    container.appendChild(row);
  });
}

function renderPayload(payload) {
  setText("overall-stanza-meter", payload?.overall_stanza_meter);
  setText("total-matra-count", payload?.total_matra_count, 0);
  setText("diagnostic-count", Array.isArray(payload?.parser_diagnostics) ? payload.parser_diagnostics.length : 0, 0);
  setText("transliteration-output", payload?.transliteration);

  appendListItems(byId("sandhi-output"), payload?.sandhi, (item) => `${text(item?.rule)}: ${text(item?.before)} -> ${text(item?.after)}`);
  renderPadas(payload?.padas);
  renderSyllables(payload?.phonological_syllables);
  appendListItems(byId("derivation-history-output"), payload?.derivation_history, (step) => `${text(step?.stage)}: ${text(step?.input)} -> ${text(step?.output)} (${text(step?.rule)})`);
  renderGraph(payload?.prakriya_graph);
  renderLexical(payload?.lexical_lookup);
  appendListItems(byId("parser-diagnostics-output"), payload?.parser_diagnostics, (item) => `${text(item?.level)}: ${text(item?.message)}`);
  renderExperimental(payload?.experimental_payload);
}

async function readJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload || { detail: { code: "api_error", message: `HTTP ${response.status}` } };
    renderApiError(detail);
    throw new Error(detail.detail?.message || `HTTP ${response.status}`);
  }
  renderApiError(null);
  return payload;
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJsonResponse(response);
}

async function readDebugJsonResponse(response, targetId) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload || { detail: { code: "debug_api_error", message: `HTTP ${response.status}` } };
    renderDebugError(targetId, detail);
    throw new Error(detail.detail?.message || `HTTP ${response.status}`);
  }
  renderDebugError(targetId, null);
  return payload;
}

async function postDebugJson(url, body, targetId) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readDebugJsonResponse(response, targetId);
}

async function getDebugJson(url, targetId) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readDebugJsonResponse(response, targetId);
}

async function analyzeCurrentInput() {
  if (!inputNode) return;
  const inputText = inputNode.value.trim();
  if (!inputText) {
    setStatus("Enter Sanskrit text to analyze.", true);
    return;
  }

  setStatus("Analyzing...");
  setBusy(analyzeButton, true);

  try {
    const response = await fetch("/api/v3/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input_text: inputText }),
    });
    const payload = await readJsonResponse(response);
    renderPayload(payload);
    setStatus("Analysis complete");
  } catch (error) {
    console.error("[Sanskrit] Analysis error:", error);
    setStatus("Analysis unavailable", true);
  } finally {
    setBusy(analyzeButton, false);
  }
}

async function runSandhi() {
  setStatus("Running sandhi...");
  setBusy(sandhiButton, true);

  try {
    const data = await postJson("/api/v3/sandhi", {
      word1: fieldValue("sandhi-word1"),
      word2: fieldValue("sandhi-word2"),
    });
    renderSandhiResult(data);
    renderDerivationTimeline(data?.derivation_path);
    renderGovernancePanel(data?.governance);
    renderAmbiguityPanel(data?.ambiguity);
    setStatus("Sandhi complete");
  } catch (error) {
    console.error("[Sanskrit] Sandhi error:", error);
    setStatus("Sandhi unavailable", true);
  } finally {
    setBusy(sandhiButton, false);
  }
}

function morphologyMode() {
  return all('input[name="morphology-mode"]').find((input) => input.checked)?.value || "noun";
}

function updateMorphologyFields() {
  const mode = morphologyMode();
  all("[data-morphology-fields]").forEach((node) => {
    node.classList.toggle("hidden", node.dataset.morphologyFields !== mode);
  });
}

function morphologyRequest() {
  if (morphologyMode() === "verb") {
    return {
      url: "/api/v3/morphology/verb/conjugate",
      body: {
        dhatu: fieldValue("morphology-dhatu"),
        lakara: fieldValue("morphology-lakara"),
        person: fieldValue("morphology-person"),
        number: fieldValue("morphology-verb-number"),
      },
    };
  }

  return {
    url: "/api/v3/morphology/noun/inflect",
    body: {
      stem: fieldValue("morphology-stem"),
      case: fieldValue("morphology-case"),
      number: fieldValue("morphology-number"),
    },
  };
}

async function runMorphology() {
  setStatus("Running morphology...");
  setBusy(morphologyButton, true);

  try {
    const request = morphologyRequest();
    const data = await postJson(request.url, request.body);
    renderMorphologyResult(data);
    renderDerivationTimeline(data?.derivation_path);
    renderGovernancePanel(data?.governance);
    renderAmbiguityPanel(data?.ambiguity);
    setStatus("Morphology complete");
  } catch (error) {
    console.error("[Sanskrit] Morphology error:", error);
    setStatus("Morphology unavailable", true);
  } finally {
    setBusy(morphologyButton, false);
  }
}

async function handleDebugSessionCreate() {
  setStatus("Creating debug session...");
  setBusy(debugCreateButton, true);

  try {
    currentDebugSession = await postDebugJson(
      "/api/v3/debug/session/create",
      {
        input_text: fieldValue("debug-session-input"),
        metadata: { source: "sanskrit_tab_debug_ui" },
      },
      "debug-session-error-output",
    );
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    setStatus("Debug session created");
  } catch (error) {
    console.error("[Sanskrit] Debug session create error:", error);
    setStatus("Debug session unavailable", true);
  } finally {
    setBusy(debugCreateButton, false);
  }
}

async function handleDebugSessionAppend() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session before appending a step.",
      },
    });
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Appending debug step...");
  setBusy(debugAppendButton, true);

  try {
    const steps = Array.isArray(currentDebugSession.steps) ? currentDebugSession.steps : [];
    const lastStep = steps.length > 0 ? steps[steps.length - 1] : null;
    currentDebugSession = await postDebugJson(
      "/api/v3/debug/session/append",
      {
        session: currentDebugSession,
        step: {
          engine: "debug.ui",
          operation: "manual_debug_step",
          input_state: { text: "debug-input" },
          output_state: { text: "debug-output" },
          parent_step_id: lastStep?.step_id || null,
          derivation_path: [],
          metadata: { source: "sanskrit_tab_debug_ui" },
        },
      },
      "debug-session-error-output",
    );
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    setStatus("Debug step appended");
  } catch (error) {
    console.error("[Sanskrit] Debug session append error:", error);
    setStatus("Debug append unavailable", true);
  } finally {
    setBusy(debugAppendButton, false);
  }
}

async function handleDebugAmbiguityDemo() {
  setStatus("Loading ambiguity demo...");
  setBusy(debugAmbiguityButton, true);

  try {
    const ambiguity = await getDebugJson("/api/v3/debug/ambiguity-demo", "debug-session-error-output");
    renderDebugAmbiguity(ambiguity);
    setStatus("Ambiguity demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Debug ambiguity error:", error);
    setStatus("Ambiguity demo unavailable", true);
  } finally {
    setBusy(debugAmbiguityButton, false);
  }
}

function renderInitialState() {
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
  renderSandhiResult(null);
  renderMorphologyResult(null);
  renderDerivationTimeline(null);
  renderGovernancePanel(null);
  renderAmbiguityPanel(null);
  renderApiError(null);
  renderDebugSession(null);
  renderDebugSessionSteps(null);
  renderDebugAmbiguity(null);
  renderDebugError("debug-session-error-output", null);
}

export function init(node) {
  mountNode = node;
  analyzeButton = byId("analyze-sanskrit");
  sandhiButton = byId("run-sandhi");
  morphologyButton = byId("run-morphology");
  debugCreateButton = byId("debug-create-session");
  debugAppendButton = byId("debug-append-step");
  debugAmbiguityButton = byId("debug-load-ambiguity");
  inputNode = byId("sanskrit-input");

  analyzeButton?.addEventListener("click", analyzeCurrentInput);
  sandhiButton?.addEventListener("click", runSandhi);
  morphologyButton?.addEventListener("click", runMorphology);
  debugCreateButton?.addEventListener("click", handleDebugSessionCreate);
  debugAppendButton?.addEventListener("click", handleDebugSessionAppend);
  debugAmbiguityButton?.addEventListener("click", handleDebugAmbiguityDemo);
  all('input[name="morphology-mode"]').forEach((input) => input.addEventListener("change", updateMorphologyFields));
  inputNode?.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      analyzeCurrentInput();
    }
  });

  renderInitialState();
  updateMorphologyFields();

  if (inputNode && !inputNode.value.trim()) inputNode.value = DEFAULT_PAYLOAD.input_text;
  analyzeCurrentInput();
}

export function render() {
  // The Sanskrit tab is driven by its own linguistic API payload, not shared scalar controls.
}

export function destroy() {
  analyzeButton?.removeEventListener("click", analyzeCurrentInput);
  sandhiButton?.removeEventListener("click", runSandhi);
  morphologyButton?.removeEventListener("click", runMorphology);
  debugCreateButton?.removeEventListener("click", handleDebugSessionCreate);
  debugAppendButton?.removeEventListener("click", handleDebugSessionAppend);
  debugAmbiguityButton?.removeEventListener("click", handleDebugAmbiguityDemo);
  all('input[name="morphology-mode"]').forEach((input) => input.removeEventListener("change", updateMorphologyFields));
  mountNode = null;
  analyzeButton = null;
  sandhiButton = null;
  morphologyButton = null;
  debugCreateButton = null;
  debugAppendButton = null;
  debugAmbiguityButton = null;
  currentDebugSession = null;
  inputNode = null;
}
