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

function renderCorpusImportPreviewPanel(summary = {}) {
  const duplicateIds = Array.isArray(summary.duplicateIds)
    ? summary.duplicateIds
    : [];

  const typeCounts = summary.typeCounts || {};

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Record Count: " + escapeHtml(summary.recordCount || 0),
    "Estimated Insert Count: " + escapeHtml(summary.estimatedInsertCount || 0),
    "Estimated Skip Count: " + escapeHtml(summary.estimatedSkipCount || 0),
    "Estimated KB: " + escapeHtml(summary.estimatedKilobytes || 0),

    "",
    "Type Counts:",
    "- dhatu: " + escapeHtml(typeCounts.dhatu || 0),
    "- sutra: " + escapeHtml(typeCounts.sutra || 0),
    "- stotra: " + escapeHtml(typeCounts.stotra || 0),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false",

    "",
    "Duplicate IDs:",
    ...duplicateIds.map((id) => "- " + escapeHtml(id))
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Import Preview",
    status: summary.valid ? "IMPORT_PREVIEW_READY" : "IMPORT_PREVIEW_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusImportPreviewPanel
};