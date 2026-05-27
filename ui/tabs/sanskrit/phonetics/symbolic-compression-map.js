import { expandPratyahara } from "./pratyahara-engine.js";

export const SYMBOLIC_COMPRESSION_SAFETY_NOTE =
  "Symbolic compression map is deterministic structural metadata only; no authoritative Paninian derivation claim is made.";

export const SYMBOLIC_COMPRESSION_RULES = [
  {
    id: "ac",
    label: "vowels",
    source: "Maheshvara pratyahara",
    pratyahara: { start: "अ", marker: "च्" },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  },
  {
    id: "hal",
    label: "consonants",
    source: "Maheshvara pratyahara",
    pratyahara: { start: "ह", marker: "ल्" },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  },
  {
    id: "ik",
    label: "simple vowels i/u/r/l class",
    source: "Maheshvara pratyahara",
    pratyahara: { start: "इ", marker: "क्" },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  },
  {
    id: "ec",
    label: "e/o/ai/au class",
    source: "Maheshvara pratyahara",
    pratyahara: { start: "ए", marker: "च्" },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  },
  {
    id: "yan",
    label: "semivowel class",
    source: "Maheshvara pratyahara",
    pratyahara: { start: "य", marker: "ण्" },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  },
];

export function expandCompressionRule(rule) {
  return expandPratyahara(rule.pratyahara.start, rule.pratyahara.marker);
}
