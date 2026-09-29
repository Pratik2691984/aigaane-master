import { PingalEngine } from './pingal_engine.mjs';

const engine = new PingalEngine({ strictPadaEnd: false, expandVedicSemivowels: false });
const engineVedic = new PingalEngine({ strictPadaEnd: false, expandVedicSemivowels: true });

const testSuites = [
  { name: 'Conjunct traversal: krsna (Devanagari)', input: 'कृष्ण', expectedWeights: 'Gl', expectedSyllables: 2 },
  { name: 'Conjunct traversal: krsna (IAST)', input: 'kṛṣṇa', expectedWeights: 'Gl', expectedSyllables: 2 },
  { name: 'Samyogapara check: gacchati (Devanagari)', input: 'गच्छति', expectedWeights: 'Gll', expectedSyllables: 3 },
  { name: 'Vowel-Initial word: atha (IAST)', input: 'atha', expectedWeights: 'll', expectedSyllables: 2 },
  { name: 'Vowel-Initial word: iti (Devanagari)', input: 'इति', expectedWeights: 'll', expectedSyllables: 2 },
  { name: 'Word-final halanta: ramam (IAST)', input: 'rāmam', expectedWeights: 'GG', expectedSyllables: 2 },
  { name: 'Anusvara & Visarga: samskrtam ramah', input: 'संस्कृतम् रामः', expectedWeights: 'GlGGG', expectedSyllables: 5 },
  { name: 'Gayatri Pada 1 (Standard 7 syl)', input: 'तत्सवितुर्वरेण्यम्', expectedWeights: 'GllGlGG', expectedSyllables: 7, customEngine: engine },
  { name: 'Gayatri Pada 1 (Vedic 8 syl expanded)', input: 'tat savitur vareṇyaṃ', expectedWeights: 'GllGlGlG', expectedSyllables: 8, customEngine: engineVedic },
  { name: 'Gita 1.1 Hemistich (16 syl Anustubh)', input: 'धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः', expectedWeights: 'GGGGlGGGllGGlGlG', expectedSyllables: 16 }
];

console.log('\n================================================================');
console.log('       PINGAL SASTRA COMPUTATIONAL VERIFICATION TABLE           ');
console.log('================================================================\n');

let passed = 0;
for (const tc of testSuites) {
  const eng = tc.customEngine || engine;
  const res = eng.scan(tc.input);

  const sylOk = res.totalSyllables === tc.expectedSyllables;
  const weightOk = !tc.expectedWeights || res.weightString === tc.expectedWeights;
  const ok = sylOk && weightOk;
  if (ok) passed++;

  const status = ok ? ' PASS ' : ' FAIL ';
  console.log('[' + status + '] ' + tc.name.padEnd(42) + ' | Syl: ' + String(res.totalSyllables).padStart(2) + ' | Weights: ' + res.weightString);
}

console.log('\n----------------------------------------------------------------');
console.log('Execution Summary: ' + passed + ' / ' + testSuites.length + ' Test Suites Succeeded.');
console.log('----------------------------------------------------------------\n');
