// Anumana Tab Controller

let mountNode = null;

const NAKSHATRA_LIST = [
    "Ashvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā",
    "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Chitrā", "Svāti", "Viśākhā", "Anurādhā", "Jyeṣṭhā",
    "Mūla", "Pūrva Aṣāḍhā", "Uttara Aṣāḍhā", "Śravaṇā", "Dhanisṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
];

function updateDisplay(padaId, nakshatraId, padaProgress = 0) {
    const root = mountNode || document;
    
    const displayPada = (padaId !== undefined && padaId !== null) ? padaId + 1 : '---';
    const displayNakshatra = (nakshatraId !== undefined && NAKSHATRA_LIST[nakshatraId]) ? NAKSHATRA_LIST[nakshatraId] : '---';
    
    const currentPadaEl = root.querySelector('#currentPada');
    const currentNakshatraEl = root.querySelector('#currentNakshatra');
    
    if (currentPadaEl) currentPadaEl.innerText = displayPada;
    if (currentNakshatraEl) currentNakshatraEl.innerText = displayNakshatra;
    
    if (padaId !== undefined && padaId !== null) {
        const nextPada = (padaId + 1) % 108;
        const nextNakshatraId = Math.floor(nextPada / 4);
        const displayNextPada = nextPada + 1;
        const displayNextNakshatra = NAKSHATRA_LIST[nextNakshatraId];
        
        const nextPadaEl = root.querySelector('#nextPada');
        const nextNakshatraEl = root.querySelector('#nextNakshatra');
        const timeToTransitionEl = root.querySelector('#timeToTransition');
        
        if (nextPadaEl) nextPadaEl.innerText = displayNextPada;
        if (nextNakshatraEl) nextNakshatraEl.innerText = displayNextNakshatra;
        
        const progress = Math.min(Math.max(0, padaProgress), 1);
        const remainingPercent = ((1 - progress) * 100).toFixed(1);
        if (timeToTransitionEl) timeToTransitionEl.innerText = `${remainingPercent}% of pāda`;
        
        const timelineProgress = root.querySelector('#timelineProgress');
        if (timelineProgress) timelineProgress.style.width = `${progress * 100}%`;
    }
}

function buildTimeline() {
    const root = mountNode || document;
    const bar = root.querySelector('#timelineBar');
    if (!bar) return;
    
    if (bar.children.length === 0) {
        const progress = document.createElement('div');
        progress.className = 'timeline-progress';
        progress.id = 'timelineProgress';
        bar.appendChild(progress);
    }
}

export function init(node) {
    mountNode = node;
    buildTimeline();
    console.log('[Anumana] Tab mounted');
}

export function render(state, node) {
    if (node) mountNode = node;
    if (!mountNode) {
        console.warn('[Anumana] No mount node, skipping render');
        return;
    }
    if (!state) {
        console.error('[Anumana] State is undefined!');
        return;
    }
    
    if (!mountNode?.querySelector('#timelineProgress')) {
        buildTimeline();
    }
    
    const padaId = state.pada_id ?? 0;
    const nakshatraId = state.nakshatra_id ?? 0;
    const padaProgress = state.pada_progress ?? 0;
    
    updateDisplay(padaId, nakshatraId, padaProgress);
}

export function destroy() {
    mountNode = null;
    console.log('[Anumana] Tab destroyed');
}