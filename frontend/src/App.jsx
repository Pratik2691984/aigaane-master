import { useEffect, useState } from "react";
import AigaaneInspector from "./AigaaneInspector";
import { probeEngine } from "./engineStatus";

export default function App() {
  const [engineStatus, setEngineStatus] = useState("checking...");

  useEffect(() => {
    probeEngine().then((res) => setEngineStatus(res.status));
  }, []);

  return (
    <div>
      <div
        style={{
          padding: "10px",
          background: engineStatus === "ok" ? "#064e3b" : "#7f1d1d",
          color: "white",
          textAlign: "center",
          fontWeight: "bold",
        }}
      >
        Engine Status: {engineStatus.toUpperCase()}
      </div>
      <AigaaneInspector />
    </div>
  );
}