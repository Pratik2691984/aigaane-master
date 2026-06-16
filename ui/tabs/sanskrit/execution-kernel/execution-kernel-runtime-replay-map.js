"use strict";

const REPLAY_SCHEMA = "sanskrit-runtime-replay.v1";

const REPLAY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  BLOCKED: "BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeRuntimeReplayPlan(input = {}) {
  return freeze({
    replayId: String(input.replayId || "runtime-replay"),
    createdAt: String(input.createdAt || "static"),

    sourceSnapshotId: String(input.sourceSnapshotId || "source-unresolved"),
    targetSnapshotId: String(input.targetSnapshotId || "target-unresolved"),

    sourceHash: String(input.sourceHash || "source-pending"),
    targetHash: String(input.targetHash || "target-pending"),

    replayMode: String(input.replayMode || "inspection-only"),
    replayAllowed: Boolean(input.replayAllowed === true),

    stepCount: Math.max(0, Number(input.stepCount || 0)),

    steps: freeze([...(Array.isArray(input.steps) ? input.steps : [])]),
    warnings: freeze([...(Array.isArray(input.warnings) ? input.warnings : [])]),

    diagnostics: freeze({...(isObject(input.diagnostics) ? input.diagnostics : {})}),
    metadata: freeze({...(isObject(input.metadata) ? input.metadata : {})})
  });
}

function buildRuntimeReplayPlan(input = {}) {
  const normalized = normalizeRuntimeReplayPlan(input);

  return freeze({
    schemaVersion: REPLAY_SCHEMA,
    state: normalized.stepCount > 0 ? REPLAY_STATES.BLOCKED : REPLAY_STATES.EMPTY,
    ...normalized,
    replayAllowed: false
  });
}

function validateRuntimeReplayPlan(plan = {}) {
  const errors = [];

  if (!isObject(plan)) errors.push("plan");
  if (typeof plan.replayMode !== "string") errors.push("replayMode");
  if (typeof plan.replayAllowed !== "boolean") errors.push("replayAllowed");

  if (
    !Number.isInteger(Number(plan.stepCount)) ||
    Number(plan.stepCount) < 0
  ) {
    errors.push("stepCount");
  }

  if (!Array.isArray(plan.steps)) errors.push("steps");
  if (!Array.isArray(plan.warnings)) errors.push("warnings");
  if (!isObject(plan.diagnostics)) errors.push("diagnostics");
  if (!isObject(plan.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  REPLAY_SCHEMA,
  REPLAY_STATES,
  normalizeRuntimeReplayPlan,
  buildRuntimeReplayPlan,
  validateRuntimeReplayPlan
};