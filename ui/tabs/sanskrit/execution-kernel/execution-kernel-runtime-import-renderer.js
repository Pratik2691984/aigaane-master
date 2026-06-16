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

function renderRuntimeImportPanel(record = {}) {
  const attestations = Array.isArray(record.attestations) ? record.attestations : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Import Status: " + escapeHtml(record.importStatus || "review-only"),
    "Import Mode: " + escapeHtml(record.importMode || "inspection-import"),
    "Source Export Status: " + escapeHtml(record.sourceExportStatus || "export-ready"),
    "Source Export Mode: " + escapeHtml(record.sourceExportMode || "inspection-export"),
    "Source Certificate: " + escapeHtml(
      record.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    renderFlag("Import Allowed", false),
    renderFlag("Replay Allowed", false),
    renderFlag("Execution Allowed", false),
    renderFlag("Mutation Allowed", false),
    renderFlag("Publication Allowed", false),
    renderFlag("Rollback Allowed", false),
    renderFlag("Canonical Write Allowed", false),

    "Attestation Count: " + escapeHtml(record.attestationCount || 0),
    "Warning Count: " + escapeHtml(record.warningCount || 0),

    "Attestations:",
    ...attestations.map((attestation) => "- " + escapeHtml(attestation)),

    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Import",
    status: attestations.length > 0 ? "REVIEW_ONLY" : "EMPTY",
    readOnly: true,

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
  renderRuntimeImportPanel
};