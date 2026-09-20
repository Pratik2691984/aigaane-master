"use strict";

const {
  buildRuntimeAuditRecord,
  normalizeRuntimeAuditRecord
} = require("./execution-kernel-runtime-audit-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeAuditFindings(plan = {}) {
  const findings = [
    "execution-blocked",
    "mutation-blocked",
    "canonical-write-blocked",
    "replay-inspection-only"
  ];

  if (Number(plan.stepCount || 0) > 0) {
    findings.push("runtime-transition-detected");
  }

  if (Array.isArray(plan.warnings) && plan.warnings.length > 0) {
    findings.push("warnings-present");
  }

  return freeze(findings);
}

function createRuntimeAuditRecord(plan = {}) {
  const findings = deriveRuntimeAuditFindings(plan);

  return buildRuntimeAuditRecord({
    replayId: plan.replayId || "runtime-replay",
    replayMode: plan.replayMode || "inspection-only",
    replayAllowed: false,

    sourceHash: plan.sourceHash || "source-pending",
    targetHash: plan.targetHash || "target-pending",

    stepCount: Number(plan.stepCount || 0),
    auditStatus: "review-only",

    findings,
    warnings: Array.isArray(plan.warnings) ? plan.warnings : [],

    diagnostics: {
      auditReady: true,
      readOnly: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      findingCount: findings.length
    }
  });
}

function inspectRuntimeAuditRecord(record = {}) {
  const normalized = normalizeRuntimeAuditRecord(record);

  return freeze({
    ready: true,
    auditStatus: "review-only",
    replayAllowed: false,
    findingCount: normalized.findings.length,
    warningCount: normalized.warnings.length,
    readOnly: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeAuditRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeAuditRecord(a)) ===
      JSON.stringify(normalizeRuntimeAuditRecord(b)),
    replayAllowed: false,
    readOnly: true
  });
}

module.exports = {
  deriveRuntimeAuditFindings,
  createRuntimeAuditRecord,
  inspectRuntimeAuditRecord,
  compareRuntimeAuditRecords
};