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

function renderRuntimeUiAuditPanel(record = {}) {
  const auditEntries = Array.isArray(record.auditEntries) ? record.auditEntries : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Audit Status: " + escapeHtml(record.uiAuditStatus),
    "UI Audit Mode: " + escapeHtml(record.uiAuditMode),
    "Source UI Replay Status: " + escapeHtml(record.sourceUiReplayStatus),
    "Source UI Replay Mode: " + escapeHtml(record.sourceUiReplayMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "View Allowed: false",
    "Session Allowed: false",
    "Workspace Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Audit Entry Count: " + escapeHtml(
      record.auditEntryCount || auditEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Audit Entries:",
    ...auditEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Audit",
    status: auditEntries.length ? "UI_AUDIT_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiAuditPanel
};