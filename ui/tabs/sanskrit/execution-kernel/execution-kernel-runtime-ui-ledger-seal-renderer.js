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

function renderRuntimeUiLedgerSealPanel(record = {}) {
  const entries = Array.isArray(record.ledgerSealEntries)
    ? record.ledgerSealEntries
    : [];

  const body = [
    "Ledger Status: " + escapeHtml(record.uiLedgerSealStatus),
    "Ledger Mode: " + escapeHtml(record.uiLedgerSealMode),

    "Source Archive Seal ID: " + escapeHtml(record.sourceArchiveSealId),
    "Source Import Seal ID: " + escapeHtml(record.sourceImportSealId),
    "Source Export Seal ID: " + escapeHtml(record.sourceExportSealId),
    "Source Certification Seal ID: " + escapeHtml(
      record.sourceCertificationSealId
    ),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Ledger Seal Allowed: false",
    "Archive Seal Allowed: false",
    "Import Seal Allowed: false",
    "Export Seal Allowed: false",
    "Certification Seal Allowed: false",
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
    title: "Runtime UI Ledger Seal",
    status: entries.length ? "UI_LEDGER_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiLedgerSealPanel
};