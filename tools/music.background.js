// C:\aigaane-master\tools\music.background.js
// Background Audio Tool – TIS v1.0 Compliant

let audioCtx = null;
let oscillator = null;
let gainNode = null;

const BASE_FREQ = 240; // Traditional Indian Sa (can be tuned)

export const tool = {
  id: "music_audio",
  type: "background",
  subscriptions: ["shruti_ratio"],
  timeout: 20,
  always_run: true,
  
  run(state) {
    const ratio = state?.shruti_ratio;
    if (!ratio || !Number.isFinite(ratio)) return;
    
    const freq = BASE_FREQ * ratio;
    
    // Lazy init (user gesture required)
    if (!audioCtx) {
      // Wait for user unlock (handled in app.js)
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
    
    // Smooth frequency transition (no clicks)
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