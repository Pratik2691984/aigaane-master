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

function renderRuntimeUiRegistrySealPanel(
  record = {}
) {

  const entries =
    Array.isArray(
      record.registrySealEntries
    )
      ? record.registrySealEntries
      : [];

  const body = [

    "Registry Status: "
      + escapeHtml(
          record.uiRegistrySealStatus
        ),

    "Registry Mode: "
      + escapeHtml(
          record.uiRegistrySealMode
        ),

    "Source Evidence Seal ID: "
      + escapeHtml(
          record.sourceEvidenceSealId
        ),

    "Source Ledger Seal ID: "
      + escapeHtml(
          record.sourceLedgerSealId
        ),

    "",

    "Entry Count: "
      + entries.length,

    "",

    "Execution Allowed: false",

    "Mutation Allowed: false",

    "Publication Allowed: false",

    "Canonical Write Allowed: false",

    "",

    "Entries:",

    ...entries.map(
      (
        value
      ) =>
        " - "
        + escapeHtml(value)
    )

  ].join("\n");

  return freeze({

    title:
      "Runtime UI Registry Seal",

    status:
      entries.length
        ? "UI_REGISTRY_SEAL_READY"
        : "EMPTY",

    readOnly: true,

    body

  });

}

module.exports = {
  renderRuntimeUiRegistrySealPanel
};