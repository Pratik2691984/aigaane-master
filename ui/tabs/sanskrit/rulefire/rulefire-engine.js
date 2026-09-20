import {
  listRulefireRules,
  normalizeRulefireId,
  sortRulefireRulesByPriority,
} from "./rulefire-map.js";

const EMPTY_STATE = {
  id: "rulefire.state.initial",
  text: "",
  tokens: [],
  padas: [],
  morphology: {},
  sandhi: [],
  generatedForms: [],
  diagnostics: { warnings: [] },
};

function clonePlain(value, fallback) {
  if (!value || typeof value !== "object") return fallback;
  return JSON.parse(JSON.stringify(value));
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeValue(value) {
  return String(value ?? "")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/\u0101/g, "aa")
    .replace(/\u012b/g, "ii")
    .replace(/\u016b/g, "uu")
    .replace(/\u1e6d/g, "t")
    .replace(/[^\p{Letter}\p{Number}+.-]+/gu, "_")
    .replace(/^_+|_+$/g, "");
}

function stablePart(value) {
  return normalizeValue(value).replace(/[^\p{Letter}\p{Number}]+/gu, "_") || "unknown";
}

function normalizeState(state = {}) {
  const source = state && typeof state === "object" ? state : {};
  return {
    ...EMPTY_STATE,
    ...clonePlain(source, {}),
    tokens: asArray(source.tokens),
    padas: asArray(source.padas),
    generatedForms: asArray(source.generatedForms),
    sandhi: asArray(source.sandhi),
    morphology: source.morphology && typeof source.morphology === "object" ? clonePlain(source.morphology, {}) : {},
    diagnostics: {
      warnings: [],
      ...(source.diagnostics && typeof source.diagnostics === "object" ? clonePlain(source.diagnostics, {}) : {}),
    },
  };
}

function stageId(stage) {
  if (typeof stage === "string") return stage;
  return stage?.id || stage?.stage || "";
}

function boundaryParts(boundary) {
  const [left = "", right = ""] = String(boundary || "").split("+");
  return { left, right };
}

function candidatesForState(state) {
  const candidates = [{ kind: "state", ...state }];
  asArray(state.morphology?.nounInputs).forEach((item) => {
    candidates.push({ kind: "subanta", ...item });
  });
  if (state.morphology?.verbInput && typeof state.morphology.verbInput === "object") {
    candidates.push({ kind: "tinanta", ...state.morphology.verbInput });
  }
  asArray(state.padas).forEach((pada) => {
    candidates.push({
      kind: "prakriya",
      sourceType: pada.sourceType,
      stage: pada.sourceType === "tinanta" ? "tinantaGeneration" : "subantaGeneration",
      ...pada,
    });
  });
  asArray(state.stages).forEach((stage) => {
    candidates.push({ kind: "prakriya", stage: stageId(stage), id: stageId(stage) });
  });
  asArray(state.sandhi).forEach((transition) => {
    const boundary = transition.boundary || transition.originalBoundary || "";
    const parts = boundaryParts(boundary);
    candidates.push({
      kind: "sandhi",
      ...transition,
      boundary,
      left: transition.leftBoundary || parts.left,
      right: transition.rightBoundary || parts.right,
      stage: "sandhiExecution",
    });
  });
  return candidates;
}

function valueMatches(actual, expected) {
  if (expected === true) return Boolean(actual);
  if (Array.isArray(actual)) return actual.some((item) => valueMatches(item, expected));
  return normalizeValue(actual) === normalizeValue(expected);
}

function candidateMatchesPattern(candidate, pattern = {}) {
  return Object.entries(pattern).every(([key, expected]) => {
    if (key === "requiresPadas") return expected ? asArray(candidate.padas).length > 0 || Boolean(candidate.sourceType) : true;
    return valueMatches(candidate[key], expected);
  });
}

function applyOutputPattern(state, rule) {
  const next = normalizeState(state);
  const pattern = rule?.outputPattern || {};
  if (Array.isArray(pattern.textReplacement) && typeof next.text === "string") {
    const [before, after] = pattern.textReplacement;
    if (before) next.text = next.text.replace(before, after);
  }
  if (pattern.generatedForm) {
    next.generatedForms = [...next.generatedForms, pattern.generatedForm];
  }
  if (pattern.suffix) {
    next.generatedForms = [...next.generatedForms, pattern.suffix];
  }
  if (pattern.operation) {
    next.lastOperation = pattern.operation;
  }
  if (pattern.boundary) {
    next.sandhi = [...next.sandhi, { ruleId: rule.id, boundary: rule.inputPattern?.boundary, result: pattern.boundary }];
  }
  next.lastRuleId = rule.id;
  return next;
}

function snapshot(id, order, state, causedByRuleId = null) {
  return {
    id,
    order,
    state: clonePlain(state, {}),
    causedByRuleId,
  };
}

function firedRecord(rule, before, after, order) {
  return {
    id: `rulefire.fired.${order}.${stablePart(rule.id)}`,
    ruleId: rule.id,
    category: rule.category,
    stage: rule.stage,
    before: clonePlain(before, {}),
    after: clonePlain(after, {}),
    priority: rule.priority,
    reversible: Boolean(rule.reversible),
    confidence: "deterministic",
  };
}

function buildTraceFromFired(firedRules) {
  return firedRules.map((item, index) => ({
    id: `rulefire.trace.${index + 1}.${stablePart(item.ruleId)}`,
    step: index + 1,
    ruleId: item.ruleId,
    operation: item.stage,
    before: item.before.text || item.before.lastOperation || "",
    after: item.after.text || item.after.lastOperation || "",
  }));
}

function buildGraphProjection(firedRules) {
  const nodes = firedRules.map((item, index) => ({
    id: `rulefire.node.${index + 1}.${stablePart(item.ruleId)}`,
    type: "rulefireRule",
    label: item.ruleId,
    ruleId: item.ruleId,
    category: item.category,
    stage: item.stage,
    order: index + 1,
    confidence: "deterministic",
  }));
  const edges = [];
  for (let index = 0; index + 1 < nodes.length; index += 1) {
    edges.push({
      id: `rulefire.edge.${index + 1}.${stablePart(nodes[index].id)}.${stablePart(nodes[index + 1].id)}`,
      source: nodes[index].id,
      target: nodes[index + 1].id,
      type: "rulefireTransition",
      label: "next rulefire step",
      order: index + 1,
      confidence: "deterministic",
    });
  }
  return { nodes, edges };
}

function buildReversePreview(firedRules, enableReversePreview) {
  if (enableReversePreview === false) return [];
  return firedRules
    .filter((item) => item.reversible)
    .map((item, index) => ({
      id: `rulefire.reverse.${index + 1}.${stablePart(item.ruleId)}`,
      ruleId: item.ruleId,
      before: clonePlain(item.before, {}),
      after: clonePlain(item.after, {}),
      structuralOnly: true,
    }));
}

function stateFromInput(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  if (source.initialState && typeof source.initialState === "object") {
    return normalizeState({
      ...source.initialState,
      stages: source.stages || source.initialState.stages,
    });
  }
  return normalizeState({
    id: "rulefire.state.prakriya",
    text: source.sentenceAssembly?.preSandhiText || source.sentenceAssembly?.postSandhiText || source.text || "",
    tokens: asArray(source.sentenceAssembly?.preSandhiText?.split(/\s+/u).filter(Boolean)),
    padas: asArray(source.generatedPadas),
    generatedForms: asArray(source.generatedPadas).map((pada) => pada?.generatedForm).filter(Boolean),
    morphology: source.inputs || {},
    sandhi: asArray(source.sandhiTransitions),
    stages: asArray(source.stages),
    diagnostics: source.diagnostics || {},
  });
}

function selectedRules(input = {}) {
  const categories = Array.isArray(input.enabledCategories) && input.enabledCategories.length
    ? new Set(input.enabledCategories.map(normalizeRulefireId))
    : null;
  const stages = Array.isArray(input.stages)
    ? new Set(input.stages.map(stageId).filter(Boolean).map(normalizeRulefireId))
    : null;
  return sortRulefireRulesByPriority(listRulefireRules()).filter((rule) => {
    if (categories && !categories.has(normalizeRulefireId(rule.category))) return false;
    if (stages && stages.size > 0 && !stages.has(normalizeRulefireId(rule.stage))) return false;
    if (stages && stages.size === 0) return false;
    return true;
  });
}

export function evaluateRuleEligibility(rule, state = {}) {
  const safeRule = rule && typeof rule === "object" ? rule : {};
  const safeState = normalizeState(state);
  const match = candidatesForState(safeState).find((candidate) => candidateMatchesPattern(candidate, safeRule.inputPattern || {}));
  return {
    eligible: Boolean(safeRule.id && match),
    ruleId: safeRule.id || null,
    matchedCandidate: match ? clonePlain(match, {}) : null,
    confidence: "deterministic",
  };
}

export function fireRule(rule, state = {}) {
  const safeRule = rule && typeof rule === "object" ? rule : {};
  const before = normalizeState(state);
  const eligibility = evaluateRuleEligibility(safeRule, before);
  if (!eligibility.eligible) {
    return {
      fired: false,
      ruleId: safeRule.id || null,
      before,
      after: before,
      eligibility,
      confidence: "deterministic",
    };
  }
  return {
    fired: true,
    ruleId: safeRule.id,
    before,
    after: applyOutputPattern(before, safeRule),
    eligibility,
    confidence: "deterministic",
  };
}

export function executeRulefire(input = {}) {
  const source = input && typeof input === "object" ? input : {};
  const initialState = stateFromInput(source);
  let currentState = normalizeState(initialState);
  const warnings = [];
  if (!input || typeof input !== "object") warnings.push("Input was missing or not an object; deterministic empty rulefire execution returned.");

  const firedRules = [];
  const snapshots = [snapshot("rulefire.snapshot.0.initial", 0, currentState)];

  selectedRules(source).forEach((rule, index) => {
    const result = fireRule(rule, currentState);
    if (!result.fired) return;
    currentState = result.after;
    firedRules.push(firedRecord(rule, result.before, result.after, firedRules.length + 1));
    snapshots.push(snapshot(`rulefire.snapshot.${snapshots.length}.${stablePart(rule.id)}`, snapshots.length, currentState, rule.id));
  });

  if (firedRules.length === 0) warnings.push("No deterministic rulefire rule matched explicit inputPattern metadata.");

  const trace = source.enableTrace === false ? [] : buildTraceFromFired(firedRules);
  const graphProjection = buildGraphProjection(firedRules);
  return {
    schemaVersion: "rulefire.v1",
    status: "ready",
    executionType: "deterministic-rulefire",
    initialState: clonePlain(initialState, {}),
    finalState: clonePlain(currentState, {}),
    firedRules,
    snapshots: source.enableSnapshots === false ? [] : snapshots,
    trace,
    graphProjection,
    reversePreview: buildReversePreview(firedRules, source.enableReversePreview),
    diagnostics: {
      firedCount: firedRules.length,
      snapshotCount: source.enableSnapshots === false ? 0 : snapshots.length,
      unresolvedCount: firedRules.length === 0 ? 1 : 0,
      warnings,
    },
  };
}

export function buildRulefireTrace(input = {}) {
  return executeRulefire({ ...(input && typeof input === "object" ? input : {}), enableTrace: true });
}

export function attachRulefireToGraph(graph = {}, rulefire = {}) {
  const base = clonePlain(graph, {
    schemaVersion: "prakriya-trace-graph.v1",
    status: "ready",
    graphType: "deterministic-prakriya-trace",
    nodes: [],
    edges: [],
    overlays: [],
    diagnostics: { nodeCount: 0, edgeCount: 0, overlayCount: 0, unresolvedCount: 0, warnings: [] },
    metadata: {},
  });
  const sourceNodes = asArray(base.nodes);
  const sourceEdges = asArray(base.edges);
  const projection = rulefire?.graphProjection && typeof rulefire.graphProjection === "object"
    ? rulefire.graphProjection
    : { nodes: [], edges: [] };
  const ruleNodes = asArray(projection.nodes).map((node, index) => ({
    ...node,
    id: node.id || `rulefire.node.${index + 1}`,
    sourceLayer: "rulefire",
  }));
  const ruleEdges = asArray(projection.edges).map((edge, index) => ({
    ...edge,
    id: edge.id || `rulefire.edge.${index + 1}`,
    sourceLayer: "rulefire",
  }));
  const anchor = sourceNodes.find((node) => node.type === "sentenceComposition") || sourceNodes[sourceNodes.length - 1] || null;
  const bridgeEdge = anchor && ruleNodes.length
    ? [{
        id: `rulefire.edge.bridge.${stablePart(anchor.id)}.${stablePart(ruleNodes[0].id)}`,
        source: anchor.id,
        target: ruleNodes[0].id,
        type: "rulefireBridge",
        label: "rulefire projection",
        order: sourceEdges.length + 1,
        sourceLayer: "rulefire",
        confidence: "deterministic",
      }]
    : [];
  const nodes = [...sourceNodes, ...ruleNodes];
  const edges = [...sourceEdges, ...bridgeEdge, ...ruleEdges];
  return {
    ...base,
    nodes,
    edges,
    metadata: {
      ...(base.metadata || {}),
      rulefireAttached: true,
      rulefire: {
        status: rulefire?.status || "ready",
        firedCount: rulefire?.diagnostics?.firedCount || 0,
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

