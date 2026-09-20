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

function renderFlag(label, value) {
  return label + ": " + escapeHtml(value === true);
}

function renderRuntimeCatalogPanel(record = {}) {
  const records = Array.isArray(record.records) ? record.records : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Catalog Status: " + escapeHtml(record.catalogStatus || "catalog-ready"),
    "Catalog Mode: " + escapeHtml(record.catalogMode || "inspection-catalog"),
    "Source Manifest Status: " + escapeHtml(record.sourceManifestStatus || "manifest-ready"),
    "Source Manifest Mode: " + escapeHtml(record.sourceManifestMode || "inspection-manifest"),
    "Source Certificate: " + escapeHtml(
      record.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    renderFlag("Catalog Allowed", false),
    renderFlag("Manifest Allowed", false),
    renderFlag("Archive Allowed", false),
    renderFlag("Import Allowed", false),
    renderFlag("Replay Allowed", false),
    renderFlag("Execution Allowed", false),
    renderFlag("Mutation Allowed", false),
    renderFlag("Publication Allowed", false),
    renderFlag("Rollback Allowed", false),
    renderFlag("Canonical Write Allowed", false),

    "Record Count: " + escapeHtml(record.recordCount || 0),
    "Warning Count: " + escapeHtml(record.warningCount || 0),

    "Records:",
    ...records.map((entry) => "- " + escapeHtml(entry)),

    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Catalog",
    status: records.length > 0 ? "CATALOG_READY" : "EMPTY",
    readOnly: true,

    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    body
  });
}

module.exports = {
  renderRuntimeCatalogPanel
};