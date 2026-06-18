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

function renderRuntimeUiExportSealPanel(record = {}) {
  const entries = Array.isArray(record.exportSealEntries)
    ? record.exportSealEntries
    : [];

  const body = [
    "Export Status: " + escapeHtml(record.uiExportSealStatus),
    "Export Mode: " + escapeHtml(record.uiExportSealMode),

    "Source Certification Seal ID: " + escapeHtml(
      record.sourceCertificationSealId
    ),
    "Source Governance Seal ID: " + escapeHtml(record.sourceGovernanceSealId),
    "Source Audit Seal ID: " + escapeHtml(record.sourceAuditSealId),
    "Source Replay Seal ID: " + escapeHtml(record.sourceReplaySealId),
    "Source Snapshot Seal ID: " + escapeHtml(record.sourceSnapshotSealId),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Export Seal Allowed: false",
    "Certification Seal Allowed: false",
    "Governance Seal Allowed: false",
    "Audit Seal Allowed: false",
    "Replay Seal Allowed: false",
    "Snapshot Seal Allowed: false",
    "Controller Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Entries:",
    ...entries.map((v) => " - " + escapeHtml(v))
  ].join("\n");

  return freeze({
    title: "Runtime UI Export Seal",
    status: entries.length ? "UI_EXPORT_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiExportSealPanel
};