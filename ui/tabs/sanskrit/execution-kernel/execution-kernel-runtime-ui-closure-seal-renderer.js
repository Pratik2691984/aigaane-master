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

function renderRuntimeUiClosureSealPanel(record = {}) {
  const entries = Array.isArray(record.closureSealEntries)
    ? record.closureSealEntries
    : [];

  const body = [
    "Closure Status: " + escapeHtml(record.uiClosureSealStatus),
    "Closure Mode: " + escapeHtml(record.uiClosureSealMode),

    "Source Attestation Seal ID: " + escapeHtml(record.sourceAttestationSealId),
    "Source Provenance Seal ID: " + escapeHtml(record.sourceProvenanceSealId),
    "Source Integrity Seal ID: " + escapeHtml(record.sourceIntegritySealId),
    "Source Registry Seal ID: " + escapeHtml(record.sourceRegistrySealId),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Closure Seal Allowed: false",
    "Attestation Seal Allowed: false",
    "Provenance Seal Allowed: false",
    "Integrity Seal Allowed: false",
    "Registry Seal Allowed: false",
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
    title: "Runtime UI Closure Seal",
    status: entries.length ? "UI_CLOSURE_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiClosureSealPanel
};