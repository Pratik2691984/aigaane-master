import { CORPUS_GOVERNANCE } from "./governance/corpus_gate.js";
import { resolveCoordinates } from "./core/sanskrit_resolver.js";
import { build49DState, l2, vectorToBlocks, gunaSattva } from "./core/state_49d.js";
import { computeAnumana } from "./engines/anumana.js";
import { calculateFriction } from "./engines/friction.js";
import { evaluateCollapse } from "./engines/collapse.js";

export class AigaaneMasterEngine {
  constructor() {
    this.governance = CORPUS_GOVERNANCE;
    this.historyRing = [];
  }

  resolve(theta) {
    const coordinates = resolveCoordinates(theta);
    const vector49 = build49DState(coordinates.angle, coordinates.pada_id, coordinates.nakshatra_id);
    const prev = this.historyRing.length ? this.historyRing[this.historyRing.length - 1] : null;

    const anumana = computeAnumana({
      S: vector49,
      theta: coordinates.angle,
      A_prev: prev && prev.anumana ? prev.anumana.A_next : null,
      pada_id: coordinates.pada_id,
      nakshatra_id: coordinates.nakshatra_id,
      t: this.historyRing.length
    });

    const collapse = evaluateCollapse(vector49, prev ? prev.vector49 : null);

    const frame = {
      angle: coordinates.angle,
      coordinates,
      phase_lock: coordinates.phase_lock,
      vector49,
      blocks: vectorToBlocks(vector49),
      sattva: gunaSattva(vector49),
      anumana: {
        coherence: anumana.coherence,
        intensity: anumana.intensity,
        phi: anumana.phi,
        A_next: anumana.A_next
      },
      collapse,
      governance: {
        readOnly: this.governance.readOnly,
        canonicalWrite: this.governance.canonicalWrite,
        corpusRecords: this.governance.activeCount
      },
      timestamp: 0
    };

    if (this.historyRing.length >= 108) this.historyRing.shift();
    this.historyRing.push(frame);
    return frame;
  }

  friction(opts) {
    return calculateFriction(opts);
  }

  distanceTo(frame, reference) {
    return l2(frame.vector49, reference);
  }
}

export { CORPUS_GOVERNANCE, l2, calculateFriction, computeAnumana, evaluateCollapse };
