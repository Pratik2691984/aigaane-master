// js/katha_timing.js

const NAVAGRAHA_TIMING = {
    'Sunday':    { planet: 'Surya',   raga: 'Bhairav',  baseFreq: 432, color: '#f97316', deity: 'Shiva' },
    'Monday':    { planet: 'Chandra', raga: 'Bhairavi', baseFreq: 108, color: '#38bdf8', deity: 'Parvati' },
    'Tuesday':   { planet: 'Mangala', raga: 'Yaman',    baseFreq: 324, color: '#ef4444', deity: 'Kartikeya' },
    'Wednesday': { planet: 'Budha',   raga: 'Kalyani',  baseFreq: 216, color: '#22c55e', deity: 'Vishnu' },
    'Thursday':  { planet: 'Guru',    raga: 'Todi',     baseFreq: 720, color: '#eab308', deity: 'Brihaspati' },
    'Friday':    { planet: 'Shukra',  raga: 'Bageshri', baseFreq: 528, color: '#ec4899', deity: 'Lakshmi' },
    'Saturday':  { planet: 'Shani',   raga: 'Bhoopali', baseFreq: 64,  color: '#64748b', deity: 'Hanuman' }
};

function getCurrentRitualConfig() {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
    return NAVAGRAHA_TIMING[today] || NAVAGRAHA_TIMING['Sunday'];
}

function initKathaRitualUI() {
    const config = getCurrentRitualConfig();
    
    // Create the banner element
    const banner = document.createElement('div');
    banner.id = 'navagraha-banner';
    banner.style.cssText = `
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid ${config.color};
        padding: 12px 20px;
        margin-bottom: 20px;
        border-radius: 4px;
        font-family: monospace;
        color: #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    
    banner.innerHTML = `
        <div>
            <span style="font-size: 0.8rem; color: #64748b; text-transform: uppercase;">Active Planetary Operator</span><br>
            <strong style="color: ${config.color}; font-size: 1.2rem;">${config.planet} (${config.deity})</strong>
            <span style="color: #94a3b8;"> · Rāga: ${config.raga} · Base: ${config.baseFreq} Hz</span>
        </div>
        <div style="font-size: 0.8rem; color: #64748b;">
            Navagraha Timing Matrix
        </div>
    `;

    // Insert it at the top of the body (or inside a specific container if you prefer)
    document.body.insertBefore(banner, document.body.firstChild);
}

// The Fix: Wait for the DOM to be ready before inserting the banner
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKathaRitualUI);
} else {
    // DOM is already ready (handles deferred scripts)
    initKathaRitualUI();
}