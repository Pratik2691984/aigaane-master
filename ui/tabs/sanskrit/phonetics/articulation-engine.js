import { VARNA_ARTICULATION_GRID } from "./varna-grid.js";

export function lookupArticulation(sound) {
  const normalized = String(sound || "").trim();

  for (const group of VARNA_ARTICULATION_GRID) {
    if (group.sounds.includes(normalized)) {
      return {
        sound: normalized,
        articulation: group.articulation,
        label: group.label,
        known: true,
      };
    }
  }

  return {
    sound: normalized,
    articulation: "unknown",
    label: "Unknown",
    known: false,
  };
}

export function analyzeArticulationSequence(input = "") {
  const sounds = Array.from(String(input || "")).filter(
    (character) => character.trim() !== "",
  );

  const analysis = sounds.map(lookupArticulation);

  const summary = analysis.reduce(
    (counts, item) => {
      counts.total += 1;

      counts.byArticulation[item.articulation] =
        (counts.byArticulation[item.articulation] || 0) + 1;

      return counts;
    },
    {
      total: 0,
      byArticulation: {},
    },
  );

  return {
    input,
    analysis,
    summary,
    safetyNote:
      "Deterministic articulation inspection only; no pronunciation or chanting correctness claim is made.",
  };
}