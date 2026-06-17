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

function renderRuntimeUiCertificationPanel(record = {}) {
  const certificationEntries = Array.isArray(record.certificationEntries)
    ? record.certificationEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Certification Status: " + escapeHtml(record.uiCertificationStatus),
    "UI Certification Mode: " + escapeHtml(record.uiCertificationMode),
    "Source UI Audit Status: " + escapeHtml(record.sourceUiAuditStatus),
    "Source UI Audit Mode: " + escapeHtml(record.sourceUiAuditMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Certification Allowed: false",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "View Allowed: false",
    "Session Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Certification Entry Count: " + escapeHtml(
      record.certificationEntryCount || certificationEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Certification Entries:",
    ...certificationEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Certification",
    status: certificationEntries.length ? "UI_CERTIFICATION_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiCertificationPanel
};