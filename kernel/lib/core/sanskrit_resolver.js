/** Pure coordinate map: theta -> pada / naksatra / matrika / sruti / rasa. */

export const SHRUTI_RATIOS = Object.freeze([
  1,
  256 / 243,
  16 / 15,
  10 / 9,
  9 / 8,
  32 / 27,
  6 / 5,
  5 / 4,
  81 / 64,
  4 / 3,
  27 / 20,
  45 / 32,
  729 / 512,
  3 / 2,
  128 / 81,
  8 / 5,
  5 / 3,
  27 / 16,
  16 / 9,
  9 / 5,
  15 / 8,
  243 / 128
]);

export const NAKSHATRA_NAMES = Object.freeze([
  "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
  "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
  "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
  "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
  "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
  "Uttara Bhadrapada", "Revati"
]);

export const VISHAKHA = Object.freeze({
  angle: 210,
  toleranceDeg: 0.1,
  pada_id: 63,
  nakshatra_id: 15,
  shruti_ratio: 1.5,
  phase_lock: "LOCKED"
});

export function wrapAngle(theta) {
  return ((Number(theta) % 360) + 360) % 360;
}

export function resolveCoordinates(theta) {
  const angle = wrapAngle(theta);
  const pada_id = Math.floor((108 * angle) / 360);
  const nakshatra_id = Math.floor(pada_id / 4);
  const phoneme_id = Math.floor((49 * pada_id) / 108);
  const shruti_id = Math.floor((22 * pada_id) / 108);
  const rasa_id = pada_id % 9;
  const isVishakha210 = Math.abs(angle - VISHAKHA.angle) < VISHAKHA.toleranceDeg;
  const shruti_ratio = isVishakha210 ? VISHAKHA.shruti_ratio : SHRUTI_RATIOS[shruti_id];
  return Object.freeze({
    angle,
    pada_id,
    nakshatra_id,
    nakshatra: NAKSHATRA_NAMES[nakshatra_id],
    phoneme_id,
    shruti_id,
    rasa_id,
    shruti_ratio,
    phase_lock: isVishakha210 ? VISHAKHA.phase_lock : "UNLOCKED",
    isVishakha210
  });
}

export function padaRange(pada_id) {
  const start = (pada_id * 360) / 108;
  const end = ((pada_id + 1) * 360) / 108;
  return { start, end, mid: (start + end) / 2 };
}
