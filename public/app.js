// public/app.js
// Aigaane — Frontend
// Live tabs: Sanskrit, Agent, Morphology, Corpus
// Informational tabs: Śāstra, Coming Soon, About

(() => {
  'use strict';

  const API = Object.freeze({
    INFO:            '/api/info',
    HEALTH:          '/api/health',
    SANDHI:          '/api/v3/sandhi',
    SCAN:            '/api/v3/chandas/scan',
    ANUSTUBH:        '/api/v3/chandas/anustubh',
    TRISHTUBH:       '/api/v3/chandas/trishtubh',
    JAGATI:          '/api/v3/chandas/jagati',
    AGENT:           '/api/v3/agent/lyric',
    AGENT_REFINE:    '/api/v3/agent/refine',
    EXPORT_PDF:      '/api/v3/export/pdf',
    NOUN_INFLECT:    '/api/v3/morphology/noun/inflect',
    NOUN_FORM:       '/api/v3/morphology/noun/form',
    STEM_CLASSES:    '/api/v3/morphology/noun/stem-classes',
    CORPUS_SEARCH:   '/api/v3/corpus/search',
    CORPUS_STATS:    '/api/v3/corpus/stats',
    CORPUS_SOURCES:  '/api/v3/corpus/sources',
    CHANGELOG:       '/api/v3/changelog',
  });

  const LIMITS = Object.freeze({
    PHONEME_MAX: 8,
    TEXT_MAX: 2000,
    TIMEOUT_MS: 15000,
  });

  // ─── DOM helpers ───

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function el(tag, opts = {}, children = []) {
    const node = document.createElement(tag);
    if (opts.class) node.className = opts.class;
    if (opts.text != null) node.textContent = String(opts.text);
    if (opts.attrs) {
      for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
    }
    for (const child of children) {
      if (child == null) continue;
      node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return node;
  }

  function clearNode(node) {
    node.replaceChildren();
  }

  function sanitize(s, maxLen) {
    if (typeof s !== 'string') return '';
    return s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
            .slice(0, maxLen)
            .trim();
  }

  async function postJSON(url, body, headers = {}) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), LIMITS.TIMEOUT_MS);
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: JSON.stringify(body),
        signal: ctrl.signal,
        credentials: 'omit',
        cache: 'no-store',
      });
      clearTimeout(timer);
      const data = await res.json().catch(() => ({ detail: 'Invalid JSON' }));
      if (!res.ok) {
        const msg = typeof data.detail === 'string' ? data.detail : 'HTTP ' + res.status;
        throw new Error(msg);
      }
      return data;
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error('Request timed out');
      throw err;
    }
  }

  async function getJSON(url) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), LIMITS.TIMEOUT_MS);
    try {
      const res = await fetch(url, {
        signal: ctrl.signal,
        credentials: 'omit',
        cache: 'no-store',
      });
      clearTimeout(timer);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return await res.json();
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error('Request timed out');
      throw err;
    }
  }

  // ─── Output helpers ───

  function renderError(node, message) {
    node.replaceChildren(
      el('div', { class: 'output-result' }, [
        el('span', { class: 'rule-tag rule-none', text: 'Error' }),
        el('p', { class: 'placeholder', text: message }),
      ])
    );
    node.classList.add('has-error');
    node.classList.remove('has-success');
  }

  function renderLoading(node) {
    node.replaceChildren(el('div', { class: 'loading', text: 'Computing…' }));
    node.classList.remove('has-error', 'has-success');
  }

  // ─── Sandhi view ───

  function renderSandhiResult(node, data) {
    const wrapper = el('div', { class: 'output-result' }, [
      el('div', { class: 'output-eq' }, [
        el('span', { class: 'in', text: data.p1 }),
        el('span', { class: 'arrow', text: ' + ' }),
        el('span', { class: 'in', text: data.p2 }),
        el('span', { class: 'arrow', text: ' → ' }),
        el('span', { class: 'out', text: data.result }),
      ]),
      data.rule_applied && data.rule_applied !== 'none'
        ? el('span', { class: 'rule-tag', text: 'Sūtra ' + data.rule_applied })
        : el('span', { class: 'rule-tag rule-none', text: 'No rule — literal' }),
    ]);
    node.replaceChildren(wrapper);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function buildSandhiView(info, health) {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(
      el('section', { class: 'panel' }, [
        el('header', { class: 'panel-head' }, [
          el('h2', { text: info && info.name ? info.name : 'Aigaane Sanskrit Engine' }),
          el('p', { class: 'panel-sub', text: 'Deterministic Pāṇinian sandhi. Every derivation cites the governing sūtra.' }),
        ]),
        el('div', { class: 'status-line' }, [
          el('span', { class: 'dot online', attrs: { 'aria-hidden': 'true' } }),
          el('span', { text: health && health.version
            ? 'Online · v' + health.version + (health.current_golden_build ? ' · ' + health.current_golden_build : '')
            : 'Online · engine ready' }),
        ]),
      ])
    );

    const p1 = el('input', { attrs: { type: 'text', id: 'sandhi-p1', maxlength: '8',
      placeholder: 'a or aḥ', value: 'a', spellcheck: 'false', autocomplete: 'off' } });
    const p2 = el('input', { attrs: { type: 'text', id: 'sandhi-p2', maxlength: '8',
      placeholder: 'i or iti', value: 'i', spellcheck: 'false', autocomplete: 'off' } });
    const swapBtn = el('button', { class: 'btn btn-ghost', text: 'Swap', attrs: { type: 'button' } });
    const clearBtn = el('button', { class: 'btn btn-ghost', text: 'Clear', attrs: { type: 'button' } });
    const submit = el('button', { class: 'btn btn-primary', text: 'Combine', attrs: { type: 'submit' } });
    const output = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Result will appear here.' }),
    ]);

    const sandhiForm = el('form', { class: 'form', attrs: { autocomplete: 'off' } }, [
      el('div', { class: 'form-row' }, [
        el('label', {}, [
          el('span', { class: 'label', text: 'First phoneme / word-final' }),
          p1,
          el('small', { class: 'hint', text: 'IAST input — e.g. a, aḥ, t' }),
        ]),
        el('label', {}, [
          el('span', { class: 'label', text: 'Second phoneme / word-initial' }),
          p2,
          el('small', { class: 'hint', text: 'IAST input — e.g. i, iti, c' }),
        ]),
      ]),
      el('div', { class: 'form-actions' }, [submit, swapBtn, clearBtn]),
    ]);

    const sectionSandhi = el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h3', { text: 'Sandhi Combiner' }),
        el('p', { class: 'panel-sub', text: 'Aṣṭādhyāyī 6.1 and 8.4 rules.' }),
      ]),
      sandhiForm,
      output,
      el('div', { class: 'presets' }, [
        el('span', { class: 'presets-label', text: 'Examples:' }),
        ...[['a', 'i'], ['a', 'a'], ['a', 'e'], ['i', 'a'], ['t', 'c'], ['aḥ', 'a']].map(([a, b]) =>
          el('button', { class: 'chip', text: a + ' + ' + b,
            attrs: { type: 'button', 'data-p1': a, 'data-p2': b } })
        ),
      ]),
    ]);
    fragment.appendChild(sectionSandhi);

    sandhiForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const v1 = sanitize(p1.value, LIMITS.PHONEME_MAX);
      const v2 = sanitize(p2.value, LIMITS.PHONEME_MAX);
      if (!v1 || !v2) { renderError(output, 'Both inputs are required.'); return; }
      renderLoading(output);
      try {
        const data = await postJSON(API.SANDHI, { p1: v1, p2: v2 });
        renderSandhiResult(output, data);
      } catch (err) { renderError(output, err.message); }
    });

    swapBtn.addEventListener('click', () => {
      const a = p1.value; p1.value = p2.value; p2.value = a; p1.focus();
    });
    clearBtn.addEventListener('click', () => {
      p1.value = ''; p2.value = ''; output.replaceChildren(el('p', { class: 'placeholder', text: 'Result will appear here.' })); output.classList.remove('has-error', 'has-success'); p1.focus();
    });

    $$('.chip[data-p1]', sectionSandhi).forEach((chip) => {
      chip.addEventListener('click', () => {
        p1.value = chip.getAttribute('data-p1') || '';
        p2.value = chip.getAttribute('data-p2') || '';
        sandhiForm.requestSubmit();
      });
    });

    return fragment;
  }

  // ─── Chandas view ───

  function renderScansion(node, data) {
    const syllables = Array.isArray(data.syllables) ? data.syllables : [];
    const nodes = [];
    nodes.push(el('p', { class: 'pattern-line', text: data.pattern || '' }));

    const grid = el('div', { class: 'pattern' });
    for (const s of syllables) {
      const weight = s.weight === 'G' ? 'Guru −' : 'Laghu ⏑';
      grid.appendChild(el('div', {
        class: 'syllable',
        attrs: { 'aria-label': s.text + ' ' + weight },
      }, [
        el('span', { class: 'glyph', text: s.text }),
        el('span', { class: 'weight ' + s.weight, text: s.weight }),
      ]));
    }
    nodes.push(grid);
    nodes.push(el('div', { class: 'output-result' }, [
      el('span', { class: 'rule-tag', text: data.length + ' syllables' }),
    ]));

    node.replaceChildren(...nodes);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function renderMeterValidation(node, data, meterName) {
    const nodes = [];
    nodes.push(el('div', {
      class: 'validation-summary ' + (data.is_valid ? 'valid' : 'invalid'),
    }, [
      el('span', { class: 'label', text: data.is_valid ? '✓ Valid ' + meterName : '✗ Not a valid ' + meterName }),
    ]));

    if (Array.isArray(data.padas) && data.padas.length) {
      const list = el('div', { class: 'pada-list' });
      for (const p of data.padas) {
        const row = el('div', {
          class: 'pada ' + (p.is_valid ? 'is-valid' : 'is-invalid'),
        }, [
          el('span', { class: 'pada-num', text: 'Pāda ' + p.index }),
          el('span', { class: 'pada-pattern', text: p.text_pattern || '—' }),
          el('span', { class: 'pada-variety', text: p.variety || '—' }),
        ]);
        if (p.reason) row.appendChild(el('span', { class: 'pada-reason', text: p.reason }));
        list.appendChild(row);
      }
      nodes.push(list);
    }

    if (Array.isArray(data.errors) && data.errors.length) {
      const ul = el('ul', { class: 'error-list' });
      for (const err of data.errors) ul.appendChild(el('li', { text: err }));
      nodes.push(ul);
    }

    node.replaceChildren(...nodes);
    node.classList.add(data.is_valid ? 'has-success' : 'has-error');
  }

  function buildChandasView() {
    const fragment = document.createDocumentFragment();

    const scanText = el('textarea', { attrs: { rows: '3', maxlength: '2000',
      spellcheck: 'false', placeholder: 'rāmo gacchati' } });
    scanText.value = 'rāmo gacchati';
    const scanOutput = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Scansion will appear here.' }),
    ]);
    const scanForm = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Sanskrit text (IAST)' }),
        scanText,
        el('small', { class: 'hint', text: 'e.g. rāmaḥ, agni, tapaḥsvādhyāyanirataṃ' }),
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Scan', attrs: { type: 'submit' } }),
      ]),
    ]);

    const meterSelect = el('select', { class: 'meter-select', attrs: { id: 'meter-select' } }, [
      el('option', { text: 'Anuṣṭubh (4 × 8 = 32 syllables)', attrs: { value: 'anustubh', selected: 'selected' } }),
      el('option', { text: 'Triṣṭubh (4 × 11 = 44 syllables)', attrs: { value: 'trishtubh' } }),
      el('option', { text: 'Jagatī (4 × 12 = 48 syllables)', attrs: { value: 'jagati' } }),
    ]);

    const meterText = el('textarea', { attrs: { rows: '4', maxlength: '2000',
      spellcheck: 'false', placeholder: 'tapaḥsvādhyāyanirataṃ tapasvī vāgvidāṃ varam' } });
    meterText.value = 'tapaḥsvādhyāyanirataṃ tapasvī vāgvidāṃ varam';

    const meterOutput = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Validation will appear here.' }),
    ]);

    const meterForm = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Meter' }),
        meterSelect,
      ]),
      el('label', {}, [
        el('span', { class: 'label', text: 'Verse (IAST)' }),
        meterText,
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Validate', attrs: { type: 'submit' } }),
      ]),
    ]);

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Chandas Scanner' }),
        el('p', { class: 'panel-sub', text: 'Laghu (⏑) and Guru (−) weights per Piṅgala.' }),
      ]),
      scanForm,
      scanOutput,
    ]));
    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Meter Validator' }),
        el('p', { class: 'panel-sub', text: 'Anuṣṭubh · Triṣṭubh · Jagatī' }),
      ]),
      meterForm,
      meterOutput,
    ]));

    scanForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = sanitize(scanText.value, LIMITS.TEXT_MAX);
      if (!text) { renderError(scanOutput, 'Enter text to scan.'); return; }
      renderLoading(scanOutput);
      try {
        const data = await postJSON(API.SCAN, { text });
        renderScansion(scanOutput, data);
      } catch (err) { renderError(scanOutput, err.message); }
    });

    meterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = sanitize(meterText.value, LIMITS.TEXT_MAX);
      if (!text) { renderError(meterOutput, 'Enter a verse to validate.'); return; }
      renderLoading(meterOutput);
      const meter = meterSelect.value;
      const meterName = meter === 'anustubh' ? 'Anuṣṭubh' : (meter === 'trishtubh' ? 'Triṣṭubh' : 'Jagatī');
      try {
        const endpoint = meter === 'anustubh' ? API.ANUSTUBH : (meter === 'trishtubh' ? API.TRISHTUBH : API.JAGATI);
        const data = await postJSON(endpoint, { text });
        renderMeterValidation(meterOutput, data, meterName);
      } catch (err) { renderError(meterOutput, err.message); }
    });

    return fragment;
  }

  // ─── Agent view ───

  function buildAgentView() {
    const fragment = document.createDocumentFragment();

    const state = {
      lastVerse: '',
      lastPattern: '',
      lastMeter: 'anuṣṭubh',
    };

    const prompt = el('textarea', {
      attrs: { rows: '3', maxlength: '2000', placeholder: 'Saraswatī Vandana in Anuṣṭubh' },
    });
    prompt.value = 'Saraswatī Vandana in Anuṣṭubh';

    const apiKeyInput = el('input', {
      attrs: { type: 'password', maxlength: '128', placeholder: 'API key (X-API-Key)',
               autocomplete: 'off', spellcheck: 'false' },
    });

    const meterSelect = el('select', { class: 'meter-select', attrs: { id: 'agent-meter' } }, [
      el('option', { text: 'Anuṣṭubh (4 × 8 = 32)', attrs: { value: 'anuṣṭubh', selected: 'selected' } }),
      el('option', { text: 'Triṣṭubh (4 × 11 = 44)', attrs: { value: 'trishtubh' } }),
      el('option', { text: 'Jagatī (4 × 12 = 48)', attrs: { value: 'jagati' } }),
    ]);

    const output = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Verse will stream here.' }),
    ]);

    const actionRow = el('div', { class: 'form-actions', attrs: { style: 'display: none;' } });

    const pdfBtn = el('button', { class: 'btn btn-ghost', text: 'Download PDF', attrs: { type: 'button' } });
    const refineToggleBtn = el('button', { class: 'btn btn-ghost', text: 'Refine…', attrs: { type: 'button' } });

    actionRow.appendChild(pdfBtn);
    actionRow.appendChild(refineToggleBtn);

    const refineInput = el('textarea', {
      attrs: { rows: '2', maxlength: '500', placeholder: 'e.g. Make it more devotional.' },
    });

    const refineBtn = el('button', { class: 'btn btn-primary', text: 'Apply Refinement', attrs: { type: 'submit' } });

    const refineOutput = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Refined verse will stream here.' }),
    ]);

    const refineForm = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Refinement instruction' }),
        refineInput,
      ]),
      el('div', { class: 'form-actions' }, [refineBtn]),
    ]);

    const refinePanel = el('div', { class: 'refine-panel', attrs: { style: 'display: none;' } }, [
      el('header', { class: 'panel-head' }, [
        el('h3', { text: 'Refine Verse' }),
        el('p', { class: 'panel-sub', text: 'Iterate on the last generated verse.' }),
      ]),
      refineForm,
      refineOutput,
    ]);

    const form = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Prompt' }),
        prompt,
      ]),
      el('label', {}, [
        el('span', { class: 'label', text: 'Meter' }),
        meterSelect,
      ]),
      el('label', {}, [
        el('span', { class: 'label', text: 'API Key (not stored)' }),
        apiKeyInput,
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Generate', attrs: { type: 'submit' } }),
      ]),
    ]);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const key = apiKeyInput.value.trim();
      if (!key) { renderError(output, 'API key required'); return; }
      renderLoading(output);
      actionRow.style.display = 'none';
      refinePanel.style.display = 'none';

      const meter = meterSelect.value;
      state.lastMeter = meter;

      try {
        const res = await fetch(API.AGENT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
          body: JSON.stringify({ prompt: prompt.value, meter: meter, max_attempts: 5 }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Request failed' }));
          renderError(output, err.detail || ('HTTP ' + res.status));
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        const stages = [];
        let buffer = '';

        const log = el('pre', { class: 'stream-log' });
        output.replaceChildren(log);

        while (true) {
          const chunk = await reader.read();
          if (chunk.done) break;
          buffer += decoder.decode(chunk.value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const event = JSON.parse(line.slice(6));
              stages.push(event);
              log.textContent += JSON.stringify(event, null, 2) + '\n';
              log.scrollTop = log.scrollHeight;
            } catch (e) { /* skip malformed */ }
          }
        }

        const last = stages[stages.length - 1];
        if (last && last.stage === 'complete') {
          state.lastVerse = last.verse || '';
          state.lastPattern = last.pattern || '';
          output.replaceChildren(
            el('pre', { class: 'verse-output', text: last.verse || '' }),
            el('p', { class: 'pattern-line', text: last.pattern || '' }),
            el('span', { class: 'rule-tag',
                         text: 'Quanta: ' + (last.quanta ? (last.quanta.spent + ' / ' + last.quanta.ceiling) : '?') }),
          );
          output.classList.add('has-success');
          actionRow.style.display = '';
        } else {
          renderError(output, last && last.message ? last.message : 'Generation incomplete');
        }
      } catch (err) { renderError(output, err.message); }
    });

    pdfBtn.addEventListener('click', async () => {
      if (!state.lastVerse) return;
      pdfBtn.disabled = true;
      const originalText = pdfBtn.textContent;
      pdfBtn.textContent = 'Generating…';
      try {
        const res = await fetch(API.EXPORT_PDF, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'Aigaane Verse', verse: state.lastVerse, pattern: state.lastPattern }),
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'aigaane-verse.pdf';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (err) {
        alert('PDF export failed: ' + err.message);
      } finally {
        pdfBtn.disabled = false;
        pdfBtn.textContent = originalText;
      }
    });

    refineToggleBtn.addEventListener('click', () => {
      const visible = refinePanel.style.display !== 'none';
      refinePanel.style.display = visible ? 'none' : '';
      if (!visible) refineInput.focus();
    });

    refineForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const key = apiKeyInput.value.trim();
      if (!key) { renderError(refineOutput, 'API key required'); return; }
      if (!state.lastVerse) { renderError(refineOutput, 'Generate a verse first'); return; }
      const refinement = sanitize(refineInput.value, 500);
      if (!refinement) { renderError(refineOutput, 'Enter a refinement instruction'); return; }

      renderLoading(refineOutput);

      try {
        const res = await fetch(API.AGENT_REFINE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
          body: JSON.stringify({
            previous_verse: state.lastVerse,
            refinement: refinement,
            meter: state.lastMeter,
            max_attempts: 3,
          }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Request failed' }));
          renderError(refineOutput, err.detail || ('HTTP ' + res.status));
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        const stages = [];
        let buffer = '';

        const log = el('pre', { class: 'stream-log' });
        refineOutput.replaceChildren(log);

        while (true) {
          const chunk = await reader.read();
          if (chunk.done) break;
          buffer += decoder.decode(chunk.value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const event = JSON.parse(line.slice(6));
              stages.push(event);
              log.textContent += JSON.stringify(event, null, 2) + '\n';
              log.scrollTop = log.scrollHeight;
            } catch (e) { /* skip malformed */ }
          }
        }

        const last = stages[stages.length - 1];
        if (last && last.stage === 'complete') {
          state.lastVerse = last.verse || '';
          state.lastPattern = last.pattern || '';
          refineOutput.replaceChildren(
            el('pre', { class: 'verse-output', text: last.verse || '' }),
            el('p', { class: 'pattern-line', text: last.pattern || '' }),
            el('span', { class: 'rule-tag',
                         text: 'Quanta: ' + (last.quanta ? (last.quanta.spent + ' / ' + last.quanta.ceiling) : '?') }),
          );
          refineOutput.classList.add('has-success');
        } else {
          renderError(refineOutput, last && last.message ? last.message : 'Refinement incomplete');
        }
      } catch (err) { renderError(refineOutput, err.message); }
    });

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Agentic Verse Generator' }),
        el('p', { class: 'panel-sub', text: 'Generates metrically-validated Sanskrit verse. Every draft is scanned by the deterministic engine.' }),
      ]),
      form,
      output,
      actionRow,
      refinePanel,
    ]));

    return fragment;
  }

  // ─── Morphology view ───

  const STEM_CLASS_OPTIONS = [
    { value: 'a-masc', label: 'a-stem masculine — deva (god)' },
    { value: 'a-neut', label: 'a-stem neuter — phala (fruit)' },
    { value: 'ā-fem',  label: 'ā-stem feminine — senā (army)' },
    { value: 'i-masc', label: 'i-stem masculine — agni (fire)' },
    { value: 'i-fem',  label: 'i-stem feminine — mati (thought)' },
    { value: 'u-masc', label: 'u-stem masculine — viṣṇu' },
    { value: 'ū-fem',  label: 'ū-stem feminine — bhū (earth)' },
  ];

  function renderParadigmTable(node, data) {
    if (!data || !Array.isArray(data.forms) || !data.forms.length) {
      renderError(node, 'No forms returned');
      return;
    }

    const byVibhakti = new Map();
    for (const f of data.forms) {
      if (!byVibhakti.has(f.vibhakti)) byVibhakti.set(f.vibhakti, {});
      byVibhakti.get(f.vibhakti)[f.vacana] = f.form;
    }

    const table = el('table', { class: 'paradigm-table' });
    const thead = el('thead');
    thead.appendChild(el('tr', {}, [
      el('th', { text: 'Vibhakti (case)' }),
      el('th', { text: 'Ekavacana (sg.)' }),
      el('th', { text: 'Dvivacana (du.)' }),
      el('th', { text: 'Bahuvacana (pl.)' }),
    ]));
    table.appendChild(thead);

    const tbody = el('tbody');
    for (const entry of byVibhakti) {
      const vibhakti = entry[0];
      const row = entry[1];
      tbody.appendChild(el('tr', {}, [
        el('td', { class: 'vibhakti-cell', text: vibhakti }),
        el('td', { class: 'form-cell', text: row.ekavacana || '—' }),
        el('td', { class: 'form-cell', text: row.dvivacana || '—' }),
        el('td', { class: 'form-cell', text: row.bahuvacana || '—' }),
      ]));
    }
    table.appendChild(tbody);

    const header = el('div', { class: 'paradigm-header' }, [
      el('span', { class: 'rule-tag', text: data.lemma + ' · ' + data.stem_class }),
      el('span', { class: 'rule-tag', text: data.count + ' forms' }),
    ]);

    node.replaceChildren(header, table);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function buildMorphologyView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Subanta — Nominal Declension' }),
        el('p', { class: 'panel-sub', text: 'Generate the full 24-form paradigm (8 vibhaktis × 3 vacanas) for any nominal stem.' }),
      ]),
    ]));

    const lemmaInput = el('input', {
      attrs: { type: 'text', id: 'morph-lemma', maxlength: '64',
               placeholder: 'deva', value: 'deva',
               spellcheck: 'false', autocomplete: 'off' },
    });

    const stemSelect = el('select', { class: 'meter-select', attrs: { id: 'morph-stem' } },
      STEM_CLASS_OPTIONS.map(function (o) {
        return el('option', { text: o.label, attrs: { value: o.value } });
      })
    );

    const output = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Paradigm will appear here.' }),
    ]);

    const form = el('form', { class: 'form' }, [
      el('div', { class: 'form-row' }, [
        el('label', {}, [
          el('span', { class: 'label', text: 'Lemma (IAST)' }),
          lemmaInput,
          el('small', { class: 'hint', text: 'e.g. deva, senā, agni, viṣṇu' }),
        ]),
        el('label', {}, [
          el('span', { class: 'label', text: 'Stem class' }),
          stemSelect,
        ]),
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Generate paradigm', attrs: { type: 'submit' } }),
      ]),
    ]);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const lemma = sanitize(lemmaInput.value, 64);
      const stemClass = stemSelect.value;
      if (!lemma) { renderError(output, 'Enter a lemma.'); return; }
      renderLoading(output);
      try {
        const data = await postJSON(API.NOUN_INFLECT, { lemma: lemma, stem_class: stemClass });
        renderParadigmTable(output, data);
      } catch (err) { renderError(output, err.message); }
    });

    const presetsRow = el('div', { class: 'presets' }, [
      el('span', { class: 'presets-label', text: 'Quick examples:' }),
      ...[
        ['deva', 'a-masc'], ['phala', 'a-neut'], ['senā', 'ā-fem'],
        ['agni', 'i-masc'], ['mati', 'i-fem'], ['viṣṇu', 'u-masc'], ['bhū', 'ū-fem'],
      ].map(function (pair) {
        return el('button', { class: 'chip', text: pair[0] + ' (' + pair[1] + ')',
          attrs: { type: 'button', 'data-lemma': pair[0], 'data-sc': pair[1] } });
      }),
    ]);

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h3', { text: 'Generate paradigm' }),
      ]),
      form,
      output,
      presetsRow,
    ]));

    presetsRow.querySelectorAll('.chip[data-lemma]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        lemmaInput.value = chip.getAttribute('data-lemma') || '';
        stemSelect.value = chip.getAttribute('data-sc') || 'a-masc';
        form.requestSubmit();
      });
    });

    return fragment;
  }

  // ─── Corpus view ───

  function renderCorpusResults(node, data) {
    if (!data || !Array.isArray(data.results)) {
      renderError(node, 'Invalid search response');
      return;
    }
    if (data.results.length === 0) {
      node.replaceChildren(el('p', { class: 'placeholder', text: 'No verses matched your search.' }));
      node.classList.remove('has-error', 'has-success');
      return;
    }

    const header = el('div', { class: 'paradigm-header' }, [
      el('span', { class: 'rule-tag', text: data.total_returned + ' result(s)' }),
      el('span', { class: 'rule-tag rule-none', text: 'query: "' + data.query + '"' }),
    ]);

    const cards = el('div', { class: 'corpus-results' });
    for (const r of data.results) {
      const v = r.verse;
      const foot = el('footer', { class: 'corpus-foot' }, [
        el('span', { class: 'corpus-meter', text: v.meter }),
      ]);
      (v.themes || []).forEach(function (t) {
        foot.appendChild(el('span', { class: 'theme-chip', text: t }));
      });
      foot.appendChild(el('span', { class: 'corpus-score', text: 'score ' + r.score.toFixed(1) }));

      const card = el('article', { class: 'corpus-card' }, [
        el('header', { class: 'corpus-head' }, [
          el('span', { class: 'corpus-location', text: v.location }),
          el('span', { class: 'corpus-source', text: v.source }),
        ]),
        el('p', { class: 'corpus-iast', text: v.iast }),
        v.gloss ? el('p', { class: 'corpus-gloss', text: v.gloss }) : null,
        foot,
      ]);
      cards.appendChild(card);
    }

    node.replaceChildren(header, cards);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function buildCorpusView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Itihāsa Corpus Search' }),
        el('p', { class: 'panel-sub', text: 'Search Rāmāyaṇa and Mahābhārata verses by keyword, source, meter, or theme.' }),
      ]),
    ]));

    const queryInput = el('input', {
      attrs: { type: 'text', id: 'corpus-query', maxlength: '200',
               placeholder: 'rāma · dharma · sarasvatī · karma',
               value: 'dharma', spellcheck: 'false', autocomplete: 'off' },
    });

    const sourceSelect = el('select', { class: 'meter-select', attrs: { id: 'corpus-source' } }, [
      el('option', { text: 'Any source', attrs: { value: '' } }),
      el('option', { text: 'Rāmāyaṇa', attrs: { value: 'Rāmāyaṇa' } }),
      el('option', { text: 'Mahābhārata', attrs: { value: 'Mahābhārata' } }),
    ]);

    const limitSelect = el('select', { class: 'meter-select', attrs: { id: 'corpus-limit' } }, [
      el('option', { text: '5 results', attrs: { value: '5', selected: 'selected' } }),
      el('option', { text: '10 results', attrs: { value: '10' } }),
      el('option', { text: '20 results', attrs: { value: '20' } }),
    ]);

    const output = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Search results will appear here.' }),
    ]);

    const form = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Search query' }),
        queryInput,
        el('small', { class: 'hint', text: 'Searches IAST text, gloss, and theme tags' }),
      ]),
      el('div', { class: 'form-row' }, [
        el('label', {}, [
          el('span', { class: 'label', text: 'Source filter' }),
          sourceSelect,
        ]),
        el('label', {}, [
          el('span', { class: 'label', text: 'Results' }),
          limitSelect,
        ]),
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Search', attrs: { type: 'submit' } }),
      ]),
    ]);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const query = sanitize(queryInput.value, 200);
      const body = {
        query: query,
        limit: parseInt(limitSelect.value, 10) || 5,
      };
      const src = sourceSelect.value;
      if (src) body.source = src;
      renderLoading(output);
      try {
        const data = await postJSON(API.CORPUS_SEARCH, body);
        renderCorpusResults(output, data);
      } catch (err) { renderError(output, err.message); }
    });

    const presetsRow = el('div', { class: 'presets' }, [
      el('span', { class: 'presets-label', text: 'Quick queries:' }),
      ...['rāma', 'dharma', 'karma', 'sarasvatī', 'avatāra', 'gītā'].map(function (q) {
        return el('button', { class: 'chip', text: q,
          attrs: { type: 'button', 'data-query': q } });
      }),
    ]);

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h3', { text: 'Search the corpus' }),
      ]),
      form,
      output,
      presetsRow,
    ]));

    presetsRow.querySelectorAll('.chip[data-query]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        queryInput.value = chip.getAttribute('data-query') || '';
        form.requestSubmit();
      });
    });

    return fragment;
  }

  // ─── Śāstra view ───

  const SASTRA_TREE = {
    sruti: {
      label: 'Śruti — Axiomatic Core',
      subtitle: 'That which is heard (revealed, authorless)',
      children: [
        { name: 'Ṛgveda', subtitle: 'Hymns of cosmic order', status: 'metadata', meta: 'Saṃhitā: 10 Maṇḍalas · 1,028 Sūktas · 10,552+ verses',
          parts: [{ name: 'Saṃhitā' }, { name: 'Brāhmaṇas', meta: 'Aitareya, Kauṣītaki / Śāṅkhāyana' }, { name: 'Āraṇyakas', meta: 'Aitareya, Kauṣītaki' }, { name: 'Upaniṣads', meta: 'Aitareya, Kauṣītaki' }] },
        { name: 'Śukla Yajurveda', subtitle: 'White Yajurveda', status: 'metadata', meta: 'Vājasaneyi Saṃhitā',
          parts: [{ name: 'Śatapatha Brāhmaṇa', meta: '100 Adhyāyas' }, { name: 'Āraṇyaka', meta: 'Embedded in 14th Kāṇḍa' }, { name: 'Upaniṣads', meta: 'Īśā, Bṛhadāraṇyaka' }] },
        { name: 'Kṛṣṇa Yajurveda', subtitle: 'Black Yajurveda', status: 'metadata', meta: 'Taittirīya, Maitrāyaṇī, Kaṭha, Kapiṣṭhala',
          parts: [{ name: 'Taittirīya Brāhmaṇa' }, { name: 'Taittirīya Āraṇyaka' }, { name: 'Upaniṣads', meta: 'Taittirīya, Kaṭha, Śvetāśvatara, Maitrāyaṇī' }] },
        { name: 'Sāmaveda', subtitle: 'Musical & melodic chants', status: 'metadata', meta: '1,875 verses (derived from Ṛgveda)',
          parts: [{ name: 'Brāhmaṇas', meta: 'Pañcaviṃśa, Ṣaḍviṃśa, Jaiminīya' }, { name: 'Upaniṣads', meta: 'Chāndogya, Kena' }] },
        { name: 'Atharvaveda', subtitle: 'Daily life, healing, protection', status: 'metadata', meta: '20 Kāṇḍas · 730 hymns',
          parts: [{ name: 'Gopatha Brāhmaṇa' }, { name: 'Upaniṣads', meta: 'Praśna, Muṇḍaka, Māṇḍūkya' }] },
        { name: 'Muktikā Canon', subtitle: '108 Upaniṣads by Vedic Śākhā', status: 'metadata',
          parts: [{ name: 'Ṛgveda', meta: '10 Upaniṣads' }, { name: 'Śukla Yajurveda', meta: '19 Upaniṣads' }, { name: 'Kṛṣṇa Yajurveda', meta: '32 Upaniṣads' }, { name: 'Sāmaveda', meta: '16 Upaniṣads' }, { name: 'Atharvaveda', meta: '31 Upaniṣads' }] },
      ],
    },
    smrti: {
      label: 'Smṛti — Hermeneutic Closure',
      subtitle: 'That which is remembered (tradition-anchored)',
      children: [
        { name: 'Vedāṅgas', subtitle: 'Six structural auxiliary disciplines', status: 'partial',
          parts: [{ name: 'Śikṣā', meta: 'Phonetics & phonology', status: 'live' }, { name: 'Vyākaraṇa', meta: 'Grammar — sandhi + subanta', status: 'partial' }, { name: 'Chandas', meta: 'Prosody — 3 meters', status: 'partial' }, { name: 'Nirukta', meta: 'Etymology', status: 'coming' }, { name: 'Kalpa', meta: 'Ritual mechanics', status: 'coming' }, { name: 'Jyotiṣa', meta: 'Astronomy', status: 'coming' }] },
        { name: 'Ṣaḍ Darśanas', subtitle: 'Six classical philosophical systems', status: 'metadata',
          parts: [{ name: 'Nyāya', meta: 'Logic — Akṣapāda Gautama' }, { name: 'Vaiśeṣika', meta: 'Atomism — Kaṇāda' }, { name: 'Sāṅkhya', meta: 'Puruṣa & Prakṛti — Kapila' }, { name: 'Yoga', meta: 'Meditation — Patañjali' }, { name: 'Pūrva Mīmāṃsā', meta: 'Hermeneutics — Jaimini' }, { name: 'Uttara Mīmāṃsā', meta: 'Vedānta — Bādarāyaṇa' }] },
        { name: 'Itihāsas', subtitle: 'Epic historical narratives', status: 'partial',
          parts: [{ name: 'Rāmāyaṇa', meta: 'Vālmīki — 7 Kāṇḍas', status: 'partial' }, { name: 'Mahābhārata', meta: 'Vyāsa — 18 Parvas', status: 'partial' }] },
        { name: 'Purāṇas', subtitle: 'Cyclic cosmogony & universal history', status: 'metadata',
          parts: [{ name: 'Sāttvika', meta: 'Viṣṇu, Bhāgavata, Nārada, Garuḍa, Padma, Varāha' }, { name: 'Rājasika', meta: 'Brahmā, Brahmāṇḍa, Brahmavaivarta, Mārkaṇḍeya, Bhaviṣya, Vāmana' }, { name: 'Tāmasika', meta: 'Śiva, Liṅga, Skanda, Agni, Matsya, Kūrma' }, { name: 'Upapurāṇas', meta: '18 secondary texts' }] },
        { name: 'Dharmaśāstras', subtitle: 'Social ethics & civil law', status: 'metadata',
          parts: [{ name: 'Dharma Sūtras', meta: 'Āpastamba, Gautama, Baudhāyana' }, { name: 'Dharma Smṛtis', meta: 'Manusmṛti, Yājñavalkya, Nārada' }] },
        { name: 'Upavedas', subtitle: 'Four classical applied sciences', status: 'metadata',
          parts: [{ name: 'Āyurveda', meta: 'Medicine' }, { name: 'Dhanurveda', meta: 'Warfare' }, { name: 'Gāndharvaveda', meta: 'Music & drama' }, { name: 'Sthāpatyaveda', meta: 'Architecture' }] },
        { name: 'Āgamas & Tantras', subtitle: 'Initiatory practice, iconography', status: 'metadata',
          parts: [{ name: 'Śaiva Āgamas', meta: '28 Siddhānta + Trika' }, { name: 'Vaiṣṇava Āgamas', meta: 'Pāñcarātra, Vaikhānasa' }, { name: 'Śākta Tantras', meta: '64 Tantras' }] },
        { name: 'Bhakti Sādhana', subtitle: 'Devotional classics & poetics', status: 'metadata',
          parts: [{ name: 'Bhakti Sūtras', meta: 'Nārada, Śāṇḍilya' }, { name: 'Dravidian Canons', meta: 'Divya Prabandham, Tevāram' }, { name: 'Regional Classics', meta: 'Rāmacaritamānasa, Gītagovinda' }] },
        { name: 'Prakaraṇa Granthas', subtitle: 'Independent philosophical treatises', status: 'metadata',
          parts: [{ name: 'Advaita', meta: 'Vivekacūḍāmaṇi, Pañcadaśī' }, { name: 'Non-dualism', meta: 'Aṣṭāvakra Gītā, Yoga Vāsiṣṭha' }] },
      ],
    },
    purusartha: {
      label: 'Puruṣārtha — Applied Objectives',
      subtitle: 'Secular & supporting texts',
      children: [
        { name: 'Arthaśāstra', subtitle: 'Political economy & statecraft', status: 'metadata', meta: 'Kauṭilya' },
        { name: 'Nāṭyaśāstra', subtitle: 'Dramaturgy & aesthetics', status: 'metadata', meta: 'Bharata Muni' },
        { name: 'Kāma Sūtra', subtitle: 'Social dynamics & erotics', status: 'metadata', meta: 'Vātsyāyana' },
        { name: 'Bṛhat Saṃhitā', subtitle: 'Physical sciences & divination', status: 'metadata', meta: 'Varāhamihira' },
        { name: 'Nīti Literature', subtitle: 'Strategic pedagogy', status: 'metadata', meta: 'Pañcatantra, Hitopadeśa' },
      ],
    },
  };

  function buildSastraView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Hindu Śāstra Taxonomy' }),
        el('p', { class: 'panel-sub', text: 'Complete philological taxonomy — Śruti, Smṛti, and Puruṣārtha.' }),
      ]),
    ]));

    const branchKeys = ['sruti', 'smrti', 'purusartha'];
    for (let b = 0; b < branchKeys.length; b++) {
      const branch = SASTRA_TREE[branchKeys[b]];
      const section = el('section', { class: 'panel sastra-branch' }, [
        el('header', { class: 'panel-head' }, [
          el('h2', { text: branch.label }),
          el('p', { class: 'panel-sub', text: branch.subtitle }),
        ]),
      ]);
      const grid = el('div', { class: 'sastra-grid' });
      for (let c = 0; c < branch.children.length; c++) {
        const category = branch.children[c];
        const card = el('div', { class: 'sastra-card sastra-status-' + category.status });
        const cardHead = el('div', { class: 'sastra-card-head' }, [
          el('h3', { text: category.name }),
        ]);
        if (category.status === 'live') {
          cardHead.appendChild(el('span', { class: 'status-badge status-live', text: 'Live' }));
        } else if (category.status === 'partial') {
          cardHead.appendChild(el('span', { class: 'status-badge status-partial', text: 'Partial' }));
        } else {
          cardHead.appendChild(el('span', { class: 'status-badge status-meta', text: 'Documented' }));
        }
        card.appendChild(cardHead);
        if (category.subtitle) {
          card.appendChild(el('p', { class: 'sastra-subtitle', text: category.subtitle }));
        }
        if (category.meta) {
          card.appendChild(el('p', { class: 'sastra-meta', text: category.meta }));
        }
        if (category.parts && category.parts.length) {
          const partList = el('ul', { class: 'sastra-parts' });
          for (let p = 0; p < category.parts.length; p++) {
            const part = category.parts[p];
            const li = el('li', { class: 'sastra-part' }, [
              el('span', { class: 'sastra-part-name', text: part.name }),
            ]);
            if (part.meta) {
              li.appendChild(el('span', { class: 'sastra-part-meta', text: part.meta }));
            }
            if (part.status) {
              const tagText = part.status === 'live' ? 'Live'
                            : part.status === 'partial' ? 'Partial'
                            : part.status === 'coming' ? 'Soon' : 'Docs';
              li.appendChild(el('span', { class: 'sastra-part-tag status-' + part.status, text: tagText }));
            }
            partList.appendChild(li);
          }
          card.appendChild(partList);
        }
        grid.appendChild(card);
      }
      section.appendChild(grid);
      fragment.appendChild(section);
    }
    return fragment;
  }

  // ─── Coming Soon view ───

  const COMING_SOON = [
    { title: 'Tiṅanta — Verbal Conjugation', desc: 'All 10 gaṇas × 10 lakāras, active and middle voice.', effort: '4–6 weeks' },
    { title: 'Samāsa — Compound Formation', desc: 'Six compound types (Tatpuruṣa, Bahuvrīhi, Dvandva, etc.) with vigraha splitting.', effort: '2–3 weeks' },
    { title: 'Nirukta Engine', desc: 'Etymological analysis using Yāska\'s principles.', effort: '2–3 weeks' },
    { title: 'Kalpa — Ritual Sequence', desc: 'Śrauta, Gṛhya, and Dharma Sūtra ritual validation.', effort: '3–4 weeks' },
    { title: 'Jyotiṣa — Calendar Engine', desc: 'Pañcāṅga computation and astronomical timekeeping.', effort: '4–6 weeks' },
    { title: 'Purāṇa Corpus', desc: '18 Mahāpurāṇas + 18 Upapurāṇas as searchable text.', effort: '3–4 weeks' },
    { title: 'Bhakti Corpus', desc: 'Divya Prabandham, Tirumurai, and vernacular devotional classics.', effort: '2 weeks' },
    { title: 'Brahma Sūtra Concordance', desc: 'Commentarial matrix across 7 Vedāntic schools (Saṅkara, Rāmānuja, Madhva, etc.).', effort: '2–3 months' },
    { title: 'Arthaśāstra Engine', desc: 'Kauṭilyan policy reasoning and statecraft analysis.', effort: '2–3 months' },
    { title: 'Nāṭyaśāstra Rasa Analysis', desc: 'Aesthetic experience and performance grammar.', effort: '2–3 months' },
    { title: 'Āgamic & Tantric Systems', desc: 'Śaiva Siddhānta, Vaiṣṇava Pāñcarātra, Śākta Śrī Vidyā.', effort: '6–12 months' },
  ];

  function buildComingSoonView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Coming Soon' }),
        el('p', { class: 'panel-sub', text: 'Planned extensions and capabilities. Each has an effort estimate. Order is by priority.' }),
      ]),
    ]));

    const grid = el('div', { class: 'soon-grid' });
    for (let i = 0; i < COMING_SOON.length; i++) {
      const item = COMING_SOON[i];
      grid.appendChild(el('div', { class: 'soon-card' }, [
        el('div', { class: 'soon-card-head' }, [
          el('h3', { text: item.title }),
          el('span', { class: 'soon-badge', text: item.effort }),
        ]),
        el('p', { class: 'soon-desc', text: item.desc }),
      ]));
    }
    fragment.appendChild(grid);

    return fragment;
  }
  // ─── Changelog view ───

  function buildChangelogView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Changelog' }),
        el('p', { class: 'panel-sub', text: 'Release history. Machine-readable at /api/v3/changelog.' }),
      ]),
    ]));

    const output = el('div', { class: 'changelog-list' }, [
      el('p', { class: 'placeholder', text: 'Loading releases…' }),
    ]);
    fragment.appendChild(output);

    getJSON(API.CHANGELOG)
      .then(function (data) {
        const releases = (data && data.releases) || [];
        if (releases.length === 0) {
          output.replaceChildren(el('p', { class: 'placeholder', text: 'No releases yet.' }));
          return;
        }

        const cards = [];
        for (let i = 0; i < releases.length; i++) {
          const r = releases[i];
          const changes = r.changes || {};
          const body = [];

          if (changes.added && changes.added.length) {
            body.push(el('h3', { text: 'Added' }));
            const ul = el('ul');
            for (let j = 0; j < changes.added.length; j++) {
              ul.appendChild(el('li', { text: changes.added[j] }));
            }
            body.push(ul);
          }
          if (changes.fixed && changes.fixed.length) {
            body.push(el('h3', { text: 'Fixed' }));
            const ul2 = el('ul');
            for (let k = 0; k < changes.fixed.length; k++) {
              ul2.appendChild(el('li', { text: changes.fixed[k] }));
            }
            body.push(ul2);
          }

          cards.push(el('article', { class: 'panel changelog-entry' }, [
            el('header', { class: 'panel-head' }, [
              el('h3', { text: 'v' + r.version + ' — ' + r.name }),
              el('p', { class: 'panel-sub', text: r.date }),
            ]),
          ].concat(body)));
        }

        output.replaceChildren(...cards);
      })
      .catch(function (err) {
        output.replaceChildren(
          el('p', { class: 'placeholder', text: 'Could not load changelog: ' + err.message })
        );
      });

    return fragment;
  }

  // ─── About view ───

  function buildAboutView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'About Aigaane' }),
        el('p', { class: 'panel-sub', text: 'A deterministic-plus-agentic platform for Sanskrit language and literature.' }),
      ]),
    ]));

    const grid = el('div', { class: 'about-grid' });

    grid.appendChild(el('div', { class: 'about-card' }, [
      el('h3', { text: 'Architecture' }),
      el('p', { text: 'Two-track design. Track B is a deterministic Pāṇinian compiler — no LLM, no stochastic behavior. Track A is an agentic RAG layer that generates content but delegates every verification to Track B.' }),
    ]));

    const endpointsCard = el('div', { class: 'about-card' }, [
      el('h3', { text: 'Live Endpoints' }),
    ]);
    const endpointList = el('ul', { class: 'about-endpoints' });
    const endpoints = [
      { path: 'POST /api/v3/sandhi', note: 'Public · Sandhi engine' },
      { path: 'POST /api/v3/chandas/scan', note: 'Public · Laghu/Guru scansion' },
      { path: 'POST /api/v3/chandas/anustubh', note: 'Public · Anuṣṭubh validator' },
      { path: 'POST /api/v3/chandas/trishtubh', note: 'Public · Triṣṭubh validator' },
      { path: 'POST /api/v3/chandas/jagati', note: 'Public · Jagatī validator' },
      { path: 'POST /api/v3/morphology/noun/inflect', note: 'Public · Subanta paradigm' },
      { path: 'POST /api/v3/corpus/search', note: 'Public · Itihāsa search' },
      { path: 'POST /api/v3/export/pdf', note: 'Public · PDF export' },
      { path: 'POST /api/v3/agent/lyric', note: 'X-API-Key · Agentic generation' },
      { path: 'POST /api/v3/agent/refine', note: 'X-API-Key · Multi-turn refinement' },
      { path: 'GET /api/v3/changelog', note: 'Public · Release history' },
    ];
    for (let i = 0; i < endpoints.length; i++) {
      endpointList.appendChild(el('li', {}, [
        el('code', { text: endpoints[i].path }),
        el('span', { text: ' · ' + endpoints[i].note }),
      ]));
    }
    endpointsCard.appendChild(endpointList);
    grid.appendChild(endpointsCard);

    grid.appendChild(el('div', { class: 'about-card' }, [
      el('h3', { text: 'Philological Foundation' }),
      el('p', { text: 'Grounded in the complete Hindu Śāstra taxonomy. Every sūtra cited. Every category documented. Six Vedāṅgas mapped; three implemented computationally.' }),
    ]));

    grid.appendChild(el('div', { class: 'about-card' }, [
      el('h3', { text: 'Deterministic Guarantee' }),
      el('p', { text: 'Given the same input, the engine always returns the same output. No LLM self-scanning. No hallucination in phonology, scansion, or meter validation.' }),
    ]));

    fragment.appendChild(grid);
    return fragment;
  }

  // ─── Tabs ───

  function mountTab(tabName) {
    const viewport = $('#viewport');
    if (!viewport) return;
    clearNode(viewport);

    switch (tabName) {
      case 'sanskrit':
        Promise.all([
          getJSON(API.INFO).catch(function () { return null; }),
          getJSON(API.HEALTH).catch(function () { return null; }),
        ]).then(function (results) {
          viewport.replaceChildren(buildSandhiView(results[0], results[1]));
          viewport.appendChild(buildChandasView());
        });
        break;
      case 'agent':
        viewport.replaceChildren(buildAgentView());
        break;
      case 'morphology':
        viewport.replaceChildren(buildMorphologyView());
        break;
      case 'corpus':
        viewport.replaceChildren(buildCorpusView());
        break;
      case 'sastra':
        viewport.replaceChildren(buildSastraView());
        break;
      case 'soon':
        viewport.replaceChildren(buildComingSoonView());
        break;
      case 'about':
        viewport.replaceChildren(buildAboutView());
        break;
      default:
        viewport.replaceChildren(buildSandhiView(null, null));
        viewport.appendChild(buildChandasView());
    }

    $$('.nav-btn').forEach(function (btn) {
      const isActive = btn.getAttribute('data-tab') === tabName;
      btn.classList.toggle('active', isActive);
      if (isActive) btn.setAttribute('aria-current', 'page');
      else btn.removeAttribute('aria-current');
    });
  }

  // ─── Health probe ───

  async function probeHealth() {
    const dot = $('#status-dot');
    const text = $('#status-text');
    if (!dot || !text) return;
    try {
      await postJSON(API.SANDHI, { p1: 'a', p2: 'a' });
      dot.classList.add('online');
      dot.classList.remove('offline');
      text.textContent = 'API online';
    } catch (err) {
      dot.classList.add('offline');
      dot.classList.remove('online');
      text.textContent = 'API unreachable';
    }
  }

  // ─── Bootstrap ───

  function init() {
    const year = $('#year');
    if (year) year.textContent = String(new Date().getFullYear());

    $$('.nav-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        mountTab(btn.getAttribute('data-tab') || 'sanskrit');
      });
    });

    mountTab('sanskrit');
    probeHealth();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();