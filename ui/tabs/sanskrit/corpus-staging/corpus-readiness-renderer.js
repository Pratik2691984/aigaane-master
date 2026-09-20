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

function renderCorpusReadinessPanel(summary = {}) {
  const errors = Array.isArray(summary.errors) ? summary.errors : [];
  const warnings = Array.isArray(summary.warnings) ? summary.warnings : [];

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Promotion Eligible: " + escapeHtml(Boolean(summary.promotionEligible)),
    "Readiness Score: " + escapeHtml(summary.readinessScore || 0),
    "Batch Count: " + escapeHtml(summary.batchCount || 0),
    "Record Count: " + escapeHtml(summary.recordCount || 0),
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Readiness",
    status: summary.valid ? "READY" : "BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusReadinessPanel
};