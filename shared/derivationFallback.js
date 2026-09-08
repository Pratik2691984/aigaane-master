/** Client-side deterministic mock if /api/v3 is 501 or unreachable. */

export const DERIVATION_PATHS = {
  sandhi: "/api/v3/sandhi",
  verbConjugate: "/api/v3/morphology/verb/conjugate",
  nounInflect: "/api/v3/morphology/noun/inflect",
  prakriya: "/api/v3/prakriya",
  chandas: "/api/v3/chandas",
};

export function localFallback(engine, record) {
  return {
    status: "mock_fallback",
    source: "client_memory",
    engine,
    kernelMounted: false,
    canonicalWrite: false,
    promotionAllowed: false,
    importAllowed: false,
    previewOnly: true,
    readOnly: true,
    recordId: record?.id ?? null,
    note: "Local fallback — network unavailable or 501. Write flags unchanged.",
  };
}

export async function callDerivation(engine, record) {
  const path = DERIVATION_PATHS[engine];
  const params = new URLSearchParams();
  if (record?.id) params.set("id", record.id);
  if (record?.root) params.set("root", record.root);
  if (record?.text) params.set("text", record.text);
  const url = `${path}?${params.toString()}`;
  try {
    const res = await fetch(url, { method: "GET", cache: "no-store" });
    if (!res.ok) return { httpStatus: res.status, ...localFallback(engine, record) };
    const body = await res.json();
    return { httpStatus: res.status, ...body, canonicalWrite: false, readOnly: true };
  } catch (err) {
    return { httpStatus: 0, error: String(err), ...localFallback(engine, record) };
  }
}
