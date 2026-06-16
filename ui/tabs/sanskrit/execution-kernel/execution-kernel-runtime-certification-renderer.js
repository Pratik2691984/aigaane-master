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

function renderRuntimeCertificationPanel(record = {}) {
  const attestations = Array.isArray(record.attestations) ? record.attestations : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Certification Status: " + escapeHtml(record.certificationStatus || "certified-for-inspection"),
    "Certificate: " + escapeHtml(record.certificate || "controlled-runtime-inspection-only"),
    "Governance Status: " + escapeHtml(record.governanceStatus || "inspection-approved"),
    "Decision: " + escapeHtml(record.decision || "approve-inspection-only"),

    renderFlag("Replay Allowed", false),
    renderFlag("Execution Allowed", false),
    renderFlag("Mutation Allowed", false),
    renderFlag("Publication Allowed", false),
    renderFlag("Rollback Allowed", false),
    renderFlag("Canonical Write Allowed", false),

    "Control Count: " + escapeHtml(record.controlCount || 0),
    "Finding Count: " + escapeHtml(record.findingCount || 0),
    "Warning Count: " + escapeHtml(record.warningCount || 0),

    "Attestations:",
    ...attestations.map((attestation) => "- " + escapeHtml(attestation)),

    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Certification",
    status: attestations.length > 0 ? "CERTIFIED_FOR_INSPECTION" : "EMPTY",
    readOnly: true,

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
  renderRuntimeCertificationPanel
};