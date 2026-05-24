// C:\aigaane-master\ui\tabs\music\controller.js
// Music Tab – Sonic Mandala with Rāga Constraint Display

let mountNode = null;

function generateSectorPath(cx, cy, r, startAngle, endAngle) {
    const startRad = startAngle * Math.PI / 180;
    const endRad = endAngle * Math.PI / 180;
    const x1 = cx + r * Math.cos(startRad);
    const y1 = cy + r * Math.sin(startRad);
    const x2 = cx + r * Math.cos(endRad);
    const y2 = cy + r * Math.sin(endRad);
    const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;
    return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
}

function buildMandala() {
    const svg = mountNode?.querySelector('#sonic-mandala');
    if (!svg) return;
    
    const existingSegments = svg.querySelectorAll('.pada-segment');
    existingSegments.forEach(seg => seg.remove());
    
    const radius = 180;
    const center = 200;
    
    for (let i = 0; i < 108; i++) {
        const startAngle = i * (360 / 108);
        const endAngle = (i + 1) * (360 / 108);
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", generateSectorPath(center, center, radius, startAngle, endAngle));
        path.setAttribute("class", "pada-segment");
        path.setAttribute("data-pada", i);
        path.style.fill = "rgba(212, 175, 55, 0.05)";
        path.style.stroke = "rgba(255, 255, 255, 0.1)";
        path.style.strokeWidth = "0.8";
        path.style.transition = "fill 0.2s";
        svg.appendChild(path);
    }
    console.log('[Music] Mandala built with 108 segments');
}

function highlightPada(padaId) {
    const svg = mountNode?.querySelector('#sonic-mandala');
    if (!svg) return;
    
    const segments = svg.querySelectorAll('.pada-segment');
    segments.forEach((seg, idx) => {
        if (idx === padaId) {
            seg.style.fill = "var(--vedic-saffron)";
            seg.style.stroke = "var(--gold)";
        } else {
            seg.style.fill = "rgba(212, 175, 55, 0.05)";
            seg.style.stroke = "rgba(255, 255, 255, 0.1)";
        }
    });
}

function updateDisplay(padaId, shrutiRatio) {
    const root = mountNode || document;
    
    const padaDisplay = root.querySelector('#active-pada');
    const freqDisplay = root.querySelector('#active-freq');
    const ratioDisplay = root.querySelector('#ratio-display');
    
    const displayPada = (padaId !== undefined && padaId !== null) ? padaId + 1 : '---';
    
    if (padaDisplay) padaDisplay.innerText = displayPada;
    
    if (freqDisplay && shrutiRatio) {
        const freq = (240 * shrutiRatio).toFixed(1);
        freqDisplay.innerText = `${freq} Hz`;
    }
    
    if (ratioDisplay && shrutiRatio) {
        ratioDisplay.innerText = shrutiRatio.toFixed(4);
    }
}

function updateRagaDisplay() {
    const root = mountNode || document;
    const ragaState = window._ragaState;
    
    console.log('[Music] Updating Rāga display:', ragaState);
    
    const ragaNameEl = root.querySelector('#raga-name');
    const ragaRasaEl = root.querySelector('#raga-rasa');
    
    if (ragaState) {
        if (ragaNameEl) {
            ragaNameEl.innerText = ragaState.ragaName || '---';
            console.log('[Music] Set Rāga name to:', ragaState.ragaName);
        }
        if (ragaRasaEl) {
            ragaRasaEl.innerText = ragaState.ragaRasa || '---';
        }
    } else {
        if (ragaNameEl) ragaNameEl.innerText = '---';
        if (ragaRasaEl) ragaRasaEl.innerText = '---';
    }
}

function initRagaSelector() {
    const root = mountNode || document;
    const ragaSelect = root.querySelector('#raga-select');
    
    if (ragaSelect && window.setRaga) {
        // Clear existing listeners
        const newSelect = ragaSelect.cloneNode(true);
        ragaSelect.parentNode.replaceChild(newSelect, ragaSelect);
        
        newSelect.addEventListener('change', (e) => {
            console.log('[Music] Rāga changed to:', e.target.value);
            window.setRaga(e.target.value);
            // Update display after raga change
            setTimeout(() => updateRagaDisplay(), 50);
        });
        
        // Set initial value from current raga state
        if (window._ragaState && window._ragaState.currentRaga) {
            newSelect.value = window._ragaState.currentRaga;
        }
    }
}

export function init(node) {
    mountNode = node;
    buildMandala();
    initRagaSelector();
    console.log('[Music] Tab mounted');
}

export function render(state, node) {
    if (node) mountNode = node;
    if (!mountNode) return;
    if (!state) {
        console.error('[Music] State is undefined!');
        return;
    }
    
    const padaId = state.pada_id ?? 0;
    const shrutiRatio = state.shruti_ratio ?? 1;
    
    const svg = mountNode?.querySelector('#sonic-mandala');
    if (svg && svg.querySelectorAll('.pada-segment').length === 0) {
        buildMandala();
    }
    
    highlightPada(padaId);
    updateDisplay(padaId, shrutiRatio);
    updateRagaDisplay();
    initRagaSelector();
}

export function destroy() {
    mountNode = null;
    console.log('[Music] Tab destroyed');
}