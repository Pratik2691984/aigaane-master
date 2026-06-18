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

function renderCorpusIntakePanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Source Record Count: " + escapeHtml(summary.sourceRecordCount || 0),
    "Intake Record Count: " + escapeHtml(summary.intakeRecordCount || 0),
    "Skipped Record Count: " + escapeHtml(summary.skippedRecordCount || 0),
    "Intake Batch Count: " + escapeHtml(summary.intakeBatchCount || 0),
    "Batch Size: " + escapeHtml(summary.batchSize || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Intake",
    status: summary.valid ? "INTAKE_READY" : "INTAKE_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusIntakePanel
};