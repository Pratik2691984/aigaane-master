/**
 * Deterministic Metric-Harmonic Sequencer Engine
 */

import { PingalEngine } from './pingal_engine.mjs';
import { getThaatCents } from './sruti_tables.mjs';
import { RASA_ENVELOPES } from './rasa_envelopes.mjs';

const STABLE_NOTE_INDICES = [0, 2, 4];
const PASSING_NOTE_INDICES = [1, 3, 5, 6];

export function buildSequence(verseText, options = {}) {
  const thaatKey = options.thaat || 'yaman';
  const rasaKey = options.rasa || 'shanta';
  const bpm = options.bpm || 108;
  const baseSaHz = options.baseSaHz || 136.10;
  const totalSteps = options.totalSteps || 16;

  const engine = new PingalEngine({
    strictPadaEnd: options.strictPadaEnd ?? false,
    collapseSemivowels: options.collapseSemivowels ?? false
  });

  const scanResult = engine.scan(verseText);
  const stepMatrix = engine.compileStepMatrix(scanResult, totalSteps);
  const thaatCents = getThaatCents(thaatKey);
  const env = RASA_ENVELOPES[rasaKey] || RASA_ENVELOPES.shanta;

  const stepDurationSec = (60.0 / bpm) / 4.0;

  let stableCounter = 0;
  let passingCounter = 0;

  const events = stepMatrix.map((stepItem, idx) => {
    const isGuru = stepItem.weight === 'G';

    let noteIdx;
    if (isGuru) {
      noteIdx = STABLE_NOTE_INDICES[stableCounter % STABLE_NOTE_INDICES.length];
      stableCounter++;
    } else {
      noteIdx = PASSING_NOTE_INDICES[passingCounter % PASSING_NOTE_INDICES.length];
      passingCounter++;
    }

    const centOffset = thaatCents[noteIdx % thaatCents.length];
    const freqHz = Number((baseSaHz * Math.pow(2, centOffset / 1200.0)).toFixed(2));
    const timeSec = Number((idx * stepDurationSec).toFixed(4));
    const durationSec = Number((stepDurationSec * (isGuru ? 2.0 : 1.0)).toFixed(4));

    return {
      step: idx,
      time: timeSec,
      duration: durationSec,
      syllable: stepItem.syllable,
      weight: stepItem.weight,
      noteIndex: noteIdx,
      freqCents: centOffset,
      freqHz: freqHz,
      velocity: stepItem.velocity,
      gate: stepItem.gate,
      rasa: rasaKey,
      adsr: {
        attack: env.attack,
        decay: env.decay,
        sustain: env.sustain,
        release: env.release
      },
      filterQ: env.filterQ,
      cutoffMod: env.cutoffMod
    };
  });

  return {
    meta: {
      verse: verseText,
      thaat: thaatKey,
      rasa: rasaKey,
      bpm: bpm,
      baseSaHz: baseSaHz,
      matchedChandas: scanResult.matchedChandas.name,
      totalMatras: scanResult.totalMatras,
      totalSteps: totalSteps
    },
    events: events
  };
}
