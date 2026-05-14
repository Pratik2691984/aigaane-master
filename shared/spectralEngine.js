    // shared/spectralEngine.js
    // 49D → Spectral Field Synthesis (continuous buffer)

    export function playSpectralField(vector, meta = {}, anomalies = []) {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const sampleRate = ctx.sampleRate;
        const duration = 2.0;                // seconds
        const bufferSize = sampleRate * duration;
        const buffer = ctx.createBuffer(1, bufferSize, sampleRate);
        const data = buffer.getChannelData(0);

        // Base frequency derived from Śruti (first two dimensions)
        const baseFreq = 220 + (vector[0] + vector[1]) * 220; // 220–440 Hz

        // Fill buffer sample by sample
        for (let i = 0; i < bufferSize; i++) {
            let t = i / sampleRate;            // time in seconds
            let sample = 0;

            // Sum contributions from all 49 dimensions as harmonic partials
            for (let k = 0; k < 49; k++) {
                const v = vector[k];
                if (v === 0) continue;

                // Frequency: logarithmically spread from fundamental up to ~8 kHz
                const freq = baseFreq * Math.pow(2, k / 12); // roughly semitone steps
                // Amplitude from vector value weighted by energy layer (dimensions 28-34)
                const energyLayer = vector[28 + (k % 7)] || 0.5;
                const amp = v * energyLayer * 0.02;   // keep overall level low

                // Phase from biological layer (dimensions 35-41)
                const phaseOffset = vector[35 + (k % 7)] * Math.PI;

                sample += amp * Math.sin(2 * Math.PI * freq * t + phaseOffset);
            }

            // Add noise texture from Guna dimensions (21-27)
            const noiseAmount = (vector[21] + vector[22] + vector[23]) / 3;
            sample += (Math.random() - 0.5) * noiseAmount * 0.1;

            data[i] = sample;
        }

        // Normalise to avoid clipping
        let max = 0;
        for (let i = 0; i < bufferSize; i++) {
            if (Math.abs(data[i]) > max) max = Math.abs(data[i]);
        }
        if (max > 0) {
            for (let i = 0; i < bufferSize; i++) data[i] /= max;
        }

        // Create audio source
        const source = ctx.createBufferSource();
        source.buffer = buffer;

        // Low‑pass filter (cutoff from stellar layer)
        const filter = ctx.createBiquadFilter();
        filter.type = "lowpass";
        filter.frequency.value = 1000 + vector[42] * 8000; // 1k–9kHz
        filter.Q.value = 1.0;

        // Stereo panner from spatial layer (first dimension)
        const panner = ctx.createStereoPanner();
        panner.pan.value = (vector[0] * 2 - 1) * 0.6;

        // Gain (overall volume from energy average)
        const energyAvg = vector.slice(28, 35).reduce((a,b)=>a+b,0)/7;
        const gain = ctx.createGain();
        gain.gain.value = 0.3 + energyAvg * 0.4;

        // Envelope: slow attack, longer decay
        const now = ctx.currentTime;
        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(gain.gain.value, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + duration - 0.2);

        // Connect nodes
        source.connect(filter);
        filter.connect(gain);
        gain.connect(panner);
        panner.connect(ctx.destination);

        source.start();
        source.stop(now + duration);

        // --- Anomaly overlay (optional) ---
        if (anomalies.length > 0) {
            anomalies.forEach(anom => {
                const osc = ctx.createOscillator();
                const g = ctx.createGain();
                let freq = baseFreq;
                switch (anom.type) {
                    case 'discordance': freq = baseFreq * 1.7; osc.type = 'square'; break;
                    case 'phase_lock_error': freq = baseFreq * 0.6; osc.type = 'sawtooth'; break;
                    case 'energy_spike': freq = baseFreq * 2.2; osc.type = 'triangle'; break;
                    default: freq = baseFreq * 1.1; osc.type = 'sine';
                }
                osc.frequency.value = freq;
                g.gain.value = 0.08;
                osc.connect(g);
                g.connect(ctx.destination);
                const t = now + 0.1;
                osc.start(t);
                osc.stop(t + 0.4);
                g.gain.setValueAtTime(0, t);
                g.gain.linearRampToValueAtTime(0.08, t + 0.02);
                g.gain.exponentialRampToValueAtTime(0.0001, t + 0.4);
            });
        }
    }