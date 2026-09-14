import { AigaaneMasterEngine, computeAnumana, l2 } from "../lib/engine_master.js";
import { CORPUS_GOVERNANCE } from "../lib/governance/corpus_gate.js";
import { resolveCoordinates, padaRange } from "../lib/core/sanskrit_resolver.js";
import { build49DState } from "../lib/core/state_49d.js";

let failed = 0;
function assert(cond, msg) {
  if (!cond) { console.error("FAIL", msg); failed++; }
  else console.log("OK  ", msg);
}

const gold = build49DState(210, 63, 15);
const engine = new AigaaneMasterEngine();
const frame = engine.resolve(210);

assert(frame.coordinates.pada_id === 63, "210 pada_id === 63");
assert(frame.coordinates.nakshatra_id === 15, "210 nakshatra_id === 15");
assert(Math.abs(frame.coordinates.shruti_ratio - 1.5) < 1e-12, "sruti === 1.5");
assert(frame.phase_lock === "LOCKED", "phase_lock LOCKED");
assert(frame.sattva > 0.8, "Sattva > 0.80");
assert(l2(frame.vector49, gold) < 1e-6, "L2 < 1e-6");

const seen = new Set();
for (let p = 0; p < 108; p++) {
  const range = padaRange(p);
  const c = resolveCoordinates((range.start + range.end) / 2);
  assert(c.pada_id === p, "slot " + p);
  if (p > 0) {
    assert(Math.abs(padaRange(p - 1).end - range.start) < 1e-12, "no gap " + p);
  }
  seen.add(c.pada_id);
}
assert(seen.size === 108, "108 padas");
assert(resolveCoordinates(0).pada_id === 0, "0 -> 0");
assert(resolveCoordinates(359.999).pada_id === 107, "359.999 -> 107");

const S = build49DState(45, 13, 3);
const a1 = computeAnumana({ S: S, theta: 45, pada_id: 13, nakshatra_id: 3, t: 7 });
const a2 = computeAnumana({ S: S, theta: 45, pada_id: 13, nakshatra_id: 3, t: 7 });
let same = true;
for (let i = 0; i < 49; i++) if (a1.A_next[i] !== a2.A_next[i]) same = false;
assert(same, "deterministic Anumana");

assert(CORPUS_GOVERNANCE.canonicalWrite === false, "write false");
assert(CORPUS_GOVERNANCE.activeCount === 45, "inventory 45");
assert(frame.governance.canonicalWrite === false, "frame write false");

if (failed) process.exit(1);
console.log("Phase 10 freeze: all assertions passed.");
