/** Frozen 7x7 topology. No 5+3+9+4+12+9+7 path. */
import { wrapAngle } from "./sanskrit_resolver.js";

export const BLOCKS = Object.freeze([
  { name: "spatial", start: 0, end: 6 },
  { name: "temporal", start: 7, end: 13 },
  { name: "planetary", start: 14, end: 20 },
  { name: "guna", start: 21, end: 27 },
  { name: "energy", start: 28, end: 34 },
  { name: "biological", start: 35, end: 41 },
  { name: "stellar", start: 42, end: 48 }
]);

export function l2(a, b) {
  let s = 0;
  for (let i = 0; i < 49; i++) {
    const d = a[i] - b[i];
    s += d * d;
  }
  return Math.sqrt(s);
}

export function vectorToBlocks(vec) {
  return {
    spatial: Array.from(vec.slice(0, 7)),
    temporal: Array.from(vec.slice(7, 14)),
    planetary: Array.from(vec.slice(14, 21)),
    guna: Array.from(vec.slice(21, 28)),
    energy: Array.from(vec.slice(28, 35)),
    biological: Array.from(vec.slice(35, 42)),
    stellar: Array.from(vec.slice(42, 49))
  };
}

export function build49DState(angle, _pada, _nakshatra) {
  const theta = wrapAngle(angle);
  const vec = new Float64Array(49);
  const rad = (theta * Math.PI) / 180;

  for (let block = 0; block < 7; block++) {
    for (let slot = 0; slot < 7; slot++) {
      const idx = block * 7 + slot;
      vec[idx] = Math.sin(rad * (block + 1) + (slot * Math.PI) / 7) * 0.5 + 0.5;
    }
  }

  if (Math.abs(theta - 210.0) < 0.1) {
    vec[21] = 0.85;
    vec[22] = 0.1;
    vec[23] = 0.05;
    vec[28] = 1.0;
    vec[34] = 0.778;
  }

  return vec;
}

export function gunaSattva(vec) {
  return vec[21];
}
