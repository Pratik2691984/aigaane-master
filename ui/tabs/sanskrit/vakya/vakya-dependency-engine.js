import {
  getDependencyRelationByKaraka,
  normalizeDependencyRole,
} from "./vakya-dependency-map.js";

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function stablePart(value) {
  return String(value ?? "unknown")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function collectMorphologyEntries(morphologyTransitions) {
  if (Array.isArray(morphologyTransitions)) return morphologyTransitions;
  if (!morphologyTransitions || typeof morphologyTransitions !== "object") return [];
  return [
    ...asArray(morphologyTransitions.entries),
    ...asArray(morphologyTransitions.tokens),
    ...asArray(morphologyTransitions.nodes),
    ...asArray(morphologyTransitions.graph?.nodes),
    ...asArray(morphologyTransitions.morphology?.roots),
    ...asArray(morphologyTransitions.morphology?.stems),
    ...asArray(morphologyTransitions.morphology?.suffixes),
    ...asArray(morphologyTransitions.morphology?.surfaceForms),
  ];
}

function collectTokens(inputTokens, morphologyEntries) {
  const explicitTokens = asArray(inputTokens)
    .filter((token) => token && typeof token === "object")
    .map((token, index) => ({
      token: token.token || token.text || token.label || token.id || `token_${index}`,
      index: Number.isInteger(token.index) ? token.index : index,
    }));

  if (explicitTokens.length) return explicitTokens;

  return morphologyEntries
    .filter((entry) => entry && typeof entry === "object")
    .map((entry, index) => ({
      token: entry.token || entry.surface || entry.form || entry.label || entry.id || `token_${index}`,
      index: Number.isInteger(entry.index) ? entry.index : index,
    }));
}

function morphologyMarkers(entry) {
  const values = [
    entry?.morphology,
    entry?.morphologyType,
    entry?.morphologyClass,
    entry?.verbType,
    entry?.verbForm,
    entry?.formType,
    entry?.type,
    entry?.stage,
    entry?.category,
    entry?.marker,
    entry?.tag,
    ...(Array.isArray(entry?.tags) ? entry.tags : []),
    ...(Array.isArray(entry?.markers) ? entry.markers : []),
  ];

  if (entry?.isFiniteVerb === true || entry?.finiteVerb === true || entry?.tinganta === true || entry?.tiṅanta === true) {
    values.push("finite-verb", "tinganta");
  }

  return values.map((value) => normalizeDependencyRole(value)).filter(Boolean);
}

function isFiniteVerbEntry(entry) {
  const markers = morphologyMarkers(entry);
  return markers.some((marker) => [
    "tinganta",
    "tiṅanta",
    "finite-verb",
    "finiteverb",
    "verb-finite",
  ].includes(marker));
}

function entryToken(entry, index) {
  return entry?.token || entry?.surface || entry?.form || entry?.label || entry?.id || `token_${index}`;
}

function entryIndex(entry, fallback) {
  return Number.isInteger(entry?.index) ? entry.index : fallback;
}

function anchorId(token, index) {
  return ["vakya", "anchor", stablePart(index), stablePart(token)].join(".");
}

function nodeId(token, index, role) {
  return ["vakya", "node", stablePart(index), stablePart(token), stablePart(role)].join(".");
}

function edgeId(source, target, relation) {
  return ["vakya", "edge", stablePart(source), stablePart(target), stablePart(relation)].join(".");
}

function karakaNodes(karakaOverlay) {
  return asArray(karakaOverlay?.nodes).filter((node) => node && typeof node === "object");
}

export function buildVakyaDependencyOverlay(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const morphologyEntries = collectMorphologyEntries(source.morphologyTransitions);
  const tokens = collectTokens(source.tokens, morphologyEntries);
  const warnings = [];

  const anchors = morphologyEntries
    .filter((entry) => entry && typeof entry === "object" && isFiniteVerbEntry(entry))
    .map((entry, index) => {
      const token = entryToken(entry, index);
      const resolvedIndex = entryIndex(entry, index);
      return {
        id: anchorId(token, resolvedIndex),
        token,
        index: resolvedIndex,
        anchorType: "finite-verb",
        source: "morphology-transition",
        confidence: "deterministic",
      };
    });

  const primaryAnchor = anchors[0] || null;
  const nodes = [];
  const edges = [];
  let unresolvedCount = 0;

  karakaNodes(source.karakaOverlay).forEach((karakaNode, index) => {
    const role = primaryAnchor ? karakaNode.karaka : "unresolvedCandidate";
    const node = {
      id: nodeId(karakaNode.token, karakaNode.index ?? index, role),
      token: karakaNode.token || `token_${index}`,
      index: Number.isInteger(karakaNode.index) ? karakaNode.index : index,
      role,
      karaka: karakaNode.karaka || null,
      morphology: karakaNode.vibhakti || null,
      linkedKarakaNode: karakaNode.id || null,
      linkedSemanticNode: karakaNode.linkedSemanticNode || null,
      linkedDerivationNode: karakaNode.linkedDerivationNode || null,
      linkedRuleTrace: karakaNode.linkedRuleTrace || null,
    };
    nodes.push(node);

    if (!primaryAnchor) {
      unresolvedCount += 1;
      return;
    }

    const relation = getDependencyRelationByKaraka(karakaNode.karaka);
    if (!relation) {
      unresolvedCount += 1;
      return;
    }

    edges.push({
      id: edgeId(node.id, primaryAnchor.id, relation.id),
      source: node.id,
      target: primaryAnchor.id,
      relation: relation.id,
      label: relation.label,
      confidence: "deterministic",
      sourceLayer: "vakya-dependency",
    });
  });

  if (!primaryAnchor && nodes.length > 0) {
    warnings.push("No deterministic finite verb anchor found; kāraka candidates remain unresolvedCandidate.");
  }

  return {
    schemaVersion: "vakya-dependency-overlay.v1",
    status: "ready",
    overlayType: "vakya-dependency",
    anchors,
    nodes,
    edges,
    diagnostics: {
      tokenCount: tokens.length,
      anchorCount: anchors.length,
      nodeCount: nodes.length,
      edgeCount: edges.length,
      unresolvedCount,
      warnings,
    },
  };
}

export function attachVakyaOverlay(graph, overlayData = {}, bridge = {}) {
  if (typeof bridge.attachOverlayItems !== "function") return graph;
  return bridge.attachOverlayItems(graph, "vakya", overlayData, ["anchors", "nodes"], ["edges"]);
}
