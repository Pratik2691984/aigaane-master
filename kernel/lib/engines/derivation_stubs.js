import { CORPUS_GOVERNANCE } from "../governance/corpus_gate.js";

const FLAGS = Object.freeze({
  status: "mock_fallback",
  httpHint: 501,
  kernelMounted: false,
  canonicalWrite: CORPUS_GOVERNANCE.canonicalWrite,
  promotionAllowed: CORPUS_GOVERNANCE.promotionAllowed,
  importAllowed: CORPUS_GOVERNANCE.importAllowed,
  previewOnly: true,
  readOnly: true
});

function envelope(engine, record) {
  return Object.assign({}, FLAGS, { engine: engine, record: record });
}

export function sandhi(record) { return envelope("sandhi", record); }
export function verbConjugate(record) { return envelope("verb_conjugate", record); }
export function nounInflect(record) { return envelope("noun_inflect", record); }
export function prakriya(record) { return envelope("prakriya", record); }
export function chandas(record) { return envelope("chandas", record); }
