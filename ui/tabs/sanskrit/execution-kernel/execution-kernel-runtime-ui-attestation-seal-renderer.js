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

function renderRuntimeUiAttestationSealPanel(record = {}) {
  const entries = Array.isArray(record.attestationSealEntries)
    ? record.attestationSealEntries
    : [];

  const body = [
    "Attestation Status: " + escapeHtml(record.uiAttestationSealStatus),
    "Attestation Mode: " + escapeHtml(record.uiAttestationSealMode),

    "Source Provenance Seal ID: " + escapeHtml(record.sourceProvenanceSealId),
    "Source Integrity Seal ID: " + escapeHtml(record.sourceIntegritySealId),
    "Source Registry Seal ID: " + escapeHtml(record.sourceRegistrySealId),
    "Source Evidence Seal ID: " + escapeHtml(record.sourceEvidenceSealId),

    "",
    "Entry Count: " + entries.length,

    "",
    "Allowed Flags:",
    "Attestation Seal Allowed: false",
    "Provenance Seal Allowed: false",
    "Integrity Seal Allowed: false",
    "Registry Seal Allowed: false",
    "Evidence Seal Allowed: false",
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
    title: "Runtime UI Attestation Seal",
    status: entries.length ? "UI_ATTESTATION_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiAttestationSealPanel
};