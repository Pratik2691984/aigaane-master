// js/jyotirlinga_agent.js

const JYOTIRLINGAS = [
    { id: 'somnath', name: 'Somnath', freq: 108, q: 12400, desc: 'Cryogenic Ocean / Weather' },
    { id: 'mallikarjuna', name: 'Mallikarjuna', freq: 216, q: 11000, desc: 'Symmetrical Dual-Rail' },
    { id: 'mahakaleshwar', name: 'Mahakaleshwar', freq: 432, q: 9800, desc: 'Entropy Inversion / Time' },
    { id: 'omkareshwar', name: 'Omkareshwar', freq: 528, q: 13000, desc: 'Topological Qubit Waveguide' },
    { id: 'kedarnath', name: 'Kedarnath', freq: 64, q: 15000, desc: 'Absolute-Zero Cold Storage' },
    { id: 'bhimashankar', name: 'Bhimashankar', freq: 720, q: 9000, desc: 'High-Voltage Kinetic' },
    { id: 'kashi', name: 'Kashi Vishwanath', freq: 1080, q: 16000, desc: 'Central Optical Photon Router' },
    { id: 'trimbakeshwar', name: 'Trimbakeshwar', freq: 324, q: 12000, desc: 'Tri-Core Qutrit Matrix' },
    { id: 'baidyanath', name: 'Baidyanath', freq: 432, q: 10500, desc: 'Algorithmic Self-Healer' },
    { id: 'nageshwar', name: 'Nageshwar', freq: 864, q: 11500, desc: 'Serpent Shielding Array' },
    { id: 'ramanathaswamy', name: 'Ramanathaswamy', freq: 144, q: 10000, desc: 'High-Density Sand Matrix' },
    { id: 'grishneshwar', name: 'Grishneshwar', freq: 288, q: 12500, desc: 'Surface-Acoustic Thermal' }
];

class JyotirlingaSoundAgent {
    constructor() { this.ctx = null; this.masterGain = null; this.activeSources = []; this.analyser = null; }
    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.value = 0.3;
            this.analyser = this.ctx.createAnalyser();
            this.analyser.fftSize = 256;
            this.masterGain.connect(this.analyser);
            this.analyser.connect(this.ctx.destination);
        }
        if (this.ctx.state === 'suspended') this.ctx.resume();
    }

    exciteNode(node) {
        this.init();
        this.stop();
        const t = this.ctx.currentTime;

        // Fundamental (Sattva)
        const osc = this.ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(node.freq, t);

        // Subharmonic (Tamas - 1/4th frequency)
        const subOsc = this.ctx.createOscillator();
        subOsc.type = 'triangle';
        subOsc.frequency.setValueAtTime(node.freq / 4, t);

        // Q-Factor Decay Envelope (Rajas)
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0, t);
        gain.gain.linearRampToValueAtTime(0.8, t + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, t + (node.q / 2000));

        osc.connect(gain); subOsc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(t); subOsc.start(t);
        osc.stop(t + (node.q / 2000)); subOsc.stop(t + (node.q / 2000));

        this.activeSources.push(osc, subOsc);
    }

    stop() {
        this.activeSources.forEach(s => { try { s.stop(); } catch(e){} });
        this.activeSources = [];
    }
}

const audioAgent = new JyotirlingaSoundAgent();
let activeNode = JYOTIRLINGAS[0];

// UI Binding
document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('nodeGrid');
    JYOTIRLINGAS.forEach((node, i) => {
        const card = document.createElement('div');
        card.className = `node-card ${i === 0 ? 'active' : ''}`;
        card.innerHTML = `<h4 style="color:var(--gold-primary); margin:0 0 5px 0;">${node.name}</h4><p style="font-size:0.8rem; color:var(--text-muted); margin:0;">${node.freq} Hz · Q${node.q}</p>`;
        card.onclick = () => {
            document.querySelectorAll('.node-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            activeNode = node;
            document.getElementById('activeNodeName').innerText = node.name;
        };
        grid.appendChild(card);
    });

    document.getElementById('playBtn').onclick = () => audioAgent.exciteNode(activeNode);
    document.getElementById('stopBtn').onclick = () => audioAgent.stop();
    
    // Simple visualizer loop
    const canvas = document.getElementById('acousticVisualizer');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight;
    const dataArray = new Uint8Array(128);
    
    function draw() {
        requestAnimationFrame(draw);
        if (!audioAgent.analyser) return;
        audioAgent.analyser.getByteFrequencyData(dataArray);
        ctx.fillStyle = '#05070a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        const barW = canvas.width / 128;
        for (let i = 0; i < 128; i++) {
            const h = (dataArray[i] / 255) * canvas.height;
            ctx.fillStyle = `hsl(${40 + i}, 80%, 60%)`;
            ctx.fillRect(i * barW, canvas.height - h, barW - 1, h);
        }
    }
    draw();
});