const NODE_TYPES = [
  "input",
  "subantaGeneration",
  "tinantaGeneration",
  "padaAssembly",
  "sandhiExecution",
  "sentenceComposition",
  "reversePreview",
  "diagnostic",
  "unresolved",
];

const EDGE_TYPES = [
  "feeds",
  "transforms",
  "assembles",
  "appliesSandhi",
  "reversesTo",
  "annotates",
  "unresolved",
];

function stablePart(value) {
  return String(value ?? "unknown")
    .normalize("NFC")
    .trim()
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, "_")
    .replace(/^_+|_+$/g, "") || "unknown";
}

function clonePlain(value, fallback) {
  if (!value || typeof value !== "object") return fallback;
  return JSON.parse(JSON.stringify(value));
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function makeNode(partial) {
  return {
    id: partial.id,
    type: partial.type,
    label: partial.label || partial.id,
    stage: partial.stage || partial.type,
    order: partial.order || 0,
    input: partial.input ?? null,
    output: partial.output ?? null,
    ruleId: partial.ruleId || null,
    sourceTraceId: partial.sourceTraceId || null,
    sourceLayer: partial.sourceLayer || "prakriya-composition",
    reversible: Boolean(partial.reversible),
    confidence: "deterministic",
  };
}

function makeEdge(partial) {
  return {
    id: partial.id,
    source: partial.source,
    target: partial.target,
    type: partial.type,
    label: partial.label || partial.type,
    order: partial.order || 0,
    confidence: "deterministic",
  };
}

function stageForPada(pada) {
  if (pada?.sourceType === "subanta") return "subantaGeneration";
  if (pada?.sourceType === "tinanta") return "tinantaGeneration";
  return "unresolved";
}

function graphDiagnostics(nodes, edges, overlays, warnings) {
  return {
    nodeCount: nodes.length,
    edgeCount: edges.length,
    overlayCount: overlays.length,
    unresolvedCount: nodes.filter((node) => node.type === "unresolved").length,
    warnings,
  };
}

export function listPrakriyaGraphNodeTypes() {
  return [...NODE_TYPES];
}

export function listPrakriyaGraphEdgeTypes() {
  return [...EDGE_TYPES];
}

export function buildPrakriyaTraceGraph(execution = {}) {
  const source = execution && typeof execution === "object" ? execution : {};
  const nodes = [];
  const edges = [];
  const warnings = [];
  let order = 1;
  let edgeOrder = 1;

  nodes.push(makeNode({
    id: "prakriya.input",
    type: "input",
    label: "Prakriya Input",
    stage: "input",
    order: order += 1,
    input: clonePlain(source.inputs, {}),
    output: null,
    reversible: false,
  }));

  asArray(source.generatedPadas).forEach((pada, index) => {
    if (!pada || typeof pada !== "object") {
      const id = `prakriya.unresolved.pada.${index}`;
      nodes.push(makeNode({
        id,
        type: "unresolved",
        label: "Malformed Pada",
        stage: "unresolvedComposition",
        order: order += 1,
        input: pada ?? null,
        output: null,
        reversible: false,
      }));
      edges.push(makeEdge({
        id: `prakriya.edge.${edgeOrder}.input.${stablePart(id)}`,
        source: "prakriya.input",
        target: id,
        type: "unresolved",
        order: edgeOrder += 1,
      }));
      warnings.push(`Malformed generated pada at index ${index}.`);
      return;
    }

    const stage = stageForPada(pada);
    const nodeId = `prakriya.${stage}.${stablePart(pada.id || index)}`;
    nodes.push(makeNode({
      id: nodeId,
      type: pada.generatedForm ? stage : "unresolved",
      label: pada.generatedForm || "unresolved pada",
      stage,
      order: order += 1,
      input: { sourceType: pada.sourceType, id: pada.id },
      output: pada.generatedForm || "",
      ruleId: pada.sourceRuleId,
      reversible: Boolean(pada.generatedForm),
    }));
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.input.${stablePart(nodeId)}`,
      source: "prakriya.input",
      target: nodeId,
      type: pada.generatedForm ? "transforms" : "unresolved",
      order: edgeOrder += 1,
    }));
  });

  const assembly = source.sentenceAssembly && typeof source.sentenceAssembly === "object" ? source.sentenceAssembly : {};
  const assemblyId = "prakriya.padaAssembly.sentence";
  nodes.push(makeNode({
    id: assemblyId,
    type: "padaAssembly",
    label: "Pada Assembly",
    stage: "padaAssembly",
    order: order += 1,
    input: asArray(assembly.orderedPadas),
    output: assembly.preSandhiText || "",
    reversible: true,
  }));
  nodes
    .filter((node) => node.type === "subantaGeneration" || node.type === "tinantaGeneration")
    .forEach((node) => {
      edges.push(makeEdge({
        id: `prakriya.edge.${edgeOrder}.${stablePart(node.id)}.assembly`,
        source: node.id,
        target: assemblyId,
        type: "assembles",
        order: edgeOrder += 1,
      }));
    });

  asArray(source.sandhiTransitions).forEach((transition, index) => {
    if (!transition || typeof transition !== "object") {
      warnings.push(`Malformed sandhi transition at index ${index}.`);
      return;
    }
    const nodeId = `prakriya.sandhiExecution.${stablePart(transition.id || index)}`;
    nodes.push(makeNode({
      id: nodeId,
      type: "sandhiExecution",
      label: transition.ruleId || transition.originalBoundary || "sandhi boundary",
      stage: "sandhiExecution",
      order: order += 1,
      input: transition.originalBoundary || transition.boundary || null,
      output: transition.transformedBoundary || null,
      ruleId: transition.ruleId,
      sourceTraceId: transition.id || null,
      reversible: Boolean(transition.reversible),
    }));
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.assembly.${stablePart(nodeId)}`,
      source: assemblyId,
      target: nodeId,
      type: "appliesSandhi",
      order: edgeOrder += 1,
    }));
  });

  const sentenceId = "prakriya.sentenceComposition.output";
  nodes.push(makeNode({
    id: sentenceId,
    type: "sentenceComposition",
    label: "Sentence Composition",
    stage: "sentenceComposition",
    order: order += 1,
    input: assembly.preSandhiText || "",
    output: assembly.postSandhiText || assembly.preSandhiText || "",
    reversible: true,
  }));
  edges.push(makeEdge({
    id: `prakriya.edge.${edgeOrder}.assembly.sentence`,
    source: assemblyId,
    target: sentenceId,
    type: "feeds",
    order: edgeOrder += 1,
  }));
  nodes.filter((node) => node.type === "sandhiExecution").forEach((node) => {
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.${stablePart(node.id)}.sentence`,
      source: node.id,
      target: sentenceId,
      type: "feeds",
      order: edgeOrder += 1,
    }));
  });

  asArray(source.trace).forEach((traceNode, index) => {
    if (!traceNode || typeof traceNode !== "object") {
      warnings.push(`Malformed trace entry at index ${index}.`);
      return;
    }
    const nodeId = `prakriya.trace.${stablePart(traceNode.id || index)}`;
    nodes.push(makeNode({
      id: nodeId,
      type: "diagnostic",
      label: traceNode.operation || traceNode.stage || "trace",
      stage: traceNode.stage || "trace",
      order: order += 1,
      input: traceNode.before ?? null,
      output: traceNode.after ?? null,
      sourceTraceId: traceNode.id || null,
      reversible: false,
    }));
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.trace.${stablePart(nodeId)}`,
      source: sentenceId,
      target: nodeId,
      type: "annotates",
      order: edgeOrder += 1,
    }));
  });

  asArray(source.reversePreview).forEach((item, index) => {
    if (!item || typeof item !== "object") return;
    const nodeId = `prakriya.reversePreview.${stablePart(item.id || index)}`;
    nodes.push(makeNode({
      id: nodeId,
      type: "reversePreview",
      label: item.generated || "reverse preview",
      stage: "reversePreview",
      order: order += 1,
      input: item.generated || null,
      output: clonePlain(item.reconstructed, item.reconstructed ?? null),
      reversible: true,
    }));
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.reverse.${stablePart(nodeId)}`,
      source: sentenceId,
      target: nodeId,
      type: "reversesTo",
      order: edgeOrder += 1,
    }));
  });

  asArray(source.diagnostics?.warnings).forEach((warning, index) => {
    const nodeId = `prakriya.diagnostic.${index}.${stablePart(warning)}`;
    nodes.push(makeNode({
      id: nodeId,
      type: "diagnostic",
      label: "Diagnostic",
      stage: "diagnostic",
      order: order += 1,
      input: null,
      output: warning,
      reversible: false,
    }));
    edges.push(makeEdge({
      id: `prakriya.edge.${edgeOrder}.diagnostic.${index}`,
      source: sentenceId,
      target: nodeId,
      type: "annotates",
      order: edgeOrder += 1,
    }));
  });

  if (!execution || typeof execution !== "object") warnings.push("Execution was missing or not an object; deterministic empty graph returned.");

  return {
    schemaVersion: "prakriya-trace-graph.v1",
    status: "ready",
    graphType: "deterministic-prakriya-trace",
    nodes,
    edges,
    overlays: [],
    diagnostics: graphDiagnostics(nodes, edges, [], warnings),
  };
}

export function serializePrakriyaTraceGraph(graph = {}) {
  const safeGraph = graph && typeof graph === "object" ? graph : {};
  return JSON.stringify(clonePlain(safeGraph, {}), null, 2);
}

export function attachPrakriyaOverlay(graph = {}, overlayData = {}) {
  const base = clonePlain(graph, {
    schemaVersion: "prakriya-trace-graph.v1",
    status: "ready",
    graphType: "deterministic-prakriya-trace",
    nodes: [],
    edges: [],
    overlays: [],
    diagnostics: { nodeCount: 0, edgeCount: 0, overlayCount: 0, unresolvedCount: 0, warnings: [] },
  });
  const overlays = asArray(base.overlays);
  const overlay = {
    id: `prakriya.overlay.${overlays.length}.${stablePart(overlayData?.sourceLayer || overlayData?.id || "annotation")}`,
    sourceLayer: overlayData?.sourceLayer || "external-overlay",
    data: clonePlain(overlayData, {}),
    confidence: "deterministic",
  };
  const next = {
    ...base,
    overlays: [...overlays, overlay],
  };
  next.diagnostics = graphDiagnostics(asArray(next.nodes), asArray(next.edges), next.overlays, asArray(next.diagnostics?.warnings));
  return next;
}
