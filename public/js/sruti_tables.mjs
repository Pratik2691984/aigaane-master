/**
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
