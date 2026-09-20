import { inspectDerivationGraph } from "../derivation/derivation-graph-engine.js";
import {
  DHATU_SEMANTIC_EDGES,
  DHATU_SEMANTIC_NODES,
  DHATU_SEMANTIC_SAFETY_NOTE,
} from "./dhatu-semantic-map.js";

export function buildDhatuSemanticGraph() {
  return {
    nodes: DHATU_SEMANTIC_NODES,
    edges: DHATU_SEMANTIC_EDGES,
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  };
}

// Placeholder-safe only; no authoritative semantic or grammatical correctness claim is made.
export function inspectDhatuSemanticGraph(input = "") {
  const normalizedInput = String(input ?? "");
  const graph = buildDhatuSemanticGraph();
  const derivationOverlay = inspectDerivationGraph(normalizedInput);
  const clusters = graph.nodes.filter((node) => node.type === "semantic_cluster");

  return {
    input: normalizedInput,
    graph: {
      nodes: graph.nodes,
      edges: graph.edges,
    },
    derivationOverlay,
    clusters,
    summary: {
      nodeCount: graph.nodes.length,
      edgeCount: graph.edges.length,
      clusterCount: clusters.length,
      derivationNodeCount: derivationOverlay.summary?.nodeCount || 0,
      derivationEdgeCount: derivationOverlay.summary?.edgeCount || 0,
    },
    safetyNote: DHATU_SEMANTIC_SAFETY_NOTE,
  };
}

export function attachSemanticOverlay(graph, overlayData = {}, bridge = {}) {
  if (typeof bridge.attachOverlayItems !== "function") return graph;
  return bridge.attachOverlayItems(graph, "semantic", overlayData?.graph || overlayData, ["nodes"], ["edges"]);
}
