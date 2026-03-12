// src/hooks/useBuilder.js
import { useState, useCallback } from "react";
import { buildPresentation } from "../api/pptxApi";

export function useBuilder() {
  const [status, setStatus]     = useState("idle");   // idle | loading | done | error
  const [events, setEvents]     = useState([]);
  const [result, setResult]     = useState(null);     // { file_id, filename }
  const [error, setError]       = useState(null);
  const [telemetry, setTelemetry] = useState(null);

  const build = useCallback(async (brief) => {
    setStatus("loading");
    setEvents([]);
    setResult(null);
    setError(null);
    setTelemetry(null);

    await buildPresentation(
      brief,
      (event) => {
        if (event.type === "telemetry") { setTelemetry(event); return; }
        setEvents((prev) => [...prev, event]);
      },
      (done)  => {
        setStatus("done");
        if (done) setResult(done);
      },
      (msg)   => { setError(msg); setStatus("error"); },
    );
  }, []);

  const reset = useCallback(() => {
    setStatus("idle");
    setEvents([]);
    setResult(null);
    setError(null);
    setTelemetry(null);
  }, []);

  return { status, events, result, error, telemetry, build, reset };
}
