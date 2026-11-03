/**
 * Gāndharva Studio III - High-Fidelity Acoustic Driver (v1.0 Production)
 * Ahobala 5-limit tuning, physical string modeling, and drone resonance.
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
    this.droneNodes = [];
    this.srutiProfile = null;
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
      this.droneGain.gain.setValueAtTime(0.22, this.ctx.currentTime);
      this.droneGain.connect(this.masterGain);
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  }

  async loadSrutiMatrix(saHz = 240.0) {
    this.baseHz = saHz;
    try {
      const res = await fetch(`${this.apiBase}/api/v1/sruti?sa_hz=${saHz}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      let items = [];
      if (data.profile) {
        // Adapt live Ahobala profile schema
        items = Object.entries(data.profile).map(([sym, v]) => ({
          svara_symbol: sym,
          name: (SWARA_CANONICAL[sym] && SWARA_CANONICAL[sym].name) || sym,
          ratio: v.ratio || (SWARA_CANONICAL[sym] ? SWARA_CANONICAL[sym].ratio_str : "1"),
          frequency_hz: v.freq_hz ? +(v.freq_hz * (saHz / (data.base_hz || 240.0))).toFixed(2) : +(saHz * (SWARA_CANONICAL[sym]?.ratio_val || 1.0)).toFixed(2),
          cents: v.cents || 0.0,
          midi_anchor: v.midi_anchor || (SWARA_CANONICAL[sym]?.midi_anchor || 60)
        }));
      } else if (Array.isArray(data.intervals)) {
        items = data.intervals.map(i => ({
          svara_symbol: i.svara_symbol || i.symbol,
          name: i.name,
          ratio: i.ratio,
          frequency_hz: +(i.frequency_hz || i.freq_hz).toFixed(2),
          cents: i.cents || 0.0,
          midi_anchor: 60
        }));
      }

      this.srutiProfile = items;
      return items;
    } catch (e) {
      console.warn("API offline or unreachable, using local Ahobala canon:", e);
      return this.getLocalAhobalaCanon(saHz);
    }
  }

  getLocalAhobalaCanon(saHz = 240.0) {
    this.srutiProfile = Object.entries(SWARA_CANONICAL).map(([sym, c]) => ({
      svara_symbol: sym,
      name: c.name,
      ratio: c.ratio_str,
      frequency_hz: +(saHz * c.ratio_val).toFixed(2),
      cents: +(1200 * Math.log2(c.ratio_val)).toFixed(2),
      midi_anchor: c.midi_anchor
    }));
    return this.srutiProfile;
  }

  pluckString(frequencyHz, duration = 1.8, velocity = 0.85) {
    this.init();
    const now = this.ctx.currentTime;

    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    const filter = this.ctx.createBiquadFilter();
    const gain = this.ctx.createGain();

    // Physical pluck emulation: fundamental + 2nd harmonic
    osc1.type = "sawtooth";
    osc2.type = "triangle";
    osc1.frequency.setValueAtTime(frequencyHz, now);
    osc2.frequency.setValueAtTime(frequencyHz * 2.0, now);

    // Dynamic damping
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(frequencyHz * 7.0, now);
    filter.frequency.exponentialRampToValueAtTime(frequencyHz * 1.1, now + duration);

    // Attack impulse envelope
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(velocity * 0.45, now + 0.012);
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

  startTanpuraDrone(saHz = 240.0) {
    this.init();
    this.stopTanpuraDrone();

    // Ahobala Drone: Mandra Pa (saHz * 0.75), Madhya Sa (saHz), Tāra Sa (saHz * 2.0)
    const pitches = [saHz * 0.75, saHz, saHz, saHz * 0.5];
    this.droneNodes = pitches.map((hz, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = idx === 0 ? "triangle" : "sine";
      osc.frequency.setValueAtTime(hz, this.ctx.currentTime);
      // Gentle micro-chorus
      osc.detune.setValueAtTime((idx - 1.5) * 4.2, this.ctx.currentTime);

      gain.gain.setValueAtTime(0.001, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.18 / (idx + 1), this.ctx.currentTime + 1.2);

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
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.7);
        osc.stop(now + 0.75);
      } catch (e) {}
    });
    this.droneNodes = [];
  }

  playSwaraSequence(swaraList, saHz = 240.0, tempoBpm = 76) {
    this.init();
    const beatSec = 60.0 / tempoBpm;
    let offset = 0.08;

    swaraList.forEach((item) => {
      let hz = 240.0;
      if (typeof item === "string" && SWARA_CANONICAL[item]) {
        hz = saHz * SWARA_CANONICAL[item].ratio_val;
      } else if (item.ratio) {
        hz = saHz * item.ratio;
      } else if (item.hz) {
        hz = item.hz;
      }

      setTimeout(() => {
        this.pluckString(hz, beatSec * 1.6, 0.8);
      }, offset * 1000);

      offset += beatSec;
    });
  }
}

window.GandharvaAudioDriver = GandharvaAudioDriver;
window.SWARA_CANONICAL = SWARA_CANONICAL;
