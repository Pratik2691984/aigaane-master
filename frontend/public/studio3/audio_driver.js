/**
 * Gāndharva Studio III - Karplus-Strong Physical Modeling Engine (v1.0 Production)
 * - Recursive circular delay buffer with feedback damping for authentic string plucks.
 * - Dual-string alternating Tanpura drone (Sa 240Hz / Pa 360Hz).
 * - Ahobala 5-limit pure mathematical ratios.
 */

const SWARA_CANONICAL = {
  "S":  { name: "Ṣaḍja", ratio_str: "1", ratio_val: 1.0, midi_anchor: 60 },
  "r":  { name: "Komal Ṛṣabha", ratio_str: "256/243", ratio_val: 256/243, midi_anchor: 61 },
  "G":  { name: "Śuddha Gāndhāra", ratio_str: "5/4", ratio_val: 5/4, midi_anchor: 64 },
  "M":  { name: "Śuddha Madhyama", ratio_str: "4/3", ratio_val: 4/3, midi_anchor: 65 },
  "P":  { name: "Pañcama", ratio_str: "3/2", ratio_val: 3/2, midi_anchor: 67 },
  "d":  { name: "Komal Dhaivata", ratio_str: "128/81", ratio_val: 128/81, midi_anchor: 68 },
  "N":  { name: "Śuddha Niṣāda", ratio_str: "15/8", ratio_val: 15/8, midi_anchor: 71 },
  "S'": { name: "Tāra Ṣaḍja", ratio_str: "2", ratio_val: 2.0, midi_anchor: 72 }
};

class GandharvaAudioDriver {
  constructor(apiBase = "https://aigaane-api-977695793163.asia-south1.run.app") {
    this.apiBase = apiBase;
    this.ctx = null;
    this.masterGain = null;
    this.droneGain = null;
    this.droneTimer = null;
    this.isDroneActive = false;
    this.baseHz = 240.0;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();

      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.85, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);

      this.droneGain = this.ctx.createGain();
      this.droneGain.gain.setValueAtTime(0.35, this.ctx.currentTime);
      this.droneGain.connect(this.masterGain);
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  }

  /**
   * Karplus-Strong string pluck synthesis.
   * Generates a burst of white noise fed into a feedback delay loop with lowpass damping.
   */
  pluckString(freqHz, duration = 2.2, velocity = 0.9) {
    this.init();
    const ctx = this.ctx;
    const now = ctx.currentTime;

    const period = 1.0 / freqHz;
    const bufferSize = Math.max(128, Math.floor(ctx.sampleRate * period));

    // 1. Excitation Noise Burst
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      noiseData[i] = (Math.random() * 2 - 1) * velocity;
    }

    const noiseSource = ctx.createBufferSource();
    noiseSource.buffer = noiseBuffer;

    // 2. Delay Line with Lowpass Damping Filter
    const delay = ctx.createDelay();
    delay.delayTime.setValueAtTime(period, now);

    const dampingFilter = ctx.createBiquadFilter();
    dampingFilter.type = "lowpass";
    dampingFilter.frequency.setValueAtTime(Math.min(freqHz * 6.0, 16000), now);

    const feedback = ctx.createGain();
    feedback.gain.setValueAtTime(0.992, now); // high string resonance

    const voiceGain = ctx.createGain();
    voiceGain.gain.setValueAtTime(1.0, now);
    voiceGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    // Feedback loop wiring: noise -> delay -> damping -> feedback -> delay
    noiseSource.connect(delay);
    delay.connect(dampingFilter);
    dampingFilter.connect(feedback);
    feedback.connect(delay);

    // Output wiring
    dampingFilter.connect(voiceGain);
    voiceGain.connect(this.masterGain);

    noiseSource.start(now);
    noiseSource.stop(now + period);

    // Clean disconnect
    setTimeout(() => {
      try {
        voiceGain.disconnect();
        delay.disconnect();
        dampingFilter.disconnect();
        feedback.disconnect();
      } catch (e) {}
    }, duration * 1000 + 100);
  }

  /**
   * Authentic Karplus-Strong Tanpura Drone.
   * Periodically plucks Pa (360Hz) and Sa (240Hz) with natural decay overlap.
   */
  startTanpuraDrone(saHz = 240.0) {
    this.init();
    this.stopTanpuraDrone();
    this.isDroneActive = true;
    this.baseHz = saHz;

    const paHz = saHz * 1.5;
    const mandraSaHz = saHz * 0.5;
    let step = 0;

    const cyclePluck = () => {
      if (!this.isDroneActive) return;
      if (step === 0) {
        this.pluckString(paHz, 4.5, 0.45); // Pa
      } else if (step === 1 || step === 2) {
        this.pluckString(saHz, 4.0, 0.40); // Madhya Sa
      } else {
        this.pluckString(mandraSaHz, 5.0, 0.50); // Kharja / Mandra Sa
      }
      step = (step + 1) % 4;
      this.droneTimer = setTimeout(cyclePluck, 1200); // 1.2s alternating plucks
    };

    cyclePluck();
  }

  stopTanpuraDrone() {
    this.isDroneActive = false;
    if (this.droneTimer) {
      clearTimeout(this.droneTimer);
      this.droneTimer = null;
    }
  }

  async loadSrutiMatrix(saHz = 240.0) {
    this.baseHz = saHz;
    try {
      const res = await fetch(`${this.apiBase}/api/v1/sruti?sa_hz=${saHz}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      let items = [];
      if (data.profile) {
        items = Object.entries(data.profile).map(([sym, v]) => ({
          svara_symbol: sym,
          name: SWARA_CANONICAL[sym]?.name || sym,
          ratio: v.ratio || SWARA_CANONICAL[sym]?.ratio_str || "1",
          frequency_hz: +(saHz * (SWARA_CANONICAL[sym]?.ratio_val || 1.0)).toFixed(2),
          cents: v.cents || 0.0,
          midi_anchor: v.midi_anchor || SWARA_CANONICAL[sym]?.midi_anchor || 60
        }));
      }
      return items;
    } catch (e) {
      return Object.entries(SWARA_CANONICAL).map(([sym, c]) => ({
        svara_symbol: sym,
        name: c.name,
        ratio: c.ratio_str,
        frequency_hz: +(saHz * c.ratio_val).toFixed(2),
        cents: +(1200 * Math.log2(c.ratio_val)).toFixed(2),
        midi_anchor: c.midi_anchor
      }));
    }
  }

  playSwaraSequence(swaraList, saHz = 240.0, tempoBpm = 76) {
    this.init();
    const beatSec = 60.0 / tempoBpm;
    let offset = 0.05;

    swaraList.forEach((item) => {
      let hz = saHz;
      let dur = beatSec * 1.8;

      if (typeof item === "string" && SWARA_CANONICAL[item]) {
        hz = saHz * SWARA_CANONICAL[item].ratio_val;
      } else if (item.ratio) {
        hz = saHz * item.ratio;
      } else if (item.hz) {
        hz = item.hz;
      }

      if (item.weight === "G") dur = beatSec * 2.4;
      if (item.weight === "L") dur = beatSec * 1.2;

      setTimeout(() => {
        this.pluckString(hz, dur, 0.85);
      }, offset * 1000);

      offset += beatSec;
    });
  }
}

window.GandharvaAudioDriver = GandharvaAudioDriver;
window.SWARA_CANONICAL = SWARA_CANONICAL;
