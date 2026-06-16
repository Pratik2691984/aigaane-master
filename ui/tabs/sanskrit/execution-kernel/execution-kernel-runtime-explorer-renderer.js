"use strict";

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderRuntimeExplorerPanel(record = {}) {
  const items = Array.isArray(record.items)
    ? record.items
    : [];

  return Object.freeze({
    title: "Runtime Explorer",
    status: items.length
      ? "EXPLORER_READY"
      : "EMPTY",

    readOnly: true,

    body: [
      "Explorer Status: " +
        escapeHtml(record.explorerStatus),

      "Explorer Mode: " +
        escapeHtml(record.explorerMode),

      "",

      "Items:",

      ...items.map(
        (item) =>
          "- " + escapeHtml(item)
      )
    ].join("\n")
  });
}

module.exports = {
  renderRuntimeExplorerPanel
};