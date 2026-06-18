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

function renderRuntimeUiAuditSealPanel(record = {}) {
  const auditSealEntries = Array.isArray(record.auditSealEntries)
    ? record.auditSealEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Audit Seal Status: " + escapeHtml(record.uiAuditSealStatus),
    "UI Audit Seal Mode: " + escapeHtml(record.uiAuditSealMode),
    "Source UI Replay Seal Status: " + escapeHtml(record.sourceUiReplaySealStatus),
    "Source UI Replay Seal ID: " + escapeHtml(record.sourceUiReplaySealId),
    "Source UI Snapshot Seal ID: " + escapeHtml(record.sourceUiSnapshotSealId),
    "Source UI Seal ID: " + escapeHtml(record.sourceUiSealId),

    "",
    "Allowed Flags:",
    "Audit Seal Allowed: false",
    "Replay Seal Allowed: false",
    "UI Snapshot Seal Allowed: false",
    "UI Seal Allowed: false",
    "Controller Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Audit Seal Entry Count: " + escapeHtml(
      record.auditSealEntryCount || auditSealEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Audit Seal Entries:",
    ...auditSealEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Audit Seal",
    status: auditSealEntries.length ? "UI_AUDIT_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiAuditSealPanel
};