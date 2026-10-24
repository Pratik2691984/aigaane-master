/**
 * studio.js - Comprehensive Vedic Archaeoacoustics Engine
 * Production Ready - Pure Client-side Integration
 */

const PLANCK_CONSTANT = 6.62607015e-34;

const VEDIC_BIO_BUS = {
  "0000": { chakra: "Sahasrāra", plexus: "Cerebral Cortex", bija: "OM", vak: "Parā Vāk", canonical_hz: 261.63, state: "0000", marma_gates: ["Adhipati", "Simanta"], instClass: "susira" },
  "0001": { chakra: "Ājñā", plexus: "Epithalamus", bija: "OM", vak: "Paśyantī Vāk", canonical_hz: 246.94, state: "0001", marma_gates: ["Āvarta", "Sthapanī"], instClass: "ghana" },
  "0010": { chakra: "Viśuddha", plexus: "Laryngeal", bija: "HAM", vak: "Madhyamā Vāk", canonical_hz: 220.00, state: "0010", marma_gates: ["Nīlā", "Manyā"], instClass: "susira" },
  "0100": { chakra: "Anāhata", plexus: "Cardiac", bija: "YAM", vak: "Vaikharī Vāk", canonical_hz: 130.81, state: "0100", marma_gates: ["Hṛdaya", "Stanamūla"], instClass: "tata" },
  "1000": { chakra: "Maṇipūra", plexus: "Coeliac", bija: "RAM", vak: "Vaikharī Vāk", canonical_hz: 98.00, state: "1000", marma_gates: ["Nābhi"], instClass: "avanaddha" },
  "1010": { chakra: "Svādhiṣṭhāna", plexus: "Sacral", bija: "VAM", vak: "Vaikharī Vāk", canonical_hz: 73.42, state: "1010", marma_gates: ["Vitapa", "Lohitākṣa"], instClass: "ghana" },
  "1100": { chakra: "Mūlādhāra", plexus: "Coccygeal", bija: "LAM", vak: "Vaikharī Vāk", canonical_hz: 42.00, state: "1100", marma_gates: ["Guda", "Kukundara"], instClass: "avanaddha" }
};

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
      if (!AudioCtx) {
        console.warn("Web Audio API is not supported in this browser environment.");
        return;
      }
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
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume().catch(() => {});
    }
  }

  toggleMute(btn) {
    this.init();
    if (!this.masterGain || !this.ctx) return;
    this.isMuted = !this.isMuted;
    this.masterGain.gain.setValueAtTime(this.isMuted ? 0 : 0.35, this.ctx.currentTime);
    if (btn) {
      btn.textContent = this.isMuted ? "🔇 Sound: MUTED" : "🔊 Sound: ON";
      btn.classList.toggle("active", this.isMuted);
    }
  }

  toggleTanpura(btn) {
    this.init();
    if (!this.ctx) return;
    if (this.tanpuraNode) {
      try { this.tanpuraNode.stop(); } catch (e) {}
      this.tanpuraNode = null;
      if (btn) {
        btn.textContent = "🪕 Tanpura Drone: OFF";
        btn.classList.remove("active");
      }
      return;
    }
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(130.81, t);
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(450, t);
    gain.gain.setValueAtTime(0.12, t);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);
    osc.start(t);
    this.tanpuraNode = osc;
    if (btn) {
      btn.textContent = "🪕 Tanpura Drone: ACTIVE";
      btn.classList.add("active");
    }
  }

  playVoice(type, freq = 220, bija = null) {
    this.init();
    if (this.isMuted || !this.ctx) return;
    this.activeFreq = freq;
    const t = this.ctx.currentTime;
    if (window.quantaBrain) window.quantaBrain.evaluateAcousticQuanta(freq);

    if (type === "tata") {
      [1, 2, 3, 4, 5].forEach((m, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = i % 2 === 0 ? "sawtooth" : "triangle";
        osc.frequency.setValueAtTime(freq * m, t);
        gain.gain.setValueAtTime(0.22 / m, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + Math.max(0.1, 2.6 - i * 0.2));
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start(t);
        osc.stop(t + 2.6);
      });
    } else if (type === "avanaddha") {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq * 2.2, t);
      osc.frequency.exponentialRampToValueAtTime(Math.max(1, freq), t + 0.08);
      osc.frequency.linearRampToValueAtTime(25, t + 1.8);
      gain.gain.setValueAtTime(0.8, t);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.8);
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(t);
      osc.stop(t + 1.8);
    } else if (type === "susira") {
      const osc = this.ctx.createOscillator();
      const trem = this.ctx.createOscillator();
      const tremG = this.ctx.createGain();
      const gain = this.ctx.createGain();
      trem.frequency.setValueAtTime(5.5, t);
      tremG.gain.setValueAtTime(8, t);
      trem.connect(osc.frequency);
      osc.type = "sine";
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
    } else if (type === "ghana") {
      [freq, freq + 2.0].forEach(f => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sine";
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
    if (!this.ctx) return;
    const src = this.ctx.createOscillator();
    src.type = "sawtooth";
    src.frequency.setValueAtTime(baseFreq, time);
    const f1 = this.ctx.createBiquadFilter();
    const f2 = this.ctx.createBiquadFilter();
    f1.type = "bandpass";
    f2.type = "bandpass";
    const presets = {
      "LAM": [400, 800], "VAM": [500, 1500], "RAM": [600, 1900],
      "YAM": [350, 2200], "HAM": [730, 1090], "OM": [450, 600]
    };
    const [p1, p2] = presets[syllable] || presets["OM"];
    f1.frequency.setValueAtTime(p1, time); f1.Q.setValueAtTime(8, time);
    f2.frequency.setValueAtTime(p2, time); f2.Q.setValueAtTime(10, time);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, time);
    g.gain.linearRampToValueAtTime(0.2, time + 0.05);
    g.gain.exponentialRampToValueAtTime(0.0001, time + 0.8);
    src.connect(f1); src.connect(f2);
    f1.connect(g); f2.connect(g);
    g.connect(this.masterGain);
    src.start(time); src.stop(time + 0.85);
  }

  startFFTVisualizer() {
    const canvas = document.getElementById("realtime-scope");
    if (!canvas || !this.analyser) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const draw = () => {
      requestAnimationFrame(draw);
      this.analyser.getByteFrequencyData(dataArray);
      ctx.fillStyle = "#0a0c10";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      const barWidth = (canvas.width / bufferLength) * 1.5;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;
        ctx.fillStyle = "#ffb74d";
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    };
    draw();
  }

  startDualChannelVisualizer() {
    const canvas = document.getElementById("ida-pingala-canvas");
    if (!canvas) return;
    canvas.width = canvas.offsetWidth || 460;
    canvas.height = canvas.offsetHeight || 200;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const render = () => {
      requestAnimationFrame(render);
      ctx.fillStyle = "#05070a";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      const w = canvas.width;
      const h = canvas.height;
      const mid = h / 2;
      ctx.strokeStyle = "#1b2333"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, mid); ctx.lineTo(w, mid); ctx.stroke();
      const speed = Math.max(0.02, Math.min(0.12, (this.activeFreq / 600) * 0.08));
      this.phaseIda += speed; this.phasePingala += speed;
      ctx.strokeStyle = "#00f3ff"; ctx.lineWidth = 2;
      ctx.beginPath();
      for (let x = 0; x < w; x++) {
        const y = mid + Math.sin(x * 0.025 + this.phaseIda) * 35;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.strokeStyle = "#ff3b00"; ctx.lineWidth = 2;
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

class QuantaBrainEngine {
  constructor(audioEngine) {
    this.audio = audioEngine;
    this.currentQuanta = 99.00;
    this.activeWave = { band: "ALPHA (α)", color: "#38bdf8", stateDesc: "Sāttvic Stillness", frequencyDelta: 10.0 };
    this.eegCanvas = null;
    this.eegCtx = null;
    this.wavePhase = 0;
  }

  evaluateAcousticQuanta(freq) {
    const energyJoules = PLANCK_CONSTANT * freq;
    const quantaIndex = Math.min(99.9, (freq / 432) * 99).toFixed(2);
    let eegState = { band: "ALPHA (α)", color: "#38bdf8", stateDesc: "Harmonized Sensory Equilibrium", frequencyDelta: 10.0 };
    if (freq < 60) eegState = { band: "DELTA (δ)", color: "#ef4444", stateDesc: "Subconscious Grounding", frequencyDelta: 2.5 };
    else if (freq < 140) eegState = { band: "THETA (θ)", color: "#a855f7", stateDesc: "Dhyāna Meditation", frequencyDelta: 6.0 };
    else if (freq < 300) eegState = { band: "ALPHA (α)", color: "#38bdf8", stateDesc: "Sāttvic Stillness", frequencyDelta: 10.0 };
    else if (freq < 900) eegState = { band: "BETA (β)", color: "#eab308", stateDesc: "Cognitive Focus", frequencyDelta: 18.0 };
    else eegState = { band: "GAMMA (γ)", color: "#4ade80", stateDesc: "Prāṇic Surge", frequencyDelta: 40.0 };
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
    if (eegEl) { eegEl.textContent = eegState.band; eegEl.style.color = eegState.color; }
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
    ctx.strokeStyle = "#161b26"; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, mid); ctx.lineTo(w, mid); ctx.stroke();
    const delta = this.activeWave.frequencyDelta;
    const color = this.activeWave.color;
    this.wavePhase += delta * 0.015;
    ctx.strokeStyle = color; ctx.lineWidth = 2;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const noise = Math.sin(x * 0.1 + this.wavePhase * 2) * 2.5;
      const y = mid + Math.sin(x * 0.04 + this.wavePhase) * (h * 0.32) + noise;
      if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

const audioEngine = new VedicAudioEngine();
window.audioEngine = audioEngine;
const quantaBrain = new QuantaBrainEngine(audioEngine);
window.quantaBrain = quantaBrain;
let allInstruments = [];
let activeClass = "all";

document.addEventListener("DOMContentLoaded", () => {
  const muteBtn = document.getElementById("mute-btn");
  if (muteBtn) muteBtn.onclick = (e) => audioEngine.toggleMute(e.target);
  const tanpuraBtn = document.getElementById("tanpura-btn");
  if (tanpuraBtn) tanpuraBtn.onclick = (e) => audioEngine.toggleTanpura(e.target);
  const modalCloseBtn = document.getElementById("modal-close-btn");
  if (modalCloseBtn) modalCloseBtn.onclick = () => {
    const mb = document.getElementById("modal-backdrop");
    if (mb) mb.classList.remove("open");
  };
  quantaBrain.initCanvas("eeg-canvas");
  quantaBrain.evaluateAcousticQuanta(130.81);

  fetch("data/instruments.json")
    .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
    .then((data) => {
      allInstruments = Array.isArray(data) ? data : data.instruments || [];
      if (allInstruments.length === 0) throw new Error("Empty JSON");
      console.log("✅ Loaded Instruments from JSON:", allInstruments.length);
      updateCounts(); renderGrid(); bindEvents(); injectGatraVinaSVG("gatra-vina-mount");
    })
    .catch((err) => {
      console.warn("⚠️ Using fallback dataset:", err);
      allInstruments = window.INSTRUMENTS_FALLBACK || [];
      updateCounts(); renderGrid(); bindEvents(); injectGatraVinaSVG("gatra-vina-mount");
    });
});

function updateCounts() {
  const countEl = document.getElementById("count-all");
  if (countEl) countEl.textContent = allInstruments.length;
  ["tata", "avanaddha", "susira", "ghana"].forEach((c) => {
    const el = document.getElementById(`count-${c}`);
    if (el) el.textContent = allInstruments.filter((i) => i.classification === c).length;
  });
}

function renderGrid() {
  const container = document.getElementById("instruments-grid");
  if (!container) return;
  const searchInput = document.getElementById("search-input");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
  const sortSelect = document.getElementById("sort-select");
  const sortMode = sortSelect ? sortSelect.value : "rank";

  const fallbackInstruments = [
    { id: "rudra-veena", rank: 1, name: "Rudra Vīṇā", name_iast: "Rudra Vīṇā", name_devanagari: "रुद्रवीणा", classification: "tata", organology: "Tubular stick zither with dual spherical calabash resonators", primary_attestation: "Nāṭya Śāstra 28.14", score: 99.4, description_short: "Colossal dual-gourd stick zither consecrated to Lord Shiva.", acoustics: { formula_latex: "f_n = (nv/2L)(1 + ε_j + π²Bn²/8L²)", fundamental_hz: 130.81, damping_ratio: 0.08 }, liturgical_context: { spatial_placement: "Brahmā-sthāna", actuator: "Wire mezrāb", bio_membrane: "Calabash & teak" } },
    { id: "bhumi-dundubhi", rank: 18, name: "Bhūmi-dundubhi", name_iast: "Bhūmi-dundubhi", name_devanagari: "भूमिदुन्दुभि", classification: "avanaddha", organology: "Earth-pit drum with pegged bovine hide", primary_attestation: "Śatapatha Brāhmaṇa", score: 96.8, description_short: "An earth-pit resonator covered with staked bull hide.", acoustics: { formula_latex: "f ≈ c_s / (4(d + 0.4D))", fundamental_hz: 42.0, damping_ratio: 0.45 }, liturgical_context: { spatial_placement: "West-Northwest perimeter", actuator: "Ox-tail switch", bio_membrane: "Untanned bovine hide" } },
    { id: "venu", rank: 30, name: "Veṇu / Vaṃśa", name_iast: "Veṇu / Bānsurī", name_devanagari: "वेणु / बांसुरी", classification: "susira", organology: "Transverse bamboo flute with fire-pierced embouchure", primary_attestation: "Ṛgveda 8.69.9", score: 99.3, description_short: "Lord Krishna's sacred flute.", acoustics: { formula_latex: "f_n = nc / 2(L + 1.2r)", fundamental_hz: 349.23, damping_ratio: 0.03 }, liturgical_context: { spatial_placement: "North of altar", actuator: "Planar lip air-stream", bio_membrane: "Cured bamboo" } },
    { id: "ghanta", rank: 42, name: "Ghaṇṭā", name_iast: "Ghaṇṭā", name_devanagari: "घण्टा", classification: "ghana", organology: "Panchaloha bell with Garuda clapper", primary_attestation: "Yajurveda Taittirīya", score: 98.8, description_short: "The voice of all deities.", acoustics: { formula_latex: "f_{m,n} = (h/2πR²)√(E/12ρ(1-ν²))λ_{m,n}", fundamental_hz: 523.25, damping_ratio: 0.002 }, liturgical_context: { spatial_placement: "Priest's left hand", actuator: "Bronze clapper", bio_membrane: "Panchaloha alloy" } }
  ];

  const sourceData = allInstruments && allInstruments.length > 0 ? allInstruments : fallbackInstruments;
  let list = sourceData.filter((i) => {
    const matchesClass = activeClass === "all" || i.classification === activeClass;
    const matchesSearch = !query ||
      (i.name && i.name.toLowerCase().includes(query)) ||
      (i.name_iast && i.name_iast.toLowerCase().includes(query)) ||
      (i.name_devanagari && i.name_devanagari.includes(query));
    return matchesClass && matchesSearch;
  });

  if (sortMode === "score") list.sort((a, b) => (b.score || 0) - (a.score || 0));
  else if (sortMode === "alpha") list.sort((a, b) => (a.name_iast || "").localeCompare(b.name_iast || ""));
  else list.sort((a, b) => (a.rank || 99) - (b.rank || 99));

  container.innerHTML = list.map((inst) => `
    <div class="inst-card" onclick="openDetails('${inst.id}')">
      <div>
        <div class="card-top">
          <span>#${String(inst.rank || "?").padStart(2, "0")}</span>
          <span class="badge ${inst.classification || ""}">${inst.classification || ""}</span>
          <span>Score: ${inst.score || "?"}</span>
        </div>
        <div class="card-title">
          <span class="devanagari">${inst.name_devanagari || ""}</span>
          <h3>${inst.name_iast || inst.name}</h3>
        </div>
        <p class="organology-sub">${inst.organology || ""}</p>
        <div class="formula-preview">${inst.acoustics?.formula_latex || "f_n = (n·v) / 2L"}</div>
        <p class="card-desc">${inst.description_short || ""}</p>
      </div>
      <div class="card-footer">
        <span style="font-size:0.75rem; color:#94a3b8;">${inst.acoustics?.fundamental_hz || 220} Hz</span>
        <button class="excite-card-btn" onclick="event.stopPropagation(); audioEngine.playVoice('${inst.classification}', ${inst.acoustics?.fundamental_hz || 220})">🔊 Excite Model</button>
      </div>
    </div>
  `).join("");
}

function bindEvents() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.onclick = () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeClass = btn.dataset.class;
      const bioView = document.getElementById("bio-laboratory");
      const gridView = document.getElementById("instruments-grid");
      if (activeClass === "bio") {
        if (gridView) gridView.style.display = "none";
        if (bioView) bioView.style.display = "block";
      } else {
        if (bioView) bioView.style.display = "none";
        if (gridView) gridView.style.display = "grid";
        renderGrid();
      }
    };
  });
  const searchInput = document.getElementById("search-input");
  if (searchInput) searchInput.oninput = renderGrid;
  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) sortSelect.onchange = renderGrid;
}

function injectGatraVinaSVG(containerId) {
  const mount = document.getElementById(containerId);
  if (!mount) return;
  mount.innerHTML = `
    <svg viewBox="0 0 400 780" style="width:100%; height:100%;">
      <defs>
        <linearGradient id="central-axis" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#00f3ff"/>
          <stop offset="50%" stop-color="#ff00ff"/>
          <stop offset="100%" stop-color="#ff3b00"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
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
    </svg>`;
  mount.querySelectorAll(".node-gate").forEach((el) => {
    el.style.cursor = "pointer";
    el.addEventListener("click", () => triggerBioBus(el.getAttribute("data-address")));
  });
}

function renderSVGNode(addr, x, y, col, label) {
  return `<g class="node-gate" data-address="${addr}" transform="translate(${x}, ${y})" cursor="pointer">
    <circle r="16" fill="#11151d" stroke="${col}" stroke-width="2"/>
    <circle class="core" r="6" fill="${col}"/>
    <text x="24" y="4" fill="${col}" font-size="11" font-family="monospace">${label}</text>
  </g>`;
}

function triggerBioBus(address) {
  const node = VEDIC_BIO_BUS[address];
  if (!node) return;
  audioEngine.playVoice(node.instClass, node.canonical_hz, node.bija);
  document.querySelectorAll(".node-gate").forEach((el) => {
    const core = el.querySelector(".core");
    if (!core) return;
    if (el.getAttribute("data-address") === address) {
      core.setAttribute("filter", "url(#glow)");
      core.setAttribute("r", "9");
    } else {
      core.removeAttribute("filter");
      core.setAttribute("r", "6");
    }
  });
  const busEl = document.getElementById("tele-bus");
  const marmaEl = document.getElementById("tele-marma");
  const bijaEl = document.getElementById("tele-bija");
  const hzEl = document.getElementById("tele-hz");
  const vakEl = document.getElementById("tele-vak");
  if (busEl) busEl.textContent = `ACTIVE [${node.state}]`;
  if (marmaEl) marmaEl.textContent = node.marma_gates.join(" | ");
  if (bijaEl) bijaEl.textContent = node.bija;
  if (hzEl) hzEl.textContent = `${node.canonical_hz} Hz`;
  if (vakEl) vakEl.textContent = node.vak;
}

function openDetails(id) {
  const inst = allInstruments.find((i) => i.id === id) || {
    id: "rudra-veena", name: "Rudra Vīṇā", name_iast: "Rudra Vīṇā", name_devanagari: "रुद्रवीणा",
    classification: "tata", organology: "Tubular stick zither",
    primary_attestation: "Nāṭya Śāstra 28.14",
    acoustics: { formula_latex: "f_n = (nv/2L)", fundamental_hz: 130.81 }
  };
  const fundHz = inst.acoustics?.fundamental_hz || 130.81;
  const ratios = [
    { s: "Sa", d: "सा", r: 1.0 }, { s: "Re", d: "रे", r: 9 / 8 },
    { s: "Ga", d: "ग", r: 5 / 4 }, { s: "Ma", d: "म", r: 4 / 3 },
    { s: "Pa", d: "प", r: 3 / 2 }, { s: "Dha", d: "ध", r: 5 / 3 },
    { s: "Ni", d: "नि", r: 15 / 8 }, { s: "Ṡa", d: "सां", r: 2.0 }
  ];
  const modalContent = document.getElementById("modal-content");
  if (!modalContent) return;
  modalContent.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-card); padding-bottom: 1rem;">
      <span class="badge ${inst.classification || ""}">${(inst.classification || "TATA").toUpperCase()}</span>
      <h2 style="color:#fff; margin-top:0.4rem;">${inst.name_iast || inst.name} (${inst.name_devanagari || ""})</h2>
      <p style="color:var(--text-sub); font-size:0.9rem;">${inst.organology || ""}</p>
    </div>
    <div style="margin: 1rem 0;">
      <h4 style="font-size:0.85rem; color:var(--accent-gold); text-transform:uppercase;">Interactive Swara Scale</h4>
      <div class="swara-row">
        ${ratios.map((x) => `<button class="swara-btn" onclick="audioEngine.playVoice('${inst.classification}', ${fundHz * x.r})">
          <span>${x.d}</span>
          <span style="font-size:0.75rem;">${x.s}</span>
          <span class="swara-hz">${Math.round(fundHz * x.r)}Hz</span>
        </button>`).join("")}
      </div>
    </div>
    <div class="research-subgrid">
      <div class="subcard">
        <h4>🔬 Governing Physics</h4>
        <ul>
          <li><strong>Equation:</strong> <code>${inst.acoustics?.formula_latex || "N/A"}</code></li>
          <li><strong>Pitch:</strong> ${fundHz} Hz</li>
        </ul>
      </div>
      <div class="subcard">
        <h4>📜 Ritual Context</h4>
        <ul>
          <li><strong>Attestation:</strong> ${inst.primary_attestation || "N/A"}</li>
          <li><strong>Placement:</strong> ${inst.liturgical_context?.spatial_placement || "N/A"}</li>
        </ul>
      </div>
    </div>`;
  const modalBackdrop = document.getElementById("modal-backdrop");
  if (modalBackdrop) modalBackdrop.classList.add("open");
}