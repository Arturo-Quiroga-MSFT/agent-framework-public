// src/components/AnalystPanel.jsx
import React, { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Upload, Search, RotateCcw, FileText } from "lucide-react";
import { useAnalyst } from "../hooks/useAnalyst";

export default function AnalystPanel() {
  const [file, setFile]         = useState(null);
  const [question, setQuestion] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef                = useRef(null);
  const { status, output, error, analyse, reset } = useAnalyst();

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
    reset();
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
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
          </div>
        </div>
      )}

      {status === "done" && (
        <div className="result-container">
          <div className="result-header">
            <span className="success-dot" />
            <span>Analysis complete</span>
            <button className="btn-ghost" onClick={handleReset}>
              <RotateCcw size={14} /> New analysis
            </button>
          </div>
          <div className="stream-output">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
