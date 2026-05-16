export const GHATIS_PER_DAY = 60;
export const PALAS_PER_GHATI = 60;
export const MINUTES_PER_GHATI = 24;

export function minutesToGhatis(minutes) {
  return minutes / MINUTES_PER_GHATI;
}

export function ghatisToMinutes(ghatis) {
  return ghatis * MINUTES_PER_GHATI;
}

export function getCurrentGhatis(sunriseDate, now) {
  const msSinceSunrise = now.getTime() - sunriseDate.getTime();
  const minutesSinceSunrise = msSinceSunrise / 60000;
  const ghatis = minutesToGhatis(minutesSinceSunrise);
  return ((ghatis % GHATIS_PER_DAY) + GHATIS_PER_DAY) % GHATIS_PER_DAY;
}
