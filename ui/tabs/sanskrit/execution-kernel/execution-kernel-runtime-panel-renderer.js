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

function renderRuntimePanelPanel(record = {}) {
  const sections = Array.isArray(record.sections) ? record.sections : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Panel Status: " + escapeHtml(record.panelStatus),
    "Panel Mode: " + escapeHtml(record.panelMode),
    "Source View Status: " + escapeHtml(record.sourceViewStatus),
    "Source View Mode: " + escapeHtml(record.sourceViewMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "Panel Allowed: false",
    "View Allowed: false",
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
    "Section Count: " + escapeHtml(record.sectionCount || sections.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Sections:",
    ...sections.map((section) => "- " + escapeHtml(section)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Panel",
    status: sections.length ? "PANEL_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimePanelPanel
};