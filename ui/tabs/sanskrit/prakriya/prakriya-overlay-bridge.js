import { buildChandasProsodyOverlay, attachChandasOverlay } from "../chandas/chandas-prosody-engine.js";
import { buildKarakaOverlay, attachKarakaOverlay } from "../karaka/karaka-overlay-engine.js";
import { buildSandarbhaContextOverlay, attachSandarbhaOverlay } from "../sandarbha/sandarbha-context-engine.js";
import { inspectDhatuSemanticGraph, attachSemanticOverlay } from "../semantic/dhatu-semantic-engine.js";
import { inspectRuleTrace, attachRuleTraceOverlay } from "../trace/rule-trace-engine.js";
import { buildVakyaDependencyOverlay, attachVakyaOverlay } from "../vakya/vakya-dependency-engine.js";

const EMPTY_GRAPH = {
  schemaVersion: "prakriya-trace-graph.v1",
  status: "ready",
  graphType: "deterministic-prakriya-trace",
  nodes: [],
  edges: [],
  overlays: [],
  diagnostics: { nodeCount: 0, edgeCount: 0, overlayCount: 0, unresolvedCount: 0, warnings: [] },
};

const OVERLAY_TYPES = ["karaka", "vakya", "chandas", "sandarbha", "semantic", "rule-trace"];

function clonePlain(value, fallback) {
  if (!value || typeof value !== "object") return fallback;
  return JSON.parse(JSON.stringify(value));
}

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

function normalizeGraph(graph) {
  const base = clonePlain(graph, EMPTY_GRAPH);
  return {
    ...EMPTY_GRAPH,
    ...base,
    nodes: asArray(base.nodes),
    edges: asArray(base.edges),
    overlays: asArray(base.overlays),
    diagnostics: {
      ...EMPTY_GRAPH.diagnostics,
      ...(base.diagnostics && typeof base.diagnostics === "object" ? base.diagnostics : {}),
    },
    metadata: {
      ...(base.metadata && typeof base.metadata === "object" ? base.metadata : {}),
    },
  };
}

function overlayCount(graph) {
  return asArray(graph.nodes).reduce((total, node) => total + Object.keys(node.overlays || {}).length, 0)
    + asArray(graph.edges).reduce((total, edge) => total + Object.keys(edge.overlays || {}).length, 0)
    + asArray(graph.overlays).length;
}

function updateOverlayMetadata(graph, overlayType) {
  const attached = new Set(asArray(graph.metadata?.overlaysAttached));
  if (overlayType) attached.add(overlayType);
  const overlaysAttached = OVERLAY_TYPES.filter((type) => attached.has(type));
  const diagnostics = {
    ...(graph.diagnostics || {}),
    nodeCount: asArray(graph.nodes).length,
    edgeCount: asArray(graph.edges).length,
    overlayCount: overlayCount(graph),
    unresolvedCount: asArray(graph.nodes).filter((node) => node?.type === "unresolved").length,
    warnings: asArray(graph.diagnostics?.warnings),
  };
  return {
    ...graph,
    diagnostics,
    metadata: {
      ...(graph.metadata || {}),
      overlaysAttached,
      overlayBridge: {
        status: "ready",
        schemaVersion: "prakriya-overlay-bridge.v1",
      },
    },
  };
}

function textCandidates(item) {
  return [
    item?.id,
    item?.originalId,
    item?.sourceTraceId,
    item?.sourceRuleId,
    item?.ruleId,
    item?.linkedKarakaNode,
    item?.linkedVakyaNode,
    item?.linkedSemanticNode,
    item?.linkedDerivationNode,
    item?.linkedRuleTrace,
    item?.token,
    item?.text,
    item?.surface,
    item?.form,
    item?.label,
  ].filter((value) => value !== null && value !== undefined && value !== "");
}

function nodeMatchesOverlay(node, item) {
  const nodeValues = textCandidates(node).map(stablePart);
  const itemValues = textCandidates(item).map(stablePart);
  if (nodeValues.some((value) => itemValues.includes(value))) return true;
  const nodeText = stablePart([node?.label, node?.output, node?.input].filter(Boolean).join(" "));
  return itemValues.some((value) => value !== "unknown" && nodeText.includes(value));
}

function defaultNodeIdForOverlay(graph, overlayType, item) {
  const nodes = asArray(graph.nodes);
  const direct = nodes.find((node) => nodeMatchesOverlay(node, item));
  if (direct) return direct.id;
  const byType = {
    karaka: ["padaAssembly", "sentenceComposition", "subantaGeneration"],
    vakya: ["sentenceComposition", "padaAssembly"],
    chandas: ["sentenceComposition", "sandhiExecution"],
    sandarbha: ["sentenceComposition", "diagnostic"],
    semantic: ["tinantaGeneration", "sentenceComposition"],
    "rule-trace": ["sandhiExecution", "diagnostic", "sentenceComposition"],
  };
  const preferred = byType[overlayType] || [];
  return nodes.find((node) => preferred.includes(node.type))?.id || nodes[0]?.id || null;
}

function edgeMatchesOverlay(edge, item) {
  const itemValues = textCandidates(item).map(stablePart);
  return [edge?.id, edge?.source, edge?.target, edge?.type, edge?.label]
    .map(stablePart)
    .some((value) => itemValues.includes(value));
}

function defaultEdgeIdForOverlay(graph, overlayType, item) {
  const edges = asArray(graph.edges);
  const direct = edges.find((edge) => edgeMatchesOverlay(edge, item));
  if (direct) return direct.id;
  const byType = {
    vakya: ["assembles", "feeds"],
    chandas: ["feeds", "appliesSandhi"],
    sandarbha: ["annotates", "feeds"],
    "rule-trace": ["appliesSandhi", "annotates"],
  };
  const preferred = byType[overlayType] || [];
  return edges.find((edge) => preferred.includes(edge.type))?.id || edges[0]?.id || null;
}

function attachOverlaySummary(graph, overlayType, overlayData) {
  const next = cloneGraph(graph);
  const summary = {
    id: `prakriya.overlay.${stablePart(overlayType)}`,
    overlayType,
    sourceLayer: overlayType,
    status: overlayData?.status || "ready",
    diagnostics: clonePlain(overlayData?.diagnostics || overlayData?.summary, {}),
    confidence: "deterministic",
  };
  const overlays = asArray(next.overlays).filter((overlay) => overlay.overlayType !== overlayType);
  return updateOverlayMetadata({ ...next, overlays: [...overlays, summary] }, overlayType);
}

function attachOverlayItems(graph, overlayType, overlayData, itemKeys, edgeKeys = ["edges"]) {
  let next = attachOverlaySummary(graph, overlayType, overlayData);
  itemKeys.forEach((key) => {
    asArray(overlayData?.[key]).forEach((item) => {
      const nodeId = defaultNodeIdForOverlay(next, overlayType, item);
      if (nodeId) next = attachOverlayToNode(next, nodeId, overlayType, { sourceCollection: key, ...item });
    });
  });
  edgeKeys.forEach((key) => {
    asArray(overlayData?.[key]).forEach((item) => {
      const edgeId = defaultEdgeIdForOverlay(next, overlayType, item);
      if (edgeId) next = attachOverlayToEdge(next, edgeId, overlayType, { sourceCollection: key, ...item });
    });
  });
  return next;
}

function inputText(execution, options) {
  if (typeof options.inputText === "string") return options.inputText;
  if (typeof options.text === "string") return options.text;
  const assembly = execution?.sentenceAssembly || {};
  return assembly.postSandhiText || assembly.preSandhiText || execution?.inputText || execution?.input_text || "";
}

function tokensFromText(text) {
  return String(text || "")
    .split(/\s+/)
    .filter(Boolean)
    .map((token, index) => ({ token, index }));
}

function overlayPayloads(execution, options) {
  const source = execution && typeof execution === "object" ? execution : {};
  const text = inputText(source, options);
  const morphologyTransitions = options.morphologyTransitions || source.morphologyTransitions || source.morphology || {};
  const semanticOverlay = options.semanticOverlay || options.semanticOverlays || inspectDhatuSemanticGraph(text);
  const ruleTrace = options.ruleTrace || options.ruleTraceChain || inspectRuleTrace(text);
  const derivationGraph = options.derivationGraph || semanticOverlay.derivationOverlay || ruleTrace.overlays?.derivationGraph || {};
  const karakaOverlay = options.karakaOverlay || buildKarakaOverlay({
    morphologyTransitions,
    semanticOverlays: semanticOverlay,
    derivationGraph,
    ruleTraceChain: ruleTrace,
  });
  const vakyaDependencyOverlay = options.vakyaDependencyOverlay || options.vakyaOverlay || buildVakyaDependencyOverlay({
    tokens: options.tokens || tokensFromText(text),
    morphologyTransitions,
    karakaOverlay,
    semanticOverlays: semanticOverlay,
    derivationGraph,
    ruleTraceChain: ruleTrace,
  });
  const sandarbhaContextOverlay = options.sandarbhaContextOverlay || options.sandarbhaOverlay || buildSandarbhaContextOverlay({
    tokens: options.tokens || tokensFromText(text),
    morphologyTransitions,
    karakaOverlay,
    vakyaDependencyOverlay,
    semanticOverlays: semanticOverlay.graph || semanticOverlay,
    derivationGraph: derivationGraph.graph || derivationGraph,
    ruleTraceChain: ruleTrace,
  });
  const chandasProsodyOverlay = options.chandasProsodyOverlay || options.chandasOverlay || buildChandasProsodyOverlay({
    text,
    tokens: options.tokens || tokensFromText(text),
    phoneticAnalysis: options.phoneticAnalysis,
    sandhiTransitions: source.sandhiTransitions || options.sandhiTransitions,
    symbolicCompression: options.symbolicCompression,
    phoneticTopology: options.phoneticTopology,
    morphologyTransitions,
    sandarbhaContextOverlay,
    derivationGraph,
  });
  return {
    karakaOverlay,
    vakyaDependencyOverlay,
    chandasProsodyOverlay,
    sandarbhaContextOverlay,
    semanticOverlay,
    ruleTrace,
  };
}

export function cloneGraph(graph) {
  return normalizeGraph(graph);
}

export function attachOverlayToNode(graph, nodeId, overlayType, overlayData) {
  const next = cloneGraph(graph);
  const nodes = asArray(next.nodes).map((node) => {
    if (node?.id !== nodeId) return node;
    return {
      ...node,
      overlays: {
        ...(node.overlays || {}),
        [overlayType]: clonePlain(overlayData, {}),
      },
    };
  });
  return updateOverlayMetadata({ ...next, nodes }, overlayType);
}

export function attachOverlayToEdge(graph, edgeId, overlayType, overlayData) {
  const next = cloneGraph(graph);
  const edges = asArray(next.edges).map((edge) => {
    if (edge?.id !== edgeId) return edge;
    return {
      ...edge,
      overlays: {
        ...(edge.overlays || {}),
        [overlayType]: clonePlain(overlayData, {}),
      },
    };
  });
  return updateOverlayMetadata({ ...next, edges }, overlayType);
}

export function findNodeByOriginalId(graph, originalId) {
  const stableOriginal = stablePart(originalId);
  return asArray(graph?.nodes).find((node) => textCandidates(node).map(stablePart).includes(stableOriginal)) || null;
}

export function findEdgeByEndpoint(graph, source, target, type) {
  return asArray(graph?.edges).find((edge) => (
    edge?.source === source
    && edge?.target === target
    && (!type || edge?.type === type || edge?.relation === type)
  )) || null;
}

export function attachAllOverlays(graph, execution, options = {}) {
  const base = cloneGraph(graph);
  if (!graph || typeof graph !== "object") return updateOverlayMetadata(base);
  const payloads = overlayPayloads(execution, options);
  let next = base;
  next = attachKarakaOverlay(next, payloads.karakaOverlay, { attachOverlayItems });
  next = attachVakyaOverlay(next, payloads.vakyaDependencyOverlay, { attachOverlayItems });
  next = attachChandasOverlay(next, payloads.chandasProsodyOverlay, { attachOverlayItems });
  next = attachSandarbhaOverlay(next, payloads.sandarbhaContextOverlay, { attachOverlayItems });
  next = attachSemanticOverlay(next, payloads.semanticOverlay, { attachOverlayItems });
  next = attachRuleTraceOverlay(next, payloads.ruleTrace, { attachOverlayItems });
  return updateOverlayMetadata(next);
}

