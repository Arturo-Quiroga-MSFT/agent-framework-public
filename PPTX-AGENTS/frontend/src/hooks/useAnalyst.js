// src/hooks/useAnalyst.js
import { useState, useCallback, useRef } from "react";
import { analysePresentation } from "../api/pptxApi";

export function useAnalyst() {
  const [status, setStatus]     = useState("idle");   // idle | loading | done | error
  const [output, setOutput]     = useState("");
  const [error, setError]       = useState(null);
  const abortRef                = useRef(false);

  const analyse = useCallback(async (file, question) => {
    abortRef.current = false;
    setStatus("loading");
    setOutput("");
    setError(null);

    await analysePresentation(
      file,
      question,
      (chunk) => {
        if (!abortRef.current) setOutput((prev) => prev + chunk);
      },
      () => { if (!abortRef.current) setStatus("done"); },
      (msg) => { if (!abortRef.current) { setError(msg); setStatus("error"); } },
    );
  }, []);

  const reset = useCallback(() => {
    abortRef.current = true;
    setStatus("idle");
    setOutput("");
    setError(null);
  }, []);

  return { status, output, error, analyse, reset };
}
