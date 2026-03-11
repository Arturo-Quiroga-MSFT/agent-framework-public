// src/components/BuilderPanel.jsx
import React, { useState } from "react";
import { Wand2, Download, RotateCcw, CheckCircle, AlertCircle, Loader } from "lucide-react";
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
  const { status, events, result, error, build, reset } = useBuilder();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!brief.trim()) return;
    build(brief.trim());
  };

  const handleReset = () => {
    setBrief("");
    reset();
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
          {/* Event log */}
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
              <summary>Slide outline ({contentEvent.json.slides.length} slides)</summary>
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

          {/* Download button */}
          {result && (
            <div className="download-bar">
              <CheckCircle size={18} className="success-icon" />
              <span><strong>{result.filename}</strong> is ready</span>
              <a
                className="btn-download"
                href={downloadUrl(result.file_id)}
                download={result.filename}
              >
                <Download size={16} /> Download PPTX
              </a>
              <button className="btn-ghost" onClick={handleReset}>
                <RotateCcw size={14} /> New presentation
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
