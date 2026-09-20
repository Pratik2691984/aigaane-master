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

function renderRuntimeControllerPanel(record = {}) {
  const bindings = Array.isArray(record.bindings) ? record.bindings : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Controller Status: " + escapeHtml(record.controllerStatus),
    "Controller Mode: " + escapeHtml(record.controllerMode),
    "Source Panel Status: " + escapeHtml(record.sourcePanelStatus),
    "Source Panel Mode: " + escapeHtml(record.sourcePanelMode),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "Controller Allowed: false",
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
    "Binding Count: " + escapeHtml(record.bindingCount || bindings.length || 0),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Bindings:",
    ...bindings.map((binding) => "- " + escapeHtml(binding)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Controller",
    status: bindings.length ? "CONTROLLER_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeControllerPanel
};