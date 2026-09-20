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

function renderRuntimeWorkspacePanel(record = {}) {
  const panels = Array.isArray(record.panels) ? record.panels : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Workspace Status: " + escapeHtml(record.workspaceStatus),
    "Workspace Mode: " + escapeHtml(record.workspaceMode),
    "Source Explorer Status: " + escapeHtml(record.sourceExplorerStatus),
    "Source Explorer Mode: " + escapeHtml(record.sourceExplorerMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "Panel Count: " + escapeHtml(record.panelCount || panels.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Panels:",
    ...panels.map((panel) => "- " + escapeHtml(panel)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Workspace",
    status: panels.length ? "WORKSPACE_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeWorkspacePanel
};