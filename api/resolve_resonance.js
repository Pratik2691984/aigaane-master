// C:\aigaane-master\api\resolve_resonance.js
// ILS v1.2 Pure Resolver – Deterministic, No Side Effects

import { SHRUTI_RATIOS } from "./shruti_ratios.js";

export function resolveResonance(theta) {
    // Normalize angle to [0, 360)
    const angle = ((theta % 360) + 360) % 360;

    // Core invariant: Pāda ID (0–107)
    const p = Math.floor((108 * angle) / 360);
    
    // Progress within current pāda (0 to 0.999...)
    const pada_progress = (angle * 108 / 360) % 1;

    // Derived domains
    const nakshatra_id = Math.floor(p / 4);        // 0–26
    const phoneme_id = Math.floor((49 * p) / 108); // 0–48
    const shruti_id = Math.floor((22 * p) / 108);  // 0–21
    const rasa_id = p % 9;                         // 0–8

    const shruti_ratio = SHRUTI_RATIOS[shruti_id];

    // Hard validation – fail fast
    if (!Number.isFinite(shruti_ratio)) {
        throw new Error(`Invalid shruti ratio at p=${p}, shruti_id=${shruti_id}`);
    }

    // Frozen canonical state – immutable
    return Object.freeze({
        angle: parseFloat(angle.toFixed(4)),
        pada_id: p,
        pada_progress: pada_progress,
        nakshatra_id,
        phoneme_id,
        shruti_id,
        shruti_ratio,
        rasa_id
    });
}