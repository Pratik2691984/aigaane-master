import { useState } from "react";

const SAMPLE_INPUTS = [
  { label: "Tatpuruṣa (Primary)", value: "rAjaputraH" },
  { label: "Ambiguous (Moon Face)", value: "candramukhaH" },
  { label: "Invalid Compound", value: "rAmasyaputraH" },
  { label: "Three-token Dvandva", value: "devamanuSyanAgAH" },
  { label: "Internal Sandhi", value: "rAjendraH" },
];

export default function AigaaneInspector() {
  const [text, setText] = useState("rAjaputraH");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const parse = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/aigaane/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ text }),
      });
      setResult(await res.json());
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "system-ui",
        color: "#e2e8f0",
        background: "#0f172a",
        minHeight: "100vh",
      }}
    >
      <h1 style={{ color: "#38bdf8" }}>Aigaane Deterministic Kernel</h1>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{
            padding: "10px",
            fontSize: "16px",
            width: "300px",
            borderRadius: "6px",
            border: "1px solid #334155",
            background: "#1e293b",
            color: "white",
          }}
        />
        <button
          onClick={parse}
          disabled={loading}
          style={{
            padding: "10px 20px",
            background: "#38bdf8",
            border: "none",
            borderRadius: "6px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          {loading ? "Parsing..." : "Parse"}
        </button>
      </div>

      <div style={{ display: "flex", gap: "10px", marginBottom: "20px", flexWrap: "wrap" }}>
        {SAMPLE_INPUTS.map((s) => (
          <button
            key={s.value}
            onClick={() => setText(s.value)}
            style={{
              padding: "8px",
              background: "#1e293b",
              color: "#94a3b8",
              border: "1px solid #334155",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {result && (
        <div
          style={{
            background: "#1e293b",
            padding: "20px",
            borderRadius: "10px",
            border: "1px solid #334155",
          }}
        >
          {result.error ? (
            <div style={{ color: "#f87171" }}>Error: {result.error}</div>
          ) : (
            <>
              <h2 style={{ color: "#f472b6" }}>CEGAR Envelope</h2>

              <div
                style={{
                  marginBottom: "20px",
                  padding: "15px",
                  background: "#0f172a",
                  borderRadius: "8px",
                }}
              >
                <h3 style={{ margin: "0 0 10px 0", color: "#cbd5e1" }}>
                  Transliteration Triad
                </h3>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr 1fr",
                    gap: "10px",
                  }}
                >
                  <div>
                    <strong>Devanagari:</strong>{" "}
                    <span style={{ fontSize: "22px" }}>
                      {result.input_triad?.devanagari}
                    </span>
                  </div>
                  <div>
                    <strong>IAST:</strong>{" "}
                    <span style={{ fontSize: "22px" }}>
                      {result.input_triad?.iast}
                    </span>
                  </div>
                  <div>
                    <strong>SLP1:</strong>{" "}
                    <span style={{ fontSize: "22px" }}>
                      {result.input_triad?.slp1}
                    </span>
                  </div>
                </div>
              </div>

              <h3 style={{ color: "#4ade80" }}>
                Verified Candidates ({result.candidates?.length || 0})
              </h3>
              {result.candidates?.map((c, i) => (
                <div
                  key={i}
                  style={{
                    padding: "15px",
                    background: "#0f172a",
                    borderRadius: "8px",
                    marginBottom: "10px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <strong style={{ color: "#4ade80" }}>
                      {c.candidate_id} — Score: {c.score}
                    </strong>
                    <span style={{ color: "#94a3b8" }}>
                      {c.samasa_type || "No Samasa"}
                    </span>
                  </div>
                  {c.vigraha && (
                    <div style={{ marginTop: "5px" }}>
                      Vigraha: <em>{c.vigraha}</em>
                    </div>
                  )}
                  <div style={{ marginTop: "5px", fontSize: "12px", color: "#64748b" }}>
                    Sūtras: {c.sutra_chain?.join(", ")} | Authority:{" "}
                    {c.authority?.recension}
                  </div>
                </div>
              ))}

              <h3 style={{ color: "#f87171" }}>
                Rejected ({result.rejected?.length || 0})
              </h3>
              {result.rejected?.map((r, i) => (
                <div
                  key={i}
                  style={{
                    padding: "10px",
                    background: "#450a0a",
                    borderRadius: "8px",
                    marginBottom: "5px",
                    fontSize: "14px",
                  }}
                >
                  Reason: {r.reason_code} | Stem: {r.parse?.[0]?.stem}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}