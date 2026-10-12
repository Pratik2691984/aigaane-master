/**
 * Pingal Sastra Prosody & Scansion Engine - Verified Production Build
 */

const DEVA_VOWELS_INDEP = {
  'अ': { type: 'l' }, 'इ': { type: 'l' }, 'उ': { type: 'l' },
  'ऋ': { type: 'l' }, 'ऌ': { type: 'l' },
  'आ': { type: 'G' }, 'ई': { type: 'G' }, 'ऊ': { type: 'G' },
  'ॠ': { type: 'G' }, 'ॡ': { type: 'G' }, 'ए': { type: 'G' },
  'ऐ': { type: 'G' }, 'ओ': { type: 'G' }, 'औ': { type: 'G' }
};

const DEVA_MATRAS = {
  'ि': { type: 'l' }, 'ु': { type: 'l' }, 'ृ': { type: 'l' }, 'ॢ': { type: 'l' },
  'ा': { type: 'G' }, 'ी': { type: 'G' }, 'ू': { type: 'G' }, 'ॄ': { type: 'G' },
  'ॣ': { type: 'G' }, 'े': { type: 'G' }, 'ै': { type: 'G' }, 'ो': { type: 'G' },
  'ौ': { type: 'G' }
};

const IAST_VOWELS = {
  'a': { type: 'l' }, 'i': { type: 'l' }, 'u': { type: 'l' }, 'ṛ': { type: 'l' }, 'ḷ': { type: 'l' },
  'ā': { type: 'G' }, 'ī': { type: 'G' }, 'ū': { type: 'G' }, 'ṝ': { type: 'G' }, 'e': { type: 'G' },
  'ai': { type: 'G' }, 'o': { type: 'G' }, 'au': { type: 'G' }
};

const VIRAMA = '्';
const ANUSVARA = 'ं';
const VISARGA = 'ः';
const AVAGRAHA = 'ऽ';

export const CHANDAS_CANON = [
  { id: 'gayatri',     name: 'Gāyatrī',     padas: 3, sylPerPada: 8,  totalMatras: 24, basePattern: 'LGLGLGLG' },
  { id: 'anustubh',    name: 'Anuṣṭubh',    padas: 4, sylPerPada: 8,  totalMatras: 32, basePattern: 'LGLGLLGG' },
  { id: 'brihati',     name: 'Bṛhatī',      padas: 4, sylPerPada: 9,  totalMatras: 36, basePattern: 'LLGLLGLLG' },
  { id: 'pankti',      name: 'Paṅkti',      padas: 4, sylPerPada: 10, totalMatras: 40, basePattern: 'LGLGLGLLGG' },
  { id: 'tristubh',    name: 'Triṣṭubh',    padas: 4, sylPerPada: 11, totalMatras: 44, basePattern: 'GLLGLLGLLGG' },
  { id: 'jagati',      name: 'Jagatī',      padas: 4, sylPerPada: 12, totalMatras: 48, basePattern: 'LGLGLGLGLGLG' }
];

export function detectScript(text) {
  return /[\u0900-\u097F]/.test(text) ? 'devanagari' : 'iast';
}

export function tokenizeDevanagari(text) {
  const clean = text.replace(/[\s।॥\.,\-]/g, '');
  const tokens = [];
  const n = clean.length;
  let i = 0;

  while (i < n) {
    const ch = clean[i];
    if (ch === AVAGRAHA) { i++; continue; }

    if (DEVA_VOWELS_INDEP[ch]) {
      let cluster = ch;
      const vInfo = DEVA_VOWELS_INDEP[ch];
      i++;
      let modifier = null;
      if (i < n && (clean[i] === ANUSVARA || clean[i] === VISARGA)) {
        modifier = clean[i];
        cluster += modifier;
        i++;
      }
      tokens.push({ text: cluster, vowelType: vInfo.type, modifier, hasTrailingHalanta: false, onsetConsonantCount: 0 });
      continue;
    }

    if (/[\u0915-\u0939]/.test(ch)) {
      let cluster = '';
      let consonantCount = 0;

      while (i < n && /[\u0915-\u0939]/.test(clean[i])) {
        cluster += clean[i];
        consonantCount++;
        i++;

        if (i < n && clean[i] === VIRAMA) {
          cluster += clean[i];
          i++;
          if (i >= n || !/[\u0915-\u0939]/.test(clean[i])) {
            if (tokens.length > 0) {
              tokens[tokens.length - 1].text += cluster;
              tokens[tokens.length - 1].hasTrailingHalanta = true;
            }
            cluster = '';
            break;
          }
        } else {
          break;
        }
      }

      if (cluster.length === 0) continue;

      let vowelType = 'l';
      let modifier = null;

      if (i < n && DEVA_MATRAS[clean[i]]) {
        vowelType = DEVA_MATRAS[clean[i]].type;
        cluster += clean[i];
        i++;
      }

      if (i < n && (clean[i] === ANUSVARA || clean[i] === VISARGA)) {
        modifier = clean[i];
        cluster += modifier;
        i++;
      }

      tokens.push({ text: cluster, vowelType, modifier, hasTrailingHalanta: false, onsetConsonantCount: consonantCount });
      continue;
    }
    i++;
  }
  return tokens;
}

export function tokenizeIAST(text) {
  const clean = text.replace(/[\s।॥\.,\-]/g, '');
  const tokens = [];
  const n = clean.length;
  let i = 0;

  const diphthongs = ['ai', 'au'];
  const consonants = [
    'kh', 'gh', 'ch', 'jh', 'ṭh', 'ḍh', 'th', 'dh', 'ph', 'bh',
    'k', 'g', 'ṅ', 'c', 'j', 'ñ', 'ṭ', 'ḍ', 'ṇ', 't', 'd', 'n',
    'p', 'b', 'm', 'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h'
  ];

  while (i < n) {
    let onset = '';
    let consonantCount = 0;

    let isVowelInitial = false;
    for (const d of diphthongs) {
      if (clean.startsWith(d, i)) { isVowelInitial = true; break; }
    }
    if (!isVowelInitial && IAST_VOWELS[clean[i]?.toLowerCase()]) isVowelInitial = true;

    if (!isVowelInitial) {
      let matched = true;
      while (matched && i < n) {
        matched = false;
        for (const c of consonants) {
          if (clean.startsWith(c, i)) {
            onset += c;
            i += c.length;
            consonantCount++;
            matched = true;
            break;
          }
        }
      }
    }

    let vowelStr = '';
    let vowelType = null;

    for (const d of diphthongs) {
      if (clean.startsWith(d, i)) {
        vowelStr = d;
        vowelType = 'G';
        i += d.length;
        break;
      }
    }

    if (!vowelType && i < n && IAST_VOWELS[clean[i]?.toLowerCase()]) {
      vowelStr = clean[i];
      vowelType = IAST_VOWELS[clean[i].toLowerCase()].type;
      i++;
    }

    if (!vowelType) {
      if (onset.length > 0 && tokens.length > 0) {
        tokens[tokens.length - 1].text += onset;
        tokens[tokens.length - 1].hasTrailingHalanta = true;
      }
      continue;
    }

    let modifier = null;
    if (i < n && (clean[i] === 'ṃ' || clean[i] === 'ḥ')) {
      modifier = clean[i];
      i++;
    }

    tokens.push({ text: onset + vowelStr + (modifier || ''), vowelType, modifier, hasTrailingHalanta: false, onsetConsonantCount: consonantCount });
  }
  return tokens;
}

export function scanTokens(tokens, options = {}) {
  const strictPadaEnd = options.strictPadaEnd ?? false;
  const weights = [];
  const len = tokens.length;

  for (let i = 0; i < len; i++) {
    const tok = tokens[i];
    let weight = tok.vowelType;

    if (weight === 'G' || tok.modifier) {
      weight = 'G';
    } else if (i + 1 < len) {
      const nextTok = tokens[i + 1];
      if (nextTok.onsetConsonantCount >= 2 || tok.hasTrailingHalanta) {
        weight = 'G';
      }
    } else if (tok.hasTrailingHalanta) {
      weight = 'G';
    }

    if (i === len - 1 && strictPadaEnd) {
      weight = 'G';
    }

    weights.push({ syllable: tok.text, weight, matras: weight === 'G' ? 2 : 1 });
  }
  return weights;
}

export function matchChandas(weights) {
  const syllableCount = weights.length;
  const totalMatras = weights.reduce((acc, cur) => acc + cur.matras, 0);
  const weightStr = weights.map(w => w.weight).join('');

  let bestMatch = CHANDAS_CANON[1];
  let lowestPenalty = Infinity;

  for (const c of CHANDAS_CANON) {
    const canonicalCount = c.sylPerPada * c.padas;
    const sylDelta = Math.abs(canonicalCount - syllableCount);
    let hammingDist = 0;
    const patLen = c.basePattern.length;
    for (let i = 0; i < syllableCount; i++) {
      if (weightStr[i] !== c.basePattern[i % patLen]) hammingDist++;
    }
    const penalty = (sylDelta * 3.0) + (hammingDist * 1.0);
    if (penalty < lowestPenalty) {
      lowestPenalty = penalty;
      bestMatch = c;
    }
  }

  const maxPossible = bestMatch.sylPerPada * bestMatch.padas * 4.0;
  const confidence = Math.max(0, Math.min(1.0, 1.0 - (lowestPenalty / maxPossible)));

  return { ...bestMatch, confidence: Number(confidence.toFixed(3)), observedSyllables: syllableCount, observedMatras: totalMatras };
}

export function compileStepMatrix(weights, totalSteps = 16) {
  const matrix = [];
  const sylCount = weights.length;

  for (let step = 0; step < totalSteps; step++) {
    if (sylCount === 0) {
      matrix.push({ step, weight: null, duration: 0, velocity: 0, gate: 0, syllable: '' });
      continue;
    }
    const sylIndex = Math.floor((step / totalSteps) * sylCount);
    const syl = weights[sylIndex];
    const isGuru = syl.weight === 'G';

    matrix.push({
      step,
      weight: syl.weight,
      duration: isGuru ? 2.0 : 1.0,
      velocity: isGuru ? 0.95 : 0.65,
      gate: isGuru ? 0.85 : 0.40,
      syllable: syl.syllable
    });
  }
  return matrix;
}

export class PingalEngine {
  constructor(options = {}) {
    this.options = {
      strictPadaEnd: options.strictPadaEnd ?? false,
      expandVedicSemivowels: options.expandVedicSemivowels ?? false
    };
  }

  scan(text) {
    let processedText = text;
    if (this.options.expandVedicSemivowels) {
      processedText = processedText
        .replace(/वरेण्य/g, 'वरेणिय')
        .replace(/vareṇy/g, 'vareṇiy');
    }

    const script = detectScript(processedText);
    const tokens = script === 'devanagari'
      ? tokenizeDevanagari(processedText)
      : tokenizeIAST(processedText);

    const weights = scanTokens(tokens, this.options);
    const chandasMatch = matchChandas(weights);

    return {
      script,
      totalSyllables: weights.length,
      totalMatras: chandasMatch.observedMatras,
      weights,
      weightString: weights.map(w => w.weight).join(''),
      matchedChandas: chandasMatch
    };
  }

  compileStepMatrix(scannedResult, totalSteps = 16) {
    return compileStepMatrix(scannedResult.weights, totalSteps);
  }
}
