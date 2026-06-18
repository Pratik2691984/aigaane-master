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

function renderRuntimeUiProvenanceSealPanel(record = {}) {
  const entries = Array.isArray(record.provenanceSealEntries)
    ? record.provenanceSealEntries
    : [];

  const body = [
    "Provenance Status: " + escapeHtml(record.uiProvenanceSealStatus),
    "Provenance Mode: " + escapeHtml(record.uiProvenanceSealMode),

    "Source Integrity Seal ID: " + escapeHtml(record.sourceIntegritySealId),
    "Source Registry Seal ID: " + escapeHtml(record.sourceRegistrySealId),
    "Source Evidence Seal ID: " + escapeHtml(record.sourceEvidenceSealId),
    "Source Ledger Seal ID: " + escapeHtml(record.sourceLedgerSealId),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Provenance Seal Allowed: false",
    "Integrity Seal Allowed: false",
    "Registry Seal Allowed: false",
    "Evidence Seal Allowed: false",
    "Ledger Seal Allowed: false",
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
    title: "Runtime UI Provenance Seal",
    status: entries.length ? "UI_PROVENANCE_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiProvenanceSealPanel
};