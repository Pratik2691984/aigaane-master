// public/app.js
// Aigaane — Frontend
// Live tabs: Sanskrit (Track B), Agent (Track A)
// Informational tabs: Śāstra (taxonomy), Coming Soon, About
//
// Week 1 additions:
//   - Meter selector (Anuṣṭubh / Triṣṭubh / Jagatī)
//   - PDF export button
//   - Multi-turn refinement panel
//   - Updated Coming Soon and About content

(() => {
  'use strict';

  // ─────────────────────── Configuration ───────────────────────

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
  });

  const LIMITS = Object.freeze({
    PHONEME_MAX: 8,
    TEXT_MAX:    2000,
    TIMEOUT_MS:  15000,
  });

  // ─────────────────────── Śāstra taxonomy data ───────────────────────

  const SASTRA_TREE = {
    sruti: {
      label: 'Śruti — Axiomatic Core',
      subtitle: 'That which is heard (revealed, authorless)',
      children: [
        {
          name: 'Ṛgveda',
          subtitle: 'Hymns of cosmic order',
          status: 'metadata',
          meta: 'Saṃhitā: 10 Maṇḍalas · 1,028 Sūktas · 10,552+ verses',
          parts: [
            { name: 'Saṃhitā' },
            { name: 'Brāhmaṇas', meta: 'Aitareya, Kauṣītaki / Śāṅkhāyana' },
            { name: 'Āraṇyakas', meta: 'Aitareya, Kauṣītaki' },
            { name: 'Upaniṣads', meta: 'Aitareya, Kauṣītaki' },
          ],
        },
        {
          name: 'Śukla Yajurveda',
          subtitle: 'White Yajurveda — ritual formulas',
          status: 'metadata',
          meta: 'Vājasaneyi Saṃhitā · Mādhyandina & Kāṇva recensions',
          parts: [
            { name: 'Śatapatha Brāhmaṇa', meta: '100 Adhyāyas' },
            { name: 'Āraṇyaka', meta: 'Embedded in 14th Kāṇḍa' },
            { name: 'Upaniṣads', meta: 'Īśā, Bṛhadāraṇyaka' },
          ],
        },
        {
          name: 'Kṛṣṇa Yajurveda',
          subtitle: 'Black Yajurveda — mantras with prose',
          status: 'metadata',
          meta: 'Taittirīya, Maitrāyaṇī, Kaṭha, Kapiṣṭhala',
          parts: [
            { name: 'Taittirīya Brāhmaṇa' },
            { name: 'Taittirīya Āraṇyaka' },
            { name: 'Upaniṣads', meta: 'Taittirīya, Kaṭha, Śvetāśvatara, Maitrāyaṇī' },
          ],
        },
        {
          name: 'Sāmaveda',
          subtitle: 'Musical & melodic chants',
          status: 'metadata',
          meta: '1,875 verses (derived from Ṛgveda) · Kauthuma, Rāṇāyanīya, Jaiminīya',
          parts: [
            { name: 'Brāhmaṇas', meta: 'Pañcaviṃśa / Tāṇḍya, Ṣaḍviṃśa, Jaiminīya' },
            { name: 'Āraṇyaka', meta: 'Jaiminīya Āraṇyaka' },
            { name: 'Upaniṣads', meta: 'Chāndogya, Kena' },
          ],
        },
        {
          name: 'Atharvaveda',
          subtitle: 'Daily life, healing, protection',
          status: 'metadata',
          meta: '20 Kāṇḍas · 730 hymns · Śaunaka & Paippalāda',
          parts: [
            { name: 'Gopatha Brāhmaṇa' },
            { name: 'Upaniṣads', meta: 'Praśna, Muṇḍaka, Māṇḍūkya' },
          ],
        },
        {
          name: 'Muktikā Canon',
          subtitle: '108 Upaniṣads by Vedic Śākhā',
          status: 'metadata',
          parts: [
            { name: 'Ṛgveda', meta: '10 Upaniṣads' },
            { name: 'Śukla Yajurveda', meta: '19 Upaniṣads' },
            { name: 'Kṛṣṇa Yajurveda', meta: '32 Upaniṣads' },
            { name: 'Sāmaveda', meta: '16 Upaniṣads' },
            { name: 'Atharvaveda', meta: '31 Upaniṣads' },
          ],
        },
      ],
    },
    smrti: {
      label: 'Smṛti — Hermeneutic Closure',
      subtitle: 'That which is remembered (tradition-anchored)',
      children: [
        {
          name: 'Vedāṅgas',
          subtitle: 'Six structural auxiliary disciplines',
          status: 'partial',
          parts: [
            { name: 'Śikṣā', meta: 'Phonetics & phonology', status: 'live', link: 'sanskrit' },
            { name: 'Vyākaraṇa', meta: 'Grammar (Pāṇini) — sandhi implemented', status: 'partial', link: 'sanskrit' },
            { name: 'Chandas', meta: 'Prosody (Piṅgala) — Anuṣṭubh, Triṣṭubh, Jagatī', status: 'partial', link: 'sanskrit' },
            { name: 'Nirukta', meta: 'Etymology & semantics (Yāska)', status: 'coming' },
            { name: 'Kalpa', meta: 'Ritual mechanics', status: 'coming' },
            { name: 'Jyotiṣa', meta: 'Astronomy & calendar', status: 'coming' },
          ],
        },
        {
          name: 'Ṣaḍ Darśanas',
          subtitle: 'Six classical philosophical systems',
          status: 'metadata',
          parts: [
            { name: 'Nyāya', meta: 'Logic — Akṣapāda Gautama' },
            { name: 'Vaiśeṣika', meta: 'Atomism — Kaṇāda' },
            { name: 'Sāṅkhya', meta: 'Puruṣa & Prakṛti — Kapila' },
            { name: 'Yoga', meta: 'Meditation — Patañjali' },
            { name: 'Pūrva Mīmāṃsā', meta: 'Hermeneutics — Jaimini' },
            { name: 'Uttara Mīmāṃsā', meta: 'Vedānta — Bādarāyaṇa' },
          ],
        },
        {
          name: 'Itihāsas',
          subtitle: 'Epic historical narratives',
          status: 'metadata',
          parts: [
            { name: 'Rāmāyaṇa', meta: 'Vālmīki — 7 Kāṇḍas · 24,000 verses' },
            { name: 'Mahābhārata', meta: 'Vyāsa — 18 Parvas · 100,000 verses' },
          ],
        },
        {
          name: 'Purāṇas',
          subtitle: 'Cyclic cosmogony & universal history',
          status: 'metadata',
          parts: [
            { name: 'Sāttvika', meta: 'Viṣṇu, Bhāgavata, Nārada, Garuḍa, Padma, Varāha' },
            { name: 'Rājasika', meta: 'Brahmā, Brahmāṇḍa, Brahmavaivarta, Mārkaṇḍeya, Bhaviṣya, Vāmana' },
            { name: 'Tāmasika', meta: 'Śiva, Liṅga, Skanda, Agni, Matsya, Kūrma' },
            { name: 'Upapurāṇas', meta: '18 secondary texts' },
          ],
        },
        {
          name: 'Dharmaśāstras',
          subtitle: 'Social ethics & civil law',
          status: 'metadata',
          parts: [
            { name: 'Dharma Sūtras', meta: 'Āpastamba, Gautama, Baudhāyana, Vasiṣṭha' },
            { name: 'Dharma Smṛtis', meta: 'Manusmṛti, Yājñavalkya, Nārada, Parāśara' },
          ],
        },
        {
          name: 'Upavedas',
          subtitle: 'Four classical applied sciences',
          status: 'metadata',
          parts: [
            { name: 'Āyurveda', meta: 'Medicine & health (Ṛg/Atharvaveda)' },
            { name: 'Dhanurveda', meta: 'Martial arts & warfare (Yajurveda)' },
            { name: 'Gāndharvaveda', meta: 'Music & dramaturgy (Sāmaveda)' },
            { name: 'Sthāpatyaveda', meta: 'Architecture & Vāstu (Atharvaveda)' },
          ],
        },
        {
          name: 'Āgamas & Tantras',
          subtitle: 'Initiatory practice, iconography',
          status: 'metadata',
          parts: [
            { name: 'Śaiva Āgamas', meta: '28 Siddhānta Āgamas + Kashmir Trika' },
            { name: 'Vaiṣṇava Āgamas', meta: 'Pāñcarātra & Vaikhānasa' },
            { name: 'Śākta Tantras', meta: '64 Tantras, Śrī Vidyā, Kālī Kula' },
          ],
        },
        {
          name: 'Bhakti Sādhana',
          subtitle: 'Devotional classics & poetics',
          status: 'metadata',
          parts: [
            { name: 'Bhakti Sūtras', meta: 'Nārada, Śāṇḍilya' },
            { name: 'Dravidian Canons', meta: 'Divya Prabandham, Tevāram' },
            { name: 'Regional Classics', meta: 'Rāmacaritamānasa, Sūrsāgar, Gītagovinda' },
          ],
        },
        {
          name: 'Prakaraṇa Granthas',
          subtitle: 'Independent philosophical treatises',
          status: 'metadata',
          parts: [
            { name: 'Advaita', meta: 'Vivekacūḍāmaṇi, Upadeśasāhasrī, Pañcadaśī' },
            { name: 'Radical Non-dualism', meta: 'Aṣṭāvakra Gītā, Yoga Vāsiṣṭha' },
          ],
        },
      ],
    },
    purusartha: {
      label: 'Puruṣārtha — Applied Objectives',
      subtitle: 'Secular & supporting texts',
      children: [
        {
          name: 'Arthaśāstra',
          subtitle: 'Political economy & statecraft',
          status: 'metadata',
          meta: 'Kauṭilya',
        },
        {
          name: 'Nāṭyaśāstra',
          subtitle: 'Dramaturgy & aesthetics (Rasa)',
          status: 'metadata',
          meta: 'Bharata Muni',
        },
        {
          name: 'Kāma Sūtra',
          subtitle: 'Social dynamics & erotics',
          status: 'metadata',
          meta: 'Vātsyāyana',
        },
        {
          name: 'Bṛhat Saṃhitā',
          subtitle: 'Physical sciences & divination',
          status: 'metadata',
          meta: 'Varāhamihira',
        },
        {
          name: 'Nīti Literature',
          subtitle: 'Strategic pedagogy',
          status: 'metadata',
          meta: 'Pañcatantra, Hitopadeśa',
        },
      ],
    },
  };

  // Coming Soon — updated to remove Week 1 completed items

  const COMING_SOON = [
    {
      title: 'Subanta — Nominal Declension',
      desc: 'Full Aṣṭādhyāyī 4.1.2 case endings for all stems (a, ā, i, u, ṛ, etc.).',
      effort: '3–4 weeks',
      status: 'planned',
    },
    {
      title: 'Tiṅanta — Verbal Conjugation',
      desc: 'All 10 gaṇas × 10 lakāras, active and middle voice.',
      effort: '4–6 weeks',
      status: 'planned',
    },
    {
      title: 'Samāsa — Compound Formation',
      desc: 'Six compound types (Tatpuruṣa, Bahuvrīhi, Dvandva, etc.) with vigraha splitting.',
      effort: '2–3 weeks',
      status: 'planned',
    },
    {
      title: 'Nirukta Engine',
      desc: "Etymological analysis using Yāska's principles.",
      effort: '2–3 weeks',
      status: 'planned',
    },
    {
      title: 'Kalpa — Ritual Sequence',
      desc: 'Śrauta, Gṛhya, and Dharma Sūtra ritual validation.',
      effort: '3–4 weeks',
      status: 'planned',
    },
    {
      title: 'Jyotiṣa — Calendar Engine',
      desc: 'Pañcāṅga computation and astronomical timekeeping.',
      effort: '4–6 weeks',
      status: 'planned',
    },
    {
      title: 'Itihāsa Corpus',
      desc: 'Full-text search over Rāmāyaṇa and Mahābhārata.',
      effort: '3–4 weeks',
      status: 'planned',
    },
    {
      title: 'Purāṇa Corpus',
      desc: '18 Mahāpurāṇas + 18 Upapurāṇas as searchable text.',
      effort: '3–4 weeks',
      status: 'planned',
    },
    {
      title: 'Bhakti Corpus',
      desc: 'Divya Prabandham, Tirumurai, and vernacular devotional classics.',
      effort: '2 weeks',
      status: 'planned',
    },
    {
      title: 'Brahma Sūtra Concordance',
      desc: 'Commentarial matrix across 7 Vedāntic schools (Śaṅkara, Rāmānuja, Madhva, etc.).',
      effort: '2–3 months',
      status: 'planned',
    },
    {
      title: 'Arthaśāstra Engine',
      desc: 'Kauṭilyan policy reasoning and statecraft analysis.',
      effort: '2–3 months',
      status: 'planned',
    },
    {
      title: 'Nāṭyaśāstra Rasa Analysis',
      desc: 'Aesthetic experience and performance grammar.',
      effort: '2–3 months',
      status: 'planned',
    },
    {
      title: 'Āgamic & Tantric Systems',
      desc: 'Śaiva Siddhānta, Vaiṣṇava Pāñcarātra, Śākta Śrī Vidyā.',
      effort: '6–12 months',
      status: 'planned',
    },
  ];

  // ─────────────────────── DOM helpers ───────────────────────

  const $  = (sel, root = document) => root.querySelector(sel);
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

  function clearNode(node) { node.replaceChildren(); }

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
      el('span', { class: 'label', text:
        data.is_valid ? `✓ Valid ${meterName}` : `✗ Not a valid ${meterName}` }),
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

    // ─── Unified meter validation panel (Anuṣṭubh / Triṣṭubh / Jagatī) ───

    const meterSelect = el('select', {
      class: 'meter-select',
      attrs: { id: 'meter-select' },
    }, [
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
      const meterName = meter === 'anustubh' ? 'Anuṣṭubh'
                       : meter === 'trishtubh' ? 'Triṣṭubh'
                       : 'Jagatī';
      try {
        const endpoint = meter === 'anustubh' ? API.ANUSTUBH
                        : meter === 'trishtubh' ? API.TRISHTUBH
                        : API.JAGATI;
        const data = await postJSON(endpoint, { text });
        renderMeterValidation(meterOutput, data, meterName);
      } catch (err) { renderError(meterOutput, err.message); }
    });

    return fragment;
  }

  // ─────────────────────── Agent view ───────────────────────

  function buildAgentView() {
    const fragment = document.createDocumentFragment();

    // ─── State shared across the view ───
    const state = {
      lastVerse: '',
      lastPattern: '',
      lastMeter: 'anuṣṭubh',
    };

    // ─── Prompt + API key + meter ───
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

    const meterSelect = el('select', {
      class: 'meter-select',
      attrs: { id: 'agent-meter' },
    }, [
      el('option', { text: 'Anuṣṭubh (4 × 8 = 32)', attrs: { value: 'anuṣṭubh', selected: 'selected' } }),
      el('option', { text: 'Triṣṭubh (4 × 11 = 44)', attrs: { value: 'trishtubh' } }),
      el('option', { text: 'Jagatī (4 × 12 = 48)', attrs: { value: 'jagati' } }),
    ]);

    // ─── Generation output ───
    const output = el('div', {
      class: 'output', attrs: { 'aria-live': 'polite' },
    }, [
      el('p', { class: 'placeholder', text: 'Verse will stream here.' }),
    ]);

    // ─── Action buttons (hidden until generation succeeds) ───
    const actionRow = el('div', { class: 'form-actions', attrs: { style: 'display: none;' } });

    const pdfBtn = el('button', {
      class: 'btn btn-ghost',
      text: 'Download PDF',
      attrs: { type: 'button' },
    });

    const refineToggleBtn = el('button', {
      class: 'btn btn-ghost',
      text: 'Refine…',
      attrs: { type: 'button' },
    });

    actionRow.appendChild(pdfBtn);
    actionRow.appendChild(refineToggleBtn);

    // ─── Refinement panel (hidden until user opens it) ───
    const refineInput = el('textarea', {
      attrs: { rows: '2', maxlength: '500',
               placeholder: 'e.g. Make it more devotional. Add reference to the veena.' },
    });

    const refineBtn = el('button', {
      class: 'btn btn-primary',
      text: 'Apply Refinement',
      attrs: { type: 'submit' },
    });

    const refineOutput = el('div', {
      class: 'output', attrs: { 'aria-live': 'polite' },
    }, [
      el('p', { class: 'placeholder', text: 'Refined verse will stream here.' }),
    ]);

    const refineForm = el('form', { class: 'form' }, [
      el('label', {}, [
        el('span', { class: 'label', text: 'Refinement instruction' }),
        refineInput,
        el('small', { class: 'hint',
                      text: 'Describe what to change. The verse will be regenerated with your instruction.' }),
      ]),
      el('div', { class: 'form-actions' }, [refineBtn]),
    ]);

    const refinePanel = el('div', {
      class: 'refine-panel',
      attrs: { style: 'display: none;' },
    }, [
      el('header', { class: 'panel-head' }, [
        el('h3', { text: 'Refine Verse' }),
        el('p', { class: 'panel-sub',
                  text: 'Iterate on the last generated verse.' }),
      ]),
      refineForm,
      refineOutput,
    ]);

    // ─── Main form ───
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
        el('small', { class: 'hint',
                      text: 'Sent as X-API-Key header. Never logged or persisted.' }),
      ]),
      el('div', { class: 'form-actions' }, [
        el('button', { class: 'btn btn-primary', text: 'Generate',
                       attrs: { type: 'submit' } }),
      ]),
    ]);

    // ─── Generation submit handler ───
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
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': key,
          },
          body: JSON.stringify({ prompt: prompt.value, meter, max_attempts: 5 }),
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
          state.lastVerse = last.verse || '';
          state.lastPattern = last.pattern || '';

          output.replaceChildren(
            el('pre', { class: 'verse-output', text: last.verse || '' }),
            el('p', { class: 'pattern-line', text: last.pattern || '' }),
            el('span', { class: 'rule-tag',
                         text: `Quanta: ${last.quanta?.spent ?? '?'} / ${last.quanta?.ceiling ?? '?'}` }),
          );
          output.classList.add('has-success');

          // Reveal action buttons
          actionRow.style.display = '';
        } else {
          renderError(output, last?.message || 'Generation incomplete');
        }
      } catch (err) {
        renderError(output, err.message);
      }
    });

    // ─── PDF download ───
    pdfBtn.addEventListener('click', async () => {
      if (!state.lastVerse) { return; }
      pdfBtn.disabled = true;
      const originalText = pdfBtn.textContent;
      pdfBtn.textContent = 'Generating…';
      try {
        const res = await fetch(API.EXPORT_PDF, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: 'Aigaane Verse',
            verse: state.lastVerse,
            pattern: state.lastPattern,
          }),
        });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
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

    // ─── Refine toggle ───
    refineToggleBtn.addEventListener('click', () => {
      const visible = refinePanel.style.display !== 'none';
      refinePanel.style.display = visible ? 'none' : '';
      if (!visible) {
        refineInput.focus();
      }
    });

    // ─── Refine submit ───
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
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': key,
          },
          body: JSON.stringify({
            previous_verse: state.lastVerse,
            refinement,
            meter: state.lastMeter,
            max_attempts: 3,
          }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Request failed' }));
          renderError(refineOutput, err.detail || `HTTP ${res.status}`);
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        const stages = [];
        let buffer = '';

        const log = el('pre', { class: 'stream-log' });
        refineOutput.replaceChildren(log);

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
          state.lastVerse = last.verse || '';
          state.lastPattern = last.pattern || '';

          refineOutput.replaceChildren(
            el('pre', { class: 'verse-output', text: last.verse || '' }),
            el('p', { class: 'pattern-line', text: last.pattern || '' }),
            el('span', { class: 'rule-tag',
                         text: `Quanta: ${last.quanta?.spent ?? '?'} / ${last.quanta?.ceiling ?? '?'}` }),
          );
          refineOutput.classList.add('has-success');
        } else {
          renderError(refineOutput, last?.message || 'Refinement incomplete');
        }
      } catch (err) {
        renderError(refineOutput, err.message);
      }
    });

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Agentic Verse Generator' }),
        el('p', { class: 'panel-sub',
                  text: 'Generates metrically-validated Sanskrit verse. Every draft is scanned by the deterministic Track B engine before acceptance.' }),
      ]),
      form,
      output,
      actionRow,
      refinePanel,
    ]));

    return fragment;
  }

  // ─────────────────────── Śāstra taxonomy view ───────────────────────

  function buildSastraView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Hindu Śāstra Taxonomy' }),
        el('p', { class: 'panel-sub',
                  text: 'Complete philological taxonomy — Śruti, Smṛti, and Puruṣārtha. Metadata for every category is shown below. Categories marked "Live" have computational endpoints; others are documented for future implementation.' }),
      ]),
    ]));

    for (const [key, branch] of Object.entries(SASTRA_TREE)) {
      const section = el('section', { class: 'panel sastra-branch' }, [
        el('header', { class: 'panel-head' }, [
          el('h2', { text: branch.label }),
          el('p', { class: 'panel-sub', text: branch.subtitle }),
        ]),
      ]);

      const grid = el('div', { class: 'sastra-grid' });

      for (const category of branch.children) {
        const card = el('div', { class: 'sastra-card sastra-status-' + category.status }, [
          el('div', { class: 'sastra-card-head' }, [
            el('h3', { text: category.name }),
            category.status === 'live'
              ? el('span', { class: 'status-badge status-live', text: 'Live' })
              : category.status === 'partial'
              ? el('span', { class: 'status-badge status-partial', text: 'Partial' })
              : category.status === 'metadata'
              ? el('span', { class: 'status-badge status-meta', text: 'Documented' })
              : el('span', { class: 'status-badge status-coming', text: 'Coming Soon' }),
          ]),
        ]);

        if (category.subtitle) {
          card.appendChild(el('p', { class: 'sastra-subtitle', text: category.subtitle }));
        }
        if (category.meta) {
          card.appendChild(el('p', { class: 'sastra-meta', text: category.meta }));
        }

        if (Array.isArray(category.parts) && category.parts.length) {
          const partList = el('ul', { class: 'sastra-parts' });
          for (const p of category.parts) {
            const li = el('li', { class: 'sastra-part' }, [
              el('span', { class: 'sastra-part-name', text: p.name }),
            ]);
            if (p.meta) {
              li.appendChild(el('span', { class: 'sastra-part-meta', text: p.meta }));
            }
            if (p.status) {
              li.appendChild(el('span', {
                class: 'sastra-part-tag status-' + p.status,
                text: p.status === 'live' ? 'Live' :
                      p.status === 'partial' ? 'Partial' :
                      p.status === 'coming' ? 'Soon' : 'Docs',
              }));
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

  // ─────────────────────── Coming Soon view ───────────────────────

  function buildComingSoonView() {
    const fragment = document.createDocumentFragment();

    fragment.appendChild(el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'Coming Soon' }),
        el('p', { class: 'panel-sub',
                  text: 'Planned extensions and capabilities. Each has an effort estimate. Order is by priority.' }),
      ]),
    ]));

    const grid = el('div', { class: 'soon-grid' });
    for (const item of COMING_SOON) {
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

  // ─────────────────────── About view ───────────────────────

  function buildAboutView() {
    const fragment = document.createDocumentFragment();

    const about = el('section', { class: 'panel' }, [
      el('header', { class: 'panel-head' }, [
        el('h2', { text: 'About Aigaane' }),
        el('p', { class: 'panel-sub',
                  text: 'A deterministic-plus-agentic platform for Sanskrit language and literature.' }),
      ]),
      el('div', { class: 'about-grid' }, [
        el('div', { class: 'about-card' }, [
          el('h3', { text: 'Architecture' }),
          el('p', { text: 'Two-track design. Track B is a deterministic Pāṇinian compiler — no LLM, no stochastic behavior. Track A is an agentic RAG layer that generates content but delegates every verification to Track B.' }),
        ]),
        el('div', { class: 'about-card' }, [
          el('h3', { text: 'Live Endpoints' }),
          el('ul', { class: 'about-endpoints' }, [
            el('li', {}, [
              el('code', { text: 'POST /api/v3/sandhi' }),
              el('span', { text: ' · Public · Sandhi engine' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/chandas/scan' }),
              el('span', { text: ' · Public · Laghu/Guru scansion' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/chandas/anustubh' }),
              el('span', { text: ' · Public · Anuṣṭubh validator' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/chandas/trishtubh' }),
              el('span', { text: ' · Public · Triṣṭubh validator' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/chandas/jagati' }),
              el('span', { text: ' · Public · Jagatī validator' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/export/pdf' }),
              el('span', { text: ' · Public · PDF export' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/agent/lyric' }),
              el('span', { text: ' · X-API-Key · Agentic verse generation' }),
            ]),
            el('li', {}, [
              el('code', { text: 'POST /api/v3/agent/refine' }),
              el('span', { text: ' · X-API-Key · Multi-turn refinement' }),
            ]),
          ]),
        ]),
        el('div', { class: 'about-card' }, [
          el('h3', { text: 'Philological Foundation' }),
          el('p', { text: 'Grounded in the complete Hindu Śāstra taxonomy. Every sūtra cited. Every category documented. Six Vedāṅgas mapped; three implemented computationally.' }),
        ]),
        el('div', { class: 'about-card' }, [
          el('h3', { text: 'Deterministic Guarantee' }),
          el('p', { text: 'Given the same input, the engine always returns the same output. No LLM self-scanning. No hallucination in phonology, scansion, or meter validation.' }),
        ]),
      ]),
    ]);

    fragment.appendChild(about);
    return fragment;
  }

  // ─────────────────────── Tabs ───────────────────────

  function mountTab(tabName) {
    const viewport = $('#viewport');
    if (!viewport) return;
    clearNode(viewport);

    switch (tabName) {
      case 'sanskrit':
        Promise.all([
          getJSON(API.INFO).catch(() => null),
          getJSON(API.HEALTH).catch(() => null),
        ]).then(([info, health]) => {
          viewport.replaceChildren(buildSandhiView(info, health));
          viewport.appendChild(buildChandasView());
        });
        break;
      case 'agent':
        viewport.replaceChildren(buildAgentView());
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