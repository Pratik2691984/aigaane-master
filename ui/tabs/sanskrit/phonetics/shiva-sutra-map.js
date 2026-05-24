import { MAHESHVARA_SUTRAS } from "./maheshvara-sutras.js";

export function flattenMaheshvaraSounds() {
  return MAHESHVARA_SUTRAS.flatMap((sutra) => sutra.sounds);
}

export function mapSoundToSutraIndex() {
  const mapping = {};

  MAHESHVARA_SUTRAS.forEach((sutra) => {
    sutra.sounds.forEach((sound) => {
      mapping[sound] = {
        sutraIndex: sutra.index,
        sutraText: sutra.text,
        marker: sutra.marker,
      };
    });
  });

  return mapping;
}

export function lookupMaheshvaraSound(sound) {
  const normalized = String(sound || "").trim();

  return (
    mapSoundToSutraIndex()[normalized] || {
      sutraIndex: null,
      sutraText: null,
      marker: null,
      unknown: true,
    }
  );
}