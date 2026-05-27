import { getSandarbhaRelation } from "./sandarbha-context-map.js";

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

function stableId(prefix, ...parts) {
  return [prefix, ...parts.map(stablePart)].join(".");
}

function tokenText(item, index) {
  return item?.token || item?.text || item?.surface || item?.form || item?.label || item?.id || `token_${index}`;
}

function tokenIndex(item, fallback) {
  return Number.isInteger(item?.index) ? item.index : fallback;
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
  ].filter((entry) => entry && typeof entry === "object");
}

function collectTokens(tokens, morphologyEntries) {
  const explicit = asArray(tokens)
    .filter((token) => token && typeof token === "object")
    .map((token, index) => ({
      token: tokenText(token, index),
      index: tokenIndex(token, index),
      metadata: token,
    }));
  if (explicit.length) return explicit;
  return morphologyEntries.map((entry, index) => ({
    token: tokenText(entry, index),
    index: tokenIndex(entry, index),
    metadata: entry,
  }));
}

function relationLabel(relationId) {
  return getSandarbhaRelation(relationId)?.label || relationId;
}

function makeCandidate({ token, index, candidateType, relation, links = {} }) {
  return {
    id: stableId("sandarbha.candidate", index, token, candidateType, relation),
    token,
    index,
    candidateType,
    relation,
    linkedKarakaNode: links.linkedKarakaNode || null,
    linkedVakyaNode: links.linkedVakyaNode || null,
    linkedSemanticNode: links.linkedSemanticNode || null,
    linkedDerivationNode: links.linkedDerivationNode || null,
    linkedRuleTrace: links.linkedRuleTrace || null,
    confidence: "deterministic",
  };
}

function makeEdge(source, target, relation) {
  return {
    id: stableId("sandarbha.edge", source, target, relation),
    source,
    target,
    relation,
    label: relationLabel(relation),
    confidence: "deterministic",
    sourceLayer: "sandarbha-context",
  };
}

function createNeighborhood(anchor, relation, members, sourceLayer) {
  return {
    id: stableId("sandarbha.neighborhood", anchor, relation, members.join(".")),
    anchor,
    relation,
    members,
    sourceLayer,
    confidence: "deterministic",
  };
}

function karakaNodes(karakaOverlay) {
  return asArray(karakaOverlay?.nodes).filter((node) => node && typeof node === "object");
}

function vakyaEdges(vakyaDependencyOverlay) {
  return asArray(vakyaDependencyOverlay?.edges).filter((edge) => edge && typeof edge === "object");
}

function vakyaAnchors(vakyaDependencyOverlay) {
  return asArray(vakyaDependencyOverlay?.anchors).filter((anchor) => anchor && typeof anchor === "object");
}

function semanticEdges(semanticOverlays) {
  if (Array.isArray(semanticOverlays)) return semanticOverlays.filter((edge) => edge && typeof edge === "object");
  return [
    ...asArray(semanticOverlays?.edges),
    ...asArray(semanticOverlays?.graph?.edges),
  ].filter((edge) => edge && typeof edge === "object");
}

function derivationNodes(derivationGraph) {
  return [
    ...asArray(derivationGraph?.nodes),
    ...asArray(derivationGraph?.graph?.nodes),
  ].filter((node) => node && typeof node === "object");
}

function lineageValues(node) {
  const values = [
    node?.lineage,
    node?.derivationLineage,
    node?.family,
    node?.familyId,
    ...(Array.isArray(node?.lineages) ? node.lineages : []),
  ];
  return values
    .flatMap((value) => Array.isArray(value) ? value : [value])
    .filter((value) => value !== null && value !== undefined && value !== "")
    .map(String);
}

function morphologySignature(entry) {
  const values = [
    entry?.vibhakti || entry?.case || entry?.caseName || entry?.morphology?.vibhakti,
    entry?.linga || entry?.gender || entry?.morphology?.linga,
    entry?.vacana || entry?.number || entry?.morphology?.vacana,
  ].filter(Boolean);
  return values.length ? values.map(String).join("|") : "";
}

function hasPronounMetadata(token) {
  const metadata = token?.metadata || {};
  const values = [
    metadata.pronoun,
    metadata.isPronoun,
    metadata.pronounLike,
    metadata.pos,
    metadata.type,
    metadata.category,
    metadata.tag,
    ...(Array.isArray(metadata.tags) ? metadata.tags : []),
  ];
  return values.some((value) => {
    if (value === true) return true;
    return /pronoun|sarvanama|sarvanāma/i.test(String(value ?? ""));
  });
}

export function buildSandarbhaContextOverlay(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const morphologyEntries = collectMorphologyEntries(source.morphologyTransitions);
  const tokens = collectTokens(source.tokens, morphologyEntries);
  const neighborhoods = [];
  const candidates = [];
  const edges = [];
  const warnings = [];
  const edgeKeys = new Set();

  function addEdge(edge) {
    if (edgeKeys.has(edge.id)) return;
    edgeKeys.add(edge.id);
    edges.push(edge);
  }

  vakyaEdges(source.vakyaDependencyOverlay).forEach((edge) => {
    const members = [edge.source, edge.target].filter(Boolean);
    if (members.length < 2) return;
    neighborhoods.push(createNeighborhood(edge.target, "localDependencyNeighborhood", members, "vakya-dependency"));
    addEdge(makeEdge(edge.source, edge.target, "localDependencyNeighborhood"));
  });

  vakyaAnchors(source.vakyaDependencyOverlay).forEach((anchor) => {
    neighborhoods.push(createNeighborhood(anchor.id || anchor.token, "finiteVerbContext", [anchor.id || anchor.token], "vakya-dependency"));
  });

  const sortedKaraka = karakaNodes(source.karakaOverlay).sort((a, b) => tokenIndex(a, 0) - tokenIndex(b, 0));
  for (let index = 1; index < sortedKaraka.length; index += 1) {
    const previous = sortedKaraka[index - 1];
    const current = sortedKaraka[index];
    const adjacent = Math.abs(tokenIndex(current, index) - tokenIndex(previous, index - 1)) <= 1;
    if (previous.karaka && current.karaka && previous.karaka === current.karaka && adjacent) {
      candidates.push(makeCandidate({
        token: tokenText(current, index),
        index: tokenIndex(current, index),
        candidateType: "karakaContinuity",
        relation: "karakaContinuity",
        links: { linkedKarakaNode: current.id || null },
      }));
      addEdge(makeEdge(previous.id || tokenText(previous, index - 1), current.id || tokenText(current, index), "karakaContinuity"));
    }
  }

  const sortedMorphology = morphologyEntries.sort((a, b) => tokenIndex(a, 0) - tokenIndex(b, 0));
  for (let index = 1; index < sortedMorphology.length; index += 1) {
    const previous = sortedMorphology[index - 1];
    const current = sortedMorphology[index];
    const previousSignature = morphologySignature(previous);
    const currentSignature = morphologySignature(current);
    if (previousSignature && previousSignature === currentSignature) {
      candidates.push(makeCandidate({
        token: tokenText(current, index),
        index: tokenIndex(current, index),
        candidateType: "morphologyContinuity",
        relation: "morphologyContinuity",
      }));
      addEdge(makeEdge(previous.id || tokenText(previous, index - 1), current.id || tokenText(current, index), "morphologyContinuity"));
    }
  }

  const derivation = derivationNodes(source.derivationGraph);
  for (let index = 1; index < derivation.length; index += 1) {
    const previous = derivation[index - 1];
    const current = derivation[index];
    const shared = lineageValues(previous).some((value) => lineageValues(current).includes(value));
    if (shared) {
      candidates.push(makeCandidate({
        token: current.label || current.id,
        index,
        candidateType: "derivationContinuity",
        relation: "derivationContinuity",
        links: { linkedDerivationNode: current.id || null },
      }));
      addEdge(makeEdge(previous.id || previous.label, current.id || current.label, "derivationContinuity"));
    }
  }

  semanticEdges(source.semanticOverlays).forEach((edge) => {
    if (!edge.source || !edge.target) return;
    addEdge(makeEdge(edge.source, edge.target, "semanticAdjacency"));
  });

  tokens.forEach((token) => {
    if (!hasPronounMetadata(token)) return;
    candidates.push(makeCandidate({
      token: token.token,
      index: token.index,
      candidateType: "pronounAntecedentCandidate",
      relation: "pronounAntecedentCandidate",
    }));
  });

  const unresolvedCount = candidates.filter((candidate) => (
    candidate.candidateType === "pronounAntecedentCandidate"
    || candidate.relation === "unresolvedContextCandidate"
  )).length;

  if (candidates.length === 0 && neighborhoods.length === 0 && edges.length === 0) {
    warnings.push("No deterministic sandarbha context links found; no hidden semantic interpretation was attempted.");
  }

  return {
    schemaVersion: "sandarbha-context-overlay.v1",
    status: "ready",
    overlayType: "sandarbha-context",
    neighborhoods,
    candidates,
    edges,
    diagnostics: {
      tokenCount: tokens.length,
      neighborhoodCount: neighborhoods.length,
      candidateCount: candidates.length,
      edgeCount: edges.length,
      unresolvedCount,
      warnings,
    },
  };
}
