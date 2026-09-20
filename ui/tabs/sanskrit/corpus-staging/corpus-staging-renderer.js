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

function renderCorpusStagingPanel(preview = {}) {
  const errors = Array.isArray(preview.errors) ? preview.errors : [];
  const duplicates = Array.isArray(preview.duplicateIds)
    ? preview.duplicateIds
    : [];

  const body = [
    "State: " + escapeHtml(preview.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(preview.valid)),
    "Batch Count: " + escapeHtml(preview.batchCount || 0),
    "Record Count: " + escapeHtml(preview.recordCount || 0),
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Duplicate IDs:",
    ...duplicates.map((id) => "- " + escapeHtml(id))
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Staging",
    status: preview.valid ? "STAGING_READY" : "INVALID",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusStagingPanel
};