/**
 * Aigaane — Master Frontend Controller
 * Wires all 10 endpoint panels in index.html to Cloud Run.
 */
(() => {
  'use strict';

  const API_BASE = 'https://aigaane-engine-977695793163.asia-south1.run.app';

  const $ = (id) => document.getElementById(id);

  async function postJSON(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return await res.json();
  }

  async function getJSON(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return await res.json();
  }

  // 1. Sandhi Join
  $('btn-sandhi-join')?.addEventListener('click', async () => {
    const out = $('out-sandhi-join');
    out.textContent = 'Processing...';
    try {
      const p1 = $('sandhi-p1').value;
      const p2 = $('sandhi-p2').value;
      const data = await postJSON('/api/v3/sandhi', { p1, p2 });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 2. Sandhi Split
  $('btn-sandhi-split')?.addEventListener('click', async () => {
    const out = $('out-sandhi-split');
    out.textContent = 'Processing...';
    try {
      const text = $('sandhi-split-input').value;
      const data = await postJSON('/api/v3/sandhi/split', { text });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 3. Chandas Scan
  $('btn-chandas-scan')?.addEventListener('click', async () => {
    const out = $('out-chandas');
    out.textContent = 'Scanning...';
    try {
      const text = $('chandas-input').value;
      const data = await postJSON('/api/v3/chandas/scan', { text });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 4. Chandas Vrtta
  $('btn-chandas-vrtta')?.addEventListener('click', async () => {
    const out = $('out-chandas');
    out.textContent = 'Classifying...';
    try {
      const text = $('chandas-input').value;
      const data = await postJSON('/api/v3/chandas/vrtta', { text });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 5. Chandas Anustubh
  $('btn-chandas-anustubh')?.addEventListener('click', async () => {
    const out = $('out-chandas');
    out.textContent = 'Validating...';
    try {
      const text = $('chandas-input').value;
      const data = await postJSON('/api/v3/chandas/anustubh', { text });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 6. Noun Inflect
  $('btn-noun-inflect')?.addEventListener('click', async () => {
    const out = $('out-noun');
    out.textContent = 'Inflecting...';
    try {
      const lemma = $('noun-lemma').value;
      const stem_class = $('noun-stem-class').value;
      const data = await postJSON('/api/v3/morphology/noun/inflect', { lemma, stem_class });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 7. Verb Conjugate
  $('btn-verb-conjugate')?.addEventListener('click', async () => {
    const out = $('out-verb');
    out.textContent = 'Conjugating...';
    try {
      const root = $('verb-root').value;
      const gana = parseInt($('verb-gana').value, 10);
      const lakara = $('verb-lakara').value;
      const data = await postJSON('/api/v3/morphology/verb/conjugate', { root, gana, lakara, script: 'iast' });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 8. Lexicon Lookup
  $('btn-lexicon-lookup')?.addEventListener('click', async () => {
    const out = $('out-lexicon');
    out.textContent = 'Looking up...';
    try {
      const q = $('lexicon-query').value;
      const data = await getJSON(`/api/v3/lexicon/lookup?q=${encodeURIComponent(q)}`);
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 9. Lexicon Exists
  $('btn-lexicon-exists')?.addEventListener('click', async () => {
    const out = $('out-lexicon');
    out.textContent = 'Checking...';
    try {
      const q = $('lexicon-query').value;
      const data = await getJSON(`/api/v3/lexicon/exists?q=${encodeURIComponent(q)}`);
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 10. Gandharva Render (Blob Audio)
  $('btn-gandharva-render')?.addEventListener('click', async () => {
    const out = $('out-gandharva');
    const player = $('gandharva-audio-player');
    out.textContent = 'Synthesizing...';
    player.style.display = 'none';
    
    try {
      const text = $('gandharva-text').value;
      const renderData = await postJSON('/api/v1/gandharva/render', { text });
      
      if (renderData.status === 'success') {
        out.textContent = `Scansion: ${renderData.scansion}\nFetching audio...`;
        const audioRes = await fetch(`${API_BASE}/api/v1/gandharva/audio/${renderData.file}`);
        const blob = await audioRes.blob();
        const url = URL.createObjectURL(blob);
        
        player.src = url;
        player.style.display = 'block';
        out.textContent += '\nAudio loaded!';
      } else {
        out.textContent = `Error: ${renderData.detail}`;
      }
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 11. Corpus Search
  $('btn-corpus-search')?.addEventListener('click', async () => {
    const out = $('out-corpus');
    out.textContent = 'Searching...';
    try {
      const query = $('corpus-query').value;
      const data = await postJSON('/api/v3/corpus/search', { query, limit: 2 });
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) { out.textContent = `Error: ${e.message}`; }
  });

  // 12. Footer Health Check (turns status green if Cloud Run is alive)
  async function checkHealth() {
    const text = document.getElementById('status-text');
    if (!text) return;
    try {
      await postJSON('/api/v3/sandhi', { p1: 'a', p2: 'i' });
      text.textContent = 'API Online';
      text.style.color = '#34d399'; // Green
    } catch {
      text.textContent = 'API Offline';
      text.style.color = '#f87171'; // Red
    }
  }

  // Run health check when the page loads
  checkHealth();

})();