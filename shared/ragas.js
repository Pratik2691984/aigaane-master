// C:\aigaane-master\shared\ragas.js
// Rāga Definitions – 22 Śruti System

export const RAGA_MAP = {
    YAMAN: {
        id: "yaman",
        name: "Yaman",
        allowed_shrutis: [0, 4, 7, 10, 13, 17, 20, 21],
        // Śruti indices: Sa(0), Re(4), Ga(7), Ma#(10), Pa(13), Dha(17), Ni(20), Sa'(21)
        rasa: "Shānta / Bhakti",
        time: "Evening (6 PM – 9 PM)",
        description: "Kalyan thaat – serene, devotional"
    },
    BHAIRAVI: {
        id: "bhairavi",
        name: "Bhairavi",
        allowed_shrutis: [0, 1, 3, 5, 8, 9, 12, 14, 21],
        // Komal Re(1), Komal Ga(3), Tivra Ma(9), Komal Dha(12), Komal Ni(14)
        rasa: "Karuṇā / Bhakti",
        time: "Morning (6 AM – 9 AM)",
        description: "Asavari thaat – compassionate, longing"
    },
    BHAIRAV: {
        id: "bhairav",
        name: "Bhairav",
        allowed_shrutis: [0, 1, 4, 6, 9, 13, 14, 21],
        // Komal Re(1), Komal Dha(14)
        rasa: "Raudra / Shānta",
        time: "Sunrise (4 AM – 7 AM)",
        description: "Bhairav thaat – awakening, meditative"
    },
    PURE_SCALE: {
        id: "pure",
        name: "22 Śrutis",
        allowed_shrutis: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
        rasa: "Universal Resonance",
        time: "All",
        description: "Complete just intonation – no constraints"
    }
};

export const RAGA_KEYS = Object.keys(RAGA_MAP);