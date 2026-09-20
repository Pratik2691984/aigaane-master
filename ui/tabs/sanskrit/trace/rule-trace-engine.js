import { inspectDerivationGraph } from "../derivation/derivation-graph-engine.js";
import { inspectSandhiText } from "../phonetics/sandhi-engine.js";
import { inspectSymbolicCompression } from "../phonetics/symbolic-compression-engine.js";
import { inspectDhatuSemanticGraph } from "../semantic/dhatu-semantic-engine.js";
import { inspectSutraReferenceOverlay } from "../sutra/sutra-reference-engine.js";
import {
  RULE_TRACE_EDGES,
  RULE_TRACE_NODES,
  RULE_TRACE_SAFETY_NOTE,
} from "./rule-trace-map.js";

export function buildRuleTraceGraph() {
  return {
    nodes: RULE_TRACE_NODES,
    edges: RULE_TRACE_EDGES,
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  };
}

// Trace inspection only; no authoritative Paninian interpretation or grammatical correctness claim is made.
export function inspectRuleTrace(input = "") {
  const normalizedInput = String(input ?? "");
  const traceGraph = buildRuleTraceGraph();
  const sutraReference = inspectSutraReferenceOverlay(normalizedInput);
  const derivationGraph = inspectDerivationGraph(normalizedInput);
  const dhatuSemantic = inspectDhatuSemanticGraph(normalizedInput);
  const sandhiInspection = inspectSandhiText(normalizedInput);
  const symbolicCompression = inspectSymbolicCompression();

  return {
    input: normalizedInput,
    traceGraph,
    overlays: {
      sutraReference,
      derivationGraph,
      dhatuSemantic,
      sandhiInspection,
      symbolicCompression,
    },
    summary: {
      traceNodeCount: traceGraph.nodes.length,
      traceEdgeCount: traceGraph.edges.length,
      sutraReferenceNodeCount: sutraReference.summary?.referenceNodeCount || 0,
      derivationNodeCount: derivationGraph.summary?.nodeCount || 0,
      semanticNodeCount: dhatuSemantic.summary?.nodeCount || 0,
      sandhiTransitionCount: sandhiInspection.summary?.transitionCount || 0,
      symbolicClassCount: symbolicCompression.summary?.classCount || 0,
    },
    safetyNote: RULE_TRACE_SAFETY_NOTE,
  };
}

export function attachRuleTraceOverlay(graph, overlayData = {}, bridge = {}) {
  if (typeof bridge.attachOverlayItems !== "function") return graph;
  return bridge.attachOverlayItems(graph, "rule-trace", overlayData?.traceGraph || overlayData, ["nodes"], ["edges"]);
}
