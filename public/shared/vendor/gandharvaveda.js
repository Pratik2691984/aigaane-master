/* ═══════════════════════════════════════════════════════════════════════════
   Gāndharvaveda Studio — Merged React Component
   ═══════════════════════════════════════════════════════════════════════════
   - Local scansion audio engine (Pingal mātrā scan + Web Audio / Web Speech)
   - AI prompt song generator (Rāga + Tāla + Rasa + Tanpura → Suno/Udio)
   - 23 rāgas, 9 tālas, MIDI export, .wav export, session vault
   - No JSX, no Babel — pure React.createElement
   - CSP compliant with /gandharvaveda.html policy
   ═══════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  if (!React || !ReactDOM) {
    console.error('[Gāndharvaveda] React or ReactDOM not loaded.');
    return;
  }
  var h = React.createElement;
  var useState = React.useState;
  var useEffect = React.useEffect;
  var useMemo = React.useMemo;
  var useRef = React.useRef;
  var useReducer = React.useReducer;

  /* ═══════════════════════════════════════════════════════════════════════
     DATA — Rāgas (23)
     ═══════════════════════════════════════════════════════════════════════ */
  var RAGAS = [
    { id: 'bhairav',    name: 'Bhairav',    dev: 'भैरव',      thaat: 'Bhairav',    time: 'dawn',      mood: 'solemn',    color: '#8a4a2a', aroha: 'S r G M P d N S\'', avaroha: 'S\' N d P M G r S', vadi: 'd', samvadi: 'r', notes: 'Komal Re, Komal Dha' },
    { id: 'bhairavi',   name: 'Bhairavi',   dev: 'भैरवी',     thaat: 'Bhairavi',   time: 'morning',   mood: 'devotional',color: '#a04a5a', aroha: 'S r g M P d n S\'', avaroha: 'S\' n d P M g r S', vadi: 'M', samvadi: 'S', notes: 'All komal' },
    { id: 'yaman',      name: 'Yaman',      dev: 'यमन',       thaat: 'Kalyan',     time: 'evening',   mood: 'serene',    color: '#c9a227', aroha: 'N r G M^ D N S\'', avaroha: 'S\' N D P M^ G r S', vadi: 'G', samvadi: 'N', notes: 'Teevra Ma' },
    { id: 'kalyani',    name: 'Kalyani',    dev: 'कल्याणी',   thaat: 'Kalyan',     time: 'evening',   mood: 'serene',    color: '#c9a227', aroha: 'S R G M^ P D N S\'', avaroha: 'S\' N D P M^ G R S', vadi: 'G', samvadi: 'N', notes: 'Teevra Ma' },
    { id: 'todi',       name: 'Todi',       dev: 'तोडी',      thaat: 'Todi',       time: 'late morning',mood:'plaintive', color: '#6a4a8a', aroha: 'S r g M^ P d N S\'', avaroha: 'S\' N d P M^ g r S', vadi: 'd', samvadi: 'g', notes: 'Teevra Ma, komal Re/Ga/Dha' },
    { id: 'bhimpalasi', name: 'Bhimpalasi', dev: 'भीमपलासी',  thaat: 'Kafi',       time: 'afternoon', mood: 'romantic',  color: '#c06a5a', aroha: 'n S g M P n S\'', avaroha: 'S\' n D P M g R S', vadi: 'M', samvadi: 'S', notes: 'Komal Ga/Ni in ascent' },
    { id: 'kafi',       name: 'Kafi',       dev: 'काफी',      thaat: 'Kafi',       time: 'evening',   mood: 'devotional',color: '#a05a4a', aroha: 'S R g M P D n S\'', avaroha: 'S\' n D P M g R S', vadi: 'P', samvadi: 'S', notes: 'Komal Ga/Ni' },
    { id: 'des',        name: 'Des',        dev: 'देस',       thaat: 'Khamaj',     time: 'night',     mood: 'romantic',  color: '#c08a4a', aroha: 'S R M P N S\'', avaroha: 'S\' n D P M G R S', vadi: 'P', samvadi: 'R', notes: 'Shuddha Ni ascent, komal Ni descent' },
    { id: 'khamaj',     name: 'Khamaj',     dev: 'खमाज',      thaat: 'Khamaj',     time: 'night',     mood: 'romantic',  color: '#b07a4a', aroha: 'S G M P D N S\'', avaroha: 'S\' n D P M G R S', vadi: 'N', samvadi: 'G', notes: 'Komal Ni' },
    { id: 'marwa',      name: 'Marwa',      dev: 'मारवा',     thaat: 'Marwa',      time: 'sunset',    mood: 'intense',   color: '#8a2a3a', aroha: 'S r G M^ D N S\'', avaroha: 'S\' N D M^ G r S', vadi: 'r', samvadi: 'D', notes: 'Teevra Ma, komal Re, no Pa' },
    { id: 'poorvi',     name: 'Poorvi',     dev: 'पूर्वी',     thaat: 'Poorvi',     time: 'sunset',    mood: 'solemn',    color: '#6a3a7a', aroha: 'S r G M^ P d N S\'', avaroha: 'S\' N d P M^ G r S', vadi: 'G', samvadi: 'N', notes: 'Teevra Ma, komal Re/Dha' },
    { id: 'ahirbhairav',name: 'Ahir Bhairav',dev:'अहीर भैरव',  thaat: 'Bhairav',    time: 'dawn',      mood: 'devotional',color: '#9a5a3a', aroha: 'S r G M P D n S\'', avaroha: 'S\' n D P M G r S', vadi: 'M', samvadi: 'S', notes: 'Komal Re, komal Ni' },
    { id: 'jaunpuri',   name: 'Jaunpuri',   dev: 'जौनपुरी',   thaat: 'Asavari',    time: 'morning',   mood: 'plaintive', color: '#7a5a6a', aroha: 'S R M P d n S\'', avaroha: 'S\' n d P M G R S', vadi: 'd', samvadi: 'S', notes: 'Komal Ga/Dha/Ni' },
    { id: 'darbari',    name: 'Darbari Kanada',dev:'दरबारी कानडा',thaat:'Asavari', time: 'late night',mood: 'solemn',    color: '#4a3a6a', aroha: 'S R g M P d n S\'', avaroha: 'S\' n d P M g R S', vadi: 'r', samvadi: 'P', notes: 'Komal Ga/Dha/Ni, oscillated' },
    { id: 'adana',      name: 'Adana',      dev: 'अडाना',     thaat: 'Asavari',    time: 'late night',mood: 'intense',   color: '#5a3a5a', aroha: 'S R M P d n S\'', avaroha: 'S\' n d P M g R S', vadi: 'd', samvadi: 'R', notes: 'Komal Ga/Dha/Ni' },
    { id: 'miyan_ki_malhar',name:'Miyan ki Malhar',dev:'मियाँ की मल्हार',thaat:'Kafi',time:'monsoon',mood:'devotional',color:'#3a6a7a',aroha:'S R g M P N S\'',avaroha:'S\' n P M g R S',vadi:'P',samvadi:'R',notes:'Both Ni, monsoon rāga' },
    { id: 'megh',       name: 'Megh',       dev: 'मेघ',       thaat: 'Kafi',       time: 'monsoon',   mood: 'devotional',color: '#3a5a7a', aroha: 'S R M P N S\'', avaroha: 'S\' N P M R S', vadi: 'S', samvadi: 'P', notes: 'Monsoon, omits Ga/Dha' },
    { id: 'hindol',     name: 'Hindol',     dev: 'हिंडोल',    thaat: 'Kalyan',     time: 'dawn',      mood: 'serene',    color: '#6a8a4a', aroha: 'S G M^ D N S\'', avaroha: 'S\' N D M^ G S', vadi: 'D', samvadi: 'G', notes: 'Teevra Ma, omits Re/Pa' },
    { id: 'bageshri',   name: 'Bageshri',   dev: 'बागेश्री',   thaat: 'Kafi',       time: 'late night',mood: 'romantic',  color: '#7a4a6a', aroha: 'S g M D n S\'', avaroha: 'S\' n D M P g R S', vadi: 'M', samvadi: 'S', notes: 'Komal Ga/Ni, omits Pa ascent' },
    { id: 'shankarabharan',name:'Shankarabharan',dev:'शंकराभरण',thaat:'Bilawal',  time: 'any',       mood: 'solemn',    color: '#8a7a3a', aroha: 'S R G M P D N S\'', avaroha: 'S\' N D P M G R S', vadi: 'G', samvadi: 'N', notes: 'Carnatic major scale' },
    { id: 'kuntalavarali',name:'Kuntalavarali',dev:'कुंतलवराली',thaat:'Melakarta',time:'any',      mood: 'intense',   color: '#7a3a3a', aroha: 'S M P D N S\'', avaroha: 'S\' N D P M S', vadi: 'D', samvadi: 'S', notes: 'Pentatonic Carnatic' },
    { id: 'revati',     name: 'Revati',     dev: 'रेवती',     thaat: 'Bhairavi',   time: 'evening',   mood: 'serene',    color: '#4a6a6a', aroha: 'S r M P n S\'', avaroha: 'S\' n P M r S', vadi: 'M', samvadi: 'S', notes: 'Komal Re/Ni, pentatonic' },
    { id: 'charukesi',  name: 'Charukesi',  dev: 'चारुकेशी',   thaat: 'Melakarta',  time: 'any',       mood: 'romantic',  color: '#8a5a5a', aroha: 'S R G M P D n S\'', avaroha: 'S\' n D P M G R S', vadi: 'P', samvadi: 'R', notes: 'Shuddha Re/Ga/Ma/Dha, komal Ni' },
  ];

  /* ═══════════════════════════════════════════════════════════════════════
     DATA — Tālas (9)
     ═══════════════════════════════════════════════════════════════════════ */
  var TALAS = [
    { id: 'teentaal',   name: 'Teentaal',    dev: 'तीनताल',    beats: 16, sam: [1], khali: [9],  tali: [1,5,13],    bols: ['dha','dhin','dhin','dha','dha','dhin','dhin','dha','dha','tin','tin','ta','ta','dhin','dhin','dha'], cycle: 16 },
    { id: 'ektaal',     name: 'Ektaal',      dev: 'एकताल',     beats: 12, sam: [1], khali: [3,7], tali: [1,5,9,11], bols: ['dhin','dhin','dha','dha','dhin','dhin','dha','dha','tin','tin','ta','ta'], cycle: 12 },
    { id: 'jhaptaal',   name: 'Jhaptaal',    dev: 'झपताल',     beats: 10, sam: [1], khali: [6],  tali: [1,3,8],     bols: ['dhi','na','dhi','dhi','na','ti','na','dhi','dhi','na'], cycle: 10 },
    { id: 'rupak',      name: 'Rupak',       dev: 'रूपक',      beats: 7,  sam: [4], khali: [1],  tali: [4,6],       bols: ['tin','tin','na','dhi','na','dhi','na'], cycle: 7 },
    { id: 'keharwa',    name: 'Keharwa',     dev: 'कहरवा',     beats: 8,  sam: [1], khali: [5],  tali: [1,3],       bols: ['dha','ge','na','ti','na','ka','dhi','na'], cycle: 8 },
    { id: 'dadra',      name: 'Dadra',       dev: 'दादरा',     beats: 6,  sam: [1], khali: [4],  tali: [1,3],       bols: ['dha','dhin','na','dha','tin','na'], cycle: 6 },
    { id: 'jhoomra',    name: 'Jhoomra',     dev: 'झूमरा',     beats: 14, sam: [1], khali: [7],  tali: [1,3,5,9,11],bols: ['dhin','dha','dhin','dha','dhin','dhin','dha','tin','tin','ta','ta','dhin','dhin','dha'], cycle: 14 },
    { id: 'deepchandi', name: 'Deepchandi',  dev: 'दीपचंदी',   beats: 14, sam: [1], khali: [8],  tali: [1,4,11],    bols: ['dha','dhin','ta','dhin','dha','dhin','tin','ta','tin','ta','dhin','dha','dhin','dha'], cycle: 14 },
    { id: 'chautaal',   name: 'Chautaal',    dev: 'चौताल',     beats: 12, sam: [1], khali: [7],  tali: [1,5,9],     bols: ['dha','dha','din','ta','kita','dha','din','ta','tita','kita','dha','din'], cycle: 12 },
  ];

  /* ═══════════════════════════════════════════════════════════════════════
     DATA — Moods / Rasa
     ═══════════════════════════════════════════════════════════════════════ */
  var MOODS = [
    { id: 'devotional', label: 'Devotional (Bhakti)',  prompt: 'devotional bhajan, temple atmosphere, hand cymbals, harmonium, deep reverb' },
    { id: 'romantic',   label: 'Romantic (Śṛṅgāra)',   prompt: 'romantic classical, sitar, bansuri, soft tabla, evening ambience' },
    { id: 'plaintive',  label: 'Plaintive (Karuṇa)',   prompt: 'plaintive raga, slow alap, sarangi, mournful tone, minor inflections' },
    { id: 'serene',     label: 'Serene (Śānta)',       prompt: 'serene meditation, drone-heavy, sparse bansuri, expansive silence' },
    { id: 'solemn',     label: 'Solemn (Vīra/Raudra)', prompt: 'solemn dhrupad, deep pakhawaj, temple bell, restrained grandeur' },
    { id: 'intense',    label: 'Intense (Raudra)',     prompt: 'intense drut laya, rapid tabla, dramatic dynamics, sharp accents' },
  ];

  /* ═══════════════════════════════════════════════════════════════════════
     PINGAL — Devanagari → mātrā scan
     ═══════════════════════════════════════════════════════════════════════ */
  var SHORT_VOWELS = 'अइउऋऌ';
  var LONG_VOWELS  = 'आईऊॠॡएऐओऔ';
  var MATRAS_SHORT = 'िुृॢ';
  var MATRAS_LONG  = 'ीूॄेैोौ';
  var ANUSVARA     = 'ंँ';
  var VISARGA      = 'ः';
  var VIRAMA       = '्';
  var CONSONANTS   = 'कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहळक़ख़ग़ज़ड़ढ़फ़';
  var DIGITS       = '०१२३४५६७८९';
  var DANDA        = '।॥';

  function scanPingal(text, opts) {
    opts = opts || {};
    var verseEndGuru = opts.verseEndGuru !== false;
    var syllables = [];
    var i = 0;
    var n = text.length;

    while (i < n) {
      var ch = text[i];

      if (/\s/.test(ch)) { i++; continue; }
      if (DANDA.indexOf(ch) !== -1) { i++; continue; }
      if (/[.,;:!?"'\-—–]/.test(ch)) { i++; continue; }
      if (DIGITS.indexOf(ch) !== -1) { i++; continue; }

      if (SHORT_VOWELS.indexOf(ch) !== -1) {
        syllables.push({ char: ch, weight: 1, type: 'laghu' });
        i++;
        while (i < n && (ANUSVARA.indexOf(text[i]) !== -1 || VISARGA.indexOf(text[i]) !== -1)) {
          syllables[syllables.length - 1].weight = 2;
          syllables[syllables.length - 1].type = 'guru';
          i++;
        }
        continue;
      }
      if (LONG_VOWELS.indexOf(ch) !== -1) {
        syllables.push({ char: ch, weight: 2, type: 'guru' });
        i++;
        while (i < n && (ANUSVARA.indexOf(text[i]) !== -1 || VISARGA.indexOf(text[i]) !== -1)) {
          syllables[syllables.length - 1].weight = 2;
          syllables[syllables.length - 1].type = 'guru';
          i++;
        }
        continue;
      }

      if (CONSONANTS.indexOf(ch) !== -1) {
        var consonant = ch;
        i++;
        var matraChar = null;
        while (i < n) {
          var next = text[i];
          if (MATRAS_SHORT.indexOf(next) !== -1) { matraChar = next; i++; break; }
          if (MATRAS_LONG.indexOf(next) !== -1)  { matraChar = next; i++; break; }
          if (next === VIRAMA) { matraChar = 'virama'; i++; break; }
          break;
        }

        var weight, type;
        if (matraChar === 'virama') { weight = 0; type = 'consonant'; }
        else if (matraChar && MATRAS_LONG.indexOf(matraChar) !== -1) { weight = 2; type = 'guru'; }
        else if (matraChar && MATRAS_SHORT.indexOf(matraChar) !== -1) { weight = 1; type = 'laghu'; }
        else { weight = 1; type = 'laghu'; }

        var absorbedNasal = false;
        while (i < n && (ANUSVARA.indexOf(text[i]) !== -1 || VISARGA.indexOf(text[i]) !== -1)) {
          absorbedNasal = true;
          i++;
        }
        if (absorbedNasal && weight > 0) { weight = 2; type = 'guru'; }

        if (weight > 0) {
          syllables.push({ char: consonant + (matraChar && matraChar !== 'virama' ? matraChar : ''), weight: weight, type: type });
        }
        continue;
      }

      i++;
    }

    if (verseEndGuru && syllables.length > 0) {
      var last = syllables[syllables.length - 1];
      if (last.weight === 1) {
        last.weight = 2;
        last.type = 'guru';
        last.forced = true;
      }
    }

    var total = syllables.reduce(function (a, s) { return a + s.weight; }, 0);
    return { syllables: syllables, totalMatras: total };
  }

  function pingalNotation(syllables) {
    return syllables.map(function (s) { return s.weight === 2 ? 'G' : 'L'; }).join('');
  }

  /* ═══════════════════════════════════════════════════════════════════════
     AUDIO — Web Audio engine
     ═══════════════════════════════════════════════════════════════════════ */
  function useAudioEngine() {
    var ctxRef = useRef(null);
    var droneRef = useRef(null);
    var masterRef = useRef(null);

    function getCtx() {
      if (!ctxRef.current) {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return null;
        ctxRef.current = new AC();
        masterRef.current = ctxRef.current.createGain();
        masterRef.current.gain.value = 0.7;
        masterRef.current.connect(ctxRef.current.destination);
      }
      if (ctxRef.current.state === 'suspended') { ctxRef.current.resume(); }
      return ctxRef.current;
    }

    function pulse(freq, duration, type, gainVal) {
      var ctx = getCtx();
      if (!ctx) return;
      type = type || 'triangle';
      gainVal = gainVal || 0.18;
      var osc = ctx.createOscillator();
      var env = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq;
      env.gain.setValueAtTime(0, ctx.currentTime);
      env.gain.linearRampToValueAtTime(gainVal, ctx.currentTime + 0.01);
      env.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
      osc.connect(env); env.connect(masterRef.current);
      osc.start(); osc.stop(ctx.currentTime + duration + 0.05);
    }

    function startDrone(saHz, fifthHz) {
      var ctx = getCtx();
      if (!ctx || droneRef.current) return;
      var droneGain = ctx.createGain();
      droneGain.gain.value = 0.06;
      droneGain.connect(masterRef.current);

      var partials = [
        { f: saHz,        g: 1.0 },
        { f: saHz * 2,    g: 0.35 },
        { f: saHz * 3,    g: 0.12 },
        { f: fifthHz,     g: 0.7 },
        { f: fifthHz * 2, g: 0.25 },
        { f: saHz / 2,    g: 0.4 },
      ];
      var nodes = partials.map(function (p) {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        o.type = 'sine';
        o.frequency.value = p.f;
        g.gain.value = p.g * 0.1;
        var lfo = ctx.createOscillator();
        var lfoGain = ctx.createGain();
        lfo.frequency.value = 0.15 + Math.random() * 0.2;
        lfoGain.gain.value = p.f * 0.002;
        lfo.connect(lfoGain); lfoGain.connect(o.frequency);
        lfo.start();
        o.connect(g); g.connect(droneGain);
        o.start();
        return { o: o, g: g, lfo: lfo };
      });
      droneRef.current = { nodes: nodes, gain: droneGain };
    }

    function stopDrone() {
      if (!droneRef.current) return;
      var ctx = ctxRef.current;
      droneRef.current.gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.4);
      var nodes = droneRef.current.nodes;
      setTimeout(function () {
        nodes.forEach(function (n) { try { n.o.stop(); n.lfo.stop(); } catch (e) {} });
      }, 500);
      droneRef.current = null;
    }

    function tablaHit(type) {
      var ctx = getCtx();
      if (!ctx) return;
      if (type === 'sam') {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        o.type = 'sine';
        o.frequency.setValueAtTime(180, ctx.currentTime);
        o.frequency.exponentialRampToValueAtTime(60, ctx.currentTime + 0.3);
        g.gain.setValueAtTime(0.3, ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
        o.connect(g); g.connect(masterRef.current);
        o.start(); o.stop(ctx.currentTime + 0.55);
      } else if (type === 'khali') {
        var o2 = ctx.createOscillator();
        var g2 = ctx.createGain();
        o2.type = 'sine';
        o2.frequency.value = 880;
        g2.gain.setValueAtTime(0.15, ctx.currentTime);
        g2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
        o2.connect(g2); g2.connect(masterRef.current);
        o2.start(); o2.stop(ctx.currentTime + 0.3);
      } else {
        var o3 = ctx.createOscillator();
        var g3 = ctx.createGain();
        o3.type = 'triangle';
        o3.frequency.value = 320;
        g3.gain.setValueAtTime(0.2, ctx.currentTime);
        g3.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
        o3.connect(g3); g3.connect(masterRef.current);
        o3.start(); o3.stop(ctx.currentTime + 0.4);
      }
    }

    return { getCtx: getCtx, pulse: pulse, startDrone: startDrone, stopDrone: stopDrone, tablaHit: tablaHit };
  }

  /* ═══════════════════════════════════════════════════════════════════════
     AUDIO — Web Speech fallback
     ═══════════════════════════════════════════════════════════════════════ */
  function speakDevanagari(text, rate, onEnd) {
    if (!window.speechSynthesis) { if (onEnd) onEnd(); return false; }
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = 'hi-IN';
    u.rate = rate || 0.85;
    u.pitch = 1.0;
    var voices = window.speechSynthesis.getVoices();
    var hiVoice = voices.find(function (v) { return v.lang && v.lang.indexOf('hi') === 0; })
               || voices.find(function (v) { return v.lang && v.lang.indexOf('sa') === 0; });
    if (hiVoice) u.voice = hiVoice;
    if (onEnd) u.onend = onEnd;
    window.speechSynthesis.speak(u);
    return true;
  }

  /* ═══════════════════════════════════════════════════════════════════════
     WAV ENCODER — 16-bit PCM
     ═══════════════════════════════════════════════════════════════════════ */
  function encodeWAV(samples, sampleRate) {
    var buffer = new ArrayBuffer(44 + samples.length * 2);
    var view = new DataView(buffer);
    function writeStr(offset, str) {
      for (var i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    }
    writeStr(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeStr(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    var offset = 44;
    for (var j = 0; j < samples.length; j++) {
      var s = Math.max(-1, Math.min(1, samples[j]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      offset += 2;
    }
    return new Blob([view], { type: 'audio/wav' });
  }

  function renderScansionWAV(syllables, baseHz, sampleRate) {
    sampleRate = sampleRate || 22050;
    var out = [];
    var sr = sampleRate;
    syllables.forEach(function (syl, idx) {
      if (syl.weight === 0) return;
      var dur = syl.weight === 2 ? 0.36 : 0.18;
      var len = Math.floor(dur * sr);
      var freq = baseHz * (1 + (idx % 5) * 0.02);
      var type = syl.weight === 2 ? 'sine' : 'triangle';
      for (var i = 0; i < len; i++) {
        var t = i / sr;
        var env = Math.min(1, i / (0.02 * sr)) * Math.exp(-3.5 * t / dur);
        var sample;
        if (type === 'sine') sample = Math.sin(2 * Math.PI * freq * t);
        else sample = (2 * (t * freq - Math.floor(t * freq + 0.5)));
        out.push(sample * env * 0.35);
      }
      for (var k = 0; k < Math.floor(0.05 * sr); k++) out.push(0);
    });
    return { samples: out, sampleRate: sr };
  }

  /* ═══════════════════════════════════════════════════════════════════════
     MIDI EXPORT
     ═══════════════════════════════════════════════════════════════════════ */
  function buildMIDI(tala, tempoBPM) {
    function vlq(n) {
      var bytes = [n & 0x7F];
      n >>= 7;
      while (n > 0) { bytes.unshift((n & 0x7F) | 0x80); n >>= 7; }
      return bytes;
    }
    function u32(n) { return [(n >>> 24) & 0xFF, (n >>> 16) & 0xFF, (n >>> 8) & 0xFF, n & 0xFF]; }
    function u16(n) { return [(n >>> 8) & 0xFF, n & 0xFF]; }

    var ppq = 480;
    var beatTicks = ppq;
    var tempoUS = Math.floor(60000000 / tempoBPM);

    var track = [];
    var nameBytes = [];
    var nm = 'Gandharvaveda ' + tala.name;
    for (var i = 0; i < nm.length; i++) nameBytes.push(nm.charCodeAt(i));
    track = track.concat([0x00, 0xFF, 0x03, nameBytes.length], nameBytes);
    track = track.concat([0x00, 0xFF, 0x51, 0x03], u32(tempoUS).slice(1));

    var totalBeats = tala.beats * 2;
    var notes = [];
    for (var b = 0; b < totalBeats; b++) {
      var pos = (b % tala.beats) + 1;
      var isSam = tala.sam.indexOf(pos) !== -1;
      var isKhali = tala.khali.indexOf(pos) !== -1;
      var note = isSam ? 36 : (isKhali ? 60 : 43);
      var vel = isSam ? 110 : (isKhali ? 80 : 95);
      notes.push({ tick: b * beatTicks, note: note, vel: vel, dur: beatTicks - 20 });
    }
    notes.sort(function (a, b) { return a.tick - b.tick; });
    var last = 0;
    notes.forEach(function (n) {
      var delta = n.tick - last;
      track = track.concat(vlq(delta));
      track.push(0x99, n.note, n.vel);
      track = track.concat(vlq(n.dur));
      track.push(0x89, n.note, 0x40);
      last = n.tick + n.dur;
    });
    track = track.concat([0x00, 0xFF, 0x2F, 0x00]);

    var header = [];
    header = header.concat([0x4D, 0x54, 0x68, 0x64]);
    header = header.concat(u32(6));
    header = header.concat(u16(0), u16(1), u16(ppq));
    var trackHeader = [0x4D, 0x54, 0x72, 0x6B];
    var trackChunk = trackHeader.concat(u32(track.length), track);
    return new Uint8Array(header.concat(trackChunk));
  }

  /* ═══════════════════════════════════════════════════════════════════════
     CLIPBOARD + DOWNLOAD
     ═══════════════════════════════════════════════════════════════════════ */
  function copyText(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) {}
    try {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch (e) { return false; }
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { document.body.removeChild(a); URL.revokeObjectURL(url); }, 200);
  }

  /* ═══════════════════════════════════════════════════════════════════════
     PROMPT BUILDERS
     ═══════════════════════════════════════════════════════════════════════ */
  function buildCompactPrompt(state) {
        var raga = RAGAS.find(function (r) { return r.id === state.ragaId; }) || RAGAS[0];
    var tala = TALAS.find(function (t) { return t.id === state.talaId; }) || TALAS[0];
    var mood = MOODS.find(function (m) { return m.id === state.moodId; }) || MOODS[0];
    if (!raga || !tala || !mood) return '';
    if (!raga || !tala || !mood) return '';
    return [
      'Raga ' + raga.name + ' (' + raga.thaat + ' thaat), ' + raga.time + '.',
      'Aroha: ' + raga.aroha + '. Avaroha: ' + raga.avaroha + '.',
      'Vadi ' + raga.vadi + ', Samvadi ' + raga.samvadi + '. ' + raga.notes + '.',
      'Tala ' + tala.name + ' (' + tala.beats + ' matras), sam on beat 1.',
      'Mood: ' + mood.label + '.',
      'Instrumentation: tanpura drone in Sa, tabla, harmonium, bansuri.',
      'Style: Hindustani classical, ' + state.tempo + ' BPM, ' + state.laya + ' laya.',
    ].join('\n');
  }

  function buildCinematicPrompt(state) {
        var raga = RAGAS.find(function (r) { return r.id === state.ragaId; }) || RAGAS[0];
    var tala = TALAS.find(function (t) { return t.id === state.talaId; }) || TALAS[0];
    var mood = MOODS.find(function (m) { return m.id === state.moodId; }) || MOODS[0];
    if (!raga || !tala || !mood) return '';
    
    return [
      '=== CINEMATIC PROMPT — Gāndharvaveda Studio ===',
      '',
      'STYLE',
      '  ' + mood.prompt,
      '',
      'RĀGA',
      '  Name: ' + raga.name + ' (' + raga.dev + ')',
      '  Thaat: ' + raga.thaat,
      '  Time: ' + raga.time,
      '  Aroha: ' + raga.aroha,
      '  Avaroha: ' + raga.avaroha,
      '  Vadi: ' + raga.vadi + '  ·  Samvadi: ' + raga.samvadi,
      '  Notes: ' + raga.notes,
      '',
      'TĀLA',
      '  Name: ' + tala.name + ' (' + tala.dev + ')',
      '  Beats: ' + tala.beats + ' mātrās',
      '  Sam: ' + tala.sam.join(', ') + '  ·  Khali: ' + tala.khali.join(', ') + '  ·  Tali: ' + tala.tali.join(', '),
      '  Theka: ' + tala.bols.join(' · '),
      '',
      'TEMPO & LAYA',
      '  ' + state.tempo + ' BPM  ·  ' + state.laya + ' laya',
      '  Tanpura drone: Sa + Pa, jawari sustain',
      '',
      'STRUCTURE',
      '  Alap (free, unmetered) → Jod (pulse) → Gat (tala enters) →',
      '  Antara (upper register) → Sanchari (development) → Abhoga (climax)',
      '',
      'INSTRUMENTATION',
      '  Tanpura (drone), Tabla (rhythm), Harmonium (melody),',
      '  Bansuri (counter-melody), Sarangi (sustain), Manjira (accent)',
      '',
      'VOCAL DIRECTION',
      '  Sanskrit/Hindi, pronounced with classical prosody.',
      '  Pitch center: Sa. No autotune. Human breath audible.',
      '',
      'MIX',
      '  Wide stereo, tanpura front-left, tabla front-right,',
      '  vocal center, reverb 1.8s, no compression pumping.',
    ].join('\n');
  }

  /* ═══════════════════════════════════════════════════════════════════════
     SESSION VAULT
     ═══════════════════════════════════════════════════════════════════════ */  

	var VAULT_KEY = 'gandharvaveda.vault.v3';
  function loadVault() {
    try {
      var raw = localStorage.getItem(VAULT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function saveVault(state) {
    try {
      localStorage.setItem(VAULT_KEY, JSON.stringify({
        ragaId: state.ragaId, talaId: state.talaId, moodId: state.moodId,
        tempo: state.tempo, laya: state.laya, text: state.text,
        savedAt: Date.now(),
      }));
    } catch (e) {}
  }

  /* ═══════════════════════════════════════════════════════════════════════
     REDUCER
     ═══════════════════════════════════════════════════════════════════════ */
  var DEFAULTS = {
    ragaId: 'yaman',
    talaId: 'teentaal',
    moodId: 'devotional',
    tempo: 72,
    laya: 'madhya',
    text: 'अथातो ब्रह्मजिज्ञासा ।\nॐ भूर्भुवः स्वः ।\nवागर्थाविव संपृक्तौ वागर्थप्रतिपत्तये ।',
  };

  function safeNum(v, fallback) {
    var n = parseInt(v, 10);
    return Number.isFinite(n) && n >= 40 && n <= 180 ? n : fallback;
  }

  var initial = (function () {
    var v = loadVault() || {};
    return {
      ragaId: RAGAS.some(function (r) { return r.id === v.ragaId; })  ? v.ragaId : DEFAULTS.ragaId,
      talaId: TALAS.some(function (t) { return t.id === v.talaId; })  ? v.talaId : DEFAULTS.talaId,
      moodId: MOODS.some(function (m) { return m.id === v.moodId; })  ? v.moodId : DEFAULTS.moodId,
      tempo:  safeNum(v.tempo, DEFAULTS.tempo),
      laya:   (v.laya === 'vilambit' || v.laya === 'madhya' || v.laya === 'drut') ? v.laya : DEFAULTS.laya,
      text:   typeof v.text === 'string' && v.text.length > 0 ? v.text : DEFAULTS.text,
      tab: 'studio',
    };
  })();

  function reducer(state, action) {
    switch (action.type) {
      case 'setRaga':  return Object.assign({}, state, { ragaId: action.id });
      case 'setTala':  return Object.assign({}, state, { talaId: action.id });
      case 'setMood':  return Object.assign({}, state, { moodId: action.id });
      case 'setTempo': return Object.assign({}, state, { tempo: Number(action.value) || 72 });
      case 'setLaya':  return Object.assign({}, state, { laya: action.value });
      case 'setText':  return Object.assign({}, state, { text: action.value });
      case 'setTab':   return Object.assign({}, state, { tab: action.value });
      default: return state;
    }
  }

  /* ═══════════════════════════════════════════════════════════════════════
     COMPONENTS
     ═══════════════════════════════════════════════════════════════════════ */
  function Toggle(props) {
    return h('span', { className: 'vv-toggle-track' + (props.on ? ' active' : ''), onClick: props.onToggle },
      h('span', { className: 'vv-toggle-thumb' })
    );
  }

  function MoodBadge(props) {
    var mood = MOODS.find(function (m) { return m.id === props.id; });
    if (!mood) return null;
    return h('span', { className: 'vv-mood-badge ' + mood.id }, mood.label);
  }

  function StudioTab(state, dispatch, audio) {
        var raga = RAGAS.find(function (r) { return r.id === state.ragaId; }) || RAGAS[0];
    var tala = TALAS.find(function (t) { return t.id === state.talaId; }) || TALAS[0];

    return h('div', null,
      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Rāga — Scale & Mood'),
        h('div', { className: 'vv-raga-grid' },
          RAGAS.map(function (r) {
            return h('div', {
              key: r.id,
              className: 'vv-raga-card' + (r.id === state.ragaId ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setRaga', id: r.id }); },
            },
              h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' } },
                h('span', { style: { fontWeight: 600 } }, r.name),
                h('span', { className: 'indic', style: { fontSize: '0.85rem', color: '#d4b896' } }, r.dev)
              ),
              h('div', { className: 'vv-raga-color-bar', style: { background: r.color } }),
              h('div', { style: { fontSize: '0.72rem', color: '#d4b896' } }, r.thaat + ' · ' + r.time),
              h('div', { style: { marginTop: '0.5rem' } }, h(MoodBadge, { id: r.mood }))
            );
          })
        )
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Tāla — Rhythm Cycle'),
        h('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' } },
          TALAS.map(function (t) {
            return h('button', {
              key: t.id,
              className: 'vv-nav-btn' + (t.id === state.talaId ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setTala', id: t.id }); },
            }, t.name + ' · ' + t.beats);
          })
        ),
        h('div', { className: 'vv-beat-grid' },
          tala.bols.map(function (bol, i) {
            var pos = i + 1;
            var cls = 'vv-beat-cell';
            if (tala.sam.indexOf(pos) !== -1) cls += ' sam';
            if (tala.khali.indexOf(pos) !== -1) cls += ' khali';
            return h('div', { key: i, className: cls },
              h('div', { style: { fontSize: '0.62rem', opacity: 0.7 } }, pos),
              h('div', { style: { fontWeight: 600, marginTop: '2px' } }, bol)
            );
          })
        )
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Rasa — Emotion & Tempo'),
        h('div', { style: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' } },
          MOODS.map(function (m) {
            return h('button', {
              key: m.id,
              className: 'vv-nav-btn' + (m.id === state.moodId ? ' active' : ''),
              onClick: function () { dispatch({ type: 'setMood', id: m.id }); },
            }, m.label);
          })
        ),
        h('div', { style: { display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' } },
          h('label', { style: { fontSize: '0.78rem' } }, 'Tempo'),
          h('input', {
                        type: 'range', min: 40, max: 180, value: (Number(state.tempo) || 72),
            onChange: function (e) { dispatch({ type: 'setTempo', value: parseInt(e.target.value, 10) }); },
            style: { flex: 1, minWidth: '180px' }
          }),
          h('span', { className: 'font-mono', style: { color: '#c9a227' } }, (Number(state.tempo) || 72) + ' BPM'),
          h('select', {
            className: 'vv-select', value: state.laya,
            onChange: function (e) { dispatch({ type: 'setLaya', value: e.target.value }); },
            style: { width: 'auto' }
          },
            h('option', { value: 'vilambit' }, 'Vilambit (slow)'),
            h('option', { value: 'madhya' }, 'Madhya (medium)'),
            h('option', { value: 'drut' }, 'Drut (fast)')
          )
        )
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Tanpura Drone — Live'),
        h('div', { style: { display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' } },
          h('button', {
            className: 'vv-btn vv-btn-primary',
            onClick: function () {
              var ctx = audio.getCtx();
              if (!ctx) return;
              if (audio._droneOn) { audio.stopDrone(); audio._droneOn = false; }
              else { audio.startDrone(146.83, 220.0); audio._droneOn = true; }
            }
          }, 'Toggle Drone (D)'),
          h('span', { style: { fontSize: '0.72rem', color: '#d4b896' } }, 'Sa + Pa · jawari sustain · LFO vibrato')
        )
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Lyrics — Devanagari / IAST'),
        h('textarea', {
          className: 'vv-textarea vv-input indic',
          value: state.text,
          onChange: function (e) { dispatch({ type: 'setText', value: e.target.value }); },
          placeholder: 'अथातो ब्रह्मजिज्ञासा ।',
        })
      )
    );
  }

  function ScansionTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var scan = useMemo(function () { return scanPingal(state.text); }, [state.text]);
    var notation = useMemo(function () { return pingalNotation(scan.syllables); }, [scan]);

    return h('div', null,
      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Pingal Mātrā Scan'),
        h('div', { style: { display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' } },
          h('span', { className: 'vv-badge' }, 'Syllables: ' + scan.syllables.length),
          h('span', { className: 'vv-badge' }, 'Total mātrās: ' + scan.totalMatras),
          h('span', { className: 'vv-badge' }, 'Guru: ' + scan.syllables.filter(function (s) { return s.weight === 2; }).length),
          h('span', { className: 'vv-badge' }, 'Laghu: ' + scan.syllables.filter(function (s) { return s.weight === 1; }).length)
        ),
        h('div', {
          className: 'font-mono',
          style: {
            background: '#0a0308', borderRadius: '8px', padding: '0.85rem',
            fontSize: '0.85rem', lineHeight: '1.9', wordBreak: 'break-all',
            border: '1px solid #7a2a33', maxHeight: '260px', overflowY: 'auto'
          }
        },
          scan.syllables.map(function (s, i) {
            return h('span', {
              key: i,
              className: s.weight === 2 ? 'vv-pingal-guru' : 'vv-pingal-laghu',
              style: { marginRight: '2px', cursor: 'default' },
              title: (s.weight === 2 ? 'Guru (2)' : 'Laghu (1)') + (s.forced ? ' · verse-final' : '')
            }, s.char);
          })
        ),
        h('div', { className: 'font-mono', style: { marginTop: '0.75rem', color: '#c9a227', letterSpacing: '0.1em' } }, notation)
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Recitation Audio'),
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap' } },
          h('button', {
            className: 'vv-btn vv-btn-primary',
            onClick: function () {
              var wav = renderScansionWAV(scan.syllables, 220.0, 22050);
              var blob = encodeWAV(wav.samples, wav.sampleRate);
              var url = URL.createObjectURL(blob);
              var a = new Audio(url);
              a.play();
            }
          }, '▶ Play Scansion (Synth)'),
          h('button', {
            className: 'vv-btn vv-btn-blue',
            onClick: function () { speakDevanagari(state.text, 0.85); }
          }, '▶ Web Speech'),
          h('button', {
            className: 'vv-btn',
            onClick: function () {
              var wav = renderScansionWAV(scan.syllables, 220.0, 22050);
              var blob = encodeWAV(wav.samples, wav.sampleRate);
              downloadBlob(blob, 'gandharvaveda-scansion.wav');
            }
          }, '⤓ Download .wav')
        )
      )
    );
  }

  function PromptTab(props) {
    var state = props.state;
    var dispatch = props.dispatch;
    var compact = useMemo(function () { return buildCompactPrompt(state); }, [state]);
    var cinematic = useMemo(function () { return buildCinematicPrompt(state); }, [state]);
    var [copied, setCopied] = useState('');
    var [mode, setMode] = useState('cinematic');

    var text = mode === 'cinematic' ? cinematic : compact;

    return h('div', null,
      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'AI Prompt — Suno / Udio'),
        h('div', { style: { display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' } },
          h('button', {
            className: 'vv-nav-btn' + (mode === 'cinematic' ? ' active' : ''),
            onClick: function () { setMode('cinematic'); }
          }, 'Cinematic'),
          h('button', {
            className: 'vv-nav-btn' + (mode === 'compact' ? ' active' : ''),
            onClick: function () { setMode('compact'); }
          }, 'Compact'),
          h('button', {
            className: 'vv-btn vv-btn-primary',
            style: { marginLeft: 'auto' },
            onClick: function () {
              copyText(text);
              setCopied(mode);
              setTimeout(function () { setCopied(''); }, 1600);
            }
          }, copied === mode ? '✓ Copied' : '⧉ Copy')
        ),
        h('div', { className: 'vv-prompt-box' }, text)
      ),

      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Exports'),
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap' } },
          h('button', {
            className: 'vv-btn vv-btn-green',
            onClick: function () {
                            var tala = TALAS.find(function (t) { return t.id === state.talaId; }) || TALAS[0];
              var bytes = buildMIDI(tala, state.tempo);
              downloadBlob(new Blob([bytes], { type: 'audio/midi' }), 'gandharvaveda-' + tala.id + '.mid');
            }
          }, '⤓ MIDI (2 cycles)'),
          h('button', {
            className: 'vv-btn',
            onClick: function () {
              var scan = scanPingal(state.text);
              var wav = renderScansionWAV(scan.syllables, 220.0, 22050);
              downloadBlob(encodeWAV(wav.samples, wav.sampleRate), 'gandharvaveda-scansion.wav');
            }
          }, '⤓ Scansion .wav'),
          h('button', {
            className: 'vv-btn',
            onClick: function () {
              var blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
              downloadBlob(blob, 'gandharvaveda-session.json');
            }
          }, '⤓ Session JSON')
        )
      )
    );
  }

  function AboutTab() {
    return h('div', null,
      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'About Gāndharvaveda'),
        h('p', { style: { lineHeight: 1.7 } },
          'Gāndharvaveda, the Upaveda of music and drama, is attributed to Bharata Muni in the Nāṭyaśāstra. ' +
          'This studio implements two complementary engines:'
        ),
        h('ul', { style: { lineHeight: 1.8 } },
          h('li', null, h('strong', null, 'Pingal scansion'), ' — parses Devanagari into Laghu (1 mātrā) and Guru (2 mātrā) syllables, with verse-final guru optional.'),
          h('li', null, h('strong', null, 'AI prompt studio'), ' — composes a structured prompt from Rāga + Tāla + Rasa + tempo for neural music generators.')
        )
      ),
      h('div', { className: 'vv-panel' },
        h('div', { className: 'vv-panel-title' }, 'Mood → Rasa Map'),
        h('table', { className: 'vv-mood-table' },
          h('thead', null, h('tr', null,
            h('th', null, 'Rasa'), h('th', null, 'Mood'), h('th', null, 'Prompt fragment')
          )),
          h('tbody', null,
            MOODS.map(function (m) {
              return h('tr', { key: m.id },
                h('td', null, h('span', { className: 'vv-mood-badge ' + m.id }, m.label)),
                h('td', null, m.id),
                h('td', { className: 'font-mono', style: { fontSize: '0.7rem', color: '#d4b896' } }, m.prompt)
              );
            })
          )
        )
      )
    );
  }

  function App() {
    var [state, dispatch] = useReducer(reducer, initial);
    var audio = useAudioEngine();

    useEffect(function () {
      var t = setTimeout(function () { saveVault(state); }, 400);
      return function () { clearTimeout(t); };
    }, [state.ragaId, state.talaId, state.moodId, state.tempo, state.laya, state.text]);

    useEffect(function () {
      function onKey(e) {
        if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
        if (e.key === 'd' || e.key === 'D') {
          var ctx = audio.getCtx();
          if (!ctx) return;
          if (audio._droneOn) { audio.stopDrone(); audio._droneOn = false; }
          else { audio.startDrone(146.83, 220.0); audio._droneOn = true; }
        }
      }
      window.addEventListener('keydown', onKey);
      return function () { window.removeEventListener('keydown', onKey); };
    }, []);

    useEffect(function () {
      return function () { audio.stopDrone(); };
    }, []);

        var raga = RAGAS.find(function (r) { return r.id === state.ragaId; }) || RAGAS[0];
    var tala = TALAS.find(function (t) { return t.id === state.talaId; }) || TALAS[0];

    return h('div', null,
      h('a', { className: 'vv-external-link', href: '/' }, '← Aigaane'),
      h('header', { className: 'vv-header glass' },
        h('div', { className: 'vv-header-inner' },
          h('div', { className: 'vv-brand' }, 'Gāndharvaveda Studio'),
          h('nav', { className: 'vv-nav' },
            ['studio', 'scansion', 'prompt', 'about'].map(function (t) {
              return h('button', {
                key: t,
                className: 'vv-nav-btn' + (state.tab === t ? ' active' : ''),
                onClick: function () { dispatch({ type: 'setTab', value: t }); }
              }, t.charAt(0).toUpperCase() + t.slice(1));
            })
          )
        )
      ),

      h('main', { className: 'vv-container' },
        h('div', { style: { display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1rem' } },
          h('span', { className: 'vv-badge' }, raga.name + ' · ' + raga.thaat),
          h('span', { className: 'vv-badge' }, tala.name + ' · ' + tala.beats + ' mātrās'),
          h(MoodBadge, { id: state.moodId })
        ),

      state.tab === 'studio'   ? h(StudioTab,   { state: state, dispatch: dispatch, audio: audio }) :
        state.tab === 'scansion' ? h(ScansionTab, { state: state, dispatch: dispatch, audio: audio }) :
        state.tab === 'prompt'   ? h(PromptTab,   { state: state, dispatch: dispatch }) :
        h(AboutTab)
      ),

      h('footer', { className: 'vv-footer-fixed' },
        h('span', { style: { fontSize: '0.7rem', color: '#d4b896' } },
          'Press D for drone · ' + RAGAS.length + ' rāgas · ' + TALAS.length + ' tālas'
        ),
        h('button', {
          className: 'vv-btn vv-btn-primary',
          onClick: function () { dispatch({ type: 'setTab', value: 'prompt' }); }
        }, 'Generate Prompt →')
      )
    );
  }

  var container = document.getElementById('root');
  if (!container) return;
  container.innerHTML = '';
  var root = ReactDOM.createRoot(container);
  root.render(h(App));
})();