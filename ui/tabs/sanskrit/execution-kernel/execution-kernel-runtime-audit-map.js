"use strict";

const AUDIT_SCHEMA = "sanskrit-runtime-audit.v1";

const AUDIT_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeRuntimeAuditRecord(input = {}) {
  return freeze({
    auditId: String(input.auditId || "runtime-audit"),
    createdAt: String(input.createdAt || "static"),

    replayId: String(input.replayId || "runtime-replay"),
    replayMode: String(input.replayMode || "inspection-only"),
    replayAllowed: Boolean(input.replayAllowed === true),

    sourceHash: String(input.sourceHash || "source-pending"),
    targetHash: String(input.targetHash || "target-pending"),

    stepCount: Math.max(0, Number(input.stepCount || 0)),
    auditStatus: String(input.auditStatus || "review-only"),

    findings: freeze([...(Array.isArray(input.findings) ? input.findings : [])]),
    warnings: freeze([...(Array.isArray(input.warnings) ? input.warnings : [])]),

    diagnostics: freeze({ ...(isObject(input.diagnostics) ? input.diagnostics : {}) }),
    metadata: freeze({ ...(isObject(input.metadata) ? input.metadata : {}) })
  });
}

function buildRuntimeAuditRecord(input = {}) {
  const normalized = normalizeRuntimeAuditRecord(input);

  return freeze({
    schemaVersion: AUDIT_SCHEMA,
    state: normalized.findings.length > 0 ? AUDIT_STATES.REVIEW_ONLY : AUDIT_STATES.EMPTY,
    ...normalized,
    replayAllowed: false,
    auditStatus: "review-only"
  });
}

function validateRuntimeAuditRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");
  if (typeof record.replayMode !== "string") errors.push("replayMode");
  if (typeof record.replayAllowed !== "boolean") errors.push("replayAllowed");

  if (
    !Number.isInteger(Number(record.stepCount)) ||
    Number(record.stepCount) < 0
  ) {
    errors.push("stepCount");
  }

  if (typeof record.auditStatus !== "string") errors.push("auditStatus");
  if (!Array.isArray(record.findings)) errors.push("findings");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  AUDIT_SCHEMA,
  AUDIT_STATES,
  normalizeRuntimeAuditRecord,
  buildRuntimeAuditRecord,
  validateRuntimeAuditRecord
};