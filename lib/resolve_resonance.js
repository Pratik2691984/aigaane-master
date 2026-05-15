// C:\aigaane-master\api\resolve_resonance.js
// ILS v1.2 Pure Resolver – Deterministic, No Side Effects

import { SHRUTI_RATIOS } from "./shruti_ratios.js";

export function resolveResonance(theta) {
  const angle = ((theta % 360) + 360) % 360;
  const p = Math.floor((108 * angle) / 360);
  const pada_progress = (angle * 108 / 360) % 1;
  const nakshatra_id = Math.floor(p / 4);
  const phoneme_id = Math.floor((49 * p) / 108);
  const shruti_id = Math.floor((22 * p) / 108);
  const rasa_id = p % 9;
  const shruti_ratio = SHRUTI_RATIOS[shruti_id];

  const state = {
    angle: parseFloat(angle.toFixed(4)),
    pada_id: p,
    pada_progress: pada_progress,
    nakshatra_id: nakshatra_id,
    phoneme_id: phoneme_id,
    shruti_id: shruti_id,
    shruti_ratio: shruti_ratio,
    rasa_id: rasa_id
  };
  
  console.log('[resolver] Produced state:', state);
  
  return Object.freeze(state);
}