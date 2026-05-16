import { GHATIS_PER_DAY } from "./chronos.js";

export function getDoshaAtGhati(ghati, sunriseGhati = 0) {
  const t = (ghati - sunriseGhati + GHATIS_PER_DAY) % GHATIS_PER_DAY;
  if (t < 6) return "kapha";
  if (t < 14) return "pitta";
  if (t < 24) return "vata";
  if (t < 36) return "kapha";
  if (t < 48) return "pitta";
  return "vata";
}

export function getDoshaWindows(sunriseGhati = 0) {
  return {
    kapha: { start: sunriseGhati, end: sunriseGhati + 6 },
    pitta: { start: sunriseGhati + 6, end: sunriseGhati + 14 },
    vata: { start: sunriseGhati + 14, end: sunriseGhati + 24 }
  };
}
