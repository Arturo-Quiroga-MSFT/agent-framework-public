// src/api/pptxApi.js
// ------------------
// All communication with the FastAPI backend.

const BASE = process.env.REACT_APP_API_URL || "";

/**
 * Upload a PPTX file for analysis.
 * Calls the SSE endpoint and invokes callbacks for each chunk.
 *
 * @param {File}     file
 * @param {string}   question
 * @param {function} onChunk   - called with each text chunk string
 * @param {function} onDone    - called when stream completes
 * @param {function} onError   - called with error message string
 */
export async function analysePresentation(file, question, onChunk, onDone, onError) {
  const form = new FormData();
  form.append("file", file);
  form.append("question", question);

  try {
    const response = await fetch(`${BASE}/api/analyse`, {
      method: "POST",
      body: form,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      onError(err.detail || "Request failed");
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // incomplete line stays buffered

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.slice(6);
          if (payload === "[DONE]") {
            onDone();
            return;
          }
          // Check for error event
          try {
            const parsed = JSON.parse(payload);
            if (parsed.error) { onError(parsed.error); return; }
          } catch (_) {
            // Not JSON — it's a plain text chunk
          }
          onChunk(payload);
        }
      }
    }
    onDone();
  } catch (err) {
    onError(err.message);
  }
}

/**
 * Build a PPTX from a brief.
 * Calls the SSE endpoint and invokes callbacks for build events.
 *
 * @param {string}   brief
 * @param {function} onEvent  - called with each parsed event object
 * @param {function} onDone   - called with { file_id, filename } on success
 * @param {function} onError  - called with error message string
 */
export async function buildPresentation(brief, onEvent, onDone, onError) {
  try {
    const response = await fetch(`${BASE}/api/build`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      onError(err.detail || "Request failed");
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.slice(6);
          if (payload === "[DONE]") { onDone(null); return; }

          try {
            const event = JSON.parse(payload);
            onEvent(event);
            if (event.type === "done")  { onDone(event); return; }
            if (event.type === "error") { onError(event.message); return; }
          } catch (_) {
            // ignore non-JSON lines
          }
        }
      }
    }
  } catch (err) {
    onError(err.message);
  }
}

/**
 * Returns the download URL for a generated PPTX.
 */
export function downloadUrl(fileId) {
  return `${BASE}/api/download/${fileId}`;
}
