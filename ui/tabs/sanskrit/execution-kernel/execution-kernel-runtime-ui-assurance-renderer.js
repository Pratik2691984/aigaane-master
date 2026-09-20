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

function renderRuntimeUiAssurancePanel(record = {}) {
  const assuranceEntries = Array.isArray(record.assuranceEntries)
    ? record.assuranceEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Assurance Status: " + escapeHtml(record.uiAssuranceStatus),
    "UI Assurance Mode: " + escapeHtml(record.uiAssuranceMode),
    "Source UI Integrity Status: " + escapeHtml(record.sourceUiIntegrityStatus),
    "Source UI Integrity Mode: " + escapeHtml(record.sourceUiIntegrityMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Assurance Allowed: false",
    "UI Integrity Allowed: false",
    "UI Governance Allowed: false",
    "UI Certification Allowed: false",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Assurance Entry Count: " + escapeHtml(
      record.assuranceEntryCount || assuranceEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Assurance Entries:",
    ...assuranceEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Assurance",
    status: assuranceEntries.length ? "UI_ASSURANCE_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiAssurancePanel
};