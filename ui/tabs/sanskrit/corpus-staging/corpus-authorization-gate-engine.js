"use strict";

const {
  buildCorpusAuthorizationGateRecord
} = require("./corpus-authorization-gate-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveAuthorizationGateStatus(governance = {}) {
  if (governance.status === "governance-decision-pending") {
    return "authorization-blocked";
  }
  if (
    governance.status === "governance-blocked" ||
    governance.canonicalWriteAllowed === true ||
    governance.promotionAllowed === true ||
    governance.importAllowed === true ||
    governance.executionAllowed === true
  ) {
    return "authorization-blocked";
  }
  if (
    governance.status === "governance-cleared-for-authorization" &&
    governance.decision === "cleared-for-authorization"
  ) {
    return "authorization-ready";
  }
  return "authorization-blocked";
}

function summarizeCorpusAuthorizationGate(governance = {}) {
  const status = deriveAuthorizationGateStatus(governance);
  return freeze(
    buildCorpusAuthorizationGateRecord({
      status,
      authorized: status === "authorization-ready",
      failures: status === "authorization-ready" ? [] : ["not-authorized"]
    })
  );
}

module.exports = {
  deriveAuthorizationGateStatus,
  summarizeCorpusAuthorizationGate
};
