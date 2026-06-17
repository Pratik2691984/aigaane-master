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

function renderRuntimeUiSnapshotPanel(record = {}) {
  const snapshots = Array.isArray(record.snapshots) ? record.snapshots : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Snapshot Status: " + escapeHtml(record.uiSnapshotStatus),
    "UI Snapshot Mode: " + escapeHtml(record.uiSnapshotMode),
    "Source Controller Status: " + escapeHtml(record.sourceControllerStatus),
    "Source Controller Mode: " + escapeHtml(record.sourceControllerMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "View Allowed: false",
    "Session Allowed: false",
    "Workspace Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Snapshot Count: " + escapeHtml(record.snapshotCount || snapshots.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Snapshots:",
    ...snapshots.map((snapshot) => "- " + escapeHtml(snapshot)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Snapshot",
    status: snapshots.length ? "UI_SNAPSHOT_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiSnapshotPanel
};