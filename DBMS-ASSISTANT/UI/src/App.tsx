import { useState, useRef, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { save } from "@tauri-apps/plugin-dialog";
import { writeTextFile } from "@tauri-apps/plugin-fs";
import { Database, Send, Settings, Activity, Trash2, Lightbulb, Download } from "lucide-react";
import "./App.css";

interface ChatMessage {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ConnectionStatus {
  is_connected: boolean;
  server: string | null;
  database: string | null;
}

const SAMPLE_QUESTIONS = [
  "Show me the foreign key relationships",
  "Generate an ERD diagram",
  "Check for blocking sessions and locks",
  "Show index fragmentation levels",
  "List the top 10 largest tables",
  "Find long-running queries"
];

function App() {
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({ 
    is_connected: false, 
    server: null, 
    database: null 
  });
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Check connection status on mount and periodically
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await invoke<ConnectionStatus>("get_connection_status");
        setConnectionStatus(status);
      } catch (error) {
        console.error("Failed to get connection status:", error);
      }
    };

    // Check immediately on mount
    checkConnection();

    // Check every 5 seconds
    const interval = setInterval(checkConnection, 5000);

    return () => clearInterval(interval);
  }, []);

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
      
      // Update connection status after successful query
      setConnectionStatus(prev => ({ ...prev, is_connected: true }));
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
    invoke("clear_conversation");
  };

  const exportChat = async () => {
    if (chatHistory.length === 0) {
      alert("No conversation to export");
      return;
    }

    try {
      // Format the chat history
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const serverInfo = connectionStatus.is_connected 
        ? `Server: ${connectionStatus.server}\nDatabase: ${connectionStatus.database}\n`
        : 'Not connected\n';
      
      let content = `RDBMS Assistant - Chat Export\n`;
      content += `Export Date: ${new Date().toLocaleString()}\n`;
      content += `${serverInfo}`;
      content += `${'='.repeat(80)}\n\n`;

      chatHistory.forEach((msg, idx) => {
        content += `[${msg.timestamp.toLocaleTimeString()}] ${msg.type.toUpperCase()}\n`;
        content += `${'-'.repeat(80)}\n`;
        content += `${msg.content}\n\n`;
        if (idx < chatHistory.length - 1) {
          content += `${'='.repeat(80)}\n\n`;
        }
      });

      // Open save dialog
      const filePath = await save({
        defaultPath: `rdbms-chat-${timestamp}.txt`,
        filters: [{
          name: 'Text Files',
          extensions: ['txt']
        }, {
          name: 'Markdown Files',
          extensions: ['md']
        }]
      });

      if (filePath) {
        await writeTextFile(filePath, content);
        alert(`Chat history exported to:\n${filePath}`);
      }
    } catch (error) {
      alert(`Failed to export chat: ${error}`);
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
          <button className="icon-button" onClick={exportChat} title="Export Chat History">
            <Download className="icon" />
          </button>
          <button className="icon-button" onClick={clearChat} title="Clear Chat History">
            <Trash2 className="icon" />
          </button>
          <button className="icon-button" title="Settings">
            <Settings className="icon" />
          </button>
          <div 
            className={`status-indicator ${connectionStatus.is_connected ? 'connected' : 'disconnected'}`}
            title={connectionStatus.is_connected ? 
              `Connected to ${connectionStatus.server}/${connectionStatus.database}` : 
              'Not connected'
            }
          >
            <Activity className="icon-small" />
            <span>
              {connectionStatus.is_connected ? 
                `Connected: ${connectionStatus.database}` : 
                'Disconnected'
              }
            </span>
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
