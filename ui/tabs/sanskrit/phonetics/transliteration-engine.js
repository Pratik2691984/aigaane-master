import {
  DEVANAGARI_IAST_MAP,
  TRANSLITERATION_SAFETY_NOTE,
} from "./transliteration-map.js";
import { DEVANAGARI_IPA_MAP, IPA_SAFETY_NOTE } from "./ipa-map.js";

const TRANSLITERATION_INSPECTION_SAFETY_NOTE =
  "Deterministic transliteration inspection only; no pronunciation correctness claim is made.";

function transliterateWithMap(input, map, safetyNote) {
  const normalizedInput = String(input ?? "");
  const unknownCharacters = [];
  const output = Array.from(normalizedInput)
    .map((character) => {
      if (Object.hasOwn(map, character)) return map[character];
      if (!/\s/u.test(character) && !unknownCharacters.includes(character)) {
        unknownCharacters.push(character);
      }
      return character;
    })
    .join("");

  return {
    input: normalizedInput,
    output,
    unknownCharacters,
    safetyNote,
  };
}

export function transliterateDevanagariToIast(input = "") {
  return transliterateWithMap(input, DEVANAGARI_IAST_MAP, TRANSLITERATION_SAFETY_NOTE);
}

export function transliterateDevanagariToIpa(input = "") {
  return transliterateWithMap(input, DEVANAGARI_IPA_MAP, IPA_SAFETY_NOTE);
}

export function inspectTransliteration(input = "") {
  const normalizedInput = String(input ?? "");
  const iast = transliterateDevanagariToIast(normalizedInput);
  const ipa = transliterateDevanagariToIpa(normalizedInput);

  return {
    input: normalizedInput,
    iast,
    ipa,
    summary: {
      characterCount: Array.from(normalizedInput).length,
      iastUnknownCount: iast.unknownCharacters.length,
      ipaUnknownCount: ipa.unknownCharacters.length,
    },
    safetyNote: TRANSLITERATION_INSPECTION_SAFETY_NOTE,
  };
}
