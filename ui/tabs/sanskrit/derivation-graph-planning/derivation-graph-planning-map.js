"use strict";

/**
 * Deterministic Sanskrit Derivation Graph Planning Map
 *
 * Connects:
 *   morphology planning
 *   lakara planning
 *   sandhi planning
 *
 * into a unified derivation planning graph.
 *
 * No execution occurs here.
 */

const DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION =
  "sanskrit-derivation-graph-planning.v1";

const DERIVATION_GRAPH_NODE_TYPES = Object.freeze({
  DHATU: "DHATU",
  MORPHOLOGY: "MORPHOLOGY",
  LAKARA: "LAKARA",
  SANDHI: "SANDHI",
  DERIVATION_STATE: "DERIVATION_STATE",
  TERMINAL_STATE: "TERMINAL_STATE"
});

const DERIVATION_GRAPH_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  nonMutating: true,

  schedulerLinked: true,
  queueLinked: true,
  traceLinked: true,
  checkpointLinked: true,

  sandhiPlanningLinked: true,
  morphologyPlanningLinked: true,
  lakaraPlanningLinked: true,

  executionGuardLinked: true,

  replaySafe: true,
  runtimeIsolated: true,
  staticPreviewCompatible: true
});

const DERIVATION_GRAPH_FIELDS = Object.freeze([
  {
    id: "graph.dhatu",
    type: DERIVATION_GRAPH_NODE_TYPES.DHATU,
    required: true
  },
  {
    id: "graph.morphology",
    type: DERIVATION_GRAPH_NODE_TYPES.MORPHOLOGY,
    required: true
  },
  {
    id: "graph.lakara",
    type: DERIVATION_GRAPH_NODE_TYPES.LAKARA,
    required: true
  },
  {
    id: "graph.sandhi",
    type: DERIVATION_GRAPH_NODE_TYPES.SANDHI,
    required: true
  },
  {
    id: "graph.derivation-state",
    type: DERIVATION_GRAPH_NODE_TYPES.DERIVATION_STATE,
    required: true
  },
  {
    id: "graph.terminal-state",
    type: DERIVATION_GRAPH_NODE_TYPES.TERMINAL_STATE,
    required: true
  }
]);

function getDerivationGraphPlanningSummary() {
  return {
    schemaVersion: DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION,
    contracts: DERIVATION_GRAPH_CONTRACTS,
    fieldCount: DERIVATION_GRAPH_FIELDS.length,
    nodeTypes: Object.values(DERIVATION_GRAPH_NODE_TYPES),
    fields: DERIVATION_GRAPH_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    DERIVATION_GRAPH_PLANNING_SCHEMA_VERSION,
    DERIVATION_GRAPH_NODE_TYPES,
    DERIVATION_GRAPH_CONTRACTS,
    DERIVATION_GRAPH_FIELDS,
    getDerivationGraphPlanningSummary
  };
}