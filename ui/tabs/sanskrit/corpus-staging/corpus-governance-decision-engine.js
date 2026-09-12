"use strict";

const {
  buildCorpusGovernanceDecisionRecord
} = require("./corpus-governance-decision-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveGovernanceDecisionStatus(hold = {}, decision = null) {
  if (
    hold.status === "hold-blocked" ||
    hold.canonicalWriteAllowed === true ||
    hold.promotionAllowed === true ||
    hold.importAllowed === true ||
    hold.executionAllowed === true ||
    hold.autoPromote === true
  ) {
    return "governance-blocked";
  }
  if (decision === "blocked") {
    return "governance-blocked";
  }
  if (decision === "cleared-for-authorization") {
    return "governance-cleared-for-authorization";
  }
  return "governance-decision-pending";
}

function summarizeCorpusGovernanceDecision(hold = {}, decision = null) {
  const status = deriveGovernanceDecisionStatus(hold, decision);
  const record = buildCorpusGovernanceDecisionRecord({
    status,
    decision:
      status === "governance-cleared-for-authorization"
        ? "cleared-for-authorization"
        : status === "governance-blocked" && decision === "blocked"
          ? "blocked"
          : null,
    failures:
      status === "governance-blocked" && decision !== "blocked"
        ? ["governance-not-clearable"]
        : []
  });
  return freeze({
    ...record,
    failureCount: record.failures.length,
    isNonAuthorizing: true,
    nextGate: "38G PROMOTION AUTHORIZATION"
  });
}

module.exports = {
  deriveGovernanceDecisionStatus,
  summarizeCorpusGovernanceDecision
};
