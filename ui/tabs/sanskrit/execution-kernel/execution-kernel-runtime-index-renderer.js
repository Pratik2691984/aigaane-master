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

function renderRuntimeIndexPanel(
  record = {}
) {
  const entries =
    Array.isArray(record.entries)
      ? record.entries
      : [];

  const warnings =
    Array.isArray(record.warnings)
      ? record.warnings
      : [];

  const body = [
    "Index Status: " +
      escapeHtml(
        record.indexStatus
      ),

    "Index Mode: " +
      escapeHtml(
        record.indexMode
      ),

    "",

    "Entries:",

    ...entries.map(
      (x) =>
        "- " +
        escapeHtml(x)
    ),

    "",

    "Warnings:",

    ...warnings.map(
      (x) =>
        "- " +
        escapeHtml(x)
    )
  ].join("\n");

  return freeze({
    title:
      "Runtime Index",

    status:
      entries.length
        ? "INDEX_READY"
        : "EMPTY",

    readOnly: true,

    body
  });
}

module.exports = {
  renderRuntimeIndexPanel
};