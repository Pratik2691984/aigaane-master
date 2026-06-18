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

function renderCorpusIntakeQueuePanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Queue Item Count: " + escapeHtml(summary.queueItemCount || 0),
    "Estimated Seconds: " + escapeHtml(summary.estimatedSeconds || 0),
    "Seconds Per Record: " + escapeHtml(summary.secondsPerRecord || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false",
    "Queue Execution Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Intake Queue",
    status: summary.valid ? "QUEUE_READY" : "QUEUE_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusIntakeQueuePanel
};