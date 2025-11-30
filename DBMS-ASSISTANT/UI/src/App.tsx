import { useState } from "react";
import { Database, Send, Settings, Activity } from "lucide-react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // TODO: Call Tauri command
      // const result = await invoke("run_dba_query", { query });
      // setResponse(result);
      
      // Mock response for now
      setResponse(`Processing query: "${query}"\n\nThis will be replaced with actual results from the Python agent.`);
    } catch (error) {
      setResponse(`Error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <Database className="icon-large" />
          <div>
            <h1>RDBMS Assistant</h1>
            <p className="subtitle">AI-Powered Database Administration</p>
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-button" title="Settings">
            <Settings className="icon" />
          </button>
          <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            <Activity className="icon-small" />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <textarea
              className="query-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your database... (e.g., 'How many tables are in the database?')"
              rows={3}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="submit-button"
              disabled={isLoading || !query.trim()}
            >
              <Send className="icon" />
              {isLoading ? 'Processing...' : 'Send Query'}
            </button>
          </form>
        </div>

        <div className="results-section">
          <h2>Response</h2>
          <div className="results-display">
            {response ? (
              <pre>{response}</pre>
            ) : (
              <p className="placeholder">
                Query results will appear here...
              </p>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Powered by Microsoft Agent Framework + Tauri</p>
      </footer>
    </div>
  );
}

export default App;
