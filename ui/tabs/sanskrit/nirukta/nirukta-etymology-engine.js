import {
  getNiruktaEntry,
  listNiruktaEntries,
  normalizeNiruktaLemma,
} from "./nirukta-etymology-map.js";

function clonePlain(value, fallback) {
  if (!value || typeof value !== "object") return fallback;
  return JSON.parse(JSON.stringify(value));
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function stablePart(value) {
  return normalizeNiruktaLemma(value) || "unknown";
}

function generatedPadasFromInput(source) {
  return [
    ...asArray(source.generatedPadas),
    ...asArray(source.prakriyaExecution?.generatedPadas),
  ].filter((item) => item && typeof item === "object");
}

function graphNodeForForm(traceGraph, form, sourceType) {
  return asArray(traceGraph?.nodes).find((node) => (
    normalizeNiruktaLemma(node?.label) === normalizeNiruktaLemma(form)
    || normalizeNiruktaLemma(node?.output) === normalizeNiruktaLemma(form)
    || normalizeNiruktaLemma(node?.type) === normalizeNiruktaLemma(sourceType)
  ))?.id || null;
}

function rulefireRulesFor(entry, rulefire) {
  const fired = new Set(asArray(rulefire?.firedRules).map((item) => item?.ruleId).filter(Boolean));
  const linked = asArray(entry?.linkedRulefireRules);
  return linked.filter((ruleId) => fired.size === 0 || fired.has(ruleId));
}

function sutraDependenciesFor(entry, sutraDependency) {
  const refs = new Set([
    ...asArray(sutraDependency?.nodes).map((node) => node?.referenceId).filter(Boolean),
    ...asArray(sutraDependency?.edges).map((edge) => edge?.target).filter(Boolean),
  ]);
  const linked = asArray(entry?.linkedSutraDependencies);
  return linked.filter((dependencyId) => refs.size === 0 || refs.has(dependencyId) || [...refs].some((ref) => String(ref).includes(dependencyId)));
}

function lemmaCandidatesForPada(pada, source) {
  const candidates = [];
  const sourceType = pada?.sourceType || "";
  const input = source.prakriyaExecution?.inputs || {};
  if (sourceType === "tinanta") {
    candidates.push(input.verbInput?.dhatu);
  }
  if (sourceType === "subanta") {
    asArray(input.nounInputs).forEach((noun) => candidates.push(noun?.stem, noun?.iast));
  }
  candidates.push(pada?.lemma, pada?.stem, pada?.dhatu, pada?.generatedForm, pada?.id);
  return candidates.filter(Boolean);
}

function matchPada(pada, source) {
  for (const lemma of lemmaCandidatesForPada(pada, source)) {
    const entry = getNiruktaEntry(lemma);
    if (entry) return entry;
  }
  return null;
}

function candidateFromEntry(entry, pada, source, index) {
  const form = pada?.generatedForm || pada?.form || pada?.label || pada?.id || `form_${index}`;
  const linkedRulefireRules = rulefireRulesFor(entry, source.rulefire);
  const linkedSutraDependencies = sutraDependenciesFor(entry, source.sutraDependency);
  return {
    id: `nirukta.candidate.${index}.${stablePart(form)}.${stablePart(entry.lemma)}`,
    form,
    lemma: entry.lemma,
    category: entry.category,
    lineageType: entry.lineageType,
    semanticFamily: entry.semanticFamily,
    gloss: entry.gloss,
    linkedGraphNode: graphNodeForForm(source.traceGraph, form, pada?.sourceType),
    linkedRulefireRules,
    linkedSutraDependencies,
    confidence: "deterministic-placeholder",
  };
}

function edgeForCandidate(candidate) {
  return {
    id: `nirukta.edge.${stablePart(candidate.id)}.${stablePart(candidate.lemma)}`,
    source: candidate.id,
    target: `nirukta.entry.${stablePart(candidate.lemma)}`,
    relation: candidate.lineageType,
    label: candidate.semanticFamily,
    confidence: "deterministic",
  };
}

export function buildNiruktaOverlay(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const warnings = [];
  if (!input || typeof input !== "object") warnings.push("Input was missing or not an object; deterministic empty Nirukta overlay returned.");
  if (source.sutraDependency && typeof source.sutraDependency !== "object") warnings.push("Malformed sutra dependency payload ignored.");
  if (source.semanticOverlay && typeof source.semanticOverlay !== "object") warnings.push("Malformed semantic overlay payload ignored.");

  const candidates = [];
  const unresolved = [];
  generatedPadasFromInput(source).forEach((pada, index) => {
    const entry = matchPada(pada, source);
    const form = pada?.generatedForm || pada?.form || pada?.label || pada?.id || `form_${index}`;
    if (!entry) {
      unresolved.push({
        id: `nirukta.unresolved.${index}.${stablePart(form)}`,
        form,
        reason: "No deterministic Nirukta placeholder entry matched this visible form.",
        confidence: "deterministic-placeholder",
      });
      return;
    }
    candidates.push(candidateFromEntry(entry, pada, source, index));
  });

  const edges = candidates.map(edgeForCandidate);
  return {
    schemaVersion: "nirukta-etymology.v1",
    status: "ready",
    overlayType: "deterministic-nirukta-etymology",
    entries: listNiruktaEntries(),
    candidates,
    unresolved,
    edges,
    diagnostics: {
      candidateCount: candidates.length,
      unresolvedCount: unresolved.length,
      edgeCount: edges.length,
      warnings,
    },
  };
}

export function attachNiruktaToGraph(graph = {}, niruktaOverlay = {}) {
  const base = clonePlain(graph, {
    schemaVersion: "prakriya-trace-graph.v1",
    status: "ready",
    nodes: [],
    edges: [],
    metadata: {},
    diagnostics: { warnings: [] },
  });
  const niruktaNodes = asArray(niruktaOverlay?.candidates).map((candidate) => ({
    id: candidate.id,
    type: "niruktaEtymology",
    label: `${candidate.form} -> ${candidate.lemma}`,
    stage: "nirukta",
    sourceLayer: "nirukta-etymology",
    overlays: { nirukta: clonePlain(candidate, {}) },
    confidence: candidate.confidence,
  }));
  const niruktaEdges = asArray(niruktaOverlay?.edges).map((edge) => ({
    ...edge,
    type: edge.relation,
    sourceLayer: "nirukta-etymology",
  }));
  const nodes = [...asArray(base.nodes), ...niruktaNodes];
  const edges = [...asArray(base.edges), ...niruktaEdges];
  return {
    ...base,
    nodes,
    edges,
    metadata: {
      ...(base.metadata || {}),
      niruktaAttached: true,
      nirukta: {
        status: niruktaOverlay?.status || "ready",
        candidateCount: niruktaOverlay?.diagnostics?.candidateCount || 0,
        unresolvedCount: niruktaOverlay?.diagnostics?.unresolvedCount || 0,
      },
    },
    diagnostics: {
      ...(base.diagnostics || {}),
      nodeCount: nodes.length,
      edgeCount: edges.length,
      warnings: asArray(base.diagnostics?.warnings),
    },
  };
}

export function attachNiruktaToBackendPayload(payload = {}, niruktaOverlay = {}) {
  const base = clonePlain(payload, {});
  return {
    ...base,
    nirukta: clonePlain(niruktaOverlay, {}),
    prakriya_graph: {
      ...(base.prakriya_graph || {}),
      metadata: {
        ...(base.prakriya_graph?.metadata || {}),
        niruktaAttached: true,
      },
    },
  };
}

