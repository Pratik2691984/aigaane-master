// C:\aigaane-master\shared\invariant.js
// Runtime State Integrity Guard

export function validateState(state) {
  const checks = [
    state.pada_id >= 0 && state.pada_id < 108,
    state.nakshatra_id >= 0 && state.nakshatra_id < 27,
    state.phoneme_id >= 0 && state.phoneme_id < 49,
    state.shruti_id >= 0 && state.shruti_id < 22,
    state.rasa_id >= 0 && state.rasa_id < 9,
    Number.isFinite(state.shruti_ratio),
    state.shruti_ratio > 0 && state.shruti_ratio <= 2
  ];

  if (checks.includes(false)) {
    console.error("Invariant violation:", state);
    throw new Error("Invariant violation: Invalid Canonical State");
  }

  return true;
}

// Deep freeze utility
export function deepFreeze(obj) {
  Object.freeze(obj);
  Object.getOwnPropertyNames(obj).forEach(prop => {
    const val = obj[prop];
    if (val && typeof val === "object" && !Object.isFrozen(val)) {
      deepFreeze(val);
    }
  });
  return obj;
}