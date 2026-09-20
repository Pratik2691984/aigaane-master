import {
  DERIVATION_GRAPH_EDGES,
  DERIVATION_GRAPH_NODES,
  DERIVATION_GRAPH_SAFETY_NOTE,
} from "./derivation-graph-map.js";
import { inspectInputTopology } from "../phonetics/phonetic-topology-engine.js";
import { inspectSandhiText } from "../phonetics/sandhi-engine.js";
import { inspectSymbolicCompression } from "../phonetics/symbolic-compression-engine.js";

// Overlay inspection only; no authoritative grammatical derivation claim is made.
export function buildDerivationGraph() {
  return {
    nodes: DERIVATION_GRAPH_NODES,
    edges: DERIVATION_GRAPH_EDGES,
    safetyNote: DERIVATION_GRAPH_SAFETY_NOTE,
  };
}

export function inspectDerivationGraph(input = "") {
  const normalizedInput = String(input ?? "");
  const graph = buildDerivationGraph();
  const symbolic = inspectSymbolicCompression();
  const sandhi = inspectSandhiText(normalizedInput);
  const topology = inspectInputTopology(normalizedInput);

  const overlays = {
    activeSymbolicClasses: symbolic.classes
      .filter((item) => item.valid)
      .map((item) => item.classId),
    activeTopologyNodes: topology.activeNodeIds || [],
    activeSandhiTransitions: sandhi.transitions
      .filter((item) => item.matched)
      .map((item) => ({
        index: item.index,
        boundary: `${item.leftBoundary}+${item.rightBoundary}`,
        result: item.result,
        ruleId: item.ruleId,
      })),
  };

  return {
    input: normalizedInput,
    graph,
    overlays,
    summary: {
      nodeCount: graph.nodes.length,
      edgeCount: graph.edges.length,
      symbolicClassCount: overlays.activeSymbolicClasses.length,
      topologyNodeCount: overlays.activeTopologyNodes.length,
      sandhiTransitionCount: overlays.activeSandhiTransitions.length,
    },
    safetyNote: DERIVATION_GRAPH_SAFETY_NOTE,
  };
}
