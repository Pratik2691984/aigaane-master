"use strict";

const {
  buildCorpusGovernanceDecisionRecord
} = require("./corpus-governance-decision-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveGovernanceDecisionStatus(hold = {}, decision = null) {
  if (hold.status === "hold-blocked" || hold.canonicalWriteAllowed === true) {
    return "governance-decision-blocked";
  }
  if (decision === "blocked") {
    return "governance-decision-blocked";
  }
  if (decision === "cleared-for-authorization") {
    return hold.status === "hold-active"
      ? "governance-decision-cleared-for-authorization"
      : "governance-decision-blocked";
  }
  return "governance-decision-pending";
}

function summarizeCorpusGovernanceDecision(hold = {}, decision = null) {
  const status = deriveGovernanceDecisionStatus(hold, decision);
  return freeze(
    buildCorpusGovernanceDecisionRecord({
      status,
      decision:
        status === "governance-decision-cleared-for-authorization"
          ? "cleared-for-authorization"
          : status === "governance-decision-blocked" && decision === "blocked"
            ? "blocked"
            : null,
      failures:
        status === "governance-decision-blocked" && decision !== "blocked"
          ? ["governance-not-clearable"]
          : []
    })
  );
}

module.exports = {
  deriveGovernanceDecisionStatus,
  summarizeCorpusGovernanceDecision
};
