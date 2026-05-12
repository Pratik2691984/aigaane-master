// C:\aigaane-master\tools\music.background.js (UPDATED)
// Background Audio Tool – Now uses Rāga-constrained frequency

import { SHRUTI_RATIOS } from '../api/shruti_ratios.js';

let audioCtx = null;
let oscillator = null;
let gainNode = null;

const BASE_FREQ = 240;

// Helper to get constrained shruti ratio
function getConstrainedRatio() {
    const ragaState = window._ragaState;
    if (ragaState && ragaState.constrainedShrutiId !== undefined) {
        return SHRUTI_RATIOS[ragaState.constrainedShrutiId];
    }
    return null;
}

export const tool = {
    id: "music_audio",
    type: "background",
    subscriptions: ["shruti_ratio"],  // Still subscribes to raw
    timeout_ms: 20,
    always_run: true,
    
    run(state) {
        // Try to get constrained ratio first
        let ratio = getConstrainedRatio();
        
        // Fallback to raw if no raga constraint active
        if (!ratio) {
            ratio = state.shruti_ratio;
            if (!ratio || !Number.isFinite(ratio)) return;
        }
        
        const freq = BASE_FREQ * ratio;
        
        // Lazy init
        if (!audioCtx) {
            if (!window.audioUnlocked) return;
            
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            
            oscillator.type = "sine";
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            gainNode.gain.setValueAtTime(0.15, audioCtx.currentTime);
            oscillator.start();
        }
        
        if (oscillator && audioCtx) {
            oscillator.frequency.setTargetAtTime(freq, audioCtx.currentTime, 0.02);
        }
    },
    
    destroy() {
        if (oscillator) {
            try { oscillator.stop(); } catch(e) {}
            oscillator = null;
        }
        if (audioCtx) {
            try { audioCtx.close(); } catch(e) {}
            audioCtx = null;
        }
        gainNode = null;
    }
};