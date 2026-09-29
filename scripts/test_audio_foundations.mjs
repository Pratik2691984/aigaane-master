import { SRUTI_22_DATA, THAAT_MAP, getThaatCents } from './sruti_tables.mjs';
import { RASA_ENVELOPES } from './rasa_envelopes.mjs';

console.log('\n================================================================');
console.log('       AUDIO FOUNDATIONS: 22-SRUTI & RASA VERIFICATION          ');
console.log('================================================================\n');

const results = [];

// 1. Pancama (3/2 = 701.96 cents) — id 13
const pa = SRUTI_22_DATA.find(s => s.id === 13);
const paOk = !!(pa && Math.abs(pa.cents - 701.96) < 0.01);
results.push(['Sruti 13 (Pancama 3/2)', paOk, pa ? pa.cents + ' cents' : 'MISSING']);

// 2. Komal Re (16/15 = 111.73 cents) — id 2
const komalRe = SRUTI_22_DATA.find(s => s.id === 2);
const reOk = !!(komalRe && Math.abs(komalRe.cents - 111.73) < 0.01);
results.push(['Sruti 2 (Komal Re 16/15)', reOk, komalRe ? komalRe.cents + ' cents' : 'MISSING']);

// 3. Tivra Ma (729/512 = 611.73 cents) — id 12
const teevraMa = SRUTI_22_DATA.find(s => s.id === 12);
const maOk = !!(teevraMa && Math.abs(teevraMa.cents - 611.73) < 0.01);
results.push(['Sruti 12 (Tivra Ma 729/512)', maOk, teevraMa ? teevraMa.cents + ' cents' : 'MISSING']);

// 4. Ten thaats defined
const thaatCount = Object.keys(THAAT_MAP).length;
const thaatOk = thaatCount === 10;
results.push(['Canonical Thaats defined', thaatOk, thaatCount + ' / 10']);

// 5. Yaman scale (7 notes, index 3 must be Tivra Ma at 611.73 cents)
const yamanCents = getThaatCents('yaman');
const yamanOk = yamanCents.length === 7 && Math.abs(yamanCents[3] - 611.73) < 0.01;
results.push(['Yaman scale', yamanOk, '[' + yamanCents.join(', ') + ']']);

// 6. Nine rasas defined
const rasaCount = Object.keys(RASA_ENVELOPES).length;
const rasaOk = rasaCount === 9;
results.push(['Nava Rasas defined', rasaOk, rasaCount + ' / 9']);

// Report every result
for (const [label, ok, detail] of results) {
  const tag = ok ? ' PASS ' : ' FAIL ';
  console.log('[' + tag + '] ' + label + ': ' + detail);
}

// Summary
const allOk = results.every(r => r[1]);
console.log('\n----------------------------------------------------------------');
console.log(allOk ? 'ALL 6 CORE CHECKS PASSED' : 'SOME CHECKS FAILED');
console.log('----------------------------------------------------------------\n');

// Exit code reflects actual result
process.exit(allOk ? 0 : 1);