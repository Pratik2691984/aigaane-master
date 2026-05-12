// Resonance Tab Controller

let mountNode = null;

const RASAS = [
    { id: 0, name: "Śṛṅgāra", quality: "Love, beauty, romance", color: "#E91E63" },
    { id: 1, name: "Hāsya", quality: "Laughter, joy, comedy", color: "#FFEB3B" },
    { id: 2, name: "Karuṇa", quality: "Compassion, sadness", color: "#9C27B0" },
    { id: 3, name: "Raudra", quality: "Anger, fury", color: "#F44336" },
    { id: 4, name: "Vīra", quality: "Heroism, courage", color: "#FF9800" },
    { id: 5, name: "Bhayānaka", quality: "Fear, terror", color: "#3F51B5" },
    { id: 6, name: "Bībhatsa", quality: "Disgust, aversion", color: "#4CAF50" },
    { id: 7, name: "Adbhuta", quality: "Wonder, surprise", color: "#00BCD4" },
    { id: 8, name: "Śānta", quality: "Peace, tranquility", color: "#2196F3" }
];

function buildRasaWheel() {
    const wheel = mountNode?.querySelector('#rasaWheel');
    if (!wheel) return;
    
    if (wheel.children.length === 0) {
        RASAS.forEach((rasa, idx) => {
            const div = document.createElement('div');
            div.className = 'rasa-segment';
            div.textContent = rasa.name;
            div.style.background = rasa.color;
            div.style.opacity = '0.3';
            div.dataset.rasaId = idx;
            div.onclick = () => highlightRasa(idx);
            wheel.appendChild(div);
        });
    }
}

function highlightRasa(rasaId) {
    const wheel = mountNode?.querySelector('#rasaWheel');
    if (!wheel) return;
    
    const validId = Math.min(Math.max(0, rasaId), 8);
    const rasa = RASAS[validId] || RASAS[0];
    
    Array.from(wheel.children).forEach((child, idx) => {
        child.classList.toggle('active', idx === validId);
        child.style.opacity = idx === validId ? '1' : '0.3';
    });
    
    const currentRasaEl = mountNode?.querySelector('#currentRasa');
    const rasaIdEl = mountNode?.querySelector('#rasaId');
    const rasaQualityEl = mountNode?.querySelector('#rasaQuality');
    const rasaColorEl = mountNode?.querySelector('#rasaColor');
    
    if (currentRasaEl) currentRasaEl.innerText = rasa.name;
    if (rasaIdEl) rasaIdEl.innerText = validId;
    if (rasaQualityEl) rasaQualityEl.innerText = rasa.quality;
    if (rasaColorEl) rasaColorEl.style.background = rasa.color;
}

function updatePada(padaId) {
    const padaEl = mountNode?.querySelector('#associatedPada');
    if (padaEl) padaEl.innerText = padaId + 1;
}

export function init(node) {
    mountNode = node;
    buildRasaWheel();
    console.log('[Resonance] Tab mounted');
}

export function render(state, node) {
    if (node) mountNode = node;
    if (!mountNode) return;
    if (!state) {
        console.error('[Resonance] State is undefined!');
        return;
    }
    
    const rasaId = state.rasa_id ?? 0;
    const padaId = state.pada_id ?? 0;
    
    highlightRasa(rasaId);
    updatePada(padaId);
}

export function destroy() {
    mountNode = null;
    console.log('[Resonance] Tab destroyed');
}