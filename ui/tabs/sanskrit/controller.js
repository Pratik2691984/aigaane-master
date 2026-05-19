// Sanskrit Tab - deterministic linguistic analysis UI.

let mountNode = null;
let analyzeButton = null;
let sandhiButton = null;
let morphologyButton = null;
let inputNode = null;
let debugCreateButton = null;
let debugAppendButton = null;
let debugAmbiguityButton = null;
let debugPipelineButton = null;
let debugSaveButton = null;
let debugRefreshSessionsButton = null;
let lexiconSamplesButton = null;
let lexiconSourcesButton = null;
let lexiconValidateButton = null;
let sutraSamplesButton = null;
let sutraSourcesButton = null;
let sutraValidateButton = null;
let semanticTraceDemoButton = null;
let semanticTraceCustomButton = null;
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
    const input = step?.input_state || {};
    const output = step?.output_state || {};
    const inputText = input.text || input.word1 || input.request?.stem || JSON.stringify(input);
    const outputText = output.text || output.merged || output.form || JSON.stringify(output);
    title.textContent = `${text(step?.step_id)} ${text(step?.operation)}`;
    body.textContent = ` ${text(inputText)} -> ${text(outputText)}`;
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

function renderDebugPipelineResult(data) {
  const container = byId("debug-pipeline-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No pipeline run");
    return;
  }

  appendInspectionRow(container, "Final Output", data.final_output || "No final output");

  const pipelineSteps = Array.isArray(data.pipeline_steps) ? data.pipeline_steps : [];
  if (pipelineSteps.length === 0) {
    appendEmpty(container, "No pipeline steps returned");
    return;
  }

  pipelineSteps.forEach((step, index) => {
    const output = step?.output_state || {};
    const renderedOutput = output.merged || output.form || JSON.stringify(output);
    appendInspectionRow(
      container,
      `Step ${index + 1}`,
      renderedOutput,
      `${text(step?.engine)} · ${text(step?.operation)}`,
    );
  });
}

function pipelineDataFromSession(session) {
  const steps = Array.isArray(session?.steps) ? session.steps : [];
  const pipelineSteps = steps.filter((step) => step?.metadata?.source === "debug_session_pipeline");
  if (pipelineSteps.length === 0) return null;
  const lastStep = pipelineSteps[pipelineSteps.length - 1];
  const output = lastStep?.output_state || {};
  return {
    final_output: output.merged || output.form || "",
    pipeline_steps: pipelineSteps,
  };
}

function renderDebugStorageStatus(message, type = "neutral") {
  const node = byId("debug-storage-status");
  if (!node) return;
  node.textContent = text(message, "Storage idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderDebugSessionStorageList(data) {
  const container = byId("debug-storage-list");
  clearChildren(container);
  if (!container) return;

  const sessions = Array.isArray(data?.sessions) ? [...data.sessions] : [];
  if (sessions.length === 0) {
    appendEmpty(container, "No saved sessions");
    return;
  }

  sessions.sort((left, right) => text(right?.created_at, "").localeCompare(text(left?.created_at, "")));

  sessions.forEach((session) => {
    const row = document.createElement("div");
    row.className = "debug-storage-row";

    const meta = document.createElement("div");
    meta.className = "debug-storage-meta";
    const sessionId = document.createElement("strong");
    const details = document.createElement("small");
    sessionId.textContent = text(session?.session_id, "unknown-session");
    details.textContent = `${text(session?.created_at, "created_at unavailable")} - steps: ${text(session?.step_count, "unknown")}`;
    meta.append(sessionId, details);

    const actions = document.createElement("div");
    actions.className = "debug-storage-actions";
    const loadButton = document.createElement("button");
    loadButton.type = "button";
    loadButton.textContent = "Load";
    loadButton.addEventListener("click", () => handleDebugSessionLoad(session?.session_id));

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => handleDebugSessionDelete(session?.session_id));
    actions.append(loadButton, deleteButton);

    row.append(meta, actions);
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

async function readLexiconJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail || payload || {};
    throw new Error(detail.message || `HTTP ${response.status}`);
  }
  return payload;
}

async function getLexiconJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function getSutraJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

async function postSemanticTraceJson(url, body) {
  let response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }
  return readLexiconJsonResponse(response);
}

async function getSemanticTraceJson(url) {
  let response = await fetch(url);
  const isLocalFrontend = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
  if (!response.ok && response.status === 404 && isLocalFrontend && url.startsWith("/api/")) {
    response = await fetch(`http://127.0.0.1:8000${url}`);
  }
  return readLexiconJsonResponse(response);
}

function renderLexiconStatus(message, type = "neutral") {
  const node = byId("lexicon-status");
  if (!node) return;
  node.textContent = text(message, "Lexicon idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderLexiconError(message) {
  renderLexiconStatus(message || "Lexicon request failed", "error");
}

function renderLexiconSamples(data) {
  const container = byId("lexicon-samples-output");
  clearChildren(container);
  if (!container) return;

  const entries = Array.isArray(data?.entries) ? data.entries : [];
  if (entries.length === 0) {
    appendEmpty(container, "No sample entries");
    return;
  }

  entries.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "lexicon-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(entry?.lemma_devanagari);
    body.textContent = ` ${text(entry?.lemma_iast)} · ${text(entry?.category)}`;
    meta.textContent = `${text(entry?.lexical_id)} · status: ${text(entry?.status)}`;
    row.append(title, body, meta);
    container.appendChild(row);
  });
}

function renderLexiconSources(data) {
  const container = byId("lexicon-sources-output");
  clearChildren(container);
  if (!container) return;

  const sources = Array.isArray(data?.sources) ? data.sources : [];
  if (sources.length === 0) {
    appendEmpty(container, "No registry sources");
    return;
  }

  sources.forEach((source) => {
    const row = document.createElement("div");
    row.className = "lexicon-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const badge = document.createElement("span");
    const citation = document.createElement("small");
    title.textContent = text(source?.name);
    body.textContent = ` ${text(source?.type)}`;
    badge.className = `lexicon-badge ${source?.verified ? "verified" : "draft"}`;
    badge.textContent = source?.verified ? "verified" : "unverified";
    citation.textContent = text(source?.citation, "No citation");
    row.append(title, body, badge, citation);
    container.appendChild(row);
  });
}

function renderLexiconValidation(data) {
  const container = byId("lexicon-validation-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No validation run");
    return;
  }

  const summary = document.createElement("div");
  summary.className = `lexicon-validation-summary ${data.valid ? "success" : "error"}`;
  summary.textContent = `valid: ${data.valid === true ? "true" : "false"} · entries: ${text(data.entry_count, 0)}`;
  container.appendChild(summary);

  const ids = Array.isArray(data.validated_ids) ? data.validated_ids : [];
  appendInspectionRow(container, "Validated IDs", ids.length > 0 ? ids.join(", ") : "none");

  const errors = Array.isArray(data.errors) ? data.errors : [];
  if (errors.length === 0) {
    appendInspectionRow(container, "Errors", "none");
    renderLexiconStatus("Registry validation passed", "success");
    return;
  }

  errors.forEach((error, index) => {
    appendInspectionRow(container, `Error ${index + 1}`, typeof error === "object" ? JSON.stringify(error) : error);
  });
}

function renderSutraStatus(message, type = "neutral") {
  const node = byId("sutra-status");
  if (!node) return;
  node.textContent = text(message, "Sutra registry idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderSutraError(message) {
  renderSutraStatus(message || "Sutra registry request failed", "error");
}

function renderSutraSamples(data) {
  const container = byId("sutra-samples-output");
  clearChildren(container);
  if (!container) return;

  const sutras = Array.isArray(data?.sutras) ? data.sutras : [];
  if (sutras.length === 0) {
    appendEmpty(container, "No operational sutras");
    return;
  }

  sutras.forEach((sutra) => {
    const row = document.createElement("div");
    row.className = "sutra-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const domain = document.createElement("span");
    const status = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(sutra?.sutra_id);
    body.textContent = ` ${text(sutra?.sutra_text_devanagari)} · ${text(sutra?.sutra_text_iast)}`;
    domain.className = "sutra-badge domain";
    domain.textContent = text(sutra?.domain, "unknown");
    status.className = `sutra-badge ${sutra?.status === "canonical" ? "canonical" : "provisional"}`;
    status.textContent = text(sutra?.status, "unknown");
    meta.textContent = `${text(sutra?.source)} · ${text(sutra?.source_type)}`;
    row.append(title, body, domain, status, meta);
    container.appendChild(row);
  });
}

function renderSutraSources(data) {
  const container = byId("sutra-sources-output");
  clearChildren(container);
  if (!container) return;

  const sources = Array.isArray(data?.sources) ? data.sources : [];
  if (sources.length === 0) {
    appendEmpty(container, "No sutra sources");
    return;
  }

  sources.forEach((source) => {
    const row = document.createElement("div");
    row.className = "sutra-row";
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const badge = document.createElement("span");
    const provenance = document.createElement("small");
    title.textContent = text(source?.name);
    body.textContent = ` ${text(source?.source_type || source?.type, "unknown")}`;
    badge.className = "sutra-badge canonical";
    badge.textContent = text(source?.verified === false ? "unverified" : "governed");
    provenance.textContent = text(source?.provenance || source?.description || source?.citation, "No provenance");
    row.append(title, body, badge, provenance);
    container.appendChild(row);
  });
}

function renderSutraValidation(data) {
  const container = byId("sutra-validation-output");
  clearChildren(container);
  if (!container) return;
  if (!data) {
    appendEmpty(container, "No validation run");
    return;
  }

  const summary = document.createElement("div");
  summary.className = `sutra-validation-summary ${data.valid ? "success" : "error"}`;
  summary.textContent = `valid: ${data.valid === true ? "true" : "false"} · sutras: ${text(data.sutra_count, 0)}`;
  container.appendChild(summary);

  const ids = Array.isArray(data.validated_ids) ? data.validated_ids : [];
  appendInspectionRow(container, "Validated IDs", ids.length > 0 ? ids.join(", ") : "none");

  const errors = Array.isArray(data.errors) ? data.errors : [];
  if (errors.length === 0) {
    appendInspectionRow(container, "Errors", "none");
    renderSutraStatus("Sutra registry validation passed", "success");
    return;
  }

  errors.forEach((error, index) => {
    appendInspectionRow(container, `Error ${index + 1}`, typeof error === "object" ? JSON.stringify(error) : error);
  });
}

function renderSemanticTraceStatus(message, type = "neutral") {
  const node = byId("semantic-trace-status");
  if (!node) return;
  node.textContent = text(message, "Semantic trace idle");
  node.classList.toggle("success", type === "success");
  node.classList.toggle("error", type === "error");
}

function renderSemanticTraceError(message) {
  renderSemanticTraceStatus(message || "Semantic trace request failed", "error");
}

function renderSemanticTraceStep(step) {
  const row = document.createElement("div");
  row.className = "semantic-trace-row";

  const title = document.createElement("strong");
  const sutra = document.createElement("span");
  title.textContent = text(step?.operation, "unknown_operation");
  sutra.textContent = ` sutra: ${text(step?.sutra, "unresolved")}`;
  row.append(title, sutra);

  const ref = step?.sutra_ref || null;
  if (!ref) {
    const unresolved = document.createElement("small");
    unresolved.className = "semantic-trace-unresolved";
    unresolved.textContent = "unresolved canonical sutra reference";
    row.appendChild(unresolved);
    return row;
  }

  const metadata = document.createElement("div");
  metadata.className = "semantic-sutra-metadata";

  const devanagari = document.createElement("span");
  const iast = document.createElement("small");
  const domain = document.createElement("span");
  const status = document.createElement("span");
  devanagari.textContent = text(ref.sutra_text_devanagari);
  iast.textContent = text(ref.sutra_text_iast);
  domain.className = "semantic-trace-badge domain";
  domain.textContent = text(ref.domain, "unknown");
  status.className = `semantic-trace-badge ${ref.status === "canonical" ? "canonical" : "provisional"}`;
  status.textContent = text(ref.status, "unknown");
  metadata.append(devanagari, iast, domain, status);
  row.appendChild(metadata);
  return row;
}

function renderSemanticTrace(trace, targetId = "semantic-trace-linked-output") {
  const container = byId(targetId);
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(trace) ? trace : [];
  if (steps.length === 0) {
    appendEmpty(container, "No semantic trace steps");
    return;
  }

  steps.forEach((step) => {
    container.appendChild(renderSemanticTraceStep(step));
  });
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

async function handleDebugPipelineDemo() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session first.",
      },
    });
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Running debug pipeline...");
  setBusy(debugPipelineButton, true);

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/run-pipeline",
      {
        session: currentDebugSession,
        pipeline: [
          {
            engine: "morphology",
            request: {
              mode: "noun",
              stem: "राम",
              case: "nominative",
              number: "singular",
            },
          },
          {
            engine: "sandhi",
            request: {
              word2: "अस्ति",
            },
          },
        ],
      },
      "debug-session-error-output",
    );
    currentDebugSession = data?.session || currentDebugSession;
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    renderDebugPipelineResult(data);
    setStatus("Debug pipeline complete");
  } catch (error) {
    console.error("[Sanskrit] Debug pipeline error:", error);
    setStatus("Debug pipeline unavailable", true);
  } finally {
    setBusy(debugPipelineButton, false);
  }
}

async function handleDebugSessionSave() {
  if (!currentDebugSession) {
    renderDebugError("debug-session-error-output", {
      detail: {
        code: "debug_session_missing",
        message: "Create a debug session first.",
      },
    });
    renderDebugStorageStatus("Create a debug session first.", "error");
    setStatus("Create a debug session first.", true);
    return;
  }

  setStatus("Saving debug session...");
  renderDebugStorageStatus("Saving session...");
  setBusy(debugSaveButton, true);

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/save",
      { session: currentDebugSession },
      "debug-session-error-output",
    );
    renderDebugStorageStatus(`Saved ${text(data?.session_id, "session")}`, "success");
    await handleDebugSessionList();
    setStatus("Debug session saved");
  } catch (error) {
    console.error("[Sanskrit] Debug session save error:", error);
    renderDebugStorageStatus("Save unavailable", "error");
    setStatus("Debug save unavailable", true);
  } finally {
    setBusy(debugSaveButton, false);
  }
}

async function handleDebugSessionList() {
  setStatus("Refreshing saved sessions...");
  renderDebugStorageStatus("Refreshing saved sessions...");
  setBusy(debugRefreshSessionsButton, true);

  try {
    const data = await getDebugJson("/api/v3/debug/session/list", "debug-session-error-output");
    renderDebugSessionStorageList(data);
    const count = Array.isArray(data?.sessions) ? data.sessions.length : 0;
    renderDebugStorageStatus(`${count} saved session${count === 1 ? "" : "s"}`, "success");
    setStatus("Saved sessions refreshed");
  } catch (error) {
    console.error("[Sanskrit] Debug session list error:", error);
    renderDebugStorageStatus("Saved sessions unavailable", "error");
    setStatus("Saved sessions unavailable", true);
  } finally {
    setBusy(debugRefreshSessionsButton, false);
  }
}

async function handleDebugSessionLoad(sessionId) {
  if (!sessionId) {
    renderDebugStorageStatus("Cannot load session without an id.", "error");
    return;
  }

  setStatus("Loading saved session...");
  renderDebugStorageStatus("Loading saved session...");

  try {
    const data = await postDebugJson(
      "/api/v3/debug/session/load",
      { session_id: sessionId },
      "debug-session-error-output",
    );
    currentDebugSession = data?.session || null;
    const branches = Array.isArray(currentDebugSession?.ambiguity_branches) ? currentDebugSession.ambiguity_branches : [];
    renderDebugSession(currentDebugSession);
    renderDebugSessionSteps(currentDebugSession?.steps);
    renderDebugAmbiguity(branches.length > 0 ? { is_ambiguous: branches.length > 1, candidates: branches } : null);
    renderDebugPipelineResult(pipelineDataFromSession(currentDebugSession));
    renderDebugStorageStatus(`Loaded ${text(currentDebugSession?.session_id, "session")}`, "success");
    setStatus("Saved session loaded");
  } catch (error) {
    console.error("[Sanskrit] Debug session load error:", error);
    renderDebugStorageStatus("Load unavailable", "error");
    setStatus("Debug load unavailable", true);
  }
}

async function handleDebugSessionDelete(sessionId) {
  if (!sessionId) {
    renderDebugStorageStatus("Cannot delete session without an id.", "error");
    return;
  }

  setStatus("Deleting saved session...");
  renderDebugStorageStatus("Deleting saved session...");

  try {
    await postDebugJson(
      "/api/v3/debug/session/delete",
      { session_id: sessionId },
      "debug-session-error-output",
    );
    renderDebugStorageStatus("Deleted saved session", "success");
    await handleDebugSessionList();
    setStatus("Saved session deleted");
  } catch (error) {
    console.error("[Sanskrit] Debug session delete error:", error);
    renderDebugStorageStatus("Delete unavailable", "error");
    setStatus("Debug delete unavailable", true);
  }
}

async function handleLoadLexiconSamples() {
  setStatus("Loading lexical samples...");
  renderLexiconStatus("Loading sample entries...");
  setBusy(lexiconSamplesButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/samples");
    renderLexiconSamples(data);
    renderLexiconStatus(`${text(data?.count, 0)} sample entries loaded`, "success");
    setStatus("Lexical samples loaded");
  } catch (error) {
    console.error("[Sanskrit] Lexicon samples error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon samples unavailable", true);
  } finally {
    setBusy(lexiconSamplesButton, false);
  }
}

async function handleLoadLexiconSources() {
  setStatus("Loading lexical sources...");
  renderLexiconStatus("Loading registry sources...");
  setBusy(lexiconSourcesButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/sources");
    renderLexiconSources(data);
    renderLexiconStatus(`${text(data?.count, 0)} registry sources loaded`, "success");
    setStatus("Lexical sources loaded");
  } catch (error) {
    console.error("[Sanskrit] Lexicon sources error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon sources unavailable", true);
  } finally {
    setBusy(lexiconSourcesButton, false);
  }
}

async function handleValidateLexiconRegistry() {
  setStatus("Validating lexical registry...");
  renderLexiconStatus("Validating registry...");
  setBusy(lexiconValidateButton, true);

  try {
    const data = await getLexiconJson("/api/v3/debug/lexicon/validate");
    renderLexiconValidation(data);
    if (data?.valid === true) {
      renderLexiconStatus("Registry validation passed", "success");
      setStatus("Lexical registry valid");
    } else {
      renderLexiconStatus("Registry validation found issues", "error");
      setStatus("Lexical registry validation issues", true);
    }
  } catch (error) {
    console.error("[Sanskrit] Lexicon validation error:", error);
    renderLexiconError(error.message);
    setStatus("Lexicon validation unavailable", true);
  } finally {
    setBusy(lexiconValidateButton, false);
  }
}

async function handleLoadSutraSamples() {
  setStatus("Loading sutra registry...");
  renderSutraStatus("Loading operational sutras...");
  setBusy(sutraSamplesButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/samples");
    renderSutraSamples(data);
    renderSutraStatus(`${text(data?.count, 0)} sutras loaded`, "success");
    setStatus("Sutra registry loaded");
  } catch (error) {
    console.error("[Sanskrit] Sutra samples error:", error);
    renderSutraError(error.message);
    setStatus("Sutra registry unavailable", true);
  } finally {
    setBusy(sutraSamplesButton, false);
  }
}

async function handleLoadSutraSources() {
  setStatus("Loading sutra sources...");
  renderSutraStatus("Loading sutra sources...");
  setBusy(sutraSourcesButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/sources");
    renderSutraSources(data);
    renderSutraStatus(`${text(data?.count, 0)} sutra sources loaded`, "success");
    setStatus("Sutra sources loaded");
  } catch (error) {
    console.error("[Sanskrit] Sutra sources error:", error);
    renderSutraError(error.message);
    setStatus("Sutra sources unavailable", true);
  } finally {
    setBusy(sutraSourcesButton, false);
  }
}

async function handleValidateSutraRegistry() {
  setStatus("Validating sutra registry...");
  renderSutraStatus("Validating sutra registry...");
  setBusy(sutraValidateButton, true);

  try {
    const data = await getSutraJson("/api/v3/debug/sutras/validate");
    renderSutraValidation(data);
    if (data?.valid === true) {
      renderSutraStatus("Sutra registry validation passed", "success");
      setStatus("Sutra registry valid");
    } else {
      renderSutraStatus("Sutra registry validation found issues", "error");
      setStatus("Sutra registry validation issues", true);
    }
  } catch (error) {
    console.error("[Sanskrit] Sutra validation error:", error);
    renderSutraError(error.message);
    setStatus("Sutra validation unavailable", true);
  } finally {
    setBusy(sutraValidateButton, false);
  }
}

async function handleLoadSemanticTraceDemo() {
  setStatus("Loading semantic trace demo...");
  renderSemanticTraceStatus("Loading semantic trace demo...");
  setBusy(semanticTraceDemoButton, true);

  try {
    const data = await getSemanticTraceJson("/api/v3/debug/trace/demo");
    renderSemanticTrace(data?.linked_trace, "semantic-trace-demo-output");
    renderSemanticTraceStatus("Demo semantic trace loaded", "success");
    setStatus("Semantic trace demo loaded");
  } catch (error) {
    console.error("[Sanskrit] Semantic trace demo error:", error);
    renderSemanticTraceError(error.message);
    setStatus("Semantic trace demo unavailable", true);
  } finally {
    setBusy(semanticTraceDemoButton, false);
  }
}

async function handleLinkSemanticTrace() {
  setStatus("Linking semantic trace...");
  renderSemanticTraceStatus("Linking custom trace...");
  setBusy(semanticTraceCustomButton, true);

  try {
    const data = await postSemanticTraceJson(
      "/api/v3/debug/trace/link",
      {
        trace: [
          {
            operation: "savarna_dirgha",
            sutra: "6.1.101",
          },
          {
            operation: "scutva",
            sutra: "8.4.40",
          },
        ],
      },
    );
    renderSemanticTrace(data?.linked_trace, "semantic-trace-linked-output");
    renderSemanticTraceStatus("Custom trace linked", "success");
    setStatus("Semantic trace linked");
  } catch (error) {
    console.error("[Sanskrit] Semantic trace link error:", error);
    renderSemanticTraceError(error.message);
    setStatus("Semantic trace link unavailable", true);
  } finally {
    setBusy(semanticTraceCustomButton, false);
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
  renderDebugPipelineResult(null);
  renderDebugSessionStorageList(null);
  renderDebugStorageStatus("Storage idle");
  renderDebugError("debug-session-error-output", null);
  renderLexiconSamples(null);
  renderLexiconSources(null);
  renderLexiconValidation(null);
  renderLexiconStatus("Lexicon idle");
  renderSutraSamples(null);
  renderSutraSources(null);
  renderSutraValidation(null);
  renderSutraStatus("Sutra registry idle");
  renderSemanticTrace(null, "semantic-trace-demo-output");
  renderSemanticTrace(null, "semantic-trace-linked-output");
  renderSemanticTraceStatus("Semantic trace idle");
}

export function init(node) {
  mountNode = node;
  analyzeButton = byId("analyze-sanskrit");
  sandhiButton = byId("run-sandhi");
  morphologyButton = byId("run-morphology");
  debugCreateButton = byId("debug-create-session");
  debugAppendButton = byId("debug-append-step");
  debugAmbiguityButton = byId("debug-load-ambiguity");
  debugPipelineButton = byId("debug-run-pipeline");
  debugSaveButton = byId("debug-save-session");
  debugRefreshSessionsButton = byId("debug-refresh-sessions");
  lexiconSamplesButton = byId("lexicon-load-samples");
  lexiconSourcesButton = byId("lexicon-load-sources");
  lexiconValidateButton = byId("lexicon-validate-registry");
  sutraSamplesButton = byId("sutra-load-samples");
  sutraSourcesButton = byId("sutra-load-sources");
  sutraValidateButton = byId("sutra-validate-registry");
  semanticTraceDemoButton = byId("semantic-trace-load-demo");
  semanticTraceCustomButton = byId("semantic-trace-link-custom");
  inputNode = byId("sanskrit-input");

  analyzeButton?.addEventListener("click", analyzeCurrentInput);
  sandhiButton?.addEventListener("click", runSandhi);
  morphologyButton?.addEventListener("click", runMorphology);
  debugCreateButton?.addEventListener("click", handleDebugSessionCreate);
  debugAppendButton?.addEventListener("click", handleDebugSessionAppend);
  debugAmbiguityButton?.addEventListener("click", handleDebugAmbiguityDemo);
  debugPipelineButton?.addEventListener("click", handleDebugPipelineDemo);
  debugSaveButton?.addEventListener("click", handleDebugSessionSave);
  debugRefreshSessionsButton?.addEventListener("click", handleDebugSessionList);
  lexiconSamplesButton?.addEventListener("click", handleLoadLexiconSamples);
  lexiconSourcesButton?.addEventListener("click", handleLoadLexiconSources);
  lexiconValidateButton?.addEventListener("click", handleValidateLexiconRegistry);
  sutraSamplesButton?.addEventListener("click", handleLoadSutraSamples);
  sutraSourcesButton?.addEventListener("click", handleLoadSutraSources);
  sutraValidateButton?.addEventListener("click", handleValidateSutraRegistry);
  semanticTraceDemoButton?.addEventListener("click", handleLoadSemanticTraceDemo);
  semanticTraceCustomButton?.addEventListener("click", handleLinkSemanticTrace);
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
  debugPipelineButton?.removeEventListener("click", handleDebugPipelineDemo);
  debugSaveButton?.removeEventListener("click", handleDebugSessionSave);
  debugRefreshSessionsButton?.removeEventListener("click", handleDebugSessionList);
  lexiconSamplesButton?.removeEventListener("click", handleLoadLexiconSamples);
  lexiconSourcesButton?.removeEventListener("click", handleLoadLexiconSources);
  lexiconValidateButton?.removeEventListener("click", handleValidateLexiconRegistry);
  sutraSamplesButton?.removeEventListener("click", handleLoadSutraSamples);
  sutraSourcesButton?.removeEventListener("click", handleLoadSutraSources);
  sutraValidateButton?.removeEventListener("click", handleValidateSutraRegistry);
  semanticTraceDemoButton?.removeEventListener("click", handleLoadSemanticTraceDemo);
  semanticTraceCustomButton?.removeEventListener("click", handleLinkSemanticTrace);
  all('input[name="morphology-mode"]').forEach((input) => input.removeEventListener("change", updateMorphologyFields));
  mountNode = null;
  analyzeButton = null;
  sandhiButton = null;
  morphologyButton = null;
  debugCreateButton = null;
  debugAppendButton = null;
  debugAmbiguityButton = null;
  debugPipelineButton = null;
  debugSaveButton = null;
  debugRefreshSessionsButton = null;
  lexiconSamplesButton = null;
  lexiconSourcesButton = null;
  lexiconValidateButton = null;
  sutraSamplesButton = null;
  sutraSourcesButton = null;
  sutraValidateButton = null;
  semanticTraceDemoButton = null;
  semanticTraceCustomButton = null;
  currentDebugSession = null;
  inputNode = null;
}
