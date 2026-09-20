export const SHIKSHA_PHONEME_MAP = {
  "अ": { type: "vowel", length: "short", articulation: "kantha", group: "svara" },
  "आ": { type: "vowel", length: "long", articulation: "kantha", group: "svara" },
  "इ": { type: "vowel", length: "short", articulation: "talu", group: "svara" },
  "ई": { type: "vowel", length: "long", articulation: "talu", group: "svara" },
  "उ": { type: "vowel", length: "short", articulation: "oshtha", group: "svara" },
  "ऊ": { type: "vowel", length: "long", articulation: "oshtha", group: "svara" },
  "ऋ": { type: "vowel", length: "short", articulation: "murdha", group: "svara" },
  "ॠ": { type: "vowel", length: "long", articulation: "murdha", group: "svara" },
  "ए": { type: "vowel", length: "long", articulation: "kantha-talu", group: "svara" },
  "ऐ": { type: "vowel", length: "long", articulation: "kantha-talu", group: "svara" },
  "ओ": { type: "vowel", length: "long", articulation: "kantha-oshtha", group: "svara" },
  "औ": { type: "vowel", length: "long", articulation: "kantha-oshtha", group: "svara" },

  "क": { type: "consonant", articulation: "kantha", group: "sparsha", voicing: "unvoiced", aspiration: "unaspirated" },
  "ख": { type: "consonant", articulation: "kantha", group: "sparsha", voicing: "unvoiced", aspiration: "aspirated" },
  "ग": { type: "consonant", articulation: "kantha", group: "sparsha", voicing: "voiced", aspiration: "unaspirated" },
  "घ": { type: "consonant", articulation: "kantha", group: "sparsha", voicing: "voiced", aspiration: "aspirated" },
  "ङ": { type: "consonant", articulation: "kantha", group: "nasal", voicing: "voiced", aspiration: "unaspirated" },

  "च": { type: "consonant", articulation: "talu", group: "sparsha", voicing: "unvoiced", aspiration: "unaspirated" },
  "छ": { type: "consonant", articulation: "talu", group: "sparsha", voicing: "unvoiced", aspiration: "aspirated" },
  "ज": { type: "consonant", articulation: "talu", group: "sparsha", voicing: "voiced", aspiration: "unaspirated" },
  "झ": { type: "consonant", articulation: "talu", group: "sparsha", voicing: "voiced", aspiration: "aspirated" },
  "ञ": { type: "consonant", articulation: "talu", group: "nasal", voicing: "voiced", aspiration: "unaspirated" },

  "ट": { type: "consonant", articulation: "murdha", group: "sparsha", voicing: "unvoiced", aspiration: "unaspirated" },
  "ठ": { type: "consonant", articulation: "murdha", group: "sparsha", voicing: "unvoiced", aspiration: "aspirated" },
  "ड": { type: "consonant", articulation: "murdha", group: "sparsha", voicing: "voiced", aspiration: "unaspirated" },
  "ढ": { type: "consonant", articulation: "murdha", group: "sparsha", voicing: "voiced", aspiration: "aspirated" },
  "ण": { type: "consonant", articulation: "murdha", group: "nasal", voicing: "voiced", aspiration: "unaspirated" },

  "त": { type: "consonant", articulation: "danta", group: "sparsha", voicing: "unvoiced", aspiration: "unaspirated" },
  "थ": { type: "consonant", articulation: "danta", group: "sparsha", voicing: "unvoiced", aspiration: "aspirated" },
  "द": { type: "consonant", articulation: "danta", group: "sparsha", voicing: "voiced", aspiration: "unaspirated" },
  "ध": { type: "consonant", articulation: "danta", group: "sparsha", voicing: "voiced", aspiration: "aspirated" },
  "न": { type: "consonant", articulation: "danta", group: "nasal", voicing: "voiced", aspiration: "unaspirated" },

  "प": { type: "consonant", articulation: "oshtha", group: "sparsha", voicing: "unvoiced", aspiration: "unaspirated" },
  "फ": { type: "consonant", articulation: "oshtha", group: "sparsha", voicing: "unvoiced", aspiration: "aspirated" },
  "ब": { type: "consonant", articulation: "oshtha", group: "sparsha", voicing: "voiced", aspiration: "unaspirated" },
  "भ": { type: "consonant", articulation: "oshtha", group: "sparsha", voicing: "voiced", aspiration: "aspirated" },
  "म": { type: "consonant", articulation: "oshtha", group: "nasal", voicing: "voiced", aspiration: "unaspirated" },

  "य": { type: "consonant", articulation: "talu", group: "antastha", voicing: "voiced" },
  "र": { type: "consonant", articulation: "murdha", group: "antastha", voicing: "voiced" },
  "ल": { type: "consonant", articulation: "danta", group: "antastha", voicing: "voiced" },
  "व": { type: "consonant", articulation: "oshtha", group: "antastha", voicing: "voiced" },

  "श": { type: "consonant", articulation: "talu", group: "ushman", voicing: "unvoiced" },
  "ष": { type: "consonant", articulation: "murdha", group: "ushman", voicing: "unvoiced" },
  "स": { type: "consonant", articulation: "danta", group: "ushman", voicing: "unvoiced" },
  "ह": { type: "consonant", articulation: "kantha", group: "ushman", voicing: "voiced" },

  "ं": { type: "modifier", group: "anusvara", articulation: "nasika" },
  "ः": { type: "modifier", group: "visarga", articulation: "kantha" },
  "ँ": { type: "modifier", group: "candrabindu", articulation: "nasika" }
};