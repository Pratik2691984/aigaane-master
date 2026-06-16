"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(
      /&/g,
      "&amp;"
    )
    .replace(
      /</g,
      "&lt;"
    )
    .replace(
      />/g,
      "&gt;"
    );
}

function renderRuntimeDirectoryPanel(
  record = {}
) {
  const entries =
    Array.isArray(
      record.entries
    )
      ? record.entries
      : [];

  const warnings =
    Array.isArray(
      record.warnings
    )
      ? record.warnings
      : [];

  const body = [
    "Directory Status: " +
      escapeHtml(
        record.directoryStatus
      ),

    "Directory Mode: " +
      escapeHtml(
        record.directoryMode
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
  ].join(
    "\n"
  );

  return freeze({
    title:
      "Runtime Directory",

    status:
      entries.length
        ? "DIRECTORY_READY"
        : "EMPTY",

    readOnly: true,

    body
  });
}

module.exports = {
  renderRuntimeDirectoryPanel
};