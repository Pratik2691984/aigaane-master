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

function renderCorpusProvenancePanel(result = {}) {
  const errors = Array.isArray(result.errors) ? result.errors : [];
  const warnings = Array.isArray(result.warnings) ? result.warnings : [];
  const duplicateRecordIds = Array.isArray(result.duplicateRecordIds)
    ? result.duplicateRecordIds
    : [];
  const duplicateBatchIds = Array.isArray(result.duplicateBatchIds)
    ? result.duplicateBatchIds
    : [];
  const reusedSources = Array.isArray(result.reusedSources)
    ? result.reusedSources
    : [];

  const body = [
    "State: " + escapeHtml(result.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(result.valid)),
    "Batch Count: " + escapeHtml(result.batchCount || 0),
    "Record Count: " + escapeHtml(result.recordCount || 0),
    "Confidence Score: " + escapeHtml(result.confidenceScore || 0),
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning)),

    "",
    "Duplicate Record IDs:",
    ...duplicateRecordIds.map((id) => "- " + escapeHtml(id)),

    "",
    "Duplicate Batch IDs:",
    ...duplicateBatchIds.map((id) => "- " + escapeHtml(id)),

    "",
    "Reused Sources:",
    ...reusedSources.map((source) => "- " + escapeHtml(source))
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Provenance Audit",
    status: result.valid ? "PROVENANCE_READY" : "PROVENANCE_INVALID",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusProvenancePanel
};