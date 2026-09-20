"use strict";

const CORPUS_SIMULATION_SCHEMA = "sanskrit-bulk-corpus-simulation.v1";

const CORPUS_SIMULATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  SIMULATION_READY: "SIMULATION_READY",
  SIMULATION_BLOCKED: "SIMULATION_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusSimulationInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_SIMULATION_SCHEMA,
    simulationCount: asCount(input.simulationCount),
    snapshots: freeze(asArray(input.snapshots)),
    totalRecords: asCount(input.totalRecords),
    totalEstimatedSeconds: Number(input.totalEstimatedSeconds || 0),
    estimatedThroughputPerSecond: Number(input.estimatedThroughputPerSecond || 0),
    finalCompletionPercent: Number(input.finalCompletionPercent || 0),
    timelinePlan: freeze(isObject(input.timelinePlan) ? input.timelinePlan : {}),
    previewOnly: true,
    readOnly: true,
    simulationExecutionAllowed: false,
    timelineExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusSimulationRecord(input = {}) {
  const normalized = normalizeCorpusSimulationInput(input);

  let state = CORPUS_SIMULATION_STATES.SIMULATION_READY;

  if (normalized.simulationCount === 0) {
    state = CORPUS_SIMULATION_STATES.EMPTY;
  }

  if (normalized.timelinePlan && normalized.timelinePlan.valid === false) {
    state = CORPUS_SIMULATION_STATES.SIMULATION_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_SIMULATION_SCHEMA,
  CORPUS_SIMULATION_STATES,
  normalizeCorpusSimulationInput,
  buildCorpusSimulationRecord
};