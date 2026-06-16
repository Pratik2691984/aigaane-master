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

function renderRuntimeRegistryPanel(record = {}) {
  const entries = Array.isArray(record.entries) ? record.entries : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Registry Status: " + escapeHtml(record.registryStatus || "registry-ready"),
    "Registry Mode: " + escapeHtml(record.registryMode || "inspection-registry"),
    "Source Catalog Status: " + escapeHtml(record.sourceCatalogStatus || "catalog-ready"),
    "Source Catalog Mode: " + escapeHtml(record.sourceCatalogMode || "inspection-catalog"),
    "Source Certificate: " + escapeHtml(
      record.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    renderFlag("Registry Allowed", false),
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

    "Entry Count: " + escapeHtml(record.entryCount || 0),
    "Warning Count: " + escapeHtml(record.warningCount || 0),

    "Entries:",
    ...entries.map((entry) => "- " + escapeHtml(entry)),

    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Registry",
    status: entries.length > 0 ? "REGISTRY_READY" : "EMPTY",
    readOnly: true,

    registryAllowed: false,
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
  renderRuntimeRegistryPanel
};