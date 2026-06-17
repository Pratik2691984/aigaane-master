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

function renderRuntimeUiReplayPanel(record = {}) {
  const replayFrames = Array.isArray(record.replayFrames) ? record.replayFrames : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Replay Status: " + escapeHtml(record.uiReplayStatus),
    "UI Replay Mode: " + escapeHtml(record.uiReplayMode),
    "Source UI Snapshot Status: " + escapeHtml(record.sourceUiSnapshotStatus),
    "Source UI Snapshot Mode: " + escapeHtml(record.sourceUiSnapshotMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Replay Allowed: false",
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
    "Replay Frame Count: " + escapeHtml(
      record.replayFrameCount || replayFrames.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Replay Frames:",
    ...replayFrames.map((frame) => "- " + escapeHtml(frame)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Replay",
    status: replayFrames.length ? "UI_REPLAY_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiReplayPanel
};