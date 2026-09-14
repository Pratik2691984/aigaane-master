/** Phase 10 freeze. Never flip these flags in this commit. */
export const CORPUS_GOVERNANCE = Object.freeze({
  canonicalWrite: false,
  promotionAllowed: false,
  importAllowed: false,
  previewOnly: true,
  readOnly: true,
  activeCount: 45,
  activeInventory: 45,
  targetCount: 2000,
  targetCeiling: 2000,
  breakdown: Object.freeze({ dhatu: 37, sutra: 5, stotra: 3 }),
  windowSize: 250
});

export function assertWriteBlocked() {
  if (
    CORPUS_GOVERNANCE.canonicalWrite ||
    CORPUS_GOVERNANCE.promotionAllowed ||
    CORPUS_GOVERNANCE.importAllowed
  ) {
    throw new Error("Sanskrit governance violation: write flags must stay false");
  }
  return { ok: true, write: "BLOCKED", activeCount: CORPUS_GOVERNANCE.activeCount };
}

assertWriteBlocked();
