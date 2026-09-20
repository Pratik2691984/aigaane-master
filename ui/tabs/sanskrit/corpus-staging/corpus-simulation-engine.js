"use strict";

const {
  buildCorpusSimulationRecord
} = require("./corpus-simulation-map.js");

const {
  buildCorpusTimeline
} = require("./corpus-timeline-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildSimulationSnapshots(timeline = []) {
  const snapshots = timeline.map((item, index) => {
    return {
      snapshotId: "simulation-" + String(index + 1).padStart(3, "0"),
      timelineId: String(item.timelineId || ""),
      windowId: String(item.windowId || ""),
      order: Number(item.order || index + 1),
      recordCount: Number(item.recordCount || 0),
      elapsedSecond: Number(item.endSecond || 0),
      completionPercent: Number(item.completionPercent || 0),
      status: "simulated-complete",
      previewOnly: true
    };
  });

  return freeze(snapshots);
}

function estimateSimulationThroughput(totalRecords = 0, totalSeconds = 0) {
  if (!totalSeconds) return 0;
  return Math.round((Number(totalRecords || 0) / Number(totalSeconds || 0)) * 1000) / 1000;
}

function simulateCorpusExecution(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const timelinePlan = buildCorpusTimeline(input, windowSize, secondsPerWindow);
  const timeline = Array.isArray(timelinePlan.timeline) ? timelinePlan.timeline : [];
  const snapshots = buildSimulationSnapshots(timeline);

  const totalRecords = snapshots.reduce((sum, item) => {
    return sum + Number(item.recordCount || 0);
  }, 0);

  return buildCorpusSimulationRecord({
    simulationCount: snapshots.length,
    snapshots,
    totalRecords,
    totalEstimatedSeconds: Number(timelinePlan.totalEstimatedSeconds || 0),
    estimatedThroughputPerSecond: estimateSimulationThroughput(
      totalRecords,
      Number(timelinePlan.totalEstimatedSeconds || 0)
    ),
    finalCompletionPercent: Number(timelinePlan.finalCompletionPercent || 0),
    timelinePlan
  });
}

function summarizeCorpusSimulation(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const simulation = simulateCorpusExecution(input, windowSize, secondsPerWindow);

  return freeze({
    state: simulation.state,
    valid: simulation.state !== "SIMULATION_BLOCKED",
    simulationCount: simulation.simulationCount,
    totalRecords: simulation.totalRecords,
    totalEstimatedSeconds: simulation.totalEstimatedSeconds,
    estimatedThroughputPerSecond: simulation.estimatedThroughputPerSecond,
    finalCompletionPercent: simulation.finalCompletionPercent,
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

module.exports = {
  buildSimulationSnapshots,
  estimateSimulationThroughput,
  simulateCorpusExecution,
  summarizeCorpusSimulation
};