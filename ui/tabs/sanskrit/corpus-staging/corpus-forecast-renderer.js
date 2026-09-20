"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderCorpusForecastPanel(summary = {}) {
  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Forecast Status: " + escapeHtml(summary.forecastStatus || "forecast-ready"),
    "Total Records: " + escapeHtml(summary.totalRecords || 0),
    "Projected Finish Second: " + escapeHtml(summary.projectedFinishSecond || 0),
    "Projected Throughput / Second: " + escapeHtml(
      summary.projectedThroughputPerSecond || 0
    ),
    "Projected Completion Percent: " + escapeHtml(
      summary.projectedCompletionPercent || 0
    ),
    "Queue Exhaustion Second: " + escapeHtml(summary.queueExhaustionSecond || 0),
    "Import Readiness Forecast: " + escapeHtml(
      Boolean(summary.importReadinessForecast)
    ),

    "",
    "Preview Only: true",
    "Read Only: true",
    "Forecast Execution Allowed: false",
    "Simulation Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Forecast",
    status: summary.valid ? "FORECAST_READY" : "FORECAST_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusForecastPanel
};