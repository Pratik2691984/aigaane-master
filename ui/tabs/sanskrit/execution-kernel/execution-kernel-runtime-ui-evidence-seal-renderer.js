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

function renderRuntimeUiEvidenceSealPanel(record = {}) {
  const entries = Array.isArray(record.evidenceSealEntries)
    ? record.evidenceSealEntries
    : [];

  const body = [
    "Evidence Status: " + escapeHtml(record.uiEvidenceSealStatus),
    "Evidence Mode: " + escapeHtml(record.uiEvidenceSealMode),

    "Source Ledger Seal ID: " + escapeHtml(record.sourceLedgerSealId),
    "Source Archive Seal ID: " + escapeHtml(record.sourceArchiveSealId),
    "Source Import Seal ID: " + escapeHtml(record.sourceImportSealId),
    "Source Export Seal ID: " + escapeHtml(record.sourceExportSealId),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Evidence Seal Allowed: false",
    "Ledger Seal Allowed: false",
    "Archive Seal Allowed: false",
    "Import Seal Allowed: false",
    "Export Seal Allowed: false",
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
    title: "Runtime UI Evidence Seal",
    status: entries.length ? "UI_EVIDENCE_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiEvidenceSealPanel
};