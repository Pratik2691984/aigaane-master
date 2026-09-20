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

function renderCorpusCapacityPanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Record Count: " + escapeHtml(summary.recordCount || 0),
    "Max Records: " + escapeHtml(summary.maxRecords || 2000),
    "Remaining Capacity: " + escapeHtml(summary.remainingCapacity || 0),
    "Utilization Percent: " + escapeHtml(summary.utilizationPercent || 0),
    "Default Batch Size: " + escapeHtml(summary.defaultBatchSize || 0),
    "Projected Batch Count: " + escapeHtml(summary.projectedBatchCount || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Capacity Planner",
    status: summary.valid ? "CAPACITY_READY" : "CAPACITY_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusCapacityPanel
};