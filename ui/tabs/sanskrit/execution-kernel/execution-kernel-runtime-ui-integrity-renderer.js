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

function renderRuntimeUiIntegrityPanel(record = {}) {
  const integrityEntries = Array.isArray(record.integrityEntries)
    ? record.integrityEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Integrity Status: " + escapeHtml(record.uiIntegrityStatus),
    "UI Integrity Mode: " + escapeHtml(record.uiIntegrityMode),
    "Source UI Governance Status: " + escapeHtml(
      record.sourceUiGovernanceStatus
    ),
    "Source UI Governance Mode: " + escapeHtml(
      record.sourceUiGovernanceMode
    ),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Integrity Allowed: false",
    "UI Governance Allowed: false",
    "UI Certification Allowed: false",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "View Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Integrity Entry Count: " + escapeHtml(
      record.integrityEntryCount || integrityEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Integrity Entries:",
    ...integrityEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Integrity",
    status: integrityEntries.length ? "UI_INTEGRITY_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiIntegrityPanel
};