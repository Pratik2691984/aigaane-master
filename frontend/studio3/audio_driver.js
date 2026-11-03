/**
 * Gāndharva Studio III - 22-Śruti Acoustic & Physical Modeling Driver
 * Implements 5-limit Just Intonation, Tanpura drone, and plucked string synthesis.
 */

class GandharvaAudioDriver {
  constructor(apiBase = "https://aigaane-api-977695793163.asia-south1.run.app") {
    this.apiBase = apiBase;
    this.ctx = null;
    this.masterGain = null;
    this.droneGain = null;
    this.droneNodes = [];
    this.isPlaying = false;
    this.srutiMatrix = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.8, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);

      this.droneGain = this.ctx.createGain();
      this.droneGain.gain.setValueAtTime(0.18, this.ctx.currentTime);
      this.droneGain.connect(this.masterGain);
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  }

  async loadSrutiMatrix(saHz = 240.0) {
    try {
      const res = await fetch(`${this.apiBase}/api/v1/sruti?sa_hz=${saHz}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      this.srutiMatrix = data.intervals;
      return this.srutiMatrix;
    } catch (e) {
      console.warn("Using fallback local 22-Śruti intervals:", e);
      return null;
    }
  }

  startTanpuraDrone(saHz = 240.0) {
    this.init();
    this.stopTanpuraDrone();

    // Pa (3/2) and Sa (1/1) dual drone oscillators with gentle tremolo
    const frequencies = [saHz * 1.5, saHz, saHz * 0.5];
    this.droneNodes = frequencies.map((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      
      osc.type = idx === 0 ? "triangle" : "sine";
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      // Microtonal detune for acoustic shimmer
      osc.detune.setValueAtTime((idx - 1) * 3.5, this.ctx.currentTime);

      gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.25 / (idx + 1), this.ctx.currentTime + 1.5);

      osc.connect(gain);
      gain.connect(this.droneGain);
      osc.start();
      return { osc, gain };
    });
  }

  stopTanpuraDrone() {
    if (!this.ctx || this.droneNodes.length === 0) return;
    const now = this.ctx.currentTime;
    this.droneNodes.forEach(({ osc, gain }) => {
      try {
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);
        osc.stop(now + 0.85);
      } catch (e) {}
    });
    this.droneNodes = [];
  }

  pluckString(frequencyHz, duration = 1.8, velocity = 0.8) {
    this.init();
    const now = this.ctx.currentTime;

    // Karplus-Strong / Plucked string approximation via dual harmonic oscillators & exponential envelope
    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    const filter = this.ctx.createBiquadFilter();
    const gain = this.ctx.createGain();

    osc1.type = "sawtooth";
    osc2.type = "triangle";
    osc1.frequency.setValueAtTime(frequencyHz, now);
    osc2.frequency.setValueAtTime(frequencyHz * 2, now); // 2nd harmonic

    filter.type = "lowpass";
    filter.frequency.setValueAtTime(frequencyHz * 6, now);
    filter.frequency.exponentialRampToValueAtTime(frequencyHz * 0.8, now + duration);

    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(velocity * 0.5, now + 0.015); // Pluck attack
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + duration);
    osc2.stop(now + duration);
  }

  playSwaraSequence(swaras, baseHz = 240.0, tempoBpm = 76) {
    this.init();
    const beatDuration = 60.0 / tempoBpm;
    let time = 0.1;

    swaras.forEach((item) => {
      const hz = item.hz || (baseHz * (item.ratio || 1.0));
      setTimeout(() => {
        this.pluckString(hz, beatDuration * 1.5, 0.75);
      }, time * 1000);
      time += beatDuration;
    });
  }
}

window.GandharvaAudioDriver = GandharvaAudioDriver;
