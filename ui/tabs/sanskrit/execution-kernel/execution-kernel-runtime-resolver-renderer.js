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

function renderRuntimeResolverPanel(record = {}) {
  const resolutions = Array.isArray(record.resolutions) ? record.resolutions : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Resolver Status: " + escapeHtml(record.resolverStatus),
    "Resolver Mode: " + escapeHtml(record.resolverMode),
    "Source Search Status: " + escapeHtml(record.sourceSearchStatus),
    "Source Search Mode: " + escapeHtml(record.sourceSearchMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "Resolution Count: " + escapeHtml(
      record.resolutionCount || resolutions.length || 0
    ),
    "Warning Count: " + escapeHtml(
      record.warningCount || warnings.length || 0
    ),

    "",
    "Resolutions:",
    ...resolutions.map((resolution) => "- " + escapeHtml(resolution)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Resolver",
    status: resolutions.length ? "RESOLVER_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeResolverPanel
};