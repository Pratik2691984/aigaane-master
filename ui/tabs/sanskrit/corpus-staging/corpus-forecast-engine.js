"use strict";

const {
  buildCorpusForecastRecord
} = require("./corpus-forecast-map.js");

const {
  summarizeCorpusSimulation,
  simulateCorpusExecution
} = require("./corpus-simulation-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveForecastStatus(simulation = {}) {
  if (simulation.valid === false) {
    return "forecast-blocked";
  }

  if (
    Number(simulation.finalCompletionPercent || 0) === 100 &&
    simulation.simulationExecutionAllowed === false &&
    simulation.canonicalWriteAllowed === false
  ) {
    return "forecast-ready";
  }

  return "forecast-review";
}

function buildCorpusForecast(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const simulationSummary = summarizeCorpusSimulation(
    input,
    windowSize,
    secondsPerWindow
  );

  const simulation = simulateCorpusExecution(input, windowSize, secondsPerWindow);

  const forecastStatus = deriveForecastStatus(simulationSummary);

  return buildCorpusForecastRecord({
    forecastStatus,
    totalRecords: simulationSummary.totalRecords,
    projectedFinishSecond: simulationSummary.totalEstimatedSeconds,
    projectedThroughputPerSecond: simulationSummary.estimatedThroughputPerSecond,
    projectedCompletionPercent: simulationSummary.finalCompletionPercent,
    queueExhaustionSecond: simulationSummary.totalEstimatedSeconds,
    importReadinessForecast: forecastStatus === "forecast-ready",
    simulation
  });
}

function summarizeCorpusForecast(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const forecast = buildCorpusForecast(input, windowSize, secondsPerWindow);

  return freeze({
    state: forecast.state,
    valid: forecast.state !== "FORECAST_BLOCKED",
    forecastStatus: forecast.forecastStatus,
    totalRecords: forecast.totalRecords,
    projectedFinishSecond: forecast.projectedFinishSecond,
    projectedThroughputPerSecond: forecast.projectedThroughputPerSecond,
    projectedCompletionPercent: forecast.projectedCompletionPercent,
    queueExhaustionSecond: forecast.queueExhaustionSecond,
    importReadinessForecast: forecast.importReadinessForecast,
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

module.exports = {
  deriveForecastStatus,
  buildCorpusForecast,
  summarizeCorpusForecast
};