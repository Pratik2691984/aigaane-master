"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderCorpusBrowserPanel(state = {}, summary = {}) {
  const sections = Array.isArray(state.sections) ? state.sections : [];
  const results = Array.isArray(summary.results) ? summary.results : [];

  const sectionLines = sections.map((name) => {
    const active = name === state.section ? " [active]" : "";
    return "- " + escapeHtml(name) + active;
  });

  const resultLines = results.slice(0, 12).map((item) => {
    return "- "
      + escapeHtml(item.recordId || "")
      + " ("
      + escapeHtml(item.type || "")
      + ") "
      + escapeHtml(item.text || "");
  });

  const body = [
    "Corpus Browser",
    "Section: " + escapeHtml(state.section || "Search"),
    "Record Count: " + escapeHtml(state.recordCount || 0),
    "Query: " + escapeHtml(summary.query || ""),
    "Matches: " + escapeHtml(summary.count || 0),
    "",
    "Sections:",
    ...sectionLines,
    "",
    "Results:",
    ...(resultLines.length ? resultLines : ["- No results loaded."]),
    "",
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Corpus Browser",
    status: summary.valid === false ? "CORPUS_BLOCKED" : "CORPUS_READY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusBrowserPanel
};