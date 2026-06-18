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

function renderCorpusAllocationPanel(summary = {}) {
  const allocation = summary.allocation || {};
  const warnings = Array.isArray(summary.warnings) ? summary.warnings : [];
  const errors = Array.isArray(summary.errors) ? summary.errors : [];

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Total Reserved: " + escapeHtml(summary.totalReserved || 0),
    "Total Used: " + escapeHtml(summary.totalUsed || 0),
    "Max Records: " + escapeHtml(summary.maxRecords || 2000),
    "Free Capacity: " + escapeHtml(summary.freeCapacity || 0),

    "",
    "Allocation:",
    "- dhatu: " + escapeHtml((allocation.dhatu && allocation.dhatu.used) || 0)
      + " / " + escapeHtml((allocation.dhatu && allocation.dhatu.quota) || 0),
    "- sutra: " + escapeHtml((allocation.sutra && allocation.sutra.used) || 0)
      + " / " + escapeHtml((allocation.sutra && allocation.sutra.quota) || 0),
    "- stotra: " + escapeHtml((allocation.stotra && allocation.stotra.used) || 0)
      + " / " + escapeHtml((allocation.stotra && allocation.stotra.quota) || 0),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning)),

    "",
    "Errors:",
    ...errors.map((error) => "- " + escapeHtml(error)),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false",
    "Allocation Write Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Allocation Planner",
    status: summary.valid ? "ALLOCATION_READY" : "ALLOCATION_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusAllocationPanel
};