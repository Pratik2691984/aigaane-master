"use strict";

const {
  buildRuntimeGovernanceDecision,
  normalizeRuntimeGovernanceDecision
} = require("./execution-kernel-runtime-governance-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeGovernanceControls(record = {}) {
  const findings = stableArray(record.findings);

  const controls = [
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied",
    "inspection-only-approved"
  ];

  if (findings.includes("runtime-transition-detected")) {
    controls.push("runtime-transition-review-required");
  }

  if (findings.includes("warnings-present")) {
    controls.push("warning-review-required");
  }

  return freeze(controls);
}

function createRuntimeGovernanceDecision(record = {}) {
  const findings = stableArray(record.findings);
  const warnings = stableArray(record.warnings);
  const controls = deriveRuntimeGovernanceControls(record);

  return buildRuntimeGovernanceDecision({
    auditId: record.auditId || "runtime-audit",
    auditStatus: record.auditStatus || "review-only",

    governanceStatus: "inspection-approved",
    decision: "approve-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    findingCount: findings.length,
    warningCount: warnings.length,

    controls,
    findings,
    warnings,

    diagnostics: {
      governanceReady: true,
      readOnly: true,
      replayBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      controlCount: controls.length
    }
  });
}

function inspectRuntimeGovernanceDecision(decision = {}) {
  const normalized = normalizeRuntimeGovernanceDecision(decision);

  return freeze({
    ready: true,
    governanceStatus: "inspection-approved",
    decision: "approve-inspection-only",

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    controlCount: normalized.controls.length,
    findingCount: normalized.findingCount,
    warningCount: normalized.warningCount,

    readOnly: true,
    replayBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeGovernanceDecisions(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeGovernanceDecision(a)) ===
      JSON.stringify(normalizeRuntimeGovernanceDecision(b)),

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,
    readOnly: true
  });
}

module.exports = {
  deriveRuntimeGovernanceControls,
  createRuntimeGovernanceDecision,
  inspectRuntimeGovernanceDecision,
  compareRuntimeGovernanceDecisions
};