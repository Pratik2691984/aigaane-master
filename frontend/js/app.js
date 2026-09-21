/**
 * Aigaane — Track B Frontend
 * Deterministic Sanskrit sandhi + chandas client.
 *
 * Security posture:
 *  - No eval, no innerHTML with user content, no dynamic script tags.
 *  - All DOM updates via textContent / createElement.
 *  - All fetch calls pinned to same-origin /api/** (CSP enforced).
 *  - Input is length-bounded before send.
 *  - No credentials, no secrets, no cookies.
 */

(() => {
  'use strict';

  // ─────────────────────── Configuration ───────────────────────

  const API = Object.freeze({
    SANDHI:   '/api/v4/sandhi',
    SCAN:     '/api/v3/chandas/scan',
    ANUSTUBH: '/api/v3/chandas/anustubh',
    HEALTH:   '/api/v3/sandhi', // best-effort ping
  });

  const LIMITS = Object.freeze({
    PHONEME_MAX: 8,
    TEXT_MAX:    2000,
    TIMEOUT_MS:  15000,
  });

  // ─────────────────────── Utilities ───────────────────────

  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /** Create an element with optional class and text. Never uses innerHTML. */
  function el(tag, opts = {}, children = []) {
    const node = document.createElement(tag);
    if (opts.class)   node.className = opts.class;
    if (opts.text)    node.textContent = opts.text;
    if (opts.attrs)   for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
    if (opts.dataset) for (const [k, v] of Object.entries(opts.dataset)) node.dataset[k] = v;
    for (const child of children) {
      node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    }
    return node;
  }

  /** Safe fetch with timeout and JSON parsing. */
  async function postJSON(url, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), LIMITS.TIMEOUT_MS);
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: controller.signal,
        credentials: 'omit',
        mode: 'same-origin',
        cache: 'no-store',
      });
      clearTimeout(timer);
      const data = await res.json().catch(() => ({ detail: 'Invalid JSON response' }));
      if (!res.ok) {
        const message = typeof data.detail === 'string'
          ? data.detail
          : `Request failed with status ${res.status}`;
        throw new Error(message);
      }
      return data;
    } catch (err) {
      clearTimeout(timer);
      if (err.name === 'AbortError') throw new Error('Request timed out');
      throw err;
    }
  }

  /** Sanitize user input before send. */
  function sanitize(s, maxLen) {
    if (typeof s !== 'string') return '';
    // Strip control characters except standard whitespace.
    return s.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
            .slice(0, maxLen)
            .trim();
  }

  /** Clear an output region. */
  function clearOutput(node) {
    node.replaceChildren(el('p', { class: 'placeholder', text: 'Result will appear here.' }));
    node.classList.remove('has-error', 'has-success');
  }

  /** Render an error in an output region. */
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

  /** Render a loading state. */
  function renderLoading(node) {
    node.replaceChildren(el('div', { class: 'loading', text: 'Computing…' }));
    node.classList.remove('has-error', 'has-success');
  }

  // ─────────────────────── Sandhi ───────────────────────

  function renderSandhi(node, data) {
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

  function bindSandhi() {
    const form   = $('#sandhi-form');
    const p1     = $('#sandhi-p1');
    const p2     = $('#sandhi-p2');
    const output = $('#sandhi-output');
    const swap   = $('#sandhi-swap');
    const clear  = $('#sandhi-clear');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const v1 = sanitize(p1.value, LIMITS.PHONEME_MAX);
      const v2 = sanitize(p2.value, LIMITS.PHONEME_MAX);

      if (!v1 || !v2) {
        renderError(output, 'Both inputs are required.');
        return;
      }

      renderLoading(output);
      try {
        const data = await postJSON(API.SANDHI, { p1: v1, p2: v2 });
        renderSandhi(output, data);
      } catch (err) {
        renderError(output, err.message);
      }
    });

    swap.addEventListener('click', () => {
      const a = p1.value;
      p1.value = p2.value;
      p2.value = a;
      p1.focus();
    });

    clear.addEventListener('click', () => {
      p1.value = '';
      p2.value = '';
      clearOutput(output);
      p1.focus();
    });

    // Presets
    $$('.chip[data-sandhi-p1]').forEach((chip) => {
      chip.addEventListener('click', () => {
        p1.value = chip.dataset.sandhiP1 || '';
        p2.value = chip.dataset.sandhiP2 || '';
        form.requestSubmit();
      });
    });
  }

  // ─────────────────────── Chandas ───────────────────────

  function renderScansion(node, data) {
    const syllables = Array.isArray(data.syllables) ? data.syllables : [];
    const nodes = [];

    // Pattern line
    nodes.push(el('p', { class: 'pattern-line', text: data.pattern || '' }));

    // Syllable grid
    const grid = el('div', { class: 'pattern' });
    for (const s of syllables) {
      const weight = s.weight === 'G' ? 'Guru −' : 'Laghu ⏑';
      grid.appendChild(
        el('div', { class: 'syllable', attrs: { 'aria-label': `${s.text} ${weight}` } }, [
          el('span', { class: 'glyph',  text: s.text }),
          el('span', { class: 'weight ' + s.weight, text: s.weight }),
        ])
      );
    }
    nodes.push(grid);

    // Summary
    nodes.push(
      el('div', { class: 'output-result' }, [
        el('span', { class: 'rule-tag', text: `${data.length} syllables` }),
        data.is_valid_anuṣṭubh
          ? el('span', { class: 'rule-tag', text: '32 — possible Anuṣṭubh' })
          : null,
      ].filter(Boolean))
    );

    node.replaceChildren(...nodes);
    node.classList.add('has-success');
    node.classList.remove('has-error');
  }

  function bindChandas() {
    const form   = $('#chandas-form');
    const input  = $('#chandas-text');
    const output = $('#chandas-output');
    const clear  = $('#chandas-clear');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = sanitize(input.value, LIMITS.TEXT_MAX);
      if (!text) {
        renderError(output, 'Enter some text to scan.');
        return;
      }
      renderLoading(output);
      try {
        const data = await postJSON(API.SCAN, { text });
        renderScansion(output, data);
      } catch (err) {
        renderError(output, err.message);
      }
    });

    clear.addEventListener('click', () => {
      input.value = '';
      clearOutput(output);
      input.focus();
    });
  }

  // ─────────────────────── Anuṣṭubh ───────────────────────

  function renderAnustubh(node, data) {
    const nodes = [];

    // Summary banner
    const banner = el('div', {
      class: 'validation-summary ' + (data.is_valid ? 'valid' : 'invalid'),
    }, [
      el('span', { class: 'label', text: data.is_valid ? '✓ Valid Anuṣṭubh' : '✗ Not a valid Anuṣṭubh' }),
    ]);
    nodes.push(banner);

    // Pāda list
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
        if (p.reason) {
          row.appendChild(el('span', { class: 'pada-reason', text: p.reason }));
        }
        list.appendChild(row);
      }
      nodes.push(list);
    }

    // Errors
    if (Array.isArray(data.errors) && data.errors.length) {
      const ul = el('ul', { class: 'error-list' });
      for (const err of data.errors) ul.appendChild(el('li', { text: err }));
      nodes.push(ul);
    }

    node.replaceChildren(...nodes);
    node.classList.add(data.is_valid ? 'has-success' : 'has-error');
  }

  function bindAnustubh() {
    const form   = $('#anustubh-form');
    const input  = $('#anustubh-text');
    const output = $('#anustubh-output');
    const clear  = $('#anustubh-clear');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = sanitize(input.value, LIMITS.TEXT_MAX);
      if (!text) {
        renderError(output, 'Enter a verse to validate.');
        return;
      }
      renderLoading(output);
      try {
        const data = await postJSON(API.ANUSTUBH, { text });
        renderAnustubh(output, data);
      } catch (err) {
        renderError(output, err.message);
      }
    });

    clear.addEventListener('click', () => {
      input.value = '';
      clearOutput(output);
      input.focus();
    });
  }

  // ─────────────────────── Health check ───────────────────────

  async function probeHealth() {
    const dot  = $('#status-dot');
    const text = $('#status-text');
    if (!dot || !text) return;

    try {
      await postJSON(API.HEALTH, { p1: 'a', p2: 'a' });
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
    const yearNode = $('#year');
    if (yearNode) yearNode.textContent = String(new Date().getFullYear());

    bindSandhi();
    bindChandas();
    bindAnustubh();
    probeHealth();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();