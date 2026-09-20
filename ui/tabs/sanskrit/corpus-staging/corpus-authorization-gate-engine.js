"use strict";

const {
  buildCorpusAuthorizationGateRecord
} = require("./corpus-authorization-gate-map.js");

function freeze(v) {
  return Object.freeze(v);
}

/* Authoritative hold/authorization is backend 38G; UI is observational. */
function deriveAuthorizationGateStatus(governance = {}, hold) {
  if (hold == null) {
    return "authorization-blocked";
  }
  if (governance.status === "governance-decision-pending") {
    return "authorization-blocked";
  }
  if (
    governance.status === "governance-blocked" ||
    governance.canonicalWriteAllowed === true ||
    governance.promotionAllowed === true ||
    governance.importAllowed === true ||
    governance.executionAllowed === true ||
    hold.status === "hold-blocked" ||
    hold.autoPromote === true ||
    hold.canonicalWriteAllowed === true
  ) {
    return "authorization-blocked";
  }
  if (
    governance.status === "governance-cleared-for-authorization" &&
    governance.decision === "cleared-for-authorization" &&
    (hold.status === "hold-waiting-attestation" || hold.status === "hold-active")
  ) {
    return "authorization-ready";
  }
  return "authorization-blocked";
}

function summarizeCorpusAuthorizationGate(governance = {}, hold) {
  const status = deriveAuthorizationGateStatus(governance, hold);
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
