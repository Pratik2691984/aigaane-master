// C:\aigaane-master\ui\tabs\sanskrit\controller.js
// Sanskrit Tab – 49 Phoneme Grid (CORRECTED)

let mountNode = null;

// Complete 49 phonemes in correct Vedic order
const PHONEMES = [
    "अ","आ","इ","ई","उ","ऊ","ऋ","ॠ","लृ","ॡ","ए","ऐ","ओ","औ","अं","अः",
    "क","ख","ग","घ","ङ","च","छ","ज","झ","ञ","ट","ठ","ड","ढ","ण","त","थ","द","ध","न",
    "प","फ","ब","भ","म","य","र","ल","व","श","ष","स","ह"
];

// IAST Transliteration mapping (same order)
const TRANSLIT = [
    "a","ā","i","ī","u","ū","ṛ","ṝ","ḷ","ḹ","e","ai","o","au","aṃ","aḥ",
    "ka","kha","ga","gha","ṅa","ca","cha","ja","jha","ña","ṭa","ṭha","ḍa","ḍha","ṇa",
    "ta","tha","da","dha","na","pa","pha","ba","bha","ma","ya","ra","la","va","śa","ṣa","sa","ha"
];

// Varga grouping
const VARGA_MAP = [
    "Svara","Svara","Svara","Svara","Svara","Svara","Svara","Svara","Svara","Svara",
    "Svara","Svara","Svara","Svara","Svara","Svara",
    "Kaṇṭhya","Kaṇṭhya","Kaṇṭhya","Kaṇṭhya","Kaṇṭhya",
    "Tālavya","Tālavya","Tālavya","Tālavya","Tālavya",
    "Mūrdhanya","Mūrdhanya","Mūrdhanya","Mūrdhanya","Mūrdhanya",
    "Dantya","Dantya","Dantya","Dantya","Dantya",
    "Oṣṭhya","Oṣṭhya","Oṣṭhya","Oṣṭhya","Oṣṭhya",
    "Antastha","Antastha","Antastha","Antastha",
    "Uṣma","Uṣma","Uṣma","Uṣma"
];

function buildGrid() {
    const grid = mountNode?.querySelector('#matrikaGrid');
    if (!grid) return;
    
    if (grid.children.length === 0) {
        PHONEMES.forEach((char, idx) => {
            const div = document.createElement('div');
            div.className = 'akshara-node';
            div.textContent = char;
            div.dataset.phonemeId = idx;
            div.title = TRANSLIT[idx];
            grid.appendChild(div);
        });
    }
}

function highlightPhoneme(phonemeId) {
    const grid = mountNode?.querySelector('#matrikaGrid');
    if (!grid) return;
    
    // Clamp phonemeId to valid range
    const validId = Math.min(Math.max(0, phonemeId), 48);
    
    Array.from(grid.children).forEach((node, idx) => {
        node.classList.toggle('active', idx === validId);
    });
    
    const bigAkshara = mountNode?.querySelector('#bigAkshara');
    const translitValue = mountNode?.querySelector('#translitValue');
    const vargaValue = mountNode?.querySelector('#vargaValue');
    const phonemeIdValue = mountNode?.querySelector('#phonemeIdValue');
    const activeVargaName = mountNode?.querySelector('#active-varga-name');
    
    if (bigAkshara) bigAkshara.innerText = PHONEMES[validId];
    if (translitValue) translitValue.innerText = TRANSLIT[validId];
    if (vargaValue) vargaValue.innerText = VARGA_MAP[validId];
    if (phonemeIdValue) phonemeIdValue.innerText = validId;
    if (activeVargaName) activeVargaName.innerText = `${VARGA_MAP[validId]} Focus`;
}

export function init(node) {
    mountNode = node;
    buildGrid();
    console.log('[Sanskrit] Tab mounted');
}

export function render(state, node) {
    if (node) mountNode = node;
    if (!mountNode) return;
    
    // Get phoneme_id from canonical state
    const phonemeId = state?.phoneme_id ?? 0;
    highlightPhoneme(phonemeId);
}

export function destroy() {
    mountNode = null;
    console.log('[Sanskrit] Tab destroyed');
}