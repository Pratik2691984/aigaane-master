"use strict";

const CORPUS_FORECAST_SCHEMA = "sanskrit-bulk-corpus-forecast.v1";

const CORPUS_FORECAST_STATES = Object.freeze({
  EMPTY: "EMPTY",
  FORECAST_READY: "FORECAST_READY",
  FORECAST_BLOCKED: "FORECAST_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusForecastInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_FORECAST_SCHEMA,
    forecastStatus: String(input.forecastStatus || "forecast-ready"),
    totalRecords: asCount(input.totalRecords),
    projectedFinishSecond: Number(input.projectedFinishSecond || 0),
    projectedThroughputPerSecond: Number(input.projectedThroughputPerSecond || 0),
    projectedCompletionPercent: Number(input.projectedCompletionPercent || 0),
    queueExhaustionSecond: Number(input.queueExhaustionSecond || 0),
    importReadinessForecast: Boolean(input.importReadinessForecast),
    simulation: freeze(isObject(input.simulation) ? input.simulation : {}),
    previewOnly: true,
    readOnly: true,
    forecastExecutionAllowed: false,
    simulationExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusForecastRecord(input = {}) {
  const normalized = normalizeCorpusForecastInput(input);

  let state = CORPUS_FORECAST_STATES.FORECAST_READY;

  if (normalized.totalRecords === 0) {
    state = CORPUS_FORECAST_STATES.EMPTY;
  }

  if (
    normalized.simulation &&
    normalized.simulation.valid === false
  ) {
    state = CORPUS_FORECAST_STATES.FORECAST_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_FORECAST_SCHEMA,
  CORPUS_FORECAST_STATES,
  normalizeCorpusForecastInput,
  buildCorpusForecastRecord
};