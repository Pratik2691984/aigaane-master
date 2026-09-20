"use strict";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCorpusAuthorizationGatePanel(input = {}) {
  const status = escapeHtml(input.status || "authorization-blocked");
  const authorized = input.authorized === true ? "yes" : "no";
  const body = [
    "<section class=\"corpus-authorization-gate\">",
    "<h2>Node 38G Authorization Gate</h2>",
    "<p>Status: " + status + "</p>",
    "<p>Authorized: " + authorized + "</p>",
    "<p>Authorization is not write, promotion, import, or execution.</p>",
    "<p>Next: 38H PROMOTION PREFLIGHT</p>",
    "</section>"
  ].join("");
  return { title: "Authorization Gate", body };
}

module.exports = {
  renderCorpusAuthorizationGatePanel
};
