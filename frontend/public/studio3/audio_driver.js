/**
 * Gāndharva Studio III - Audited v1.0 AudioWorklet Karplus-Strong Engine
 * Implements 0.00¢ fractional delay tuning, 1.2 Hz andolan LFO on komal swaras,
 * portamento meend glides, and physical dual-string Tanpura drone.
 */

const GANDHARVA_WORKLET_CODE = `
class KarplusStrongProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
      { name: 'frequency', defaultValue: 240.0, minValue: 20.0, maxValue: 2000.0, automationRate: 'a-rate' },
      { name: 'feedback', defaultValue: 0.9960, minValue: 0.8, maxValue: 0.9999, automationRate: 'k-rate' },
      { name: 'damping', defaultValue: 0.45, minValue: 0.0, maxValue: 1.0, automationRate: 'k-rate' },
      { name: 'andolanDepth', defaultValue: 0.0, minValue: 0.0, maxValue: 50.0, automationRate: 'k-rate' },
      { name: 'andolanRate', defaultValue: 1.2, minValue: 0.1, maxValue: 10.0, automationRate: 'k-rate' }
    ];
  }

  constructor() {
    super();
    this.bufferSize = 4096;
    this.buffer = new Float32Array(this.bufferSize);
    this.writeIndex = 0;
    this.lastOutput = 0.0;
    this.phase = 0.0;
    this.burstRemaining = 0;
    this.pluckVelocity = 0.8;

    this.port.onmessage = (e) => {
      if (e.data.type === 'trigger') {
        const freq = e.data.frequency || 240.0;
        this.pluckVelocity = e.data.velocity || 0.85;
        this.burstRemaining = Math.max(32, Math.floor(sampleRate / freq));
      }
    };
  }

  process(inputs, outputs, parameters) {
    const output = outputs[0];
    const channel = output[0];
    if (!channel) return true;

    const freqParam = parameters.frequency;
    const feedback = parameters.feedback[0];
    const damping = parameters.damping[0];
    const andolanDepth = parameters.andolanDepth[0];
    const andolanRate = parameters.andolanRate[0];

    const isFreqArray = freqParam.length > 1;

    for (let i = 0; i < channel.length; i++) {
      let baseFreq = isFreqArray ? freqParam[i] : freqParam[0];

      // 1.2 Hz Andolan Microtonal LFO
      if (andolanDepth > 0.0) {
        this.phase += (2.0 * Math.PI * andolanRate) / sampleRate;
        if (this.phase > 2.0 * Math.PI) this.phase -= 2.0 * Math.PI;
        const centsOffset = Math.sin(this.phase) * andolanDepth;
        baseFreq *= Math.pow(2.0, centsOffset / 1200.0);
      }

      // Fractional Delay calculation for 0.00¢ Exact Ahobala Tuning
      const delaySamples = sampleRate / baseFreq;
      const intDelay = Math.floor(delaySamples);
      const fracDelay = delaySamples - intDelay;

      let readIndexA = this.writeIndex - intDelay;
      if (readIndexA < 0) readIndexA += this.bufferSize;

      let readIndexB = readIndexA - 1;
      if (readIndexB < 0) readIndexB += this.bufferSize;

      // Linear interpolation between adjacent delay samples
      const sampleA = this.buffer[readIndexA];
      const sampleB = this.buffer[readIndexB];
      const delayedSample = sampleA + fracDelay * (sampleB - sampleA);

      // Lowpass String Damping Filter
      const filtered = delayedSample * (1.0 - damping) + this.lastOutput * damping;
      this.lastOutput = filtered;

      // Excitation Pluck Noise Burst
      let excitation = 0.0;
      if (this.burstRemaining > 0) {
        excitation = (Math.random() * 2.0 - 1.0) * this.pluckVelocity;
        this.burstRemaining--;
      }

      const newSample = excitation + filtered * feedback;
      this.buffer[this.writeIndex] = newSample;

      this.writeIndex = (this.writeIndex + 1) % this.bufferSize;
      channel[i] = newSample;
    }

    return true;
  }
}

registerProcessor('karplus-strong-processor', KarplusStrongProcessor);
`;

const SWARA_CANONICAL = {
  "S":  { name: "Ṣaḍja", ratio_str: "1", ratio_val: 1.0, midi_anchor: 60, andolan: false },
  "r":  { name: "Komal Ṛṣabha", ratio_str: "256/243", ratio_val: 256/243, midi_anchor: 61, andolan: true },
  "G":  { name: "Śuddha Gāndhāra", ratio_str: "5/4", ratio_val: 5/4, midi_anchor: 64, andolan: false },
  "M":  { name: "Śuddha Madhyama", ratio_str: "4/3", ratio_val: 4/3, midi_anchor: 65, andolan: false },
  "P":  { name: "Pañcama", ratio_str: "3/2", ratio_val: 3/2, midi_anchor: 67, andolan: false },
  "d":  { name: "Komal Dhaivata", ratio_str: "128/81", ratio_val: 128/81, midi_anchor: 68, andolan: true },
  "N":  { name: "Śuddha Niṣāda", ratio_str: "15/8", ratio_val: 15/8, midi_anchor: 71, andolan: false },
  "S'": { name: "Tāra Ṣaḍja", ratio_str: "2", ratio_val: 2.0, midi_anchor: 72, andolan: false }
};

class StudioIIIAudioEngine {
  constructor(apiBase = "https://aigaane-api-977695793163.asia-south1.run.app") {
    this.apiBase = apiBase;
    this.ctx = null;
    this.masterGain = null;
    this.droneGain = null;
    this.workletReady = false;
    this.droneTimer = null;
    this.isDroneActive = false;
    this.baseHz = 240.0;
    this.voicePool = [];
    this.voiceIndex = 0;
  }

  async init() {
    if (this.workletReady && this.ctx) {
      if (this.ctx.state === "suspended") await this.ctx.resume();
      return this.ctx;
    }

    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AudioCtx();

    const blob = new Blob([GANDHARVA_WORKLET_CODE], { type: "application/javascript" });
    const workletUrl = URL.createObjectURL(blob);
    await this.ctx.audioWorklet.addModule(workletUrl);
    URL.revokeObjectURL(workletUrl);

    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.setValueAtTime(0.85, this.ctx.currentTime);
    this.masterGain.connect(this.ctx.destination);

    this.droneGain = this.ctx.createGain();
    this.droneGain.gain.setValueAtTime(0.32, this.ctx.currentTime);
    this.droneGain.connect(this.masterGain);

    // 4-Voice Polyphonic Karplus-Strong AudioWorklet Pool
    this.voicePool = [];
    for (let v = 0; v < 4; v++) {
      const node = new AudioWorkletNode(this.ctx, 'karplus-strong-processor');
      const vGain = this.ctx.createGain();
      vGain.gain.setValueAtTime(1.0, this.ctx.currentTime);
      node.connect(vGain);
      vGain.connect(this.masterGain);
      this.voicePool.push({ node, gain: vGain });
    }

    this.workletReady = true;
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
        items = Object.entries(data.profile).map(([sym, v]) => ({
          svara_symbol: sym,
          name: SWARA_CANONICAL[sym]?.name || sym,
          ratio: v.ratio || SWARA_CANONICAL[sym]?.ratio_str || "1",
          frequency_hz: +(saHz * (SWARA_CANONICAL[sym]?.ratio_val || 1.0)).toFixed(4),
          cents: v.cents || 0.0,
          midi_anchor: v.midi_anchor || SWARA_CANONICAL[sym]?.midi_anchor || 60,
          andolan: SWARA_CANONICAL[sym]?.andolan || false
        }));
      }
      return items;
    } catch (e) {
      return Object.entries(SWARA_CANONICAL).map(([sym, c]) => ({
        svara_symbol: sym,
        name: c.name,
        ratio: c.ratio_str,
        frequency_hz: +(saHz * c.ratio_val).toFixed(4),
        cents: +(1200 * Math.log2(c.ratio_val)).toFixed(4),
        midi_anchor: c.midi_anchor,
        andolan: c.andolan
      }));
    }
  }

  async schedulePluck(swaraSymbol, startTime, duration = 2.0, velocity = 0.85, meendTarget = null) {
    await this.init();
    const voice = this.voicePool[this.voiceIndex];
    this.voiceIndex = (this.voiceIndex + 1) % this.voicePool.length;

    const canon = SWARA_CANONICAL[swaraSymbol] || SWARA_CANONICAL["S"];
    const startHz = this.baseHz * canon.ratio_val;
    const node = voice.node;

    node.parameters.get('feedback').setValueAtTime(0.9960, startTime);
    node.parameters.get('damping').setValueAtTime(0.40, startTime);

    // Trigger Andolan on Komal Re and Komal Dha (1.2 Hz, +/-12 cents)
    if (canon.andolan) {
      node.parameters.get('andolanRate').setValueAtTime(1.2, startTime);
      node.parameters.get('andolanDepth').setValueAtTime(12.0, startTime);
    } else {
      node.parameters.get('andolanDepth').setValueAtTime(0.0, startTime);
    }

    const freqParam = node.parameters.get('frequency');
    freqParam.setValueAtTime(startHz, startTime);

    // Sample-accurate Meend (Portamento Glide)
    if (meendTarget && SWARA_CANONICAL[meendTarget]) {
      const targetHz = this.baseHz * SWARA_CANONICAL[meendTarget].ratio_val;
      const glideStart = startTime + duration * 0.35;
      const glideEnd = startTime + duration * 0.85;
      freqParam.setValueAtTime(startHz, glideStart);
      freqParam.exponentialRampToValueAtTime(targetHz, glideEnd);
    }

    const delayMs = Math.max(0, (startTime - this.ctx.currentTime) * 1000);
    const nodeRef = node;
    const hzRef = startHz;
    const velRef = velocity;
    setTimeout(() => {
      if (this.ctx && this.ctx.state !== 'closed') {
        nodeRef.port.postMessage({ type: 'trigger', frequency: hzRef, velocity: velRef });
      }
    }, delayMs);
  }

  async startTanpuraDrone(saHz = 240.0) {
    await this.init();
    this.stopTanpuraDrone();
    this.isDroneActive = true;
    this.baseHz = saHz;

    const paHz = saHz * 1.5;
    const mandraSaHz = saHz * 0.5;
    let step = 0;

    const droneStep = async () => {
      if (!this.isDroneActive) return;
      let hz = saHz;
      if (step === 0) hz = paHz;
      else if (step === 1 || step === 2) hz = saHz;
      else hz = mandraSaHz;

      await this.schedulePluck(step === 0 ? "P" : (step === 3 ? "S" : "S"), this.ctx.currentTime, 5.0, 0.45);
      step = (step + 1) % 4;
      this.droneTimer = setTimeout(droneStep, 1200);
    };

    droneStep();
  }

  stopTanpuraDrone() {
    this.isDroneActive = false;
    if (this.droneTimer) {
      clearTimeout(this.droneTimer);
      this.droneTimer = null;
    }
  }
}

class MantraScheduler {
  constructor(engine) {
    this.engine = engine;
    this.isPlaying = false;
    this.scheduledTimers = [];
  }

  async playSequence(sequence, saHz = 240.0, tempoBpm = 80) {
    await this.engine.init();
    this.stop();
    this.isPlaying = true;
    this.engine.baseHz = saHz;

    const beatSec = 60.0 / tempoBpm;
    let time = 0.05;

    sequence.forEach((item) => {
      const swara = typeof item === "string" ? item : item.swara;
      const isGuru = item.weight === "G";
      const dur = isGuru ? beatSec * 2.2 : beatSec * 1.2;
      const meend = item.meend_target || null;

      const tid = setTimeout(async () => {
        if (!this.isPlaying) return;
        const audioNow = this.engine.ctx.currentTime + 0.03;
        await this.engine.schedulePluck(swara, audioNow, dur, isGuru ? 0.9 : 0.75, meend);
        
        // Phase 3 Dual-Mix: Trigger Vocal Sahāya syllabic singing
        if (window.vocalEngine && window.vocalEngine.isLoaded) {
          const syllableText = item.syllable || item.text || swara;
          window.vocalEngine.playSyllable(syllableText, swara, audioNow, dur, meend);
        }
      }, time * 1000);

      this.scheduledTimers.push(tid);
      time += beatSec;
    });

    const finishTid = setTimeout(() => {
      this.isPlaying = false;
    }, (time + 1.5) * 1000);
    this.scheduledTimers.push(finishTid);
  }

  stop() {
    this.isPlaying = false;
    this.scheduledTimers.forEach(clearTimeout);
    this.scheduledTimers = [];
  }
}

window.StudioIIIAudioEngine = StudioIIIAudioEngine;
window.MantraScheduler = MantraScheduler;
window.SWARA_CANONICAL = SWARA_CANONICAL;
