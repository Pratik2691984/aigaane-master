import { VARNA_ARTICULATION_GRID } from "./varna-grid.js";

export const PHONETIC_TOPOLOGY_SAFETY_NOTE =
  "Phonetic topology map is deterministic structural visualization metadata only; no pronunciation or chanting correctness claim is made.";

const ARTICULATION_TOPOLOGY_LAYOUT = {
  "kaṇṭhya": { id: "kanthya", x: 10, y: 40 },
  "tālavya": { id: "talavya", x: 50, y: 20 },
  "mūrdhanya": { id: "murdhanya", x: 70, y: 40 },
  dantya: { id: "dantya", x: 90, y: 60 },
  "oṣṭhya": { id: "osthya", x: 50, y: 80 },
  "kaṇṭhatālavya": { id: "kanthatalavya", x: 30, y: 25 },
  "kaṇṭhoṣṭhya": { id: "kanthosthya", x: 30, y: 75 },
};

export const PHONETIC_TOPOLOGY_NODES = VARNA_ARTICULATION_GRID.map((group) => {
  const layout = ARTICULATION_TOPOLOGY_LAYOUT[group.articulation];

  return {
    id: layout.id,
    label: group.label,
    type: "articulation",
    x: layout.x,
    y: layout.y,
    sounds: [...group.sounds],
  };
});

export const PHONETIC_TOPOLOGY_EDGES = [
  {
    id: "edge.kanthya.kanthatalavya",
    source: "kanthya",
    target: "kanthatalavya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.kanthatalavya.talavya",
    source: "kanthatalavya",
    target: "talavya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.kanthya.kanthosthya",
    source: "kanthya",
    target: "kanthosthya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.kanthosthya.osthya",
    source: "kanthosthya",
    target: "osthya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.talavya.murdhanya",
    source: "talavya",
    target: "murdhanya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.murdhanya.dantya",
    source: "murdhanya",
    target: "dantya",
    relation: "articulation_adjacency",
  },
  {
    id: "edge.dantya.osthya",
    source: "dantya",
    target: "osthya",
    relation: "articulation_adjacency",
  },
];
