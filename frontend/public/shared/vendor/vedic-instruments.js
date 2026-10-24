(function () {
  'use strict';

  const data = window.VEDIC_INSTRUMENTS || [];
  let activeCategory = 'all';
  let activeSort = 'rank';

  // ---------- Audio Engine (simplified Web Audio) ----------
  let audioCtx = null;
  let analyser = null;

  function initAudio() {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.connect(audioCtx.destination);
  }

  function exciteModel(classification, freqHz) {
    initAudio();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const t = audioCtx.currentTime;

    if (classification === 'tata') {
      [1, 2, 3, 4, 5].forEach((m, i) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = i % 2 === 0 ? 'sawtooth' : 'triangle';
        osc.frequency.value = freqHz * m;
        gain.gain.setValueAtTime(0.22 / m, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 2.6 - i * 0.2);
        osc.connect(gain).connect(analyser);
        osc.start(t); osc.stop(t + 2.6);
      });
    } else if (classification === 'avanaddha') {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freqHz * 2.2, t);
      osc.frequency.exponentialRampToValueAtTime(freqHz, t + 0.08);
      osc.frequency.linearRampToValueAtTime(25, t + 1.8);
      gain.gain.setValueAtTime(0.8, t);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.8);
      osc.connect(gain).connect(analyser);
      osc.start(t); osc.stop(t + 1.8);
    } else if (classification === 'susira') {
      const osc = audioCtx.createOscillator();
      const trem = audioCtx.createOscillator();
      const tremG = audioCtx.createGain();
      const gain = audioCtx.createGain();
      trem.frequency.value = 5.5; tremG.gain.value = 8;
      trem.connect(osc.frequency);
      osc.type = 'sine'; osc.frequency.value = freqHz;
      gain.gain.setValueAtTime(0.01, t);
      gain.gain.linearRampToValueAtTime(0.35, t + 0.12);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 2.0);
      osc.connect(gain).connect(analyser);
      osc.start(t); osc.stop(t + 2.0);
      trem.start(t); trem.stop(t + 2.0);
    } else if (classification === 'ghana') {
      [freqHz, freqHz + 2.0].forEach(f => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.value = f;
        gain.gain.setValueAtTime(0.3, t);
        gain.gain.exponentialRampToValueAtTime(0.00001, t + 3.2);
        osc.connect(gain).connect(analyser);
        osc.start(t); osc.stop(t + 3.2);
      });
    }
  }

  function drawScope() {
    const canvas = document.getElementById('vi-scope');
    if (!canvas || !analyser) { requestAnimationFrame(drawScope); return; }
    const ctx = canvas.getContext('2d');
    const buf = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(buf);
    ctx.fillStyle = '#0a0c10'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    const barW = canvas.width / buf.length * 1.5;
    let x = 0;
    for (let i = 0; i < buf.length; i++) {
      const h = (buf[i] / 255) * canvas.height;
      ctx.fillStyle = '#fbbf24';
      ctx.fillRect(x, canvas.height - h, barW, h);
      x += barW + 1;
    }
    requestAnimationFrame(drawScope);
  }

  // ---------- Rendering ----------
  function applyFilterAndSort() {
    let list = data.slice();
    if (activeCategory !== 'all') list = list.filter(i => i.classification === activeCategory);
    if (activeSort === 'rank') list.sort((a, b) => a.rank - b.rank);
    else if (activeSort === 'score') list.sort((a, b) => b.score - a.score);
    else if (activeSort === 'name') list.sort((a, b) => a.name.localeCompare(b.name));
    return list;
  }

  function renderGrid() {
    const grid = document.getElementById('instrument-grid');
    const list = applyFilterAndSort();
    grid.innerHTML = list.map(inst => `
      <div class="vi-card" data-id="${inst.id}">
        <div class="vi-card-top">
          <span class="vi-rank">#${inst.rank}</span>
          <span class="vi-badge vi-${inst.classification}">${inst.classification}</span>
          <span class="vi-score">${inst.score.toFixed(1)}</span>
        </div>
        <h3 class="vi-card-name">${inst.name}</h3>
        <div class="vi-card-deva">${inst.name_devanagari}</div>
        <div class="vi-card-formula">${inst.acoustics.formula_latex}</div>
        <button class="vi-excite" data-class="${inst.classification}" data-freq="${inst.acoustics.fundamental_hz}">🔊 Excite Model</button>
      </div>
    `).join('');

    grid.querySelectorAll('.vi-card').forEach(card => {
      card.addEventListener('click', (e) => {
        if (e.target.classList.contains('vi-excite')) return;
        openDrawer(card.dataset.id);
      });
    });

    grid.querySelectorAll('.vi-excite').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        exciteModel(btn.dataset.class, parseFloat(btn.dataset.freq));
      });
    });
  }

  function openDrawer(id) {
    const inst = data.find(i => i.id === id);
    if (!inst) return;
    const drawer = document.getElementById('detail-drawer');
    const content = document.getElementById('drawer-content');
    content.innerHTML = `
      <h2>${inst.name} <span class="vi-deva">${inst.name_devanagari}</span></h2>
      <p class="vi-organology">${inst.organology}</p>
      <div class="vi-detail-grid">
        <div class="vi-detail-card">
          <h4>Governing Physics</h4>
          <div class="vi-formula">${inst.acoustics.formula_latex}</div>
          <p>Fundamental: <strong>${inst.acoustics.fundamental_hz} Hz</strong></p>
          <p>Bandwidth: ${inst.acoustics.frequency_band}</p>
          <p>Damping (ζ): ${inst.acoustics.damping_ratio}</p>
        </div>
        <div class="vi-detail-card">
          <h4>Ritual Context</h4>
          <p><strong>Attestation:</strong> ${inst.primary_attestation}</p>
          <p><strong>Placement:</strong> ${inst.liturgical_context.spatial_placement}</p>
          <p><strong>Actuator:</strong> ${inst.liturgical_context.actuator}</p>
          <p><strong>Bio-Substrate:</strong> ${inst.liturgical_context.bio_membrane}</p>
        </div>
      </div>
      <button class="vi-excite-large" data-class="${inst.classification}" data-freq="${inst.acoustics.fundamental_hz}">🔊 Excite ${inst.name}</button>
    `;
    content.querySelector('.vi-excite-large').addEventListener('click', () => {
      exciteModel(inst.classification, inst.acoustics.fundamental_hz);
    });
    drawer.setAttribute('aria-hidden', 'false');
    drawer.classList.add('open');
  }

  function closeDrawer() {
    const drawer = document.getElementById('detail-drawer');
    drawer.setAttribute('aria-hidden', 'true');
    drawer.classList.remove('open');
  }

  // ---------- Init ----------
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#category-tabs button').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#category-tabs button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCategory = btn.dataset.cat;
        renderGrid();
      });
    });
    document.getElementById('sort-select').addEventListener('change', e => {
      activeSort = e.target.value;
      renderGrid();
    });
    document.getElementById('drawer-close').addEventListener('click', closeDrawer);
    renderGrid();
    drawScope();
  });
})();