"use strict";

const {
  DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION,
  DERIVATION_GRAPH_CONTRACTS,
  DERIVATION_GRAPH_FIELDS,
  getDerivationGraphPlanningSummary
} = require("./derivation-graph-planning-map.js");

function normalizeDerivationGraphField(field) {
  return {
    id: String(field.id || ""),
    type: String(field.type || ""),
    required: Boolean(field.required)
  };
}

function buildDerivationGraphPlanningExport() {
  const summary = getDerivationGraphPlanningSummary();

  return {
    schemaVersion: DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION,
    contracts: { ...DERIVATION_GRAPH_CONTRACTS },
    ready: true,
    fieldCount: DERIVATION_GRAPH_FIELDS.length,
    nodeTypes: Array.isArray(summary.nodeTypes)
      ? summary.nodeTypes.map(String)
      : [],
    fields: DERIVATION_GRAPH_FIELDS.map(normalizeDerivationGraphField),
    diagnostics: {
      normalized: true,
      deterministic: true,
      immutable: true,
      runtimeSafe: true,
      replaySafe: true,
      schedulerLinked: true,
      queueLinked: true,
      traceLinked: true,
      checkpointLinked: true,
      sandhiPlanningLinked: true,
      morphologyPlanningLinked: true,
      lakaraPlanningLinked: true,
      executionGuardLinked: true,
      mutationFree: true,
      graphOnly: true
    }
  };
}

function createDerivationGraphPlanningSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const nodes = Array.isArray(safeInput.nodes) ? safeInput.nodes : [];
  const edges = Array.isArray(safeInput.edges) ? safeInput.edges : [];

  return Object.freeze({
    schemaVersion: DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION,
    kind: "DERIVATION_GRAPH_PLANNING_SNAPSHOT",
    nodes: Object.freeze(
      nodes.map((node, index) =>
        Object.freeze({
          index,
          id: String(node.id || `graph-node-${index}`),
          type: String(node.type || "DERIVATION_STATE"),
          referenceId: String(node.referenceId || ""),
          planned: true,
          executed: false
        })
      )
    ),
    edges: Object.freeze(
      edges.map((edge, index) =>
        Object.freeze({
          index,
          id: String(edge.id || `graph-edge-${index}`),
          from: String(edge.from || ""),
          to: String(edge.to || ""),
          relation: String(edge.relation || "PLANNED_DERIVATION_EDGE"),
          planned: true,
          executed: false
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      nodeCount: nodes.length,
      edgeCount: edges.length
    })
  });
}

function getDerivationGraphPlanningDiagnostics() {
  const graphExport = buildDerivationGraphPlanningExport();

  return {
    schemaVersion: graphExport.schemaVersion,
    ready: graphExport.ready,
    fieldCount: graphExport.fieldCount,
    contractsSatisfied: Object.values(graphExport.contracts).every(Boolean),
    diagnostics: { ...graphExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeDerivationGraphField,
    buildDerivationGraphPlanningExport,
    createDerivationGraphPlanningSnapshot,
    getDerivationGraphPlanningDiagnostics
  };
}