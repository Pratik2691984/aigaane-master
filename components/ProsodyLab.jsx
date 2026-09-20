import React, { useState, useRef } from "react";

export default function ProsodyLab() {
  const [verse, setVerse] = useState(
    "धर्मक्षेत्रे कुरुक्षेत्रे\nसमवेता युयुत्सवः\nमामकाः पाण्डवाश्चैव\nकिमकुर्वत सञ्जय"
  );
  const [meter, setMeter] = useState("anustubh");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioCtxRef = useRef(null);

  async function handleScan() {
    setLoading(true);
    try {
      const res = await fetch("https://aigaane.in/api/v3/prosody/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: verse, chandas: meter, padanta_guru: true }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Scansion failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function playTone(freq, durationSec, startTime) {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = audioCtxRef.current;
    if (ctx.state === "suspended") {
      ctx.resume();
    }

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, startTime);

    gain.gain.setValueAtTime(0.001, startTime);
    gain.gain.exponentialRampToValueAtTime(0.2, startTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + durationSec - 0.02);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(startTime);
    osc.stop(startTime + durationSec);
  }

  function playVerseAudio() {
    if (!result?.padas) return;
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = audioCtxRef.current;
    if (ctx.state === "suspended") ctx.resume();

    setIsPlaying(true);
    let currentTime = ctx.currentTime + 0.1;

    result.padas.forEach((pada) => {
      pada.weights.forEach((w) => {
        // Laghu = 1 Matra (240 Hz, 0.25s) | Guru = 2 Matras (360 Hz, 0.50s)
        const freq = w === "G" ? 360.0 : 240.0;
        const dur = w === "G" ? 0.48 : 0.24;
        playTone(freq, dur, currentTime);
        currentTime += dur + 0.06;
      });
      currentTime += 0.25; // Pada pause
    });

    const totalDurationMs = (currentTime - ctx.currentTime) * 1000;
    setTimeout(() => setIsPlaying(false), totalDurationMs);
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-slate-900 text-slate-100 rounded-xl shadow-2xl border border-slate-800">
      <h2 className="text-2xl font-bold mb-1 text-amber-400">पिङ्गल-च्छन्दो-विमर्शः (Prosody Scansion & Synthesis Lab)</h2>
      <p className="text-sm text-slate-400 mb-6">Real-time Akṣara tokenization, weight classification, and Web Audio mātrā synthesis.</p>

      <div className="mb-4">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Sanskrit Verse (Devanagari)</label>
        <textarea
          rows={5}
          value={verse}
          onChange={(e) => setVerse(e.target.value)}
          className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-lg font-serif text-slate-100 focus:outline-none focus:border-amber-500"
        />
      </div>

      <div className="flex flex-wrap gap-4 items-center mb-6">
        <select
          value={meter}
          onChange={(e) => setMeter(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-200"
        >
          <option value="anustubh">Anuṣṭubh (अनुष्टुभ् - 8 syllables)</option>
          <option value="upajati">Upajāti / Indravajrā (उपजाति - 11 syllables)</option>
          <option value="shardulavikridita">Śārdūlavikrīḍita (शार्दूलविक्रीडितम् - 19 syllables)</option>
        </select>

        <button
          onClick={handleScan}
          disabled={loading}
          className="px-6 py-2 bg-amber-600 hover:bg-amber-500 text-black font-semibold rounded-md transition duration-200 disabled:opacity-50"
        >
          {loading ? "Scanning..." : "Scan Metrics"}
        </button>

        {result && (
          <button
            onClick={playVerseAudio}
            disabled={isPlaying}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-md transition duration-200 disabled:opacity-50 flex items-center gap-2"
          >
            <span>{isPlaying ? "♫ Synthesizing Laya..." : "▶ Play Mātrā Cadence"}</span>
          </button>
        )}
      </div>

      {result && (
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <span className="text-lg font-semibold capitalize text-amber-300">
              Meter: {result.chandas} {result.variant ? `(${result.variant})` : ""}
            </span>
            <span
              className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider ${
                result.valid ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-rose-950 text-rose-400 border border-rose-800"
              }`}
            >
              {result.valid ? "Valid Cadence" : "Metric Violations Detected"}
            </span>
          </div>

          <div className="space-y-4">
            {result.padas?.map((pada) => (
              <div key={pada.pada_number} className="bg-slate-900/60 p-3 rounded border border-slate-800/80">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs text-slate-400 font-mono">Pāda {pada.pada_number}</span>
                  <span className="text-xs text-slate-400 font-mono">
                    {pada.total_syllables} akṣaras | {pada.total_matras} mātrās
                  </span>
                </div>
                <div className="text-base font-serif mb-2 text-slate-200">{pada.text}</div>
                <div className="flex flex-wrap gap-1">
                  {pada.syllables?.map((syl, i) => (
                    <div key={i} className="flex flex-col items-center">
                      <span className="text-xs text-slate-400 font-serif">{syl}</span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          pada.weights[i] === "G" ? "bg-amber-900/50 text-amber-300 border border-amber-700/50" : "bg-cyan-950 text-cyan-300 border border-cyan-800/50"
                        }`}
                      >
                        {pada.weights[i]}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {result.diagnostics?.length > 0 && (
            <div className="mt-5 border-t border-rose-950/80 pt-4">
              <h4 className="text-xs font-bold uppercase text-rose-400 mb-2">Diagnostic Faults</h4>
              <ul className="space-y-1 text-xs text-rose-300">
                {result.diagnostics.map((d, i) => (
                  <li key={i}>
                    • Pāda {d.pada}, Syllable {d.syllable}: {d.message}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
