import { expandPratyahara } from "./pratyahara-engine.js";
import {
  SYMBOLIC_COMPRESSION_RULES,
  SYMBOLIC_COMPRESSION_SAFETY_NOTE,
} from "./symbolic-compression-map.js";

const INVALID_SYMBOLIC_COMPRESSION_SAFETY_NOTE =
  "Invalid symbolic compression class; no authoritative Paninian derivation claim is made.";

export function expandSymbolicClass(classId = "") {
  const normalizedClassId = String(classId ?? "").trim().toLowerCase();
  const rule = SYMBOLIC_COMPRESSION_RULES.find((item) => item.id === normalizedClassId);

  if (!rule) {
    return {
      classId: normalizedClassId,
      valid: false,
      label: "Unknown symbolic class",
      source: "unmatched",
      sounds: [],
      safetyNote: INVALID_SYMBOLIC_COMPRESSION_SAFETY_NOTE,
    };
  }

  const expansion = expandPratyahara(rule.pratyahara.start, rule.pratyahara.marker);

  return {
    classId: normalizedClassId,
    valid: Boolean(expansion.valid),
    label: rule.label,
    source: rule.source,
    sounds: expansion.sounds || [],
    safetyNote: rule.safetyNote,
  };
}

export function inspectSymbolicCompression() {
  const classes = SYMBOLIC_COMPRESSION_RULES.map((rule) => expandSymbolicClass(rule.id));
  const validCount = classes.filter((item) => item.valid).length;
  const classCount = classes.length;

  return {
    classes,
    summary: {
      classCount,
      validCount,
      invalidCount: classCount - validCount,
    },
    safetyNote: SYMBOLIC_COMPRESSION_SAFETY_NOTE,
  };
}
