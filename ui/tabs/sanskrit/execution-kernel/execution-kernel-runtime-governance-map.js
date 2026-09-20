"use strict";

const GOVERNANCE_SCHEMA = "sanskrit-runtime-governance.v1";

const GOVERNANCE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY",
  APPROVED_FOR_INSPECTION: "APPROVED_FOR_INSPECTION"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asNonNegativeInteger(v) {
  const n = Number(v || 0);
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.floor(n));
}

function normalizeRuntimeGovernanceDecision(input = {}) {
  return freeze({
    governanceId: String(input.governanceId || "runtime-governance"),
    createdAt: String(input.createdAt || "static"),

    auditId: String(input.auditId || "runtime-audit"),
    auditStatus: String(input.auditStatus || "review-only"),

    governanceStatus: String(input.governanceStatus || "inspection-approved"),
    decision: String(input.decision || "approve-inspection-only"),

    replayAllowed: Boolean(input.replayAllowed === true),
    executionAllowed: Boolean(input.executionAllowed === true),
    mutationAllowed: Boolean(input.mutationAllowed === true),
    publicationAllowed: Boolean(input.publicationAllowed === true),
    rollbackAllowed: Boolean(input.rollbackAllowed === true),
    canonicalWriteAllowed: Boolean(input.canonicalWriteAllowed === true),

    findingCount: asNonNegativeInteger(input.findingCount),
    warningCount: asNonNegativeInteger(input.warningCount),

    controls: freeze([...(Array.isArray(input.controls) ? input.controls : [])]),
    findings: freeze([...(Array.isArray(input.findings) ? input.findings : [])]),
    warnings: freeze([...(Array.isArray(input.warnings) ? input.warnings : [])]),

    diagnostics: freeze({ ...(isObject(input.diagnostics) ? input.diagnostics : {}) }),
    metadata: freeze({ ...(isObject(input.metadata) ? input.metadata : {}) })
  });
}

function buildRuntimeGovernanceDecision(input = {}) {
  const normalized = normalizeRuntimeGovernanceDecision(input);

  return freeze({
    schemaVersion: GOVERNANCE_SCHEMA,
    state: normalized.controls.length > 0
      ? GOVERNANCE_STATES.APPROVED_FOR_INSPECTION
      : GOVERNANCE_STATES.EMPTY,

    ...normalized,

    governanceStatus: "inspection-approved",
    decision: "approve-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false
  });
}

function validateRuntimeGovernanceDecision(decision = {}) {
  const errors = [];

  if (!isObject(decision)) errors.push("decision");

  if (typeof decision.governanceStatus !== "string") {
    errors.push("governanceStatus");
  }

  if (typeof decision.decision !== "string") {
    errors.push("decisionValue");
  }

  [
    "replayAllowed",
    "executionAllowed",
    "mutationAllowed",
    "publicationAllowed",
    "rollbackAllowed",
    "canonicalWriteAllowed"
  ].forEach((field) => {
    if (typeof decision[field] !== "boolean") {
      errors.push(field);
    }
  });

  if (
    !Number.isInteger(Number(decision.findingCount)) ||
    Number(decision.findingCount) < 0
  ) {
    errors.push("findingCount");
  }

  if (
    !Number.isInteger(Number(decision.warningCount)) ||
    Number(decision.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(decision.controls)) errors.push("controls");
  if (!Array.isArray(decision.findings)) errors.push("findings");
  if (!Array.isArray(decision.warnings)) errors.push("warnings");
  if (!isObject(decision.diagnostics)) errors.push("diagnostics");
  if (!isObject(decision.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  GOVERNANCE_SCHEMA,
  GOVERNANCE_STATES,
  normalizeRuntimeGovernanceDecision,
  buildRuntimeGovernanceDecision,
  validateRuntimeGovernanceDecision
};