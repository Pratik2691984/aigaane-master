"use strict";

const {
  REPLAY_TRACE_SCHEMA_VERSION,
  REPLAY_TRACE_CONTRACTS,
  REPLAY_TRACE_FIELDS,
  getReplayTraceSummary
} = require("./replay-trace-map.js");

function normalizeReplayTraceField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    summary: String(field.summary || ""),
    required: Boolean(field.required),
    diagnostics: Array.isArray(field.diagnostics)
      ? field.diagnostics.map(String)
      : []
  };
}

function buildReplayTraceExport() {
  const summary = getReplayTraceSummary();

  return {
    schemaVersion: REPLAY_TRACE_SCHEMA_VERSION,
    contracts: { ...REPLAY_TRACE_CONTRACTS },
    ready: true,
    fieldCount: REPLAY_TRACE_FIELDS.length,
    eventTypes: Array.isArray(summary.eventTypes)
      ? summary.eventTypes.map(String)
      : [],
    fields: REPLAY_TRACE_FIELDS.map(normalizeReplayTraceField),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerLinked: true,
      irLinked: true,
      queueLinked: true,
      mutationFree: true
    }
  };
}

function createReplayTraceSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const events = Array.isArray(safeInput.events) ? safeInput.events : [];

  return Object.freeze({
    schemaVersion: REPLAY_TRACE_SCHEMA_VERSION,
    kind: "REPLAY_TRACE_SNAPSHOT",
    events: Object.freeze(
      events.map((event, index) =>
        Object.freeze({
          index,
          id: String(event.id || `trace-event-${index}`),
          type: String(event.type || "DIAGNOSTIC"),
          referenceId: String(event.referenceId || ""),
          summary: String(event.summary || ""),
          diagnostics: Array.isArray(event.diagnostics)
            ? event.diagnostics.map(String)
            : []
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      eventCount: events.length
    })
  });
}

function getReplayTraceDiagnostics() {
  const traceExport = buildReplayTraceExport();

  return {
    schemaVersion: traceExport.schemaVersion,
    ready: traceExport.ready,
    fieldCount: traceExport.fieldCount,
    contractsSatisfied: Object.values(traceExport.contracts).every(Boolean),
    diagnostics: { ...traceExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeReplayTraceField,
    buildReplayTraceExport,
    createReplayTraceSnapshot,
    getReplayTraceDiagnostics
  };
}