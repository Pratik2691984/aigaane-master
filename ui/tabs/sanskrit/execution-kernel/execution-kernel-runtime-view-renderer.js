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

function renderRuntimeViewPanel(record = {}) {
  const views = Array.isArray(record.views) ? record.views : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "View Status: " + escapeHtml(record.viewStatus),
    "View Mode: " + escapeHtml(record.viewMode),
    "Source Session Status: " + escapeHtml(record.sourceSessionStatus),
    "Source Session Mode: " + escapeHtml(record.sourceSessionMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "View Count: " + escapeHtml(record.viewCount || views.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Views:",
    ...views.map((view) => "- " + escapeHtml(view)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime View",
    status: views.length ? "VIEW_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeViewPanel
};