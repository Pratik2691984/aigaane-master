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

function renderRuntimeManifestPanel(record = {}) {
  const entries = Array.isArray(record.entries) ? record.entries : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Manifest Status: " + escapeHtml(record.manifestStatus || "manifest-ready"),
    "Manifest Mode: " + escapeHtml(record.manifestMode || "inspection-manifest"),
    "Source Archive Status: " + escapeHtml(record.sourceArchiveStatus || "archive-ready"),
    "Source Archive Mode: " + escapeHtml(record.sourceArchiveMode || "inspection-archive"),
    "Source Certificate: " + escapeHtml(
      record.sourceCertificate || "controlled-runtime-inspection-only"
    ),

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
    title: "Runtime Manifest",
    status: entries.length > 0 ? "MANIFEST_READY" : "EMPTY",
    readOnly: true,

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
  renderRuntimeManifestPanel
};