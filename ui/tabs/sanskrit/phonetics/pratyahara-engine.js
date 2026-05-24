import { MAHESHVARA_SUTRAS } from "./maheshvara-sutras.js";

function buildSequence() {
  const sequence = [];

  MAHESHVARA_SUTRAS.forEach((sutra) => {
    sutra.sounds.forEach((sound) => {
      sequence.push({
        sound,
        marker: false,
        sutraIndex: sutra.index,
      });
    });

    sequence.push({
      sound: sutra.marker,
      marker: true,
      sutraIndex: sutra.index,
    });
  });

  return sequence;
}

const SHIVA_SEQUENCE = buildSequence();

export function expandPratyahara(startSound, endMarker) {
  const start = String(startSound || "").trim();
  const marker = String(endMarker || "").trim();

  const startIndex = SHIVA_SEQUENCE.findIndex(
    (entry) => entry.sound === start && !entry.marker,
  );

  const endIndex = SHIVA_SEQUENCE.findIndex(
    (entry) => entry.sound === marker && entry.marker,
  );

  if (startIndex === -1 || endIndex === -1 || endIndex <= startIndex) {
    return {
      valid: false,
      sounds: [],
      safetyNote:
        "Invalid deterministic pratyāhāra request; no grammatical correctness claim is made.",
    };
  }

  const sounds = SHIVA_SEQUENCE.slice(startIndex, endIndex)
    .filter((entry) => !entry.marker)
    .map((entry) => entry.sound);

  return {
    valid: true,
    startSound: start,
    endMarker: marker,
    sounds,
    safetyNote:
      "Deterministic structural pratyāhāra expansion only; no authoritative grammatical claim is made.",
  };
}

export function getShivaSutraSequence() {
  return [...SHIVA_SEQUENCE];
}