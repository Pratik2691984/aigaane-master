export const DERIVATION_GRAPH_SAFETY_NOTE =
  "Derivation graph overlay is deterministic structural metadata only; no authoritative grammatical derivation claim is made.";

export const DERIVATION_GRAPH_NODES = [
  {
    id: "dhatu_gam",
    type: "dhatu",
    label: "gam",
    category: "root",
    description: "Deterministic placeholder dhatu node for structural overlay inspection.",
  },
  {
    id: "dhatu_bhu",
    type: "dhatu",
    label: "bhu",
    category: "root",
    description: "Deterministic placeholder dhatu node for structural overlay inspection.",
  },
  {
    id: "pratyaya_ti",
    type: "pratyaya",
    label: "ti",
    category: "suffix",
    description: "Deterministic placeholder pratyaya node for graph preview.",
  },
  {
    id: "pratyaya_ta",
    type: "pratyaya",
    label: "ta",
    category: "suffix",
    description: "Deterministic placeholder pratyaya node for graph preview.",
  },
  {
    id: "sandhi_ac",
    type: "sandhi",
    label: "ac sandhi",
    category: "boundary",
    description: "Structural sandhi overlay node linked to symbolic vowel class context.",
  },
  {
    id: "symbolic_hal",
    type: "symbolic",
    label: "hal",
    category: "pratyahara",
    description: "Symbolic consonant-class overlay node.",
  },
  {
    id: "symbolic_ac",
    type: "symbolic",
    label: "ac",
    category: "pratyahara",
    description: "Symbolic vowel-class overlay node linked to sandhi context.",
  },
  {
    id: "articulation_kanthya",
    type: "articulation",
    label: "kanthya",
    category: "phonetic_topology",
    description: "Phonetic topology overlay node for guttural articulation context.",
  },
];

export const DERIVATION_GRAPH_EDGES = [
  {
    id: "edge.gam.ti",
    source: "dhatu_gam",
    target: "pratyaya_ti",
    relation: "structural_overlay",
  },
  {
    id: "edge.bhu.ta",
    source: "dhatu_bhu",
    target: "pratyaya_ta",
    relation: "structural_overlay",
  },
  {
    id: "edge.hal.kanthya",
    source: "symbolic_hal",
    target: "articulation_kanthya",
    relation: "phonetic_overlay",
  },
  {
    id: "edge.ac.sandhi_ac",
    source: "symbolic_ac",
    target: "sandhi_ac",
    relation: "sandhi_overlay",
  },
];
