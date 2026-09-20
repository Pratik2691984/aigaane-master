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

function renderCorpusSimulationPanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Simulation Count: " + escapeHtml(summary.simulationCount || 0),
    "Total Records: " + escapeHtml(summary.totalRecords || 0),
    "Total Estimated Seconds: " + escapeHtml(summary.totalEstimatedSeconds || 0),
    "Estimated Throughput / Second: " + escapeHtml(
      summary.estimatedThroughputPerSecond || 0
    ),
    "Final Completion Percent: " + escapeHtml(summary.finalCompletionPercent || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Simulation Execution Allowed: false",
    "Timeline Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Simulation",
    status: summary.valid ? "SIMULATION_READY" : "SIMULATION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusSimulationPanel
};