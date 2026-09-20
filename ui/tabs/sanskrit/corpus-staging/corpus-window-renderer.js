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

function renderCorpusWindowPanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Window Size: " + escapeHtml(summary.windowSize || 0),
    "Window Count: " + escapeHtml(summary.windowCount || 0),
    "Total Reserved: " + escapeHtml(summary.totalReserved || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Window Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Window Planner",
    status: summary.valid ? "WINDOW_READY" : "WINDOW_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusWindowPanel
};