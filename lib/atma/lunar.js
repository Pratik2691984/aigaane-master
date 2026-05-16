export function getTithi(date) {
  const lunarCycle = 29.53;
  const epoch = new Date("2025-01-01T00:00:00");
  const days = (date.getTime() - epoch.getTime()) / (1000 * 3600 * 24);
  const phase = ((days % lunarCycle) + lunarCycle) % lunarCycle / lunarCycle;
  return Math.floor(phase * 30) + 1;
}

export function lunarMultiplier(tithi) {
  if (tithi === 15 || tithi === 30) return 1.5;
  if (tithi === 8 || tithi === 23) return 1.2;
  return 1.0;
}
