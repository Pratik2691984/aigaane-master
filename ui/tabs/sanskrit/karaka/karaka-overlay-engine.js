import {
  getKarakaByVibhakti,
  normalizeVibhakti,
} from "./karaka-relation-map.js";

const KARAKA_OVERLAY_SAFETY_NOTE =
  "Kāraka overlay is deterministic morphology-linked metadata only; no full syntactic parsing or grammatical correctness claim is made.";

function stablePart(value) {
  return String(value ?? "unknown")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function stableKarakaId(token, index, vibhakti, karaka) {
  return [
    "karaka",
    stablePart(index),
    stablePart(token),
    stablePart(vibhakti),
    stablePart(karaka),
  ].join(".");
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function collectMorphologyEntries(morphologyTransitions) {
  if (Array.isArray(morphologyTransitions)) return morphologyTransitions;
  if (!morphologyTransitions || typeof morphologyTransitions !== "object") return [];

  const directEntries = [
    ...asArray(morphologyTransitions.entries),
    ...asArray(morphologyTransitions.tokens),
    ...asArray(morphologyTransitions.nodes),
  ];

  const graphEntries = asArray(morphologyTransitions.graph?.nodes);
  const groupedEntries = [
    ...asArray(morphologyTransitions.morphology?.roots),
    ...asArray(morphologyTransitions.morphology?.stems),
    ...asArray(morphologyTransitions.morphology?.suffixes),
    ...asArray(morphologyTransitions.morphology?.surfaceForms),
  ];

  return [...directEntries, ...graphEntries, ...groupedEntries];
}

function entryToken(entry, index) {
  return entry?.token || entry?.surface || entry?.form || entry?.label || entry?.id || `token_${index}`;
}

function entryVibhakti(entry) {
  return entry?.vibhakti || entry?.case || entry?.caseName || entry?.morphology?.vibhakti || "";
}

export function buildKarakaOverlay(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const morphologyEntries = collectMorphologyEntries(source.morphologyTransitions);
  const warnings = [];
  const nodes = [];
  let unmatchedCount = 0;

  morphologyEntries.forEach((entry, index) => {
    if (!entry || typeof entry !== "object") {
      unmatchedCount += 1;
      warnings.push(`Skipped malformed morphology entry at index ${index}.`);
      return;
    }

    const rawVibhakti = entryVibhakti(entry);
    const vibhakti = normalizeVibhakti(rawVibhakti);
    const relation = getKarakaByVibhakti(vibhakti);

    if (!relation) {
      unmatchedCount += 1;
      return;
    }

    const token = entryToken(entry, index);
    nodes.push({
      id: stableKarakaId(token, index, vibhakti, relation.id),
      token,
      index,
      vibhakti,
      karaka: relation.id,
      karakaLabel: relation.label,
      confidence: "deterministic",
      source: "morphology-transition",
      linkedSemanticNode: entry.linkedSemanticNode || null,
      linkedRuleTrace: entry.linkedRuleTrace || null,
      linkedDerivationNode: entry.linkedDerivationNode || null,
    });
  });

  return {
    schemaVersion: "karaka-overlay.v1",
    status: "ready",
    overlayType: "karaka-relation",
    nodes,
    edges: [],
    diagnostics: {
      inspectedCount: morphologyEntries.length,
      matchedCount: nodes.length,
      unmatchedCount,
      warnings,
    },
    safetyNote: KARAKA_OVERLAY_SAFETY_NOTE,
  };
}
