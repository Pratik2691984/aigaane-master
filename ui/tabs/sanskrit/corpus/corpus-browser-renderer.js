"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
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

function renderCorpusResultCard(item = {}) {
  const recordId = escapeHtml(item.recordId || item.id || "");
  const type = escapeHtml(item.type || "");
  const text = escapeHtml(item.text || item.normalized || "");
  const meaning = escapeHtml(item.meaning || item.notes || item.metadata?.meaning || "");

  return [
    '<article class="corpus-browser-card" data-record-id="' + recordId + '" data-record-type="' + type + '">',
    '<header class="corpus-browser-card-header">',
    '<span class="corpus-browser-type-badge ' + typeClass(item.type) + '">' + type + "</span>",
    '<code class="corpus-browser-record-id">' + recordId + "</code>",
    "</header>",
    '<p class="corpus-browser-card-text">' + text + "</p>",
    meaning ? '<p class="corpus-browser-card-meta">' + meaning + "</p>" : "",
    "</article>"
  ].join("");
}

function renderCorpusResults(summary = {}, section = "Search") {
  const results = Array.isArray(summary.results)
    ? summary.results
    : Array.isArray(summary.records)
      ? summary.records.map((item) => ({
          recordId: item.id || item.recordId,
          type: item.type || summary.corpusType,
          text: item.text || item.normalized,
          meaning: item.notes || item.metadata?.meaning
        }))
      : [];

  if (!results.length) {
    return '<div class="corpus-browser-empty">No ' + escapeHtml(section) + " records loaded.</div>";
  }

  return results.map((item) => renderCorpusResultCard(item)).join("");
}

function renderCorpusTrace(state = {}, summary = {}, selected = null) {
  const lines = [
    "Schema: sanskrit-corpus-browser.v1",
    "Section: " + (state.section || "Search"),
    "Query: " + (summary.query || "(none)"),
    "Preview only: true",
    "Canonical write: blocked"
  ];

  if (selected) {
    lines.push(
      "",
      "Selected:",
      "- id: " + (selected.recordId || selected.id || ""),
      "- type: " + (selected.type || ""),
      "- text: " + (selected.text || selected.normalized || "")
    );
  }

  return lines.map((line) => '<div class="corpus-browser-trace-line">' + escapeHtml(line) + "</div>").join("");
}

function renderCorpusBrowserPanel(state = {}, summary = {}) {
  const html = [
    '<div class="corpus-browser-shell">',
    '<div class="corpus-browser-stats-grid">' + renderCorpusStats(state, summary) + "</div>",
    '<nav class="corpus-browser-nav" aria-label="Corpus sections">' + renderCorpusNav(state) + "</nav>",
    '<section class="corpus-browser-results-wrap">',
    '<h4 class="corpus-browser-results-title">' + escapeHtml(state.section || "Search") + " results</h4>",
    '<div class="corpus-browser-results-list">' + renderCorpusResults(summary, state.section) + "</div>",
    "</section>",
    '<aside class="corpus-browser-trace-wrap">',
    '<h4 class="corpus-browser-trace-title">Trace</h4>',
    '<div class="corpus-browser-trace-list">' + renderCorpusTrace(state, summary) + "</div>",
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