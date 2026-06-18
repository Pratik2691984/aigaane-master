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

function renderCorpusExecutionPreviewPanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Queue Item Count: " + escapeHtml(summary.queueItemCount || 0),
    "Estimated Seconds: " + escapeHtml(summary.estimatedSeconds || 0),
    "Estimated Throughput / Second: " + escapeHtml(
      summary.estimatedThroughputPerSecond || 0
    ),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Execution Allowed: false",
    "Queue Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Execution Preview",
    status: summary.valid ? "EXECUTION_PREVIEW_READY" : "EXECUTION_PREVIEW_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusExecutionPreviewPanel
};