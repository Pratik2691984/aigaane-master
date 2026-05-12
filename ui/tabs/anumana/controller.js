let mountNode = null;

const NAKSHATRA_LIST = [
    "Ashvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā",
    "Maghā", "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Chitrā", "Svāti", "Viśākhā", "Anurādhā", "Jyeṣṭhā",
    "Mūla", "Pūrva Aṣāḍhā", "Uttara Aṣāḍhā", "Śravaṇā", "Dhanisṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
];

function updateDisplay(padaId, nakshatraId, padaProgress = 0) {
    const displayPada = padaId + 1;  // ✅ Convert to 1-based
    const nextPada = ((padaId + 1) % 108);
    const displayNextPada = nextPada + 1;  // ✅ Convert next to 1-based
    
    const currentPadaEl = mountNode?.querySelector('#currentPada');
    const nextPadaEl = mountNode?.querySelector('#nextPada');
    
    if (currentPadaEl) currentPadaEl.innerText = displayPada;
    if (nextPadaEl) nextPadaEl.innerText = displayNextPada;
    // ... rest unchanged
}
    if (currentNakshatraEl) currentNakshatraEl.innerText = NAKSHATRA_LIST[nakshatraId];
    
    // Calculate next pāda
    const nextPada = (padaId + 1) % 108;
    const nextNakshatraId = Math.floor(nextPada / 4);
    
    // ✅ FIXED: Use pada_progress from state (0 to 1)
    const progress = Math.min(Math.max(0, padaProgress), 1);
    
    const nextPadaEl = mountNode?.querySelector('#nextPada');
    const nextNakshatraEl = mountNode?.querySelector('#nextNakshatra');
    const timeToTransitionEl = mountNode?.querySelector('#timeToTransition');
    
    if (nextPadaEl) nextPadaEl.innerText = nextPada;
    if (nextNakshatraEl) nextNakshatraEl.innerText = NAKSHATRA_LIST[nextNakshatraId];
    
    // ✅ FIXED: Update timeline progress
    const timelineProgress = mountNode?.querySelector('#timelineProgress');
    if (timelineProgress) timelineProgress.style.width = `${progress * 100}%`;
    
    if (timeToTransitionEl) {
        const remainingPercent = ((1 - progress) * 100).toFixed(1);
        timeToTransitionEl.innerText = `${remainingPercent}% of pāda`;
    }

function buildTimeline() {
    const bar = mountNode?.querySelector('#timelineBar');
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
    if (!mountNode) return;
    
    // ✅ Ensure timeline is built
    if (!mountNode?.querySelector('#timelineProgress')) {
        buildTimeline();
    }
    
    const padaId = state?.pada_id ?? 0;
    const nakshatraId = state?.nakshatra_id ?? 0;
    const padaProgress = state?.pada_progress ?? 0;
    
    updateDisplay(padaId, nakshatraId, padaProgress);
}

export function destroy() {
    mountNode = null;
    console.log('[Anumana] Tab destroyed');
}