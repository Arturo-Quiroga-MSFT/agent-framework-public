// src/components/AnalystPanel.jsx
import React, { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Upload, Search, RotateCcw, FileText, Save, Wand2 } from "lucide-react";
import { useAnalyst } from "../hooks/useAnalyst";

/**
 * Fix spacing artifacts from token-level streaming:
 *   "** bold **"  →  "**bold**"
 *   "* item *"   →  "*item*"
 *   "_ text _"   →  "_text_"
 */
function fixMarkdown(text) {
  return text
    // collapse spaces inside bold/italic markers
    .replace(/\*\*\s+([^*]+?)\s+\*\*/g, (_, t) => `**${t.trim()}**`)
    .replace(/\*\s+([^*]+?)\s+\*/g,   (_, t) => `*${t.trim()}*`)
    .replace(/_\s+([^_]+?)\s+_/g,     (_, t) => `_${t.trim()}_`)
    // fix "( Slide 2 – 8 )" → "(Slide 2–8)" style spacing
    .replace(/\(\s+/g, "(")
    .replace(/\s+\)/g, ")");
}

export default function AnalystPanel({ onBuildAddendum }) {
  const [file, setFile]         = useState(null);
  const [question, setQuestion] = useState("");
  const [dragging, setDragging] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const inputRef                = useRef(null);
  const { status, output, error, telemetry, recommendations, analyse, reset } = useAnalyst();

  const handleFile = (f) => {
    if (f && f.name.toLowerCase().endsWith(".pptx")) setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return;
    analyse(file, question || undefined);
  };

  const handleReset = () => {
    setFile(null);
    setQuestion("");
    setSelectedIds([]);
    reset();
  };

  const toggleRec = (id) =>
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );

  const handleBuildAddendum = () => {
    if (!onBuildAddendum || selectedIds.length === 0) return;
    const chosen = recommendations.filter((r) => selectedIds.includes(r.id));
    const stem   = file ? file.name.replace(/\.pptx$/i, "") : "the presentation";
    const ctx    = output.slice(0, 400).replace(/\n+/g, " ");
    const brief  =
      `ADDENDUM MODE — Generate only additional slides to extend an existing deck.\n\n` +
      `Existing deck: "${stem}"\n` +
      `Context: ${ctx}\n\n` +
      `Generate ONLY 4-6 slides that address these specific recommendations:\n` +
      chosen.map((r, i) => `${i + 1}. ${r.text}`).join("\n") +
      `\n\nIMPORTANT:\n` +
      `- Start with a section_break slide titled "Addendum: Improvements"\n` +
      `- Generate ONLY the gap-filling slides, NOT a full deck\n` +
      `- End with a closing slide\n` +
      `- Include a references slide if you consult web sources\n` +
      `- Do NOT repeat content already in the original deck\n` +
      `- 4-6 slides maximum`;
    onBuildAddendum(brief);
  };

  const handleSave = () => {
    const stem = file ? file.name.replace(/\.pptx$/i, "") : "analysis";
    const header = `# Analysis: ${stem}\n_Model: gpt-5.3-codex · Analysed ${new Date().toLocaleString()}_\n\n---\n\n`;
    const blob = new Blob([header + fixMarkdown(output)], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${stem}-analysis.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isLoading = status === "loading";

  return (
    <div className="panel">
      <div className="panel-header">
        <Search size={20} />
        <h2>Analyse Presentation</h2>
        <span className="model-badge">gpt-5.3-codex</span>
      </div>

      {status === "idle" || status === "error" ? (
        <form onSubmit={handleSubmit} className="form">
          {/* Drop zone */}
          <div
            className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pptx"
              hidden
              onChange={(e) => handleFile(e.target.files[0])}
            />
            {file ? (
              <div className="file-selected">
                <FileText size={24} />
                <span>{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(0)} KB)</span>
              </div>
            ) : (
              <div className="dropzone-hint">
                <Upload size={32} />
                <p>Drop a <strong>.pptx</strong> file here, or click to browse</p>
              </div>
            )}
          </div>

          {/* Question input */}
          <textarea
            className="question-input"
            placeholder="Ask a specific question, or leave blank for a full analysis…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
          />

          {error && <div className="error-banner">⚠ {error}</div>}

          <button className="btn-primary" type="submit" disabled={!file}>
            <Search size={16} /> Analyse
          </button>
        </form>
      ) : null}

      {isLoading && (
        <div className="stream-container">
          <div className="stream-header">
            <span className="pulse-dot" />
            <span>Analysing with gpt-5.3-codex…</span>
          </div>
          <div className="stream-output">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{fixMarkdown(output)}</ReactMarkdown>
          </div>
        </div>
      )}

      {status === "done" && (
        <div className="result-container">
          <div className="result-header">
            <span className="success-dot" />
            <span>Analysis complete</span>
            <button className="btn-ghost" onClick={handleSave}>
              <Save size={14} /> Save as Markdown
            </button>
            <button className="btn-ghost" onClick={handleReset}>
              <RotateCcw size={14} /> New analysis
            </button>
          </div>
          <div className="stream-output">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{fixMarkdown(output)}</ReactMarkdown>
          </div>
          {telemetry && (
            <div className="telemetry-bar">
              <span>⏱ {telemetry.elapsed_s}s</span>
              <span className="telem-sep">·</span>
              <span>↑ {telemetry.input_tokens.toLocaleString()} in</span>
              <span className="telem-sep">·</span>
              <span>↓ {telemetry.output_tokens.toLocaleString()} out</span>
              <span className="telem-sep">·</span>
              <span className="telem-total">{telemetry.total_tokens.toLocaleString()} tokens total</span>
              <span className="telem-model">{telemetry.model}</span>
            </div>
          )}

          {recommendations.length > 0 && (
            <div className="addendum-panel">
              <div className="addendum-header">
                <Wand2 size={15} />
                <span>Generate addendum slides from selected recommendations</span>
                <button
                  className="btn-ghost btn-xs"
                  onClick={() =>
                    selectedIds.length === recommendations.length
                      ? setSelectedIds([])
                      : setSelectedIds(recommendations.map((r) => r.id))
                  }
                >
                  {selectedIds.length === recommendations.length ? "Deselect all" : "Select all"}
                </button>
              </div>
              <ul className="rec-list">
                {recommendations.map((rec) => (
                  <li key={rec.id} className={`rec-item ${selectedIds.includes(rec.id) ? "selected" : ""}`}>
                    <label>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(rec.id)}
                        onChange={() => toggleRec(rec.id)}
                      />
                      <span>{rec.text}</span>
                    </label>
                  </li>
                ))}
              </ul>
              <button
                className="btn-primary btn-sm"
                disabled={selectedIds.length === 0}
                onClick={handleBuildAddendum}
              >
                <Wand2 size={14} /> Build {selectedIds.length || ""} addendum slide{selectedIds.length !== 1 ? "s" : ""} →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
