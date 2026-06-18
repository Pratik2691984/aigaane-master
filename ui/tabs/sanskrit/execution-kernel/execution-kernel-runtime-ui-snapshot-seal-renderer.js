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

function renderRuntimeUiSnapshotSealPanel(record = {}) {
  const snapshotSealEntries = Array.isArray(record.snapshotSealEntries)
    ? record.snapshotSealEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Snapshot Seal Status: " + escapeHtml(record.uiSnapshotSealStatus),
    "UI Snapshot Seal Mode: " + escapeHtml(record.uiSnapshotSealMode),
    "Source UI Seal Status: " + escapeHtml(record.sourceUiSealStatus),
    "Source UI Seal Mode: " + escapeHtml(record.sourceUiSealMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Snapshot Seal Allowed: false",
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
    "Snapshot Seal Entry Count: " + escapeHtml(
      record.snapshotSealEntryCount || snapshotSealEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Snapshot Seal Entries:",
    ...snapshotSealEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Snapshot Seal",
    status: snapshotSealEntries.length ? "UI_SNAPSHOT_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiSnapshotSealPanel
};