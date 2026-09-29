import { buildSequence } from './sequencer.mjs';

console.log('\n================================================================');
console.log('       SEQUENCER ENGINE COMPUTATIONAL VERIFICATION TABLE        ');
console.log('================================================================\n');

let exitCode = 0;
function assert(desc, condition) {
  const status = condition ? ' PASS ' : ' FAIL ';
  console.log('[' + status + '] ' + desc);
  if (!condition) exitCode = 1;
}

const seq1 = buildSequence('dharmaksetre kuruksetre', { thaat: 'yaman', rasa: 'shanta', bpm: 120 });
assert('16 timed events generated', seq1.events && seq1.events.length === 16);
assert('Step 0 starts at 0.0s', seq1.events[0].time === 0.0);
assert('Step 1 starts at 0.125s', seq1.events[1].time === 0.125);
assert('Step 4 starts at 0.5s', seq1.events[4].time === 0.5);

const step0 = seq1.events[0];
assert('Guru step selects stable tone index (0, 2, or 4)', [0, 2, 4].includes(step0.noteIndex));
assert('Rasa envelope attack mapped correctly', step0.adsr && step0.adsr.attack === 0.5);
assert('Rasa filterQ mapped correctly', step0.filterQ === 0.8);

const saEvent = seq1.events.find(e => e.noteIndex === 0);
assert('Sa note matches base frequency (136.10 Hz)', saEvent && Math.abs(saEvent.freqHz - 136.10) < 0.1);

const seq2 = buildSequence('dharmaksetre kuruksetre', { thaat: 'yaman', rasa: 'shanta', bpm: 120 });
assert('Sequence generation is 100% deterministic', JSON.stringify(seq1) === JSON.stringify(seq2));

console.log('\n----------------------------------------------------------------');
console.log('Sequencer Verification Status: ' + (exitCode === 0 ? 'ALL CHECKS PASSED' : 'FAILURES DETECTED'));
console.log('----------------------------------------------------------------\n');

process.exit(exitCode);
