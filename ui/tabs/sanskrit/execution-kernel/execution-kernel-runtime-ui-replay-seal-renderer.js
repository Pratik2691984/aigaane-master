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

function renderRuntimeUiReplaySealPanel(record = {}) {
  const replaySealEntries = Array.isArray(record.replaySealEntries)
    ? record.replaySealEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Replay Seal Status: " + escapeHtml(record.replaySealStatus),
    "Replay Seal Mode: " + escapeHtml(record.replaySealMode),
    "Source UI Snapshot Seal Status: " + escapeHtml(
      record.sourceUiSnapshotSealStatus
    ),
    "Source UI Snapshot Seal Mode: " + escapeHtml(
      record.sourceUiSnapshotSealMode
    ),
    "Source UI Seal Status: " + escapeHtml(record.sourceUiSealStatus),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "Replay Seal Entry Count: " + escapeHtml(
      record.replaySealEntryCount || replaySealEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Replay Seal Entries:",
    ...replaySealEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Replay Seal",
    status: replaySealEntries.length ? "UI_REPLAY_SEAL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiReplaySealPanel
};
