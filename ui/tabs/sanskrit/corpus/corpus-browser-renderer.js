"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, """);
}

function typeClass(type) {
  const value = String(type || "").toLowerCase();
  if (value === "dhatu" || value === "sutra" || value === "stotra") {
    return "corpus-type-" + value;
  }
  return "corpus-type-unknown";
}

function renderCorpusStats(state = {}, summary = {}) {
  const recordCount = Number(state.recordCount || 0);
  const matchCount = Number(summary.count || 0);
  const status = summary.valid === false ? "Blocked" : "Ready";

  return [
    '<article class="corpus-browser-stat">',
    '<span class="corpus-browser-stat-label">Indexed records</span>',
    '<strong class="corpus-browser-stat-value">' + escapeHtml(recordCount) + "</strong>",
    "</article>",
    '<article class="corpus-browser-stat">',
    '<span class="corpus-browser-stat-label">Active section</span>',
    '<strong class="corpus-browser-stat-value">' + escapeHtml(state.section || "Search") + "</strong>",
    "</article>",
    '<article class="corpus-browser-stat">',
    '<span class="corpus-browser-stat-label">Matches</span>',
    '<strong class="corpus-browser-stat-value">' + escapeHtml(matchCount) + "</strong>",
    "</article>",
    '<article class="corpus-browser-stat corpus-browser-stat-status">',
    '<span class="corpus-browser-stat-label">Status</span>',
    '<strong class="corpus-browser-stat-value">' + escapeHtml(status) + "</strong>",
    "</article>"
  ].join("");
}

function renderCorpusNav(state = {}) {
  const sections = Array.isArray(state.sections) ? state.sections : [];
  return sections.map((name) => {
    const active = name === state.section ? " is-active" : "";
    const slug = String(name).toLowerCase();
    return (
      '<button type="button" class="corpus-browser-nav-btn' + active + '"'
      + ' data-corpus-section="' + escapeHtml(slug) + '"'
      + ' aria-pressed="' + (active ? "true" : "false") + '">'
      + escapeHtml(name)
      + "</button>"
    );
  }).join("");
}

function renderCorpusResultCard(item = {}, selectedId = "") {
  const recordId = escapeHtml(item.recordId || item.id || "");
  const type = escapeHtml(item.type || "");
  const text = escapeHtml(item.text || item.normalized || "");
  const meaning = escapeHtml(item.meaning || item.notes || item.metadata?.meaning || "");
  const selected = String(item.recordId || item.id || "") === String(selectedId || "") ? " is-selected" : "";

  return [
    '<article class="corpus-browser-card' + selected + '" data-record-id="' + recordId + '" data-record-type="' + type + '">',
    '<header class="corpus-browser-card-header">',
    '<span class="corpus-browser-type-badge ' + typeClass(item.type) + '">' + type + "</span>",
    '<code class="corpus-browser-record-id">' + recordId + "</code>",
    "</header>",
    '<p class="corpus-browser-card-text">' + text + "</p>",
    meaning ? '<p class="corpus-browser-card-meta">' + meaning + "</p>" : "",
    "</article>"
  ].join("");
}

function normalizeResults(summary = {}) {
  if (Array.isArray(summary.results)) {
    return summary.results;
  }
  if (Array.isArray(summary.records)) {
    return summary.records.map((item) => ({
      recordId: item.id || item.recordId,
      type: item.type || summary.corpusType,
      text: item.text || item.normalized,
      meaning: item.notes || item.metadata?.meaning
    }));
  }
  return [];
}

function renderCorpusResults(summary = {}, section = "Search", windowState = null, selectedId = "") {
  const results = normalizeResults(summary);

  if (!results.length) {
    return '<div class="corpus-browser-empty">No ' + escapeHtml(section) + " records loaded.</div>";
  }

  const totalCount = results.length;
  const startIndex = windowState && Number.isFinite(windowState.startIndex)
    ? windowState.startIndex
    : 0;
  const endIndex = windowState && Number.isFinite(windowState.endIndex)
    ? windowState.endIndex
    : Math.min(totalCount, 25);
  const topPadding = windowState && Number.isFinite(windowState.topPadding)
    ? windowState.topPadding
    : 0;
  const bottomPadding = windowState && Number.isFinite(windowState.bottomPadding)
    ? windowState.bottomPadding
    : Math.max(0, (totalCount - endIndex) * 48);
  const totalHeight = windowState && Number.isFinite(windowState.totalHeight)
    ? windowState.totalHeight
    : totalCount * 48;

  const visibleSlice = results.slice(startIndex, endIndex);
  const cardsHtml = visibleSlice.map((item) => renderCorpusResultCard(item, selectedId)).join("");

  return [
    '<div class="corpus-results-viewport" data-total-count="' + escapeHtml(totalCount) + '" style="height:480px;overflow:auto;position:relative;">',
    '<div class="corpus-results-spacer" style="position:relative;height:' + escapeHtml(totalHeight) + 'px;">',
    '<div class="corpus-results-window" style="padding-top:' + escapeHtml(topPadding) + "px;padding-bottom:" + escapeHtml(bottomPadding) + 'px;">',
    cardsHtml,
    "</div>",
    "</div>",
    "</div>"
  ].join("");
}

function renderDerivationSteps(derivationPath) {
  return derivationPath.map((step, idx) => {
    const operation = escapeHtml(step && step.operation ? step.operation : "unnamed_op");
    const sutra = step && step.sutra
      ? '<div class="corpus-browser-trace-sutra">Sutra: ' + escapeHtml(step.sutra)
        + " (" + escapeHtml(step.sutra_name || "") + ")</div>"
      : "";
    const transition = escapeHtml(step && step.input_state ? step.input_state : "-")
      + " → "
      + escapeHtml(step && step.output_state ? step.output_state : "-");
    return [
      '<div class="corpus-browser-trace-step">',
      '<div class="corpus-browser-trace-line">Step ' + (idx + 1) + ": " + operation + "</div>",
      sutra,
      '<div class="corpus-browser-trace-line">' + transition + "</div>",
      "</div>"
    ].join("");
  }).join("");
}

function renderCorpusTrace(state = {}, summary = {}, selected = null, derivationData = null) {
  const lines = [
    "Schema: sanskrit-corpus-browser.v1",
    "Section: " + (state.section || "Search"),
    "Query: " + (summary.query || "(none)"),
    "Preview only: true",
    "Canonical write: blocked"
  ];

  if (!selected) {
    lines.push("", "Awaiting corpus selection…");
    return lines.map((line) => '<div class="corpus-browser-trace-line">' + escapeHtml(line) + "</div>").join("");
  }

  lines.push(
    "",
    "Selected:",
    "- id: " + (selected.recordId || selected.id || ""),
    "- type: " + (selected.type || ""),
    "- text: " + (selected.text || selected.normalized || "")
  );

  const header = lines.map((line) => '<div class="corpus-browser-trace-line">' + escapeHtml(line) + "</div>").join("");
  const derivationPath = derivationData && derivationData.derivation_path;

  if (!derivationPath || !Array.isArray(derivationPath) || derivationPath.length === 0) {
    return header + '<div class="corpus-browser-trace-line">derivation_path: absent</div>';
  }

  return header + renderDerivationSteps(derivationPath);
}

function renderCorpusBrowserPanel(state = {}, summary = {}, windowState = null, selected = null, derivationData = null) {
  const html = [
    '<div class="corpus-browser-shell">',
    '<div class="corpus-browser-stats-grid">' + renderCorpusStats(state, summary) + "</div>",
    '<nav class="corpus-browser-nav" aria-label="Corpus sections">' + renderCorpusNav(state) + "</nav>",
    '<section class="corpus-browser-results-wrap">',
    '<h4 class="corpus-browser-results-title">' + escapeHtml(state.section || "Search") + " results</h4>",
    '<div class="corpus-browser-results-list">' + renderCorpusResults(summary, state.section, windowState, selected && selected.recordId) + "</div>",
    "</section>",
    '<aside class="corpus-browser-trace-wrap">',
    '<h4 class="corpus-browser-trace-title">Trace</h4>',
    '<div class="corpus-browser-trace-list">' + renderCorpusTrace(state, summary, selected, derivationData) + "</div>",
    "</aside>",
    "</div>"
  ].join("");

  const results = Array.isArray(summary.results) ? summary.results : [];
  const body = [
    "Corpus Browser",
    "Section: " + (state.section || "Search"),
    "Record Count: " + (state.recordCount || 0),
    "Matches: " + (summary.count || results.length),
    "Results: " + results.length
  ].join("\n");

  return freeze({
    title: "Sanskrit Corpus Browser",
    status: summary.valid === false ? "CORPUS_BLOCKED" : "CORPUS_READY",
    readOnly: true,
    html,
    body
  });
}

module.exports = {
  renderCorpusBrowserPanel,
  renderCorpusStats,
  renderCorpusNav,
  renderCorpusResults,
  renderCorpusTrace,
  renderCorpusResultCard
};
