import { inspectSymbolicCompression } from "../phonetics/symbolic-compression-engine.js";
import { buildDhatuSemanticGraph } from "../semantic/dhatu-semantic-engine.js";
import {
  SUTRA_REFERENCE_EDGES,
  SUTRA_REFERENCE_NODES,
  SUTRA_REFERENCE_SAFETY_NOTE,
} from "./sutra-reference-map.js";

export function buildSutraReferenceOverlay() {
  return {
    nodes: SUTRA_REFERENCE_NODES,
    edges: SUTRA_REFERENCE_EDGES,
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  };
}

// Reference overlay only; no authoritative sūtra interpretation or grammatical correctness claim is made.
export function inspectSutraReferenceOverlay(input = "") {
  const normalizedInput = String(input ?? "");
  const overlay = buildSutraReferenceOverlay();
  const symbolicCompression = inspectSymbolicCompression();
  const semanticGraph = buildDhatuSemanticGraph();

  return {
    input: normalizedInput,
    overlay: {
      nodes: overlay.nodes,
      edges: overlay.edges,
    },
    symbolicCompression,
    semanticGraph,
    summary: {
      referenceNodeCount: overlay.nodes.length,
      referenceEdgeCount: overlay.edges.length,
      symbolicClassCount: symbolicCompression.summary?.classCount || 0,
      semanticNodeCount: semanticGraph.nodes.length,
      semanticEdgeCount: semanticGraph.edges.length,
    },
    safetyNote: SUTRA_REFERENCE_SAFETY_NOTE,
  };
}
