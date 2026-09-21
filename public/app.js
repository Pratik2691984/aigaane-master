// public/app.js
// Aigaane — Sanskrit Engine Frontend
// Track B: /api/v3/sandhi, /api/v3/chandas/{scan,anustubh}
// Track A: /api/v3/agent/lyric (requires X-API-Key)

(() => {
  'use strict';

  // ─────────────────────── Configuration ───────────────────────

  const API = Object.freeze({
    INFO:     '/api/info',
    HEALTH:   '/api/health',
    SANDHI:   '/api/v3/sandhi',
    SCAN:     '/api/v3/chandas/scan',
    ANUSTUBH: '/api/v3/chandas/anustubh',
    AGENT:    '/api/v3/agent/lyric',
  });

  const LIMITS = Object.freeze({
    PHONEME_MAX: 8,
    TEXT_MAX:    2000,
    TIMEOUT_MS:  15000,
  });

  // ─────────────────────── DOM helpers ───────────────────────

  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /** Create an element with class, text, and attributes. Never uses innerHTML. */
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

  function clearNode(node) { node.replaceChildren(); }

  /** Sanitize user input before sending to the API. */
  function sanitize(s, maxLen) {
    if (typeof s !== 'string') return '';
    return s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
            .slice(0, maxLen)
            .trim();
  }

  /** POST JSON with timeout and safe error handling. */
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
        const msg = typeof data.detail === 'string' ? data.detail : `HTTP ${res.status}`;
        throw new Error(msg);
      }
      return data;
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error('Request timed out');
      throw err;
    }
  }

  /** GET JSON with timeout. */
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
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error('Request timed out');
      throw err;
    }
  }

  // ─────────────────────── Output helpers ───────────────────────

  function clearOutput(node) {
    node.replaceChildren(el('p', { class: 'placeholder', text: 'Result will appear here.' }));
    node.classList.remove('has-error', 'has-success');
  }

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

  // ─────────────────────── Sandhi view ───────────────────────

  function renderSandhiResult(node, data) {
    const wrapper = el('div', { class: 'output-result' }, [
      el('div', { class: 'output-eq' }, [
        el('span', { class: 'in',    text: data.p1 }),
        el('span', { class: 'arrow', text: ' + ' }),
        el('span', { class: 'in',    text: data.p2 }),
        el('span', { class: 'arrow', text: ' → ' }),
        el('span', { class: 'out',   text: data.result }),
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
            ? `Online · v${health.version}${health.current_golden_build ? ' · ' + health.current_golden_build : ''}`
            : 'Online · engine ready' }),
        ]),
      ])
    );

    const p1 = el('input', { attrs: { type: 'text', id: 'sandhi-p1', maxlength: '8',
      placeholder: 'a or aḥ', value: 'a', spellcheck: 'false', autocomplete: 'off' } });
    const p2 = el('input', { attrs: { type: 'text', id: 'sandhi-p2', maxlength: '8',
      placeholder: 'i or iti', value: 'i', spellcheck: 'false', autocomplete: 'off' } });
    const swapBtn  = el('button', { class: 'btn btn-ghost', text: 'Swap', attrs: { type: 'button' } });
    const clearBtn = el('button', { class: 'btn btn-ghost', text: 'Clear', attrs: { type: 'button' } });
    const submit   = el('button', { class: 'btn btn-primary', text: 'Combine', attrs: { type: 'submit' } });
    const output   = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
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
        ...[
          ['a', 'i'], ['a', 'a'], ['a', 'e'],
          ['i', 'a'], ['t', 'c'], ['aḥ', 'a'],
        ].map(([a, b]) =>
          el('button', { class: 'chip', text: `${a} + ${b}`,
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
      p1.value = ''; p2.value = ''; clearOutput(output); p1.focus();
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

  // ─────────────────────── Chandas view ───────────────────────

  function renderScansion(node, data) {
    const syllables = Array.isArray(data.syllables) ? data.syllables : [];
    const nodes = [];
    nodes.push(el('p', { class: 'pattern-line', text: data.pattern || '' }));

    const grid = el('div', { class: 'pattern' });
    for (const s of syllables) {
      const weight = s.weight === 'G' ? 'Guru −' : 'Laghu ⏑';
      grid.appendChild(el('div', {
        class: 'syllable',
        attrs: { 'aria-label': `${s.text} ${weight}` },
      }, [
        el('span', { class: 'glyph', text: s.text }),
        el('span', { class: 'weight ' + s.weight, text: s.weight }),
      ]));
    }
    nodes.push(grid);

    nodes.push(el('div', { class: 'output-result' }, [
      el('span', { class: 'rule-tag', text: `${data.length} syllables` }),
      data.is_valid_anuṣṭubh
        ? el('span', { class: 'rule-tag', text: '32 — possible Anuṣṭubh' })
        : null,
    ].filter(Boolean)));

    node.replaceChildren(...nodes);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function renderAnustubh(node, data) {
    const nodes = [];
    nodes.push(el('div', {
      class: 'validation-summary ' + (data.is_valid ? 'valid' : 'invalid'),
    }, [
      el('span', { class: 'label', text: data.is_valid ? '✓ Valid Anuṣṭubh' : '✗ Not a valid Anuṣṭubh' }),
    ]));

    if (Array.isArray(data.padas) && data.padas.length) {
      const list = el('div', { class: 'pada-list' });
      for (const p of data.padas) {
        const row = el('div', {
          class: 'pada ' + (p.is_valid ? 'is-valid' : 'is-invalid'),
        }, [
          el('span', { class: 'pada-num', text: `Pāda ${p.index}` }),
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

    const anusText = el('textarea', { attrs: { rows: '4', maxlength: '2000',
      spellcheck: 'false', placeholder: 'tapaḥsvādhyāyanirataṃ tapasvī vāgvidāṃ varam' } });
    anusText.value = 'tapaḥsvādhyāyanirataṃ tapasvī vāgvidāṃ varam';
    const anusOutput = el('div', { class: 'output', attrs: { 'aria-live': 'polite' } }, [
      el('p', { class: 'placeholder', text: 'Validation will appear here.' }),
    ]);
    const anusForm = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Anuṣṭubh verse (IAST, 32 syllables)' }),
        anusText,
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
        el('h2', { text: 'Anuṣṭubh Validator' }),
        el('p', { class: 'panel-sub', text: 'Pathyā + five Vipulā variations.' }),
      ]),
      anusForm,
      anusOutput,
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

    anusForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = sanitize(anusText.value, LIMITS.TEXT_MAX);
      if (!text) { renderError(anusOutput, 'Enter a verse to validate.'); return; }
      renderLoading(anusOutput);
      try {
        const data = await postJSON(API.ANUSTUBH, { text });
        renderAnustubh(anusOutput, data);
      } catch (err) { renderError(anusOutput, err.message); }
    });

    return fragment;
  }

  // ─────────────────────── Agent view ───────────────────────

  function buildAgentView() {
    const fragment = document.createDocumentFragment();

    const prompt = el('textarea', {
      attrs: { rows: '3', maxlength: '2000',
               placeholder: 'Saraswatī Vandana in Anuṣṭubh' },
    });
    prompt.value = 'Saraswatī Vandana in Anuṣṭubh';

    const apiKeyInput = el('input', {
      attrs: { type: 'password', maxlength: '128',
               placeholder: 'API key (X-API-Key)',
               autocomplete: 'off', spellcheck: 'false' },
    });

    const output = el('div', {
      class: 'output', attrs: { 'aria-live': 'polite' },
    }, [
      el('p', { class: 'placeholder', text: 'Verse will stream here.' }),
    ]);

    const form = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Prompt' }),
        prompt,
      ]),
      el('label', {}, [
        el('span', { class: 'label', text: 'API Key (not stored)' }),
        apiKeyInput,
        el('small', { class: 'hint',
                      text: 'Sent as X-API-Key header. Never logged or persisted.' }),
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Generate',
                       attrs: { type: 'submit' } }),
      ]),
    ]);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const key = apiKeyInput.value.trim();
      if (!key) { renderError(output, 'API key required'); return; }
      renderLoading(output);

      try {
        const res = await fetch(API.AGENT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': key,
          },
          body: JSON.stringify({ prompt: prompt.value, meter: 'anuṣṭubh' }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Request failed' }));
          renderError(output, err.detail || `HTTP ${res.status}`);
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        const stages = [];
        let buffer = '';

        const log = el('pre', { class: 'stream-log' });
        output.replaceChildren(log);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try {
              const event = JSON.parse(line.slice(6));
              stages.push(event);
              log.textContent += JSON.stringify(event, null, 2) + '\n';
              log.scrollTop = log.scrollHeight;
            } catch { /* skip malformed */ }
          }
        }

        const last = stages[stages.length - 1];
        if (last && last.stage === 'complete') {
          const header = el('p', { class: 'pattern-line', text: last.pattern || '' });
          const verse = el('pre', { class: 'verse-output', text: last.verse });
          const tag = el('span', {
            class: 'rule-tag',
            text: `Quanta: ${last.quanta?.spent ?? '?'} / ${last.quanta?.ceiling ?? '?'}`,
          });
          output.replaceChildren(verse, header, tag);
          output.classList.add('has-success');
        } else {
          renderError(output, last?.message || 'Generation incomplete');
        }
      } catch (err) {
        renderError(output, err.message);
      }
    });

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Agentic Verse Generator' }),
        el('p', { class: 'panel-sub',
                  text: 'Generates metrically-validated Sanskrit verse. Every draft is scanned by the deterministic engine.' }),
      ]),
      form,
      output,
    ]));

    return fragment;
  }

  // ─────────────────────── Tabs ───────────────────────

  function mountTab(tabName) {
    const viewport = $('#viewport');
    if (!viewport) return;
    clearNode(viewport);

    if (tabName === 'sanskrit') {
      Promise.all([
        getJSON(API.INFO).catch(() => null),
        getJSON(API.HEALTH).catch(() => null),
      ]).then(([info, health]) => {
        viewport.replaceChildren(buildSandhiView(info, health));
        viewport.appendChild(buildChandasView());
      });
    } else if (tabName === 'agent') {
      viewport.replaceChildren(buildAgentView());
    }

    $$('.nav-btn').forEach((btn) => {
      const isActive = btn.getAttribute('data-tab') === tabName;
      btn.classList.toggle('active', isActive);
      if (isActive) btn.setAttribute('aria-current', 'page');
      else btn.removeAttribute('aria-current');
    });
  }

  // ─────────────────────── Health probe ───────────────────────

  async function probeHealth() {
    const dot  = $('#status-dot');
    const text = $('#status-text');
    if (!dot || !text) return;
    try {
      await postJSON(API.SANDHI, { p1: 'a', p2: 'a' });
      dot.classList.add('online');
      dot.classList.remove('offline');
      text.textContent = 'API online';
    } catch {
      dot.classList.add('offline');
      dot.classList.remove('online');
      text.textContent = 'API unreachable';
    }
  }

  // ─────────────────────── Bootstrap ───────────────────────

  function init() {
    const year = $('#year');
    if (year) year.textContent = String(new Date().getFullYear());

    $$('.nav-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
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