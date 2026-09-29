import json

sruti_code = r'''/**
 * 22-Śruti Harmonic Lattice & Thaat Repository
 * Mathematical ratios derived from Bharata Muni Nāṭyaśāstra & Śārṅgadeva Saṅgītaratnākara.
 * Exact cents calculated via: 1200 * Math.log2(numerator / denominator)
 */

export const SRUTI_22_DATA = [
  { id: 1,  name: 'Kṣobhiṇī',   svara: 'Tīvra komal Re', ratio: [256, 243] },
  { id: 2,  name: 'Tīvrā',      svara: 'Komal Re (r)',   ratio: [16, 15]   },
  { id: 3,  name: 'Kumudvatī',  svara: 'Śuddha Re (R)',  ratio: [10, 9]    },
  { id: 4,  name: 'Mandā',      svara: 'Tīvra Re',       ratio: [9, 8]     },
  { id: 5,  name: 'Chandovatī', svara: 'Ati-komal Ga',   ratio: [32, 27]   },
  { id: 6,  name: 'Dayāvatī',   svara: 'Komal Ga (g)',   ratio: [6, 5]     },
  { id: 7,  name: 'Rañjanī',    svara: 'Śuddha Ga (G)',  ratio: [5, 4]     },
  { id: 8,  name: 'Raktikā',    svara: 'Tīvra Ga',       ratio: [81, 64]   },
  { id: 9,  name: 'Raudrī',     svara: 'Śuddha Ma (m)',  ratio: [4, 3]     },
  { id: 10, name: 'Krodhā',     svara: 'Tīvra Ma (krodha)', ratio: [27, 20]},
  { id: 11, name: 'Vajrikā',    svara: 'Tīvra-tara Ma',  ratio: [45, 32]   },
  { id: 12, name: 'Prasāriṇī',  svara: 'Tīvra-tama Ma (M)', ratio: [729, 512]},
  { id: 13, name: 'Prīti',      svara: 'Pañcama (Pa)',   ratio: [3, 2]     },
  { id: 14, name: 'Mārjanī',    svara: 'Komal Dha (d)',  ratio: [128, 81]  },
  { id: 15, name: 'Kṣiti',      svara: 'Śuddha Dha (D)', ratio: [8, 5]     },
  { id: 16, name: 'Raktā',      svara: 'Tīvra Dha',      ratio: [5, 3]     },
  { id: 17, name: 'Sandīpinī',  svara: 'Tīvra-tara Dha', ratio: [27, 16]   },
  { id: 18, name: 'Ālāpinī',    svara: 'Ati-komal Ni',   ratio: [16, 9]    },
  { id: 19, name: 'Madantī',    svara: 'Komal Ni (n)',   ratio: [9, 5]     },
  { id: 20, name: 'Rohiṇī',     svara: 'Śuddha Ni (N)',  ratio: [15, 8]    },
  { id: 21, name: 'Ramyā',      svara: 'Tīvra Ni',       ratio: [243, 128] },
  { id: 22, name: 'Ugrā',       svara: 'Tāra Ṣaḍja (S\')', ratio: [2, 1]   }
].map(entry => {
  const [num, den] = entry.ratio;
  const cents = 1200 * Math.log2(num / den);
  return { ...entry, cents: Number(cents.toFixed(2)) };
});

export const THAAT_MAP = {
  bilawal: { name: 'Bilawal', srutiIds: [22, 4, 7, 9, 13, 16, 20] },
  yaman:   { name: 'Kalyan / Yaman', srutiIds: [22, 4, 7, 12, 13, 16, 20] },
  bhairav: { name: 'Bhairav', srutiIds: [22, 2, 7, 9, 13, 14, 20] },
  kafi:    { name: 'Kafi', srutiIds: [22, 4, 6, 9, 13, 16, 19] },
  bhairavi:{ name: 'Bhairavi', srutiIds: [22, 2, 6, 9, 13, 14, 19] },
  asavari: { name: 'Asavari', srutiIds: [22, 4, 6, 9, 13, 14, 19] },
  todi:    { name: 'Todi', srutiIds: [22, 2, 6, 12, 13, 14, 20] },
  purvi:   { name: 'Purvi', srutiIds: [22, 2, 7, 12, 13, 14, 20] },
  marwa:   { name: 'Marwa', srutiIds: [22, 2, 7, 12, 16, 20] },
  khammaj: { name: 'Khammaj', srutiIds: [22, 7, 9, 13, 16, 19] }
};

export function getSrutiById(id) {
  if (id === 0 || id === 22) return { id: 22, name: 'Ṣaḍja (Sa)', cents: 0.0 };
  return SRUTI_22_DATA.find(s => s.id === id) || SRUTI_22_DATA[0];
}

export function getThaatCents(thaatKey) {
  const thaat = THAAT_MAP[thaatKey] || THAAT_MAP.bilawal;
  return thaat.srutiIds.map(id => id === 22 ? 0.0 : getSrutiById(id).cents);
}

export function tuneOscillator(oscNode, baseHz, centsOffset, startTime = 0) {
  if (!oscNode || !oscNode.frequency) return;
  oscNode.frequency.setValueAtTime(baseHz, startTime);
  if (oscNode.detune) {
    oscNode.detune.setValueAtTime(centsOffset, startTime);
  }
}
'''

rasa_code = r'''/**
 * Nava Rasa Envelope Dynamics
 * Maps 9 classical rasas to Web Audio ADSR, Filter Q, and Cutoff Modifiers.
 */

export const RASA_ENVELOPES = {
  shringara: { name: 'Śṛṅgāra (Aesthetic/Romantic)', attack: 0.18, decay: 0.35, sustain: 0.70, release: 1.20, filterQ: 2.5, cutoffMod: 1.4 },
  hasya:     { name: 'Hāsya (Comic/Lively)',        attack: 0.02, decay: 0.12, sustain: 0.40, release: 0.25, filterQ: 6.0, cutoffMod: 2.2 },
  karuna:    { name: 'Karuṇa (Pathos/Compassion)',  attack: 0.30, decay: 0.50, sustain: 0.85, release: 2.00, filterQ: 1.0, cutoffMod: 0.7 },
  raudra:    { name: 'Raudra (Fury/Tempest)',       attack: 0.01, decay: 0.08, sustain: 0.90, release: 0.15, filterQ: 8.5, cutoffMod: 3.5 },
  vira:      { name: 'Vīra (Heroic/Majesty)',       attack: 0.05, decay: 0.25, sustain: 0.80, release: 0.80, filterQ: 4.0, cutoffMod: 1.8 },
  bhayanaka: { name: 'Bhayānaka (Terrifying)',      attack: 0.40, decay: 0.60, sustain: 0.50, release: 1.80, filterQ: 7.0, cutoffMod: 0.5 },
  bibhatsa:  { name: 'Bībhatsa (Aversive/Disgust)', attack: 0.03, decay: 0.40, sustain: 0.30, release: 0.40, filterQ: 9.0, cutoffMod: 0.9 },
  adbhuta:   { name: 'Adbhuta (Wonder/Mystery)',    attack: 0.22, decay: 0.30, sustain: 0.75, release: 1.50, filterQ: 3.5, cutoffMod: 2.0 },
  shanta:    { name: 'Śānta (Serene/Peace)',        attack: 0.50, decay: 0.80, sustain: 0.95, release: 2.80, filterQ: 0.8, cutoffMod: 0.8 }
};

export function applyRasaEnvelope(gainNode, filterNode, rasaKey, startTime, duration = 0.5, peakGain = 0.85, baseCutoff = 1200) {
  const env = RASA_ENVELOPES[rasaKey] || RASA_ENVELOPES.shanta;

  // Safe gain ADSR curve
  if (gainNode && gainNode.gain) {
    const g = gainNode.gain;
    g.cancelScheduledValues(startTime);
    g.setValueAtTime(0.0001, startTime);
    g.linearRampToValueAtTime(peakGain, startTime + env.attack);
    g.exponentialRampToValueAtTime(Math.max(0.0001, peakGain * env.sustain), startTime + env.attack + env.decay);
    g.setValueAtTime(Math.max(0.0001, peakGain * env.sustain), startTime + duration);
    g.exponentialRampToValueAtTime(0.0001, startTime + duration + env.release);
  }

  // Filter Shaping
  if (filterNode && filterNode.frequency) {
    const f = filterNode.frequency;
    const targetCutoff = Math.max(100, Math.min(18000, baseCutoff * env.cutoffMod));
    f.cancelScheduledValues(startTime);
    f.setValueAtTime(targetCutoff, startTime);
    if (filterNode.Q) {
      filterNode.Q.setValueAtTime(env.filterQ, startTime);
    }
  }
}
'''

test_code = r'''import { SRUTI_22_DATA, THAAT_MAP, getThaatCents, getSrutiById } from './sruti_tables.mjs';
import { RASA_ENVELOPES } from './rasa_envelopes.mjs';

console.log('\n================================================================');
console.log('       AUDIO FOUNDATIONS: 22-ŚRUTI & RASA VERIFICATION          ');
console.log('================================================================\n');

// 1. Verify Pañcama (Pa = 3/2 = 701.96 cents)
const pa = SRUTI_22_DATA.find(s => s.name === 'Prīti');
const paOk = pa && pa.cents === 701.96;
console.log(`[\({paOk ? ' PASS ' : ' FAIL '}] Śruti 13 (Pañcama 3/2):\){pa.cents} cents`);

// 2. Verify Komal Re (Tīvrā 16/15 = 111.73 cents)
const komalRe = SRUTI_22_DATA.find(s => s.name === 'Tīvrā');
const reOk = komalRe && komalRe.cents === 111.73;
console.log(`[\({reOk ? ' PASS ' : ' FAIL '}] Śruti 2 (Komal Re 16/15):\){komalRe.cents} cents`);

// 3. Verify Tīvra Ma (Prasāriṇī 729/512 = 611.73 cents)
const teevraMa = SRUTI_22_DATA.find(s => s.name === 'Prasāriṇī');
const maOk = teevraMa && teevraMa.cents === 611.73;
console.log(`[\({maOk ? ' PASS ' : ' FAIL '}] Śruti 12 (Tīvra Ma 729/512):\){teevraMa.cents} cents`);

// 4. Verify 10 Thaats defined
const thaatCount = Object.keys(THAAT_MAP).length;
const thaatOk = thaatCount === 10;
console.log(`[\({thaatOk ? ' PASS ' : ' FAIL '}] Canonical Thaats defined:\){thaatCount} / 10`);

// 5. Verify Yaman Thaat cent scale
const yamanCents = getThaatCents('yaman');
const yamanOk = yamanCents[3] === 611.73 && yamanCents.length === 7;
console.log(`[\({yamanOk ? ' PASS ' : ' FAIL '}] Yaman scale: [\){yamanCents.join(', ')}]`);

// 6. Verify 9 Rasas
const rasaCount = Object.keys(RASA_ENVELOPES).length;
const rasaOk = rasaCount === 9;
console.log(`[\({rasaOk ? ' PASS ' : ' FAIL '}] Nava Rasas defined:\){rasaCount} / 9`);

console.log('\n----------------------------------------------------------------');
const allOk = paOk && reOk && maOk && thaatOk && yamanOk && rasaOk;
console.log(`Foundations Status: ${allOk ? 'ALL 6 CORE CHECKS PASSED' : 'SOME CHECKS FAILED'}`);
console.log('----------------------------------------------------------------\n');
'''

with open('scripts/sruti_tables.mjs', 'w', encoding='utf-8') as f:
    f.write(sruti_code)

with open('scripts/rasa_envelopes.mjs', 'w', encoding='utf-8') as f:
    f.write(rasa_code)

with open('scripts/test_audio_foundations.mjs', 'w', encoding='utf-8') as f:
    f.write(test_code)

print('[OK] Audio foundations files created successfully.')
