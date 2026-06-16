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

function renderRuntimeNavigatorPanel(record = {}) {
  const routes = Array.isArray(record.routes) ? record.routes : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Navigator Status: " + escapeHtml(record.navigatorStatus),
    "Navigator Mode: " + escapeHtml(record.navigatorMode),
    "Source Resolver Status: " + escapeHtml(record.sourceResolverStatus),
    "Source Resolver Mode: " + escapeHtml(record.sourceResolverMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "Navigator Allowed: false",
    "Resolver Allowed: false",
    "Search Allowed: false",
    "Query Allowed: false",
    "Lookup Allowed: false",
    "Directory Allowed: false",
    "Index Allowed: false",
    "Registry Allowed: false",
    "Catalog Allowed: false",
    "Manifest Allowed: false",
    "Archive Allowed: false",
    "Import Allowed: false",
    "Replay Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Route Count: " + escapeHtml(record.routeCount || routes.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Routes:",
    ...routes.map((route) => "- " + escapeHtml(route)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Navigator",
    status: routes.length ? "NAVIGATOR_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeNavigatorPanel
};