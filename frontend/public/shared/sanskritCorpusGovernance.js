/**
 * Phase 10 / 11 Sanskrit corpus governance.
 * Read-only. Canonical mutation is hard-blocked.
 */

export const GOVERNANCE = Object.freeze({
  previewOnly: true,
  readOnly: true,
  canonicalWrite: false,
  promotionAllowed: false,
  importAllowed: false,
  capacity: 2000,
  windowSize: 250,
});

export const TARGETS = Object.freeze({
  dhatu: 1400,
  sutra: 400,
  stotra: 200,
  total: 2000,
});

/** Honest on-disk discovery. Not the metadata target. */
export const DISCOVERED = Object.freeze({
  dhatu: 37,
  sutra: 5,
  stotra: 3,
  total: 45,
});

export const DERIVATION_HOOKS = Object.freeze({
  sandhi: "/api/v3/sandhi",
  verbConjugate: "/api/v3/morphology/verb/conjugate",
  nounInflect: "/api/v3/morphology/noun/inflect",
  prakriya: "/api/v3/prakriya",
  chandas: "/api/v3/chandas",
});

export const PHASE10 = Object.freeze([
  "reservation",
  "allocation",
  "capacity",
  "window",
  "schedule",
  "timeline",
  "simulation",
  "forecast",
  "admission",
  "readiness",
  "advisory",
  "approval",
  "certification",
  "canonicalPreview",
]);

export const PHASE11 = Object.freeze([
  "11A_source_registry",
  "11B_raw_landing",
  "11C_normalize",
  "11D_validate",
  "11E_dedupe",
  "11F_enrich",
  "11G_certify",
  "11H_canonical_preview",
  "11I_index",
  "11L_derivation_hooks",
]);

export function assertWriteBlocked() {
  if (GOVERNANCE.canonicalWrite || GOVERNANCE.promotionAllowed || GOVERNANCE.importAllowed) {
    throw new Error("Sanskrit governance violation: write flags must stay false");
  }
  return { ok: true, write: "BLOCKED" };
}

export function inventoryStatus(discovered = DISCOVERED, targets = TARGETS) {
  const incomplete = discovered.total < targets.total;
  return {
    discovered,
    targets,
    incomplete,
    status: incomplete ? "INCOMPLETE" : "AT_TARGET",
    blockPromotion: incomplete || !GOVERNANCE.promotionAllowed,
    canonicalWrite: false,
  };
}

export function promotionReadiness(opts = {}) {
  const inv = inventoryStatus();
  const rejected = opts.rejectedCount ?? 0;
  const accepted = opts.acceptedCount ?? 0;
  const admissionReady = opts.admissionReady === true;
  const ready =
    admissionReady &&
    accepted > 0 &&
    rejected === 0 &&
    !inv.incomplete &&
    GOVERNANCE.canonicalWrite === false;
  return {
    ready: false,
    reason: inv.incomplete
      ? "inventory incomplete (45 < 2000)"
      : "canonical writes locked; readiness is advisory only",
    admissionReady,
    accepted,
    rejected,
    writeLocked: true,
    promotionAllowed: false,
    computedWouldBeReady: ready,
  };
}

assertWriteBlocked();
