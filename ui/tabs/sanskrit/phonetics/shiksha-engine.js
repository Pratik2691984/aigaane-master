import { SHIKSHA_PHONEME_MAP } from "./phoneme-map.js";

export function classifyShikshaCharacter(character) {
  const value = String(character || "");

  return {
    character: value,
    known: Boolean(SHIKSHA_PHONEME_MAP[value]),
    ...(SHIKSHA_PHONEME_MAP[value] || {
      type: "unknown",
      group: "unknown",
      articulation: "unknown",
    }),
  };
}

export function analyzeShikshaText(inputText = "") {
  const characters = Array.from(String(inputText || "")).filter(
    (character) => character.trim() !== "",
  );

  const phonemes = characters.map(classifyShikshaCharacter);

  const summary = phonemes.reduce(
    (counts, phoneme) => {
      counts.total += 1;
      counts[phoneme.type] = (counts[phoneme.type] || 0) + 1;
      counts.byArticulation[phoneme.articulation] =
        (counts.byArticulation[phoneme.articulation] || 0) + 1;
      counts.byGroup[phoneme.group] =
        (counts.byGroup[phoneme.group] || 0) + 1;
      return counts;
    },
    {
      total: 0,
      vowel: 0,
      consonant: 0,
      modifier: 0,
      unknown: 0,
      byArticulation: {},
      byGroup: {},
    },
  );

  return {
    inputText,
    phonemes,
    summary,
    safetyNote:
      "Śikṣā analysis is deterministic character classification only; no audio validation or Vedic accent verification is claimed.",
  };
}