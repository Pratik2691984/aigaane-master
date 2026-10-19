/**
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
