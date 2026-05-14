// shared/soundEngine.js
// Enhanced multi‑harmonic synthesis with 49D parameter mapping

let audioCtx = null;
let currentSources = [];

function initAudio() {
    if (audioCtx) return audioCtx;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
}

function stopCurrentSounds() {
    currentSources.forEach(source => {
        try { source.stop(); } catch(e) {}
        try { source.disconnect(); } catch(e) {}
    });
    currentSources = [];
}

export function playHarmonicTone(vector, duration = 2.5) {
    const ctx = initAudio();
    if (!ctx) return;
    if (ctx.state === 'suspended') ctx.resume();

    stopCurrentSounds();

    // Use 7 different dimensions to shape the sound
    const dim0 = vector[0];   // baseline
    const dim1 = vector[1];   // frequency modifier
    const dim2 = vector[2];   // harmonic richness
    const dim3 = vector[3];   // waveform shape
    const dim4 = vector[4];   // filter sweep
    const dim5 = vector[5];   // pan position
    const dim6 = vector[6];   // envelope decay

    // Fundamental frequency: 80 Hz to 400 Hz
    const fundamental = 80 + (dim0 + dim1) * 320;

    // Number of harmonics: 1 to 8
    const harmonicsCount = 1 + Math.floor(dim2 * 7);

    // Master gain (softer for lower freqs, louder for higher)
    const masterGain = ctx.createGain();
    masterGain.gain.value = 0.1;
    masterGain.connect(ctx.destination);

    // Stereo panner based on dim5
    const panner = ctx.createStereoPanner();
    panner.pan.value = (dim5 - 0.5) * 1.2; // range -0.6 to 0.6
    masterGain.connect(panner);
    panner.connect(ctx.destination);

    // Optional filter for brightness variation
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 500 + dim4 * 8000; // 500Hz to 8500Hz
    filter.Q.value = 5;
    // Connect masterGain to filter if you want, or bypass – let's use it for extra colour
    // For simplicity, we'll insert filter before panner
    masterGain.disconnect();
    masterGain.connect(filter);
    filter.connect(panner);

    const now = ctx.currentTime;

    for (let h = 1; h <= harmonicsCount; h++) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        // Waveform selection based on dim3 and harmonic index
        if (dim3 > 0.66 && h % 2 === 0) osc.type = 'sawtooth';
        else if (dim3 > 0.33 && h % 3 === 0) osc.type = 'triangle';
        else if (dim3 > 0.1 && h % 5 === 0) osc.type = 'square';
        else osc.type = 'sine';

        osc.frequency.value = fundamental * h;

        // Harmonic amplitude: decreases with harmonic number, modulated by dim2
        const harmonicGain = (1 / (h * 0.7)) * (0.5 + dim2 * 0.5);
        gain.gain.value = harmonicGain * 0.5;

        osc.connect(gain);
        gain.connect(masterGain);

        osc.start(now);
        osc.stop(now + duration);

        currentSources.push(osc);
    }

    // Envelope: attack 0.05s, decay shaped by dim6
    const attackTime = 0.05;
    const decayTime = 0.3 + dim6 * 1.0;
    masterGain.gain.setValueAtTime(0, now);
    masterGain.gain.linearRampToValueAtTime(0.15, now + attackTime);
    masterGain.gain.exponentialRampToValueAtTime(0.0001, now + attackTime + decayTime);

    // Also sweep filter frequency over time
    const startFreq = 300 + dim4 * 3000;
    const endFreq = 8000;
    filter.frequency.setValueAtTime(startFreq, now);
    filter.frequency.exponentialRampToValueAtTime(endFreq, now + duration * 0.7);

    // Cleanup after sound ends
    setTimeout(() => {
        currentSources = currentSources.filter(s => s !== osc);
    }, duration * 1000);
}