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

function renderCorpusSchedulePanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Schedule Count: " + escapeHtml(summary.scheduleCount || 0),
    "Total Estimated Seconds: " + escapeHtml(summary.totalEstimatedSeconds || 0),
    "Seconds Per Window: " + escapeHtml(summary.secondsPerWindow || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Schedule Execution Allowed: false",
    "Window Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Schedule",
    status: summary.valid ? "SCHEDULE_READY" : "SCHEDULE_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusSchedulePanel
};