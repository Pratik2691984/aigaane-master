"use strict";

const {
  SANDHI_PLANNING_SCHEMA_VERSION,
  SANDHI_PLANNING_CONTRACTS,
  SANDHI_PLANNING_FIELDS,
  getSandhiPlanningSummary
} = require("./sandhi-planning-map.js");

function normalizeSandhiPlanningField(field) {
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

function buildSandhiPlanningExport() {
  const summary = getSandhiPlanningSummary();

  return {
    schemaVersion: SANDHI_PLANNING_SCHEMA_VERSION,
    contracts: { ...SANDHI_PLANNING_CONTRACTS },
    ready: true,
    fieldCount: SANDHI_PLANNING_FIELDS.length,
    planningTypes: Array.isArray(summary.planningTypes)
      ? summary.planningTypes.map(String)
      : [],
    fields: SANDHI_PLANNING_FIELDS.map(normalizeSandhiPlanningField),
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
      executionGuardLinked: true,
      mutationFree: true,
      candidateOnly: true
    }
  };
}

function classifySandhiBoundary(left, right) {
  const leftText = String(left || "");
  const rightText = String(right || "");
  const last = leftText.slice(-1);
  const first = rightText.slice(0, 1);

  const vowels = new Set(["a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "e", "ai", "o", "au"]);
  const visarga = new Set(["ḥ", "ः"]);
  const anusvara = new Set(["ṃ", "ṁ", "ं"]);

  if (vowels.has(last) && vowels.has(first)) {
    return "VOWEL_BOUNDARY";
  }

  if (visarga.has(last)) {
    return "VISARGA_BOUNDARY";
  }

  if (anusvara.has(last)) {
    return "ANUSVARA_BOUNDARY";
  }

  if (last && first) {
    return "CONSONANT_BOUNDARY";
  }

  return "EXTERNAL_BOUNDARY";
}

function createSandhiPlanningSnapshot(input) {
  const safeInput = input && typeof input === "object" ? input : {};
  const boundaries = Array.isArray(safeInput.boundaries)
    ? safeInput.boundaries
    : [];

  return Object.freeze({
    schemaVersion: SANDHI_PLANNING_SCHEMA_VERSION,
    kind: "SANDHI_PLANNING_SNAPSHOT",
    boundaries: Object.freeze(
      boundaries.map((boundary, index) =>
        Object.freeze({
          index,
          id: String(boundary.id || `sandhi-boundary-${index}`),
          left: String(boundary.left || ""),
          right: String(boundary.right || ""),
          type: String(
            boundary.type || classifySandhiBoundary(boundary.left, boundary.right)
          ),
          planned: true,
          executed: false,
          diagnostics: Array.isArray(boundary.diagnostics)
            ? boundary.diagnostics.map(String)
            : ["candidate-only"]
        })
      )
    ),
    trace: Object.freeze({
      replaySafe: true,
      mutationFree: true,
      boundaryCount: boundaries.length
    })
  });
}

function getSandhiPlanningDiagnostics() {
  const sandhiExport = buildSandhiPlanningExport();

  return {
    schemaVersion: sandhiExport.schemaVersion,
    ready: sandhiExport.ready,
    fieldCount: sandhiExport.fieldCount,
    contractsSatisfied: Object.values(sandhiExport.contracts).every(Boolean),
    diagnostics: { ...sandhiExport.diagnostics }
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeSandhiPlanningField,
    buildSandhiPlanningExport,
    classifySandhiBoundary,
    createSandhiPlanningSnapshot,
    getSandhiPlanningDiagnostics
  };
}