"use strict";

/**
 * Deterministic Sanskrit Derivation IR Map
 *
 * Immutable, inspection-first intermediate representation metadata for
 * future Sanskrit derivation scheduling. This layer does not execute
 * sandhi, morphology, lakāra generation, or surface-form production.
 */

const DERIVATION_IR_SCHEMA_VERSION = "sanskrit-derivation-ir.v1";

const DERIVATION_IR_NODE_TYPES = Object.freeze({
  ENVIRONMENT: "ENVIRONMENT",
  INPUT_INTENT: "INPUT_INTENT",
  STEM: "STEM",
  ROOT: "ROOT",
  AFFIX: "AFFIX",
  TRANSFORMATION_STEP: "TRANSFORMATION_STEP",
  SNAPSHOT: "SNAPSHOT",
  TRACE: "TRACE"
});

const DERIVATION_IR_CONTRACTS = Object.freeze({
  deterministic: true,
  immutable: true,
  inspectionOnly: true,
  nonPerformative: true,
  runtimeIsolated: true,
  schedulerCompatible: true,
  replaySafe: true,
  staticPreviewCompatible: true
});

const DERIVATION_IR_FIELDS = Object.freeze([
  {
    id: "ir.environment",
    type: DERIVATION_IR_NODE_TYPES.ENVIRONMENT,
    summary: "Derivation environment metadata such as mode, source, scheduler version, and requested derivation intent.",
    required: true,
    diagnostics: ["environment-contract", "scheduler-context"]
  },
  {
    id: "ir.input-intent",
    type: DERIVATION_IR_NODE_TYPES.INPUT_INTENT,
    summary: "Normalized input intent for future derivation scheduling.",
    required: true,
    diagnostics: ["input-normalization", "intent-contract"]
  },
  {
    id: "ir.root",
    type: DERIVATION_IR_NODE_TYPES.ROOT,
    summary: "Root-level lexical unit metadata for future dhātu-aware derivations.",
    required: false,
    diagnostics: ["root-node", "dhatu-compatible"]
  },
  {
    id: "ir.affix",
    type: DERIVATION_IR_NODE_TYPES.AFFIX,
    summary: "Affix or pratyaya metadata reserved for later morphology execution.",
    required: false,
    diagnostics: ["affix-node", "morphology-compatible"]
  },
  {
    id: "ir.transformation-step",
    type: DERIVATION_IR_NODE_TYPES.TRANSFORMATION_STEP,
    summary: "A replay-safe planned transformation step without executing the transformation.",
    required: true,
    diagnostics: ["planned-step", "non-executing"]
  },
  {
    id: "ir.snapshot",
    type: DERIVATION_IR_NODE_TYPES.SNAPSHOT,
    summary: "Immutable snapshot envelope for deterministic replay chains.",
    required: true,
    diagnostics: ["snapshot-envelope", "replay-safe"]
  },
  {
    id: "ir.trace",
    type: DERIVATION_IR_NODE_TYPES.TRACE,
    summary: "Ordered trace metadata connecting scheduler decisions to planned IR snapshots.",
    required: true,
    diagnostics: ["trace-contract", "scheduler-linked"]
  }
]);

function getDerivationIrSummary() {
  return {
    schemaVersion: DERIVATION_IR_SCHEMA_VERSION,
    contracts: DERIVATION_IR_CONTRACTS,
    fieldCount: DERIVATION_IR_FIELDS.length,
    nodeTypes: Object.values(DERIVATION_IR_NODE_TYPES),
    fields: DERIVATION_IR_FIELDS.map((field) => ({ ...field }))
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    DERIVATION_IR_SCHEMA_VERSION,
    DERIVATION_IR_NODE_TYPES,
    DERIVATION_IR_CONTRACTS,
    DERIVATION_IR_FIELDS,
    getDerivationIrSummary
  };
}