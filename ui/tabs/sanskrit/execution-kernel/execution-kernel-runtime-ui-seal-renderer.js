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

function renderRuntimeUiSealPanel(record = {}) {
  const sealEntries = Array.isArray(record.sealEntries)
    ? record.sealEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Seal Status: " + escapeHtml(record.uiSealStatus),
    "UI Seal Mode: " + escapeHtml(record.uiSealMode),
    "Source UI Assurance Status: " + escapeHtml(record.sourceUiAssuranceStatus),
    "Source UI Assurance Mode: " + escapeHtml(record.sourceUiAssuranceMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Seal Allowed: false",
    "UI Assurance Allowed: false",
    "UI Integrity Allowed: false",
    "UI Governance Allowed: false",
    "UI Certification Allowed: false",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Seal Entry Count: " + escapeHtml(
      record.sealEntryCount || sealEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Seal Entries:",
    ...sealEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Seal",
    status: sealEntries.length ? "UI_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiSealPanel
};