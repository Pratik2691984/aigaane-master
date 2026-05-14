// nakshatra-engine.js

const AXES = 7;
const LAYERS = 7;

const NAKSHATRA_NAMES = [
  "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
  "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
  "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
  "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
  "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
  "Uttara Bhadrapada","Revati"
];

export function getNakshatraProfile(index, pada) {
  const name = NAKSHATRA_NAMES[index];

  const S_base = generate49D(index, pada);

  return {
    name,
    index,
    pada,
    S_base
  };
}

// Pattern-based deterministic 49D generator
function generate49D(nakshatraIndex, pada) {
  const vector = [];

  for (let l = 0; l < LAYERS; l++) {
    for (let a = 0; a < AXES; a++) {
      let value =
        Math.sin((nakshatraIndex + 1) * (a + 1) * 0.3) *
        Math.cos((pada + l + 1) * 0.5);

      // Normalize to 0–1
      value = (value + 1) / 2;

      // Quantize (0, 0.2, 0.6, 1)
      if (value > 0.75) value = 1.0;
      else if (value > 0.5) value = 0.6;
      else if (value > 0.25) value = 0.2;
      else value = 0.0;

      vector.push(value);
    }
  }

  return vector;
}