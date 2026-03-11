// src/App.jsx
import React, { useState } from "react";
import AnalystPanel from "./components/AnalystPanel";
import BuilderPanel from "./components/BuilderPanel";
import "./App.css";

const TABS = [
  { id: "analyse", label: "Analyse", emoji: "🔍" },
  { id: "build",   label: "Build",   emoji: "✨" },
];

export default function App() {
  const [tab, setTab] = useState("analyse");

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-logo">📊</span>
          <div>
            <h1>PPTX Agents</h1>
            <p>Analyse & build PowerPoint presentations with Azure AI</p>
          </div>
        </div>
        <nav className="tab-nav">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`tab-btn ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              {t.emoji} {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {tab === "analyse" && <AnalystPanel />}
        {tab === "build"   && <BuilderPanel />}
      </main>

      <footer className="app-footer">
        Analyst: <strong>gpt-5.3-codex</strong> &nbsp;·&nbsp;
        Builder: <strong>gpt-5.4</strong> (content) + <strong>gpt-5.3-codex</strong> (code)
      </footer>
    </div>
  );
}
