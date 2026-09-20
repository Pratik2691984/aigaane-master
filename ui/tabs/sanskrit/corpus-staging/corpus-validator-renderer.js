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

function renderCorpusValidatorPanel(result = {}) {
  const errors = Array.isArray(result.errors) ? result.errors : [];
  const duplicateIds = Array.isArray(result.duplicateIds)
    ? result.duplicateIds
    : [];

  const body = [
    "State: " + escapeHtml(result.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(result.valid)),
    "Record Count: " + escapeHtml(result.recordCount || 0),
    "Max Records: " + escapeHtml(result.maxRecords || 2000),
    "Readiness Score: " + escapeHtml(result.readinessScore || 0),
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Duplicate IDs:",
    ...duplicateIds.map((id) => "- " + escapeHtml(id))
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Validator",
    status: result.valid ? "VALID" : "INVALID",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusValidatorPanel
};