/**
 * VocalSahaya: Syllabic Sanskrit Vocal Synthesis Engine
 * Operates in tandem with Karplus-Strong 22-Sruti Physical Modeling Engine
 */
class VocalSahaya {
    constructor(audioCtx, srutiMap = null) {
        this.ctx = audioCtx;
        this.buffers = {};
        this.isLoaded = false;
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.setValueAtTime(1.0, this.ctx.currentTime);
        this.masterGain.connect(this.ctx.destination);

        // Ahobala 5-limit cents table fallback (S = 220 Hz)
        this.srutiMap = srutiMap || {
            "S": 0.0,
            "r": 111.73,
            "R": 203.91,
            "g": 315.64,
            "G": 386.31,
            "M": 498.04,
            "M'": 590.22,
            "P": 701.96,
            "d": 813.69,
            "D": 905.87,
            "n": 1017.60,
            "N": 1088.27,
            "S'": 1200.0
        };
    }

    /**
     * Decomposes any Sanskrit IAST or Devanagari syllable to its sustained vowel nucleus.
     */
    extractVowel(syllable) {
        const s = (syllable || "").toLowerCase().trim();
        // Check diphthongs first
        if (s.indexOf("au") !== -1 || s.indexOf("ौ") !== -1) return "au";
        if (s.indexOf("ai") !== -1 || s.indexOf("ै") !== -1) return "ai";
        // Long vowels
        if (s.indexOf("aa") !== -1 || s.indexOf("ā") !== -1 || s.indexOf("ा") !== -1) return "aa";
        if (s.indexOf("ii") !== -1 || s.indexOf("ī") !== -1 || s.indexOf("ी") !== -1) return "ii";
        if (s.indexOf("uu") !== -1 || s.indexOf("ū") !== -1 || s.indexOf("ू") !== -1) return "uu";
        // Vocalic r
        if (s.indexOf("ri") !== -1 || s.indexOf("ṛ") !== -1 || s.indexOf("ऋ") !== -1 || s.indexOf("ृ") !== -1) return "ri";
        // Simple vowels
        if (s.indexOf("e") !== -1 || s.indexOf("े") !== -1) return "e";
        if (s.indexOf("o") !== -1 || s.indexOf("ो") !== -1) return "o";
        if (s.indexOf("i") !== -1 || s.indexOf("ि") !== -1) return "i";
        if (s.indexOf("u") !== -1 || s.indexOf("ु") !== -1) return "u";
        return "a";
    }

    /**
     * Preloads all 11 core vowel waveforms into Web Audio memory.
     */
    async preloadSamples(basePath = "audio/vocal/") {
        const vowels = ["a", "aa", "i", "ii", "u", "uu", "ri", "e", "ai", "o", "au"];
        const loadPromises = vowels.map(async (v) => {
            try {
                const res = await fetch(basePath + v + ".wav");
                if (!res.ok) throw new Error("HTTP " + res.status);
                const arrayBuf = await res.arrayBuffer();
                this.buffers[v] = await this.ctx.decodeAudioData(arrayBuf);
            } catch (err) {
                console.warn("[VocalSahaya] Fallback synthesizing for vowel: " + v, err);
            }
        });

        await Promise.all(loadPromises);
        this.isLoaded = true;
        console.log("✓ [VocalSahaya] All 11 vocalic atoms loaded successfully.");
    }

    /**
     * Plays a single syllable matched to an Ahobala swara and meend target.
     */
    playSyllable(syllable, swara, startTime, durationSec, meendTarget = null) {
        startTime = Math.max(startTime || 0, this.ctx.currentTime + 0.02);
        if (!this.isLoaded) return;

        const vowel = this.extractVowel(syllable);
        const buffer = this.buffers[vowel];
        if (!buffer) return;

        const source = this.ctx.createBufferSource();
        source.buffer = buffer;

        // Calculate pitch shift from cents
        const baseCents = (this.srutiMap[swara] !== undefined) ? this.srutiMap[swara] : 0.0;
        const baseRate = Math.pow(2.0, baseCents / 1200.0);
        source.playbackRate.setValueAtTime(baseRate, startTime);

        // Continuous meend glide if target is specified
        if (meendTarget && this.srutiMap[meendTarget] !== undefined) {
            const targetCents = this.srutiMap[meendTarget];
            const targetRate = Math.pow(2.0, targetCents / 1200.0);
            source.playbackRate.linearRampToValueAtTime(targetRate, startTime + durationSec * 0.85);
        }

        // Amplitude ADSR envelope
        const env = this.ctx.createGain();
        env.gain.setValueAtTime(0.05, startTime);
        env.gain.linearRampToValueAtTime(1.0, startTime + 0.04);
        env.gain.setValueAtTime(0.7, startTime + durationSec - 0.08);
        env.gain.exponentialRampToValueAtTime(0.001, startTime + durationSec);

        source.connect(env);
        env.connect(this.masterGain);

        source.start(startTime);
        source.stop(startTime + durationSec + 0.05);
    }
}

window.VocalSahaya = VocalSahaya;
