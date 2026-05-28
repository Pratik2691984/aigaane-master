import {
  buildSutraDependencyIndex,
  listSutraDependencies,
  normalizeSutraDependencyId,
} from "./sutra-dependency-map.js";

const KNOWN_REFERENCE_IDS = new Set([
  "symbolic_ac",
  "symbolic_hal",
  "subanta_nominal_suffix_selection",
  "tinanta_lat_parasmaipada_selection",
  "subanta_generation_stage",
  "tinanta_generation_stage",
  "pada_assembly_stage",
  "sandhi_execution_stage",
  "sentence_emission_stage",
]);

function clonePlain(value, fallback) {
  if (!value || typeof value !== "object") return fallback;
  return JSON.parse(JSON.stringify(value));
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function stablePart(value) {
  return normalizeSutraDependencyId(value) || "unknown";
}

function enabledStageSet(enabledStages) {
  if (!Array.isArray(enabledStages) || enabledStages.length === 0) return null;
  return new Set(enabledStages.map(normalizeSutraDependencyId));
}

function referenceIdsFromOverlay(sutraReferenceOverlay) {
  const nodes = [
    ...asArray(sutraReferenceOverlay?.nodes),
    ...asArray(sutraReferenceOverlay?.overlay?.nodes),
  ];
  const ids = new Set(KNOWN_REFERENCE_IDS);
  nodes.forEach((node) => {
    if (node?.id) ids.add(node.id);
  });
  return ids;
}

function firedRuleIds(rulefire) {
  return asArray(rulefire?.firedRules)
    .map((item) => item?.ruleId || item?.id)
    .filter(Boolean);
}

function ruleNode(ruleId, stage, sourceLayer) {
  return {
    id: `sutra-dependency.rule.${stablePart(ruleId)}`,
    nodeType: "rulefire-rule",
    label: ruleId,
    ruleId,
    referenceId: null,
    stage,
    sourceLayer,
    confidence: "deterministic",
  };
}

function dependencyNode(referenceId, stage, sourceLayer) {
  return {
    id: `sutra-dependency.reference.${stablePart(referenceId)}`,
    nodeType: "sutra-reference",
    label: referenceId,
    ruleId: null,
    referenceId,
    stage,
    sourceLayer,
    confidence: "deterministic",
  };
}

function dependencyEdge(item) {
  return {
    id: `sutra-dependency.edge.${stablePart(item.ruleId)}.${stablePart(item.dependsOn)}`,
    source: `sutra-dependency.rule.${stablePart(item.ruleId)}`,
    target: `sutra-dependency.reference.${stablePart(item.dependsOn)}`,
    dependencyType: item.dependencyType,
    label: item.dependencyType,
    confidence: "deterministic",
  };
}

function dedupeById(items) {
  return [...new Map(items.map((item) => [item.id, item])).values()];
}

export function resolveRuleDependencies(ruleId, dependencyIndex = {}) {
  const index = Object.keys(dependencyIndex).length ? dependencyIndex : buildSutraDependencyIndex();
  const dependencies = asArray(index[normalizeSutraDependencyId(ruleId)]);
  return {
    ruleId,
    dependencies: dependencies.map((item) => ({ ...item })),
    diagnostics: {
      dependencyCount: dependencies.length,
      warnings: dependencies.length ? [] : [`No deterministic sutra dependency mapping found for ${String(ruleId ?? "unknown")}.`],
    },
  };
}

export function buildSutraDependencyGraph(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const stages = enabledStageSet(source.enabledStages);
  const referenceIds = referenceIdsFromOverlay(source.sutraReferenceOverlay);
  const fired = firedRuleIds(source.rulefire);
  const dependencyIndex = buildSutraDependencyIndex();
  const warnings = [];
  if (!input || typeof input !== "object") warnings.push("Input was missing or not an object; deterministic empty dependency graph returned.");
  if (source.rulefire && typeof source.rulefire !== "object") warnings.push("Malformed rulefire payload ignored.");
  if (source.ruleTraceOverlay && typeof source.ruleTraceOverlay !== "object") warnings.push("Malformed rule trace overlay ignored.");

  const selected = listSutraDependencies()
    .filter((item) => !stages || stages.has(normalizeSutraDependencyId(item.stage)))
    .filter((item) => fired.length === 0 || fired.map(normalizeSutraDependencyId).includes(normalizeSutraDependencyId(item.ruleId)));

  const nodes = [];
  const edges = [];
  const unresolved = [];

  selected.forEach((item) => {
    nodes.push(ruleNode(item.ruleId, item.stage, "rulefire"));
    nodes.push(dependencyNode(item.dependsOn, item.stage, item.sourceLayer));
    edges.push(dependencyEdge(item));
    if (!referenceIds.has(item.dependsOn)) {
      unresolved.push({
        id: `sutra-dependency.unresolved.${stablePart(item.ruleId)}.${stablePart(item.dependsOn)}`,
        ruleId: item.ruleId,
        referenceId: item.dependsOn,
        reason: "Dependency reference was not present in supplied sutra reference overlay.",
        confidence: "deterministic",
      });
    }
  });

  fired.forEach((ruleId) => {
    const resolution = resolveRuleDependencies(ruleId, dependencyIndex);
    warnings.push(...resolution.diagnostics.warnings);
  });

  const graph = {
    schemaVersion: "sutra-dependency.v1",
    status: "ready",
    graphType: "deterministic-sutra-dependency",
    nodes: dedupeById(nodes),
    edges: dedupeById(edges),
    unresolved,
    diagnostics: {
      nodeCount: dedupeById(nodes).length,
      edgeCount: dedupeById(edges).length,
      unresolvedCount: unresolved.length,
      warnings,
    },
  };
  return graph;
}

export function attachSutraDependenciesToRulefire(rulefire = {}, dependencyGraph = {}) {
  const base = clonePlain(rulefire, {
    schemaVersion: "rulefire.v1",
    status: "ready",
    firedRules: [],
    diagnostics: { warnings: [] },
  });
  return {
    ...base,
    sutraDependency: clonePlain(dependencyGraph, {}),
    diagnostics: {
      ...(base.diagnostics || {}),
      sutraDependencyNodeCount: asArray(dependencyGraph?.nodes).length,
      sutraDependencyEdgeCount: asArray(dependencyGraph?.edges).length,
    },
  };
}

export function attachSutraDependenciesToGraph(graph = {}, dependencyGraph = {}) {
  const base = clonePlain(graph, {
    schemaVersion: "prakriya-trace-graph.v1",
    status: "ready",
    nodes: [],
    edges: [],
    metadata: {},
    diagnostics: { warnings: [] },
  });
  const sourceNodes = asArray(base.nodes);
  const sourceEdges = asArray(base.edges);
  const dependencyNodes = asArray(dependencyGraph?.nodes).map((node) => ({
    ...node,
    type: node.nodeType || "sutraDependency",
    sourceLayer: "sutra-dependency",
  }));
  const dependencyEdges = asArray(dependencyGraph?.edges).map((edge) => ({
    ...edge,
    type: edge.dependencyType || "sutraDependency",
    sourceLayer: "sutra-dependency",
  }));
  const nodes = [...sourceNodes, ...dependencyNodes];
  const edges = [...sourceEdges, ...dependencyEdges];
  return {
    ...base,
    nodes,
    edges,
    metadata: {
      ...(base.metadata || {}),
      dependenciesAttached: true,
      sutraDependency: {
        status: dependencyGraph?.status || "ready",
        nodeCount: dependencyGraph?.diagnostics?.nodeCount || 0,
        edgeCount: dependencyGraph?.diagnostics?.edgeCount || 0,
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

