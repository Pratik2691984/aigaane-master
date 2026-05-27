import { inspectDhatuSemanticGraph } from "../semantic/dhatu-semantic-engine.js";
import { inspectRuleTrace } from "../trace/rule-trace-engine.js";
import {
  MORPHOLOGY_TRANSITION_EDGES,
  MORPHOLOGY_TRANSITION_NODES,
  MORPHOLOGY_TRANSITION_SAFETY_NOTE,
} from "./morphology-transition-map.js";

export function buildMorphologyTransitionGraph() {
  return {
    nodes: MORPHOLOGY_TRANSITION_NODES,
    edges: MORPHOLOGY_TRANSITION_EDGES,
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  };
}

// Placeholder morphology transition inspection only; no authoritative morphology generation or grammatical correctness claim is made.
export function inspectMorphologyTransitions(input = "") {
  const normalizedInput = String(input ?? "");
  const graph = buildMorphologyTransitionGraph();
  const ruleTrace = inspectRuleTrace(normalizedInput);
  const dhatuSemantic = inspectDhatuSemanticGraph(normalizedInput);
  const roots = graph.nodes.filter((node) => node.type === "dhatu");
  const stems = graph.nodes.filter((node) => node.type === "stem");
  const suffixes = graph.nodes.filter((node) => node.type === "suffix");
  const surfaceForms = graph.nodes.filter((node) => node.type === "surface_form");

  return {
    input: normalizedInput,
    graph: {
      nodes: graph.nodes,
      edges: graph.edges,
    },
    overlays: {
      ruleTrace,
      dhatuSemantic,
    },
    morphology: {
      roots,
      stems,
      suffixes,
      surfaceForms,
    },
    summary: {
      nodeCount: graph.nodes.length,
      edgeCount: graph.edges.length,
      rootCount: roots.length,
      stemCount: stems.length,
      suffixCount: suffixes.length,
      surfaceFormCount: surfaceForms.length,
      traceNodeCount: ruleTrace.summary?.traceNodeCount || 0,
      semanticNodeCount: dhatuSemantic.summary?.nodeCount || 0,
    },
    safetyNote: MORPHOLOGY_TRANSITION_SAFETY_NOTE,
  };
}
