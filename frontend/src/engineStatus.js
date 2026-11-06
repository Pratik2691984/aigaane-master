export async function probeEngine() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch("http://localhost:8000/api/v3/quanta/health", {
      signal: controller.signal,
    });
    if (!res.ok) return { status: "degraded" };
    return { status: "ok", data: await res.json() };
  } catch (err) {
    return { status: "unreachable" };
  } finally {
    clearTimeout(timer);
  }
}