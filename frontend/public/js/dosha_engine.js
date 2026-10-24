// js/dosha_engine.js

class DoshaHomeostasisEngine {
    constructor(vata, pitta, kapha) {
        this.q = { vata, pitta, kapha }; 
        this.p = { vata: 0, pitta: 0, kapha: 0 }; 
        
        // Stable time step
        this.dt = 0.02; 
    }

    _force(energy) {
        // THE FIX: Shift the equilibrium to 1.0
        // This means if energy == 1.0, force == 0 (perfect Prakriti balance)
        const equilibrium = 1.0;
        const displacement = energy - equilibrium;
        
        // Spring constant (alpha) and non-linear constraint (beta)
        const alpha = 0.5; 
        const beta = 0.1; 
        
        // Restoring force pulls back to 1.0
        return -(alpha * displacement - beta * Math.pow(displacement, 3));
    }

    step() {
        // Clamp momentum to prevent numerical explosion
        const clampMomentum = (p) => Math.max(-0.5, Math.min(0.5, p));

        // 1. Update Momentum by half step
        this.p.vata += this._force(this.q.vata) * (this.dt / 2);
        this.p.pitta += this._force(this.q.pitta) * (this.dt / 2);
        this.p.kapha += this._force(this.q.kapha) * (this.dt / 2);

        this.p.vata = clampMomentum(this.p.vata);
        this.p.pitta = clampMomentum(this.p.pitta);
        this.p.kapha = clampMomentum(this.p.kapha);

        // 2. Update Position by full step
        this.q.vata += this.p.vata * this.dt;
        this.q.pitta += this.p.pitta * this.dt;
        this.q.kapha += this.p.kapha * this.dt;

        // 3. Update Momentum by half step
        this.p.vata += this._force(this.q.vata) * (this.dt / 2);
        this.p.pitta += this._force(this.q.pitta) * (this.dt / 2);
        this.p.kapha += this._force(this.q.kapha) * (this.dt / 2);

        // Clamp position between 0.5 and 2.0 (healthy bounds)
        this.q.vata = Math.max(0.5, Math.min(2.0, this.q.vata));
        this.q.pitta = Math.max(0.5, Math.min(2.0, this.q.pitta));
        this.q.kapha = Math.max(0.5, Math.min(2.0, this.q.kapha));

        return this.q;
    }
}

// UI Injection Function
function injectAyurvedaEngine() {
    if (!window.location.pathname.includes('ayurveda')) return;
    const root = document.getElementById('root');
    if (!root) return;

    setTimeout(() => {
        if (document.getElementById('dosha-simulator-panel')) return;

        const container = document.createElement('div');
        container.id = 'dosha-simulator-panel';
        container.style.cssText = `
            background: #131820;
            border: 1px solid #2a3a4a;
            border-radius: 12px;
            padding: 24px;
            margin: 24px auto;
            max-width: 900px;
            font-family: monospace;
            color: #e2e8f0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        `;

        container.innerHTML = `
            <h2 style="color: #7a9a5a; margin-top:0;">Dynamic Dosha Homeostasis</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">Symplectic Störmer-Verlet simulation. Adding aggravating factors (spicy food, stress) pushes the system out of balance. The Prakriti restoring force pulls it back to equilibrium (1.00).</p>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;">
                <div style="background: #0f172a; padding: 12px; border-radius: 8px; border-left: 4px solid #38bdf8;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">VATA (Air/Ether)</div>
                    <div id="sim-vata" style="font-size: 1.5rem; font-weight: bold; color: #38bdf8;">1.00</div>
                </div>
                <div style="background: #0f172a; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">PITTA (Fire)</div>
                    <div id="sim-pitta" style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">1.00</div>
                </div>
                <div style="background: #0f172a; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">KAPHA (Earth/Water)</div>
                    <div id="sim-kapha" style="font-size: 1.5rem; font-weight: bold; color: #22c55e;">1.00</div>
                </div>
            </div>

            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button id="btn-vata" style="background: #38bdf8; color: #000; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">+ Aggravate Vata</button>
                <button id="btn-pitta" style="background: #ef4444; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">+ Aggravate Pitta</button>
                <button id="btn-kapha" style="background: #22c55e; color: #000; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">+ Aggravate Kapha</button>
                <button id="btn-reset" style="background: #475569; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">Reset to Prakriti</button>
            </div>
        `;

        root.insertBefore(container, root.firstChild);

        const engine = new DoshaHomeostasisEngine(1.0, 1.0, 1.0);
        const ui = {
            vata: document.getElementById('sim-vata'),
            pitta: document.getElementById('sim-pitta'),
            kapha: document.getElementById('sim-kapha')
        };

        document.getElementById('btn-vata').onclick = () => engine.q.vata += 0.3;
        document.getElementById('btn-pitta').onclick = () => engine.q.pitta += 0.3;
        document.getElementById('btn-kapha').onclick = () => engine.q.kapha += 0.3;
        
        document.getElementById('btn-reset').onclick = () => {
            engine.q = { vata: 1.0, pitta: 1.0, kapha: 1.0 };
            engine.p = { vata: 0, pitta: 0, kapha: 0 };
        };

        setInterval(() => {
            const state = engine.step();
            ui.vata.textContent = state.vata.toFixed(2);
            ui.pitta.textContent = state.pitta.toFixed(2);
            ui.kapha.textContent = state.kapha.toFixed(2);
        }, 50); 

    }, 1000);
}

document.addEventListener('DOMContentLoaded', injectAyurvedaEngine);