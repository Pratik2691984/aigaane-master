"use strict";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCorpusPostAttestationHoldPanel(input = {}) {
  const status = escapeHtml(input.status || "hold-waiting-attestation");
  const body = [
    "<section class=\"corpus-post-attestation-hold\">",
    "<h2>Node 38E Post-Attestation Hold</h2>",
    "<p>Status: " + status + "</p>",
    "<p>Hold completed: no</p>",
    "<p>Auto-promote: refused</p>",
    "<p>Attestation is not authorization.</p>",
    "<p>Next: 38F governance decision</p>",
    "</section>"
  ].join("");
  return { title: "Post-Attestation Hold", body };
}

module.exports = {
  renderCorpusPostAttestationHoldPanel
};
