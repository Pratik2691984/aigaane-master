/**
 * studio.js - Comprehensive Vedic Archaeoacoustics Engine
 * Implements class-based physical synthesis, Quantum Spanda calculations, 
 * real-time EEG brainwave entrainment, and Gātra-Vīṇā bus routing.
 */

const PLANCK_CONSTANT = 6.62607015e-34; // J·s

// 1. Complete Bio-Bus 7-Node Register
const VEDIC_BIO_BUS = {
  "0000": {
    chakra: "Sahasrāra",
    plexus: "Cerebral Cortex",
    bija: "OM",
    vak: "Parā Vāk (Unmanifest)",
    canonical_hz: 261.63,
    state: "0000",
    marma_gates: ["Adhipati", "Simanta"],
    instClass: "susira"
  },
  "0001": {
    chakra: "Ājñā",
    plexus: "Epithalamus / Optic Chiasm",
    bija: "OM",
    vak: "Paśyantī Vāk (Ideational)",
    canonical_hz: 246.94,
    state: "0001",
    marma_gates: ["Āvarta", "Sthapanī"],
    instClass: "ghana"
  },
  "0010": {
    chakra: "Viśuddha",
    plexus: "Laryngeal Pharynx",
    bija: "HAM",
    vak: "Madhyamā Vāk (Intermediate)",
    canonical_hz: 220.00,
    state: "0010",
    marma_gates: ["Nīlā", "Manyā"],
    instClass: "susira"
  },
  "0100": {
    chakra: "Anāhata",
    plexus: "Cardiac Ganglion",
    bija: "YAM",
    vak: "Vaikharī Vāk (Articulated)",
    canonical_hz: 130.81,
    state: "0100",
    marma_gates: ["Hṛdaya", "Stanamūla"],
    instClass: "tata"
  },
  "1000": {
    chakra: "Maṇipūra",
    plexus: "Coeliac Plexus",
    bija: "RAM",
    vak: "Vaikharī Vāk (Thermal)",
    canonical_hz: 98.00,
    state: "1000",
    marma_gates: ["Nābhi"],
    instClass: "avanaddha"
  },
  "1010": {
    chakra: "Svādhiṣṭhāna",
    plexus: "Sacral Plexus",
    bija: "VAM",
    vak: "Vaikharī Vāk (Fluid)",
    canonical_hz: 73.42,
    state: "1010",
    marma_gates: ["Vitapa", "Lohitākṣa"],
    instClass: "ghana"
  },
  "1100": {
    chakra: "Mūlādhāra",
    plexus: "Coccygeal Plexus",
    bija: "LAM",
    vak: "Vaikharī Vāk (Telluric)",
    canonical_hz: 42.00,
    state: "1100",
    marma_gates: ["Guda", "Kukundara"],
    instClass: "avanaddha"
  }
};

// 2. High-Performance Procedural Web Audio Engine
class VedicAudioEngine {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.analyser = null;
    this.tanpuraNode = null;
    this.isMuted = false;
    this.activeFreq = 130.81;
    this.phaseIda = 0;
    this.phasePingala = 0;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.35, this.ctx.currentTime);

      this.analyser = this.ctx.createAnalyser();
      this.analyser.fftSize = 256;
      this.masterGain.connect(this.analyser);
      this.analyser.connect(this.ctx.destination);

      this.startFFTVisualizer();
      this.startDualChannelVisualizer();
    }
    if (this.ctx.state === 'suspended') this.ctx.resume();
  }

  toggleMute(btn) {
    this.init();
    this.isMuted = !this.isMuted;
    this.masterGain.gain.setValueAtTime(this.isMuted ? 0.0 : 0.35, this.ctx.currentTime);
    btn.textContent = this.isMuted ? '🔇 Sound: MUTED' : '🔊 Sound: ON';
    btn.classList.toggle('active', this.isMuted);
  }

  toggleTanpura(btn) {
    this.init();
    if (this.tanpuraNode) {
      this.tanpuraNode.stop();
      this.tanpuraNode = null;
      btn.textContent = '🪕 Tanpura Drone: OFF';
      btn.classList.remove('active');
      return;
    }

    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(130.81, t);

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(450, t);

    gain.gain.setValueAtTime(0.12, t);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    osc.start(t);
    this.tanpuraNode = osc;
    btn.textContent = '🪕 Tanpura Drone: ACTIVE';
    btn.classList.add('active');
  }

  playVoice(type, freq = 220, bija = null) {
    this.init();
    if (this.isMuted) return;
    this.activeFreq = freq;
    const t = this.ctx.currentTime;

    // Trigger Quantum Brain Evaluation
    if (window.quantaBrain) {
      window.quantaBrain.evaluateAcousticQuanta(freq);
    }

    if (type === 'tata') {
      [1, 2, 3, 4, 5].forEach((m, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = i % 2 === 0 ? 'sawtooth' : 'triangle';
        osc.frequency.setValueAtTime(freq * m, t);
        gain.gain.setValueAtTime(0.22 / m, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 2.6 - (i * 0.2));
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 2.6);
      });
    } else if (type === 'avanaddha') {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq * 2.2, t);
      osc.frequency.exponentialRampToValueAtTime(freq, t + 0.08);
      osc.frequency.linearRampToValueAtTime(25, t + 1.8);
      gain.gain.setValueAtTime(0.8, t);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.8);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(t);
      osc.stop(t + 1.8);
    } else if (type === 'susira') {
      const osc = this.ctx.createOscillator();
      const trem = this.ctx.createOscillator();
      const tremG = this.ctx.createGain();
      const gain = this.ctx.createGain();
      trem.frequency.setValueAtTime(5.5, t);
      tremG.gain.setValueAtTime(8, t);
      trem.connect(osc.frequency);
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, t);
      gain.gain.setValueAtTime(0.01, t);
      gain.gain.linearRampToValueAtTime(0.35, t + 0.12);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 2.0);
      trem.start(t);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(t);
      osc.stop(t + 2.0);
      trem.stop(t + 2.0);
    } else if (type === 'ghana') {
      [freq, freq + 2.0].forEach(f => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, t);
        gain.gain.setValueAtTime(0.3, t);
        gain.gain.exponentialRampToValueAtTime(0.00001, t + 3.2);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 3.2);
      });
    }

    if (bija) this.injectBijaFormants(freq, bija, t);
  }

  injectBijaFormants(baseFreq, syllable, time) {
    const src = this.ctx.createOscillator();
    src.type = 'sawtooth';
    src.frequency.setValueAtTime(baseFreq, time);

    const f1 = this.ctx.createBiquadFilter();
    const f2 = this.ctx.createBiquadFilter();
    f1.type = 'bandpass';
    f2.type = 'bandpass';

    const presets = {
      "LAM": [400, 800],
      "VAM": [500, 1500],
      "RAM": [600, 1900],
      "YAM": [350, 2200],
      "HAM": [730, 1090],
      "OM":  [450, 600]
    };
    const [p1, p2] = presets[syllable] || presets["OM"];
    f1.frequency.setValueAtTime(p1, time); f1.Q.setValueAtTime(8, time);
    f2.frequency.setValueAtTime(p2, time); f2.Q.setValueAtTime(10, time);

    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0, time);
    g.gain.linearRampToValueAtTime(0.2, time + 0.05);
    g.gain.exponentialRampToValueAtTime(0.0001, time + 0.8);

    src.connect(f1); src.connect(f2);
    f1.connect(g);   f2.connect(g);
    g.connect(this.masterGain);

    src.start(time);
    src.stop(time + 0.85);
  }

  startFFTVisualizer() {
    const canvas = document.getElementById('realtime-scope');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      requestAnimationFrame(draw);
      this.analyser.getByteFrequencyData(dataArray);
      ctx.fillStyle = '#0a0c10';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 1.5;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;
        ctx.fillStyle = '#ffb74d';
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    };
    draw();
  }

  startDualChannelVisualizer() {
    const canvas = document.getElementById('ida-pingala-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const render = () => {
      requestAnimationFrame(render);
      ctx.fillStyle = '#05070a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const w = canvas.width;
      const h = canvas.height;
      const mid = h / 2;

      ctx.strokeStyle = '#1b2333';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, mid); ctx.lineTo(w, mid);
      ctx.stroke();

      const speed = Math.max(0.02, Math.min(0.12, (this.activeFreq / 600) * 0.08));
      this.phaseIda += speed;
      this.phasePingala += speed;

      // Iḍā Trace (Left / 0 / Moon / Cyan)
      ctx.strokeStyle = '#00f3ff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let x = 0; x < w; x++) {
        const y = mid + Math.sin(x * 0.025 + this.phaseIda) * 35;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Piṅgalā Trace (Right / 1 / Sun / Red-Orange)
      ctx.strokeStyle = '#ff3b00';
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let x = 0; x < w; x++) {
        const y = mid + Math.sin(x * 0.025 - this.phasePingala + Math.PI) * 35;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
    };
    render();
  }
}

// 3. Quanta & Brainwave Entrainment Engine
class QuantaBrainEngine {
  constructor(audioEngine) {
    this.audio = audioEngine;
    this.currentQuanta = 99.00;
    this.activeWave = {
      band: "ALPHA (α)",
      range: "8 – 13 Hz",
      color: "#38bdf8",
      stateDesc: "Sāttvic Stillness & Alert Serenity",
      frequencyDelta: 10.0
    };
    this.eegCanvas = null;
    this.eegCtx = null;
    this.wavePhase = 0;
  }

  evaluateAcousticQuanta(freq) {
    const energyJoules = PLANCK_CONSTANT * freq;
    const quantaIndex = Math.min(99.9, ((freq / 432) * 99)).toFixed(2);

    let eegState = {
      band: "ALPHA (α)",
      range: "8 – 13 Hz",
      color: "#38bdf8",
      stateDesc: "Harmonized Sensory Equilibrium & Neuro-Coherence",
      frequencyDelta: 10.0
    };

    if (freq < 60) {
      eegState = {
        band: "DELTA (δ)",
        range: "0.5 – 4 Hz",
        color: "#ef4444",
        stateDesc: "Subconscious Grounding & Deep Sleep Recovery",
        frequencyDelta: 2.5
      };
    } else if (freq < 140) {
      eegState = {
        band: "THETA (θ)",
        range: "4 – 8 Hz",
        color: "#a855f7",
        stateDesc: "Dhyāna Meditation, Intuition & Inner Vision",
        frequencyDelta: 6.0
      };
    } else if (freq < 300) {
      eegState = {
        band: "ALPHA (α)",
        range: "8 – 13 Hz",
        color: "#38bdf8",
        stateDesc: "Sāttvic Stillness, Clarity & Cognitive Equilibrium",
        frequencyDelta: 10.0
      };
    } else if (freq < 900) {
      eegState = {
        band: "BETA (β)",
        range: "13 – 30 Hz",
        color: "#eab308",
        stateDesc: "Active Rhythmic Processing & Cognitive Focus",
        frequencyDelta: 18.0
      };
    } else {
      eegState = {
        band: "GAMMA (γ)",
        range: "30 – 100 Hz",
        color: "#4ade80",
        stateDesc: "High-Frequency Prāṇic Surge & Lucid Perception",
        frequencyDelta: 40.0
      };
    }

    this.currentQuanta = quantaIndex;
    this.activeWave = eegState;
    this.updateHUD(energyJoules, quantaIndex, eegState);
  }

  updateHUD(energyJoules, quantaIndex, eegState) {
    const qEl = document.getElementById("hud-quanta-val");
    const eegEl = document.getElementById("hud-eeg-band");
    const stateEl = document.getElementById("hud-neuro-state");
    const energyEl = document.getElementById("hud-energy-metric");

    if (qEl) qEl.textContent = `Q-${quantaIndex}`;
    if (eegEl) {
      eegEl.textContent = eegState.band;
      eegEl.style.color = eegState.color;
    }
    if (stateEl) stateEl.textContent = eegState.stateDesc;
    if (energyEl) energyEl.textContent = `${energyJoules.toExponential(4)} J`;
  }

  initCanvas(canvasId) {
    this.eegCanvas = document.getElementById(canvasId);
    if (!this.eegCanvas) return;
    this.eegCtx = this.eegCanvas.getContext("2d");
    this.render();
  }

  render() {
    requestAnimationFrame(() => this.render());
    if (!this.eegCtx || !this.eegCanvas) return;

    const ctx = this.eegCtx;
    const w = this.eegCanvas.width;
    const h = this.eegCanvas.height;
    const mid = h / 2;

    ctx.fillStyle = "#07090e";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "#161b26";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, mid); ctx.lineTo(w, mid);
    ctx.stroke();

    const delta = this.activeWave.frequencyDelta;
    const color = this.activeWave.color;
    this.wavePhase += (delta * 0.015);

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const noise = (Math.sin(x * 0.1 + this.wavePhase * 2) * 2.5);
      const y = mid + Math.sin(x * 0.04 + this.wavePhase) * (h * 0.32) + noise;
      if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

// 4. Application Initialization
const audioEngine = new VedicAudioEngine();
window.audioEngine = audioEngine;

const quantaBrain = new QuantaBrainEngine(audioEngine);
window.quantaBrain = quantaBrain;

let allInstruments = [];
let activeClass = 'all';

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('mute-btn').onclick = (e) => audioEngine.toggleMute(e.target);
  document.getElementById('tanpura-btn').onclick = (e) => audioEngine.toggleTanpura(e.target);

  document.getElementById('modal-close-btn').onclick = () => {
    document.getElementById('modal-backdrop').classList.remove('open');
  };

  quantaBrain.initCanvas("eeg-canvas");
  quantaBrain.evaluateAcousticQuanta(130.81);

  fetch('data/instruments.json')
    .then(r => r.json())
    .then(data => {
      allInstruments = data.instruments;
      updateCounts();
      renderGrid();
      bindEvents();
      injectGatraVinaSVG('gatra-vina-mount');
    })
    .catch(err => console.error("Error loading instruments.json:", err));
});

function updateCounts() {
  document.getElementById('count-all').textContent = allInstruments.length;
  ['tata', 'avanaddha', 'susira', 'ghana'].forEach(c => {
    const el = document.getElementById(`count-${c}`);
    if (el) el.textContent = allInstruments.filter(i => i.classification === c).length;
  });
}

function renderGrid() {
  const container = document.getElementById('instruments-grid');
  const query = document.getElementById('search-input').value.toLowerCase();
  const sortMode = document.getElementById('sort-select').value;

  let list = allInstruments.filter(i => {
    const matchesClass = activeClass === 'all' || i.classification === activeClass;
    const matchesSearch = i.name.toLowerCase().includes(query) || 
                          i.name_iast.toLowerCase().includes(query) ||
                          i.name_devanagari.includes(query) ||
                          (i.primary_attestation && i.primary_attestation.toLowerCase().includes(query));
    return matchesClass && matchesSearch;
  });

  if (sortMode === 'score') list.sort((a,b) => b.score - a.score);
  else if (sortMode === 'alpha') list.sort((a,b) => a.name_iast.localeCompare(b.name_iast));
  else list.sort((a,b) => a.rank - b.rank);

  container.innerHTML = list.map(inst => `
    <div class="inst-card" onclick="openDetails('${inst.id}')">
      <div>
        <div class="card-top">
          <span>#${String(inst.rank).padStart(2, '0')}</span>
          <span class="badge ${inst.classification}">${inst.classification}</span>
          <span>Vedic: ${inst.score}</span>
        </div>
        <div class="card-title">
          <span class="devanagari">${inst.name_devanagari}</span>
          <h3>${inst.name_iast}</h3>
        </div>
        <p class="organology-sub">${inst.organology}</p>
        <div class="formula-preview">
          ${inst.acoustics?.formula_latex || 'f_n = (n·v) / 2L'}
        </div>
        <p class="card-desc">${inst.description_short}</p>
      </div>
      <div class="card-footer">
        <span style="font-size:0.75rem; color:#94a3b8;">${inst.acoustics?.fundamental_hz || 220} Hz</span>
        <button class="excite-card-btn" onclick="event.stopPropagation(); audioEngine.playVoice('${inst.classification}', ${inst.acoustics?.fundamental_hz || 220})">
          🔊 Excite Model
        </button>
      </div>
    </div>
  `).join('');
}

function bindEvents() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeClass = btn.dataset.class;

      const bioView = document.getElementById('bio-laboratory');
      const gridView = document.getElementById('instruments-grid');
      if (activeClass === 'bio') {
        gridView.style.display = 'none';
        bioView.style.display = 'block';
      } else {
        bioView.style.display = 'none';
        gridView.style.display = 'grid';
        renderGrid();
      }
    };
  });

  document.getElementById('search-input').oninput = renderGrid;
  document.getElementById('sort-select').onchange = renderGrid;
}

// 5. Bio-Bus SVG Generator & Dispatcher
function injectGatraVinaSVG(containerId) {
  const mount = document.getElementById(containerId);
  if (!mount) return;

  mount.innerHTML = `
    <svg id="gatra-vina-ui" viewBox="0 0 400 780" style="width:100%; height:100%;">
      <defs>
        <linearGradient id="central-axis" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#00f3ff"/>
          <stop offset="50%" stop-color="#ff00ff"/>
          <stop offset="100%" stop-color="#ff3b00"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
          <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      <line x1="200" y1="80" x2="200" y2="680" stroke="url(#central-axis)" stroke-width="4" opacity="0.6"/>
      <path d="M200,80 C120,180 120,280 200,380 C280,480 280,580 200,680" fill="none" stroke="#00f3ff" stroke-width="2" stroke-dasharray="4,4" opacity="0.4"/>
      <path d="M200,80 C280,180 280,280 200,380 C120,480 120,580 200,680" fill="none" stroke="#ff3b00" stroke-width="2" stroke-dasharray="4,4" opacity="0.4"/>

      ${renderSVGNode("0000", 200, 80,  "#ffffff", "0000 SAHASRĀRA")}
      ${renderSVGNode("0001", 200, 160, "#00f3ff", "0001 ĀJÑĀ")}
      ${renderSVGNode("0010", 200, 260, "#a855f7", "0010 VIŚUDDHA")}
      ${renderSVGNode("0100", 200, 370, "#22c55e", "0100 ANĀHATA")}
      ${renderSVGNode("1000", 200, 480, "#eab308", "1000 MAṆIPŪRA")}
      ${renderSVGNode("1010", 200, 580, "#f97316", "1010 SVĀDHIṢṬHĀNA")}
      ${renderSVGNode("1100", 200, 680, "#ef4444", "1100 MŪLĀDHĀRA")}
    </svg>
  `;

  mount.querySelectorAll('.node-gate').forEach(el => {
    el.addEventListener('click', () => {
      triggerBioBus(el.getAttribute('data-address'));
    });
  });
}

function renderSVGNode(addr, x, y, col, label) {
  return `
    <g class="node-gate" data-address="${addr}" transform="translate(${x}, ${y})" cursor="pointer">
      <circle r="16" fill="#11151d" stroke="${col}" stroke-width="2"/>
      <circle class="core" r="6" fill="${col}"/>
      <text x="24" y="4" fill="${col}" font-size="11" font-family="monospace">${label}</text>
    </g>
  `;
}

function triggerBioBus(address) {
  const node = VEDIC_BIO_BUS[address];
  if (!node) return;

  audioEngine.playVoice(node.instClass, node.canonical_hz, node.bija);

  document.querySelectorAll('.node-gate').forEach(el => {
    const core = el.querySelector('.core');
    if (el.getAttribute('data-address') === address) {
      core.setAttribute('filter', 'url(#glow)');
      core.setAttribute('r', '8');
    } else {
      core.removeAttribute('filter');
      core.setAttribute('r', '6');
    }
  });

  document.getElementById('tele-bus').textContent = `ACTIVE [${node.state}]`;
  document.getElementById('tele-marma').textContent = node.marma_gates.join(' | ');
  document.getElementById('tele-bija').textContent = node.bija;
  document.getElementById('tele-hz').textContent = `${node.canonical_hz} Hz`;
  document.getElementById('tele-vak').textContent = node.vak;
}

// 6. Accession Detail Drawer View
function openDetails(id) {
  const inst = allInstruments.find(i => i.id === id);
  if (!inst) return;

  const fundHz = inst.acoustics?.fundamental_hz || 220;
  const ratios = [
    { s: 'Sa', d: 'सा', r: 1.0 }, { s: 'Re', d: 'रे', r: 9/8 },
    { s: 'Ga', d: 'ग', r: 5/4 }, { s: 'Ma', d: 'म', r: 4/3 },
    { s: 'Pa', d: 'प', r: 3/2 }, { s: 'Dha', d: 'ध', r: 5/3 },
    { s: 'Ni', d: 'नि', r: 15/8 }, { s: 'Ṡa', d: 'सां', r: 2.0 }
  ];

  document.getElementById('modal-content').innerHTML = `
    <div style="border-bottom: 1px solid var(--border-card); padding-bottom: 1rem;">
      <span class="badge ${inst.classification}">${inst.classification.toUpperCase()}</span>
      <h2 style="color:#fff; margin-top:0.4rem;">${inst.name_iast} (${inst.name_devanagari})</h2>
      <p style="color:var(--text-sub); font-size:0.9rem;">${inst.organology}</p>
    </div>

    <div style="margin: 1rem 0;">
      <h4 style="font-size:0.85rem; color:var(--accent-gold); text-transform:uppercase;">Interactive Swara Scale Excitation</h4>
      <div class="swara-row">
        ${ratios.map(x => `
          <button class="swara-btn" onclick="audioEngine.playVoice('${inst.classification}', ${fundHz * x.r})">
            <span>${x.d}</span>
            <span style="font-size:0.75rem;">${x.s}</span>
            <span class="swara-hz">${Math.round(fundHz * x.r)}Hz</span>
          </button>
        `).join('')}
      </div>
    </div>

    <div class="binary-flow-box">
      <h4 style="font-size:0.85rem; color:var(--accent-teal); margin-bottom:0.5rem;">⚡ Binary Signal Flow Diagram</h4>
      <div class="flow-node">
        <span class="flow-badge">State 0 → 1</span>
        <div class="flow-meta"><h6>Mechanical Excitation</h6><p>Plectrum, breath impulse, or ox-tail striker imparts kinetic energy.</p></div>
      </div>
      <div class="flow-node">
        <span class="flow-badge">Boundary Matrix</span>
        <div class="flow-meta"><h6>Acoustic Filtering & Moding</h6><p>Jawārī curvature, subterranean cavity, or syāhi mass distribution.</p></div>
      </div>
      <div class="flow-node">
        <span class="flow-badge">Output Wave</span>
        <div class="flow-meta"><h6>Radiated Archaeoacoustic Field</h6><p>Sustained microtonal envelope or telluric shear wave propagation.</p></div>
      </div>
    </div>

    <div class="research-subgrid">
      <div class="subcard">
        <h4>🔬 Governing Physics</h4>
        <ul>
          <li><strong>Equation:</strong> <code>${inst.acoustics?.formula_latex || 'f_n = (nv) / 2L'}</code></li>
          <li><strong>Center Pitch:</strong> ${fundHz} Hz</li>
          <li><strong>Bandwidth:</strong> ${inst.acoustics?.frequency_band || 'Broadband'}</li>
          <li><strong>Damping (ζ):</strong> ${inst.acoustics?.damping_ratio || 0.1}</li>
        </ul>
      </div>
      <div class="subcard">
        <h4>📜 Sacrificial Archaeoacoustics</h4>
        <ul>
          <li><strong>Attestation:</strong> ${inst.primary_attestation}</li>
          <li><strong>Placement:</strong> ${inst.liturgical_context?.spatial_placement || 'Sacrificial Enclosure (Vedi)'}</li>
          <li><strong>Actuator:</strong> ${inst.liturgical_context?.actuator || 'Manual contact / Plectrum'}</li>
          <li><strong>Bio-Substrate:</strong> ${inst.liturgical_context?.bio_membrane || 'Seasoned wood / vegetative fiber'}</li>
        </ul>
      </div>
    </div>
  `;

  document.getElementById('modal-backdrop').classList.add('open');
}