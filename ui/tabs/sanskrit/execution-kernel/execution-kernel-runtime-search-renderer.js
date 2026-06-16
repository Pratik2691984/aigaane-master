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

function renderRuntimeSearchPanel(record = {}) {
  const results = Array.isArray(record.results) ? record.results : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Search Status: " + escapeHtml(record.searchStatus),
    "Search Mode: " + escapeHtml(record.searchMode),
    "Source Query Status: " + escapeHtml(record.sourceQueryStatus),
    "Source Query Mode: " + escapeHtml(record.sourceQueryMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "Result Count: " + escapeHtml(record.resultCount || results.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Results:",
    ...results.map((result) => "- " + escapeHtml(result)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Search",
    status: results.length ? "SEARCH_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeSearchPanel
};