import { analyzeArticulationSequence } from "./articulation-engine.js";
import {
  PHONETIC_TOPOLOGY_EDGES,
  PHONETIC_TOPOLOGY_NODES,
  PHONETIC_TOPOLOGY_SAFETY_NOTE,
} from "./phonetic-topology-map.js";

const ARTICULATION_ID_MAP = {
  "kaṇṭhya": "kanthya",
  "tālavya": "talavya",
  "mūrdhanya": "murdhanya",
  dantya: "dantya",
  "oṣṭhya": "osthya",
  "kaṇṭhatālavya": "kanthatalavya",
  "kaṇṭhoṣṭhya": "kanthosthya",
};

// Phonetic topology map is deterministic structural visualization metadata only.
export function buildPhoneticTopology() {
  return {
    nodes: PHONETIC_TOPOLOGY_NODES,
    edges: PHONETIC_TOPOLOGY_EDGES,
    safetyNote: PHONETIC_TOPOLOGY_SAFETY_NOTE,
  };
}

export function inspectInputTopology(input = "") {
  const normalizedInput = String(input ?? "");
  const topology = buildPhoneticTopology();
  const articulationAnalysis = analyzeArticulationSequence(normalizedInput);
  const activeNodeIds = [
    ...new Set(
      articulationAnalysis.analysis
        .filter((item) => item.known && ARTICULATION_ID_MAP[item.articulation])
        .map((item) => ARTICULATION_ID_MAP[item.articulation]),
    ),
  ];

  return {
    input: normalizedInput,
    activeNodeIds,
    nodes: topology.nodes,
    edges: topology.edges,
    summary: {
      nodeCount: topology.nodes.length,
      edgeCount: topology.edges.length,
      activeNodeCount: activeNodeIds.length,
      inputCharacterCount: Array.from(normalizedInput).length,
    },
    safetyNote: PHONETIC_TOPOLOGY_SAFETY_NOTE,
  };
}
