import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Database, Send, Settings, Activity, Trash2, Lightbulb } from "lucide-react";
import "./App.css";

interface ChatMessage {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SAMPLE_QUESTIONS = [
  "Show me the foreign key relationships",
  "What's the total loan balance?",
  "List all tables with row counts",
  "Show me customers by industry",
  "Find loans that are past due",
  "Generate an ERD diagram"
];

function App() {
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleSubmit = async (e: React.FormEvent, customQuery?: string) => {
    e.preventDefault();
    const questionToAsk = customQuery || query;
    if (!questionToAsk.trim()) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      content: questionToAsk,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, userMessage]);
    setQuery(""); // Clear input
    setIsLoading(true);
    
    try {
      const result = await invoke<{ success: boolean; message: string; data?: string }>(
        "run_dba_query", 
        { query: questionToAsk }
      );
      
      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.success && result.data ? result.data : result.message,
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `❌ Error: ${error}`,
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSampleQuestion = (question: string) => {
    setQuery(question);
  };

  const clearChat = () => {
    setChatHistory([]);
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
          <button className="icon-button" onClick={clearChat} title="Clear Chat History">
            <Trash2 className="icon" />
          </button>
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
        {/* Sample Questions Section */}
        <div className="sample-questions-section">
          <div className="sample-header">
            <Lightbulb className="icon-small" />
            <span>Quick Questions</span>
          </div>
          <div className="sample-buttons-grid">
            {SAMPLE_QUESTIONS.map((question, idx) => (
              <button
                key={idx}
                className="sample-question-btn"
                onClick={() => handleSampleQuestion(question)}
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Chat History Section */}
        <div className="chat-section">
          <h2>Conversation</h2>
          <div className="chat-history">
            {chatHistory.length === 0 ? (
              <div className="empty-chat">
                <Database className="icon-large" style={{ opacity: 0.3 }} />
                <p className="placeholder">Ask a question to get started...</p>
              </div>
            ) : (
              <div className="chat-messages">
                {chatHistory.map((message) => (
                  <div key={message.id} className={`chat-message ${message.type}-message`}>
                    <div className="message-content">
                      <pre>{message.content}</pre>
                    </div>
                    <div className="message-timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Query Input Section */}
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
      </main>

      <footer className="footer">
        <p>Powered by Microsoft Agent Framework + Tauri</p>
      </footer>
    </div>
  );
}

export default App;
