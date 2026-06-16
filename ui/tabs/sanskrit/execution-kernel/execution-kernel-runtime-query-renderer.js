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

function renderRuntimeQueryPanel(record = {}) {
  const entries = Array.isArray(record.entries) ? record.entries : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Query Status: " + escapeHtml(record.queryStatus),
    "Query Mode: " + escapeHtml(record.queryMode),
    "Source Lookup Status: " + escapeHtml(record.sourceLookupStatus),
    "Source Lookup Mode: " + escapeHtml(record.sourceLookupMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
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
    "Entry Count: " + escapeHtml(record.entryCount || entries.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Entries:",
    ...entries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Query",
    status: entries.length ? "QUERY_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeQueryPanel
};