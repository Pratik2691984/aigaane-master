// C:\aigaane-master\tools\raga_engine.tool.js
// Rāga Constraint Engine – Background Tool (TIS v1.0 Compliant)

import { RAGA_MAP } from '../shared/ragas.js';

// Current active raga (can be changed by UI later)
let currentRagaId = "YAMAN";

// Find closest allowed shruti in current raga
function constrainShruti(rawShrutiId, allowedShrutis) {
    if (allowedShrutis.includes(rawShrutiId)) {
        return rawShrutiId;
    }
    
    // Find closest allowed shruti
    let closest = allowedShrutis[0];
    let minDiff = Math.abs(allowedShrutis[0] - rawShrutiId);
    
    for (let i = 1; i < allowedShrutis.length; i++) {
        const diff = Math.abs(allowedShrutis[i] - rawShrutiId);
        if (diff < minDiff) {
            minDiff = diff;
            closest = allowedShrutis[i];
        }
    }
    return closest;
}

export const tool = {
    id: "raga_engine",
    type: "background",
    subscriptions: ["shruti_id", "shruti_ratio"],
    timeout_ms: 10,
    always_run: true,
    enabled: true,
    
    run(state) {
        const rawShrutiId = state.shruti_id;
        const raga = RAGA_MAP[currentRagaId];
        
        if (!raga) return;
        
        const constrainedShrutiId = constrainShruti(rawShrutiId, raga.allowed_shrutis);
        
        // Get the ratio for the constrained shruti
        // This requires SHRUTI_RATIOS to be available globally or imported
        // We'll use a lookup – for now, store the constrained ID
        
        // Store constrained values in window for other tools to use
        window._ragaState = {
            currentRaga: currentRagaId,
            ragaName: raga.name,
            constrainedShrutiId: constrainedShrutiId,
            ragaRasa: raga.rasa,
            rawShrutiId: rawShrutiId
        };
        
        // Optional: Log raga changes
        if (window._lastConstrained !== constrainedShrutiId) {
            console.log(`[Rāga] ${raga.name}: Śruti ${rawShrutiId} → ${constrainedShrutiId}`);
            window._lastConstrained = constrainedShrutiId;
        }
    },
    
    // Expose function to change raga dynamically
    setRaga(ragaId) {
        if (RAGA_MAP[ragaId]) {
            currentRagaId = ragaId;
            console.log(`[Rāga] Switched to ${RAGA_MAP[ragaId].name}`);
            return true;
        }
        return false;
    },
    
    getCurrentRaga() {
        return RAGA_MAP[currentRagaId];
    }
};

// Attach global setter for UI use
window.setRaga = (ragaId) => tool.setRaga(ragaId);
window.getRagaState = () => window._ragaState;