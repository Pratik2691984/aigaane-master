"use strict";

const {
  buildRuntimeReplayPlan,
  normalizeRuntimeReplayPlan
} = require("./execution-kernel-runtime-replay-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableValue(v) {
  if (v === undefined) return null;
  return v;
}

function deriveRuntimeReplaySteps(source = {}, target = {}) {
  const fields = [
    "executionMode",
    "pipelineStage",
    "ruleQueueLength",
    "transformCount",
    "inspectionHash"
  ];

  const steps = [];

  fields.forEach((field) => {
    const fromValue = stableValue(source[field]);
    const toValue = stableValue(target[field]);

    if (JSON.stringify(fromValue) !== JSON.stringify(toValue)) {
      steps.push(freeze({
        index: steps.length,
        field,
        from: fromValue,
        to: toValue,
        action: "inspect-change",
        execute: false,
        mutate: false
      }));
    }
  });

  return freeze(steps);
}

function createRuntimeReplayPlan(source = {}, target = {}) {
  const steps = deriveRuntimeReplaySteps(source, target);

  return buildRuntimeReplayPlan({
    sourceSnapshotId: source.snapshotId || "source-unresolved",
    targetSnapshotId: target.snapshotId || "target-unresolved",
    sourceHash: source.inspectionHash || "source-pending",
    targetHash: target.inspectionHash || "target-pending",
    replayMode: "inspection-only",
    replayAllowed: false,
    stepCount: steps.length,
    steps,
    warnings: steps.length ? ["Replay is inspection-only; execution is blocked."] : [],
    diagnostics: {
      replayReady: true,
      readOnly: true,
      executionBlocked: true,
      mutationBlocked: true,
      canonicalWriteBlocked: true
    },
    metadata: {
      comparedFieldCount: 5
    }
  });
}

function inspectRuntimeReplayPlan(plan = {}) {
  const normalized = normalizeRuntimeReplayPlan(plan);

  return freeze({
    ready: true,
    replayMode: normalized.replayMode,
    replayAllowed: false,
    stepCount: normalized.stepCount,
    readOnly: true,
    executionBlocked: true,
    mutationBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeReplayPlan(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeReplayPlan(a)) ===
      JSON.stringify(normalizeRuntimeReplayPlan(b)),
    replayAllowed: false,
    readOnly: true
  });
}

module.exports = {
  deriveRuntimeReplaySteps,
  createRuntimeReplayPlan,
  inspectRuntimeReplayPlan,
  compareRuntimeReplayPlan
};