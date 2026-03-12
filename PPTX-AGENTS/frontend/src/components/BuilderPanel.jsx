// src/components/BuilderPanel.jsx
import React, { useState } from "react";
import { Wand2, Download, RotateCcw, CheckCircle, AlertCircle, Loader, Save } from "lucide-react";
import { useBuilder } from "../hooks/useBuilder";
import { downloadUrl } from "../api/pptxApi";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

const EVENT_ICONS = {
  status:  "⚙",
  content: "📋",
  code:    "💻",
  done:    "✅",
  error:   "❌",
};

export default function BuilderPanel() {
  const [brief, setBrief]       = useState("");
  const [showCode, setShowCode] = useState(false);
  const { status, events, result, error, telemetry, build, reset } = useBuilder();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!brief.trim()) return;
    build(brief.trim());
  };

  const handleDownload = async () => {
    try {
      const res = await fetch(downloadUrl(result.file_id));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Download failed: ${err.message}`);
    }
  };

  const handleReset = () => {
    setBrief("");
    reset();
  };

  const handleSaveOutline = () => {
    const spec = contentEvent?.json;
    if (!spec) return;
    const stem = result?.filename?.replace(/\.pptx$/i, "") ?? spec.title ?? "outline";
    const lines = [
      `# ${spec.title}`,
      `_Theme: ${spec.theme} · ${spec.slides.length} slides · Generated ${new Date().toLocaleString()}_`,
      "",
      "---",
      "",
    ];
    spec.slides.forEach((s) => {
      lines.push(`## ${s.index}. ${s.title}` + (s.subtitle ? ` — *${s.subtitle}*` : ""));
      lines.push(`> Layout: \`${s.layout}\``);
      if (s.bullets?.length)  s.bullets.forEach((b) => lines.push(`- ${b}`));
      if (s.left_bullets?.length || s.right_bullets?.length) {
        if (s.left_title)  lines.push(`**${s.left_title}**`);
        s.left_bullets?.forEach((b) => lines.push(`- ${b}`));
        if (s.right_title) lines.push(`**${s.right_title}**`);
        s.right_bullets?.forEach((b) => lines.push(`- ${b}`));
      }
      if (s.notes) lines.push("", `*Speaker notes: ${s.notes}*`);
      lines.push("");
    });
    const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${stem}-outline.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isLoading = status === "loading";
  const codeEvent = events.find((e) => e.type === "code");
  const contentEvent = events.find((e) => e.type === "content");

  return (
    <div className="panel">
      <div className="panel-header">
        <Wand2 size={20} />
        <h2>Build Presentation</h2>
        <span className="model-badge">gpt-5.4 + gpt-5.3-codex</span>
      </div>

      {status === "idle" || status === "error" ? (
        <form onSubmit={handleSubmit} className="form">
          <label className="field-label">Presentation brief</label>
          <textarea
            className="brief-input"
            placeholder={`Describe the presentation you want to create.\n\nExamples:\n• "Azure AI Foundry value proposition for automotive companies, 12 slides, professional tone"\n• "Q1 2026 sales results for EMEA region with recommendations, executive audience"`}
            value={brief}
            onChange={(e) => setBrief(e.target.value)}
            rows={6}
          />

          {error && <div className="error-banner">⚠ {error}</div>}

          <button className="btn-primary" type="submit" disabled={!brief.trim()}>
            <Wand2 size={16} /> Generate Presentation
          </button>
        </form>
      ) : null}

      {(isLoading || status === "done") && (
        <div className="build-progress">
          {/* Connecting/waiting state before first event */}
          {isLoading && events.length === 0 && (
            <div className="waiting-state">
              <div className="waiting-bar" />
              <div className="waiting-label">
                <Loader size={14} className="spin" />
                Connecting to Azure AI…
              </div>
              <div className="waiting-steps">
                <div className="waiting-step">Step 1 — Generating slide content with gpt-5.4</div>
                <div className="waiting-step">Step 2 — Generating python-pptx code with gpt-5.3-codex</div>
                <div className="waiting-step">Step 3 — Executing code to build the file</div>
              </div>
            </div>
          )}

          {/* Event log */}
          {events.length > 0 && (
          <div className="event-log">
            {events.map((evt, i) => (
              <div key={i} className={`event-row event-${evt.type}`}>
                <span className="event-icon">{EVENT_ICONS[evt.type] || "•"}</span>
                <span className="event-msg">
                  {evt.type === "status"  && evt.message}
                  {evt.type === "content" && `Slide deck planned: ${evt.json?.slides?.length ?? "?"} slides — "${evt.json?.title ?? ""}"`}
                  {evt.type === "code"    && (
                    <span>
                      python-pptx code generated ({evt.python?.split("\n").length} lines){" "}
                      <button className="btn-link" onClick={() => setShowCode((v) => !v)}>
                        {showCode ? "hide" : "show"} code
                      </button>
                    </span>
                  )}
                  {evt.type === "done"  && `Done — ${evt.filename}`}
                  {evt.type === "error" && evt.message}
                </span>
                {isLoading && i === events.length - 1 && (
                  <Loader size={14} className="spin" />
                )}
              </div>
            ))}
          </div>
          )}

          {/* Generated code preview */}
          {showCode && codeEvent && (
            <div className="code-preview">
              <SyntaxHighlighter language="python" style={vscDarkPlus} showLineNumbers>
                {codeEvent.python}
              </SyntaxHighlighter>
            </div>
          )}

          {/* Slide outline */}
          {contentEvent?.json?.slides && (
            <details className="slide-outline">
              <summary>
                Slide outline ({contentEvent.json.slides.length} slides)
                {status === "done" && (
                  <button
                    className="btn-ghost outline-save-btn"
                    onClick={(e) => { e.preventDefault(); handleSaveOutline(); }}
                  >
                    <Save size={12} /> Save outline
                  </button>
                )}
              </summary>
              <ol>
                {contentEvent.json.slides.map((s) => (
                  <li key={s.index}>
                    <strong>{s.title}</strong>
                    {s.subtitle && <em> — {s.subtitle}</em>}
                    <span className="slide-layout"> [{s.layout}]</span>
                  </li>
                ))}
              </ol>
            </details>
          )}

          {/* Download bar */}
          {result && (
            <div className="download-bar">
              <CheckCircle size={18} className="success-icon" />
              <span><strong>{result.filename}</strong> is ready</span>
              <button
                className="btn-download"
                onClick={handleDownload}
              >
                <Download size={16} /> Download PPTX
              </button>
              <button className="btn-ghost" onClick={handleReset}>
                <RotateCcw size={14} /> New presentation
              </button>
            </div>
          )}

          {/* Telemetry footer */}
          {telemetry && (
            <div className="telemetry-bar">
              <span>⏱ {telemetry.elapsed_s}s</span>
              <span className="telem-sep">·</span>
              {telemetry.calls?.map((c, i) => (
                <span key={i} className="telem-call">
                  {c.model}: {c.input_tokens.toLocaleString()}↑ {c.output_tokens.toLocaleString()}↓
                </span>
              ))}
              <span className="telem-sep">·</span>
              <span className="telem-total">{telemetry.total_tokens.toLocaleString()} tokens total</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
