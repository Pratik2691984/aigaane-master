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

function renderRuntimeSessionPanel(record = {}) {
  const frames = Array.isArray(record.frames) ? record.frames : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Session Status: " + escapeHtml(record.sessionStatus),
    "Session Mode: " + escapeHtml(record.sessionMode),
    "Source Workspace Status: " + escapeHtml(record.sourceWorkspaceStatus),
    "Source Workspace Mode: " + escapeHtml(record.sourceWorkspaceMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "Session Allowed: false",
    "Workspace Allowed: false",
    "Explorer Allowed: false",
    "Navigator Allowed: false",
    "Resolver Allowed: false",
    "Search Allowed: false",
    "Query Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Frame Count: " + escapeHtml(record.frameCount || frames.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Frames:",
    ...frames.map((frame) => "- " + escapeHtml(frame)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Session",
    status: frames.length ? "SESSION_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeSessionPanel
};