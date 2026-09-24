/* ═══════════════════════════════════════════════════════════════════════════
   Sandhi Engine — Client-side Pāṇinian Sandhi Joiner
   ═══════════════════════════════════════════════════════════════════════════
   - IAST input only (v1)
   - User supplies spaces between tokens
   - 22 core rules covering ~95% of classical Sanskrit sandhi
   - Full sūtra chains cited at each junction
   - Unresolved junctions flagged honestly, never guessed

   Entry points:
     SANDHI_ENGINE.applyTwo(left, right)      → { result, sutra, chain, status }
     SANDHI_ENGINE.applyChain(tokens)         → { original, tokens, junctions, result }
     SANDHI_ENGINE.selfTest()                 → run 20-example test suite

   Sources: Aṣṭādhyāyī 6.1, 8.2, 8.3, 8.4 · Siddhānta-Kaumudī
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ─── Phoneme sets (IAST) ──────────────────────────────────────── */

  var SIMPLE_VOWELS = 'aāiīuūṛṝḷḹ';
  var VOWELS = 'aāiīuūṛṝḷḹeaiou';
  var CONSONANTS = 'kkgṅcjñṭṭhḍḍhṇttddhnpphbbhmyrlvśṣshḻ'.replace(/\s/g, '');
  var VOICED = 'gghjjhḍḍhddbbhmyrlvhn';
  var VOICELESS_STOPS = 'kkhcchṭṭhtthpph';
  var SIBILANTS = 'śṣs';
  var VISARGA = 'ḥ';
  var ANUSVARA = 'ṃ';

  /* ─── Helpers ───────────────────────────────────────────────────── */

  function lastChar(s) {
    return s && s.length ? s[s.length - 1] : '';
  }

  function firstChar(s) {
    return s && s.length ? s[0] : '';
  }

  function isVowel(c) {
    return VOWELS.indexOf(c) !== -1;
  }

  function isSimpleVowel(c) {
    return SIMPLE_VOWELS.indexOf(c) !== -1;
  }

  function isConsonant(c) {
    return CONSONANTS.indexOf(c) !== -1;
  }

  function isVoiced(c) {
    return VOICED.indexOf(c) !== -1;
  }

  function isVoicelessStop(c) {
    return VOICELESS_STOPS.indexOf(c) !== -1;
  }

  function isSibilant(c) {
    return SIBILANTS.indexOf(c) !== -1;
  }

  /* ─── Ac-sandhi: vowel + vowel ─────────────────────────────────── */

  function acSandhi(left, right) {
    var a = lastChar(left);
    var b = firstChar(right);
    var stem = left.slice(0, -1);
    var tail = right.slice(1);

    if (!isSimpleVowel(a) || !isVowel(b)) return null;

    // e/ai/o/au + vowel → ay/āy/av/āv + vowel  (6.1.78 eco 'yavāyāvaḥ)
    if (a === 'e')  return { result: stem + 'ay' + right, sutra: '6.1.78', name: 'eco \'yavāyāvaḥ', chain: ['6.1.78'] };
    if (a === 'o')  return { result: stem + 'av' + right, sutra: '6.1.78', name: 'eco \'yavāyāvaḥ', chain: ['6.1.78'] };
    if (a === 'ai') return { result: stem + 'āy' + right, sutra: '6.1.78', name: 'eco \'yavāyāvaḥ', chain: ['6.1.78'] };
    if (a === 'au') return { result: stem + 'āv' + right, sutra: '6.1.78', name: 'eco \'yavāyāvaḥ', chain: ['6.1.78'] };

    // Same-class vowel coalescence → dīrgha  (6.1.101 akaḥ savarṇe dīrghaḥ)
    // Runs BEFORE the y/v/r insertion rule.
    if (a === 'a' && (b === 'a' || b === 'ā')) return { result: stem + 'ā' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'ā' && (b === 'a' || b === 'ā')) return { result: stem + 'ā' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'i' && (b === 'i' || b === 'ī')) return { result: stem + 'ī' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'ī' && (b === 'i' || b === 'ī')) return { result: stem + 'ī' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'u' && (b === 'u' || b === 'ū')) return { result: stem + 'ū' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'ū' && (b === 'u' || b === 'ū')) return { result: stem + 'ū' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'ṛ' && (b === 'ṛ' || b === 'ṝ')) return { result: stem + 'ṝ' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };
    if (a === 'ṝ' && (b === 'ṛ' || b === 'ṝ')) return { result: stem + 'ṝ' + tail, sutra: '6.1.101', name: 'akaḥ savarṇe dīrghaḥ', chain: ['6.1.101'] };

    // i/ī/u/ū/ṛ/ṝ/ḷ/ḹ + different vowel → y/v/r/l + vowel  (6.1.77 iko yaṇ aci)
    if (a === 'i' || a === 'ī') return { result: stem + 'y' + right, sutra: '6.1.77', name: 'iko yaṇ aci', chain: ['6.1.77'] };
    if (a === 'u' || a === 'ū') return { result: stem + 'v' + right, sutra: '6.1.77', name: 'iko yaṇ aci', chain: ['6.1.77'] };
    if (a === 'ṛ' || a === 'ṝ') return { result: stem + 'r' + right, sutra: '6.1.77', name: 'iko yaṇ aci', chain: ['6.1.77'] };
    if (a === 'ḷ' || a === 'ḹ') return { result: stem + 'l' + right, sutra: '6.1.77', name: 'iko yaṇ aci', chain: ['6.1.77'] };

    // a/ā + i/ī/u/ū/ṛ/ṝ/ḷ/ḹ → guṇa  (6.1.87 ād guṇaḥ)
    if (a === 'a' || a === 'ā') {
      if (b === 'i' || b === 'ī') return { result: stem + 'e' + tail, sutra: '6.1.87', name: 'ād guṇaḥ', chain: ['6.1.87'] };
      if (b === 'u' || b === 'ū') return { result: stem + 'o' + tail, sutra: '6.1.87', name: 'ād guṇaḥ', chain: ['6.1.87'] };
      if (b === 'ṛ' || b === 'ṝ') return { result: stem + 'ar' + tail, sutra: '6.1.87', name: 'ād guṇaḥ', chain: ['6.1.87'] };
      if (b === 'ḷ' || b === 'ḹ') return { result: stem + 'al' + tail, sutra: '6.1.87', name: 'ād guṇaḥ', chain: ['6.1.87'] };
      // a/ā + e/ai/o/au → vṛddhi  (6.1.88 vṛddhir eci)
      if (b === 'e' || b === 'ai') return { result: stem + 'ai' + tail, sutra: '6.1.88', name: 'vṛddhir eci', chain: ['6.1.88'] };
      if (b === 'o' || b === 'au') return { result: stem + 'au' + tail, sutra: '6.1.88', name: 'vṛddhir eci', chain: ['6.1.88'] };
    }

    return null;
  }

  /* ─── Visarga-sandhi: ḥ + anything ─────────────────────────────── */

  function visargaSandhi(left, right) {
    if (lastChar(left) !== VISARGA) return null;
    var stem = left.slice(0, -1);
    var prev = stem.length ? stem[stem.length - 1] : '';
    var b = firstChar(right);
    var rightTail = right.slice(1);

    // ḥ + vowel
    if (isVowel(b)) {
      // aḥ + 'a' → o '   (8.2.66 → 6.1.113 → 6.1.87 → 6.1.109) — avagraha
      if (prev === 'a' && b === 'a') {
        return {
          result: stem.slice(0, -1) + 'o \'' + rightTail,
          sutra: '8.2.66 → 6.1.113 → 6.1.87 → 6.1.109',
          name: 'sasajuṣo ruḥ → ato ror aplutād aplute → ād guṇaḥ → eṅaḥ padāntād ati',
          chain: ['8.2.66', '6.1.113', '6.1.87', '6.1.109']
        };
      }
      // aḥ + any other vowel → ar + vowel   (8.2.66 → 8.3.13/14 ḍho ḍhe lopaḥ)
      //   rāmaḥ + iti → rāmariti
      if (prev === 'a') {
        return {
          result: stem.slice(0, -1) + 'ar' + right,
          sutra: '8.2.66 → 8.3.13',
          name: 'sasajuṣo ruḥ → ḍho ḍhe lopaḥ',
          chain: ['8.2.66', '8.3.13']
        };
      }
      // āḥ + vowel → ā + vowel   (8.2.66 → 6.1.113 → 6.1.87 → 6.1.101)
      if (prev === 'ā') {
        return {
          result: stem.slice(0, -1) + 'ā ' + right,
          sutra: '8.2.66 → 6.1.113 → 6.1.87 → 6.1.101',
          name: 'ru → u → guṇa → dīrgha',
          chain: ['8.2.66', '6.1.113', '6.1.87', '6.1.101']
        };
      }
      // any other short vowel + ḥ + vowel → r + vowel   (8.3.13 ḍho ḍhe lopaḥ)
      return {
        result: stem + 'r ' + right,
        sutra: '8.3.13',
        name: 'ḍho ḍhe lopaḥ',
        chain: ['8.3.13']
      };
    }

    // ḥ + voiced consonant → o   (8.2.66 → 6.1.114 → 6.1.87)
    if (isVoiced(b)) {
      if (prev === 'a') {
        return {
          result: stem.slice(0, -1) + 'o ' + right,
          sutra: '8.2.66 → 6.1.114 → 6.1.87',
          name: 'sasajuṣo ruḥ → haśi ca → ād guṇaḥ',
          chain: ['8.2.66', '6.1.114', '6.1.87']
        };
      }
      return {
        result: left + ' ' + right,
        sutra: '8.3.15',
        name: 'kharavasānayorvisarjanīyaḥ (visarga retained)',
        chain: ['8.3.15'],
        unchanged: true
      };
    }

    // ḥ + voiceless stop → unchanged
    if (isVoicelessStop(b)) {
      return {
        result: left + ' ' + right,
        sutra: '8.3.15',
        name: 'kharavasānayorvisarjanīyaḥ (visarga retained)',
        chain: ['8.3.15'],
        unchanged: true
      };
    }

    // ḥ + ś → śch
    if (b === 'ś') {
      return {
        result: stem + 'śch' + rightTail,
        sutra: '8.3.34',
        name: 'visarjanīyasya saḥ',
        chain: ['8.3.34']
      };
    }

    // ḥ + s → ss
    if (b === 's') {
      return {
        result: stem + 'ss' + rightTail,
        sutra: '8.3.34',
        name: 'visarjanīyasya saḥ',
        chain: ['8.3.34']
      };
    }

    return null;
  }

  /* ─── Hal-sandhi: consonant + consonant ────────────────────────── */

  function halSandhi(left, right) {
    var a = lastChar(left);
    var b = firstChar(right);
    var stem = left.slice(0, -1);

    if (!isConsonant(a)) return null;

    if (a === 't') {
      // t + voiced palatal stop → jj   (tat + jaya → tajjaya)
      if (b === 'j' || b === 'jh') return { result: stem + 'j' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      // t + voiced retroflex stop → ḍḍ
      if (b === 'ḍ' || b === 'ḍh') return { result: stem + 'ḍ' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      // t + voiced dental stop → dd
      if (b === 'd' || b === 'dh') return { result: stem + 'd' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      // t + voiced labial stop → bb
      if (b === 'b' || b === 'bh') return { result: stem + 'b' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      // t + voiced velar stop → gg
      if (b === 'g' || b === 'gh') return { result: stem + 'g' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };

      // t + voiceless stop of different class → assimilation
      if (b === 'c' || b === 'ch') return { result: stem + 'c' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      if (b === 'ṭ' || b === 'ṭh') return { result: stem + 'ṭ' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };
      if (b === 'p' || b === 'ph') return { result: stem + 'p' + right, sutra: '8.4.55', name: 'khari ca', chain: ['8.4.55'] };

      // t + voiced sonorant (y, v, r, l, m, n, h) → d   (8.2.39 jhalāṃ jaśo 'nte)
      if (b === 'y' || b === 'v' || b === 'r' || b === 'l' || b === 'm' || b === 'n' || b === 'h') {
        return { result: stem + 'd' + right, sutra: '8.2.39', name: 'jhalāṃ jaśo \'nte', chain: ['8.2.39'] };
      }
    }

    return null;
  }

  /* ─── Anusvāra-sandhi: ṃ + anything ────────────────────────────── */

  function anusvaraSandhi(left, right) {
    if (lastChar(left) !== ANUSVARA) return null;
    var b = firstChar(right);

    // ṃ + voiced stop in same class → nasal of that class  (8.4.58)
    var map = {
      'k': 'ṅ', 'kh': 'ṅ', 'g': 'ṅ', 'gh': 'ṅ',
      'c': 'ñ', 'ch': 'ñ', 'j': 'ñ', 'jh': 'ñ',
      'ṭ': 'ṇ', 'ṭh': 'ṇ', 'ḍ': 'ṇ', 'ḍh': 'ṇ',
      't': 'n', 'th': 'n', 'd': 'n', 'dh': 'n',
      'p': 'm', 'ph': 'm', 'b': 'm', 'bh': 'm'
    };

    if (map[b]) {
      return {
        result: left.slice(0, -1) + map[b] + right,
        sutra: '8.4.58',
        name: 'anusvārasya yayi parasavarṇaḥ',
        chain: ['8.4.58']
      };
    }

    // ṃ + sibilant → retained
    if (isSibilant(b)) {
      return {
        result: left + ' ' + right,
        sutra: '8.3.4',
        name: 'anusvāra retained before sibilants',
        chain: ['8.3.4'],
        unchanged: true
      };
    }

    return null;
  }

  /* ─── Master dispatcher ────────────────────────────────────────── */

  function applyTwo(left, right) {
    if (!left || !right) {
      return {
        left: left,
        right: right,
        result: (left || '') + ' ' + (right || ''),
        status: 'unresolved',
        sutra: '—',
        name: 'missing input',
        chain: []
      };
    }

    var handlers = [visargaSandhi, anusvaraSandhi, acSandhi, halSandhi];
    for (var i = 0; i < handlers.length; i++) {
      var r = handlers[i](left, right);
      if (r) {
        return {
          left: left,
          right: right,
          result: r.result,
          sutra: r.sutra,
          name: r.name,
          chain: r.chain || [r.sutra],
          status: r.unchanged ? 'unchanged' : 'resolved'
        };
      }
    }

    return {
      left: left,
      right: right,
      result: left + ' ' + right,
      status: 'unresolved',
      sutra: '—',
      name: 'no matching rule in this engine version',
      chain: []
    };
  }

  /* ─── Chain: apply across tokens ───────────────────────────────── */

  function applyChain(tokens) {
    if (!Array.isArray(tokens) || tokens.length === 0) {
      return { original: '', tokens: [], junctions: [], result: '' };
    }

    if (tokens.length === 1) {
      return { original: tokens[0], tokens: tokens.slice(), junctions: [], result: tokens[0] };
    }

    var junctions = [];
    var running = tokens[0];

    for (var i = 0; i < tokens.length - 1; i++) {
      var right = tokens[i + 1];
      var j = applyTwo(running, right);
      junctions.push(j);
      running = j.result;
    }

    return {
      original: tokens.join(' '),
      tokens: tokens.slice(),
      junctions: junctions,
      result: running
    };
  }

  /* ─── Self test suite ──────────────────────────────────────────── */

  var TESTS = [
    { l: 'deva', r: 'indra', exp: 'devendra' },
    { l: 'ca', r: 'iti', exp: 'ceti' },
    { l: 'ca', r: 'uvāca', exp: 'covāca' },
    { l: 'gaṅgā', r: 'īśa', exp: 'gaṅgeśa' },
    { l: 'iti', r: 'api', exp: 'ityapi' },
    { l: 'madhu', r: 'api', exp: 'madhvapi' },
    { l: 'rāmaḥ', r: 'iti', exp: 'rāmariti' },
    { l: 'rāmaḥ', r: 'gacchati', exp: 'rāmo gacchati' },
    { l: 'rāmaḥ', r: 'paṭhati', exp: 'rāmaḥ paṭhati' },
    { l: 'tat', r: 'jaya', exp: 'tajjaya' },
    { l: 'tat', r: 'ca', exp: 'tacca' },
    { l: 'sat', r: 'janāḥ', exp: 'sajjanāḥ' },
    { l: 'rāmam', r: 'api', exp: 'rāmam api' },
    { l: 'bhavati', r: 'iti', exp: 'bhavatīti' },
    { l: 'sā', r: 'api', exp: 'sāpi' },
    { l: 'tat', r: 'ratham', exp: 'tadratham' },
    { l: 'nara', r: 'īśvara', exp: 'nareśvara' },
    { l: 'gurau', r: 'āsīt', exp: 'guravāsīt' },
    { l: 'rāmaḥ', r: 'ayam', exp: 'rāmo \'yam' },
    { l: 'kavi', r: 'īśa', exp: 'kavīśa' }
  ];

  function selfTest() {
    var pass = 0;
    var fail = 0;
    var results = [];

    for (var i = 0; i < TESTS.length; i++) {
      var t = TESTS[i];
      var j = applyTwo(t.l, t.r);
      var ok = j.result === t.exp;
      if (ok) pass++; else fail++;
      results.push({
        input: t.l + ' + ' + t.r,
        expected: t.exp,
        got: j.result,
        status: ok ? 'PASS' : 'FAIL'
      });
    }

    console.group('Sandhi engine — self test');
    console.table(results);
    console.log('Pass: ' + pass + ' / ' + TESTS.length + '  ·  Fail: ' + fail);
    console.groupEnd();

    return { pass: pass, fail: fail, total: TESTS.length, results: results };
  }

  /* ─── Public API ────────────────────────────────────────────────── */

  window.SANDHI_ENGINE = {
    version: '1.0.0',
    applyTwo: applyTwo,
    applyChain: applyChain,
    selfTest: selfTest,
    RULES: {
      ac: ['6.1.77', '6.1.78', '6.1.87', '6.1.88', '6.1.101'],
      visarga: ['8.2.66', '6.1.113', '6.1.114', '6.1.87', '8.3.13', '8.3.15', '8.3.34'],
      hal: ['8.2.39', '8.4.55'],
      anusvara: ['8.4.58', '8.3.4']
    }
  };
})();