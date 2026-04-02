import { useMemo, useState, type FormEvent } from "react";
import "./App.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ChatSource = {
  title: string;
  url: string | null;
};

type ChatResponse = {
  answer: string;
  sources: ChatSource[];
  conversation_id: number;
};

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
};

function App() {
  const [message, setMessage] = useState("");
  const [explanationLevel, setExplanationLevel] = useState<"basic" | "technical">("basic");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [latestSources, setLatestSources] = useState<ChatSource[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const canSubmit = message.trim().length > 0 && !isLoading;

  const conversationLabel = useMemo(() => {
    if (conversationId === null) {
      return "New conversation";
    }

    return `Conversation #${conversationId}`;
  }, [conversationId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedMessage,
    };

    setError("");
    setMessages((current) => [...current, userMessage]);
    setMessage("");
    setIsLoading(true);

    try {
      const backendResponse = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
          explanation_level: explanationLevel,
          conversation_id: conversationId,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error("Request failed");
      }

      const data: ChatResponse = await backendResponse.json();
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        sources: data.sources,
      };

      setConversationId(data.conversation_id);
      setLatestSources(data.sources);
      setMessages((current) => [...current, assistantMessage]);
    } catch {
      setError("Could not connect to the backend or generate a response.");
      setMessages((current) => current.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Grounded Financial Guidance</p>
          <h1>FinanceBuddy</h1>
          <p className="hero-text">
            Ask about taxes, mortgages, and personal finance concepts. Each answer
            is generated from trusted retrieved evidence rather than unsupported
            guesswork.
          </p>
        </div>

        <div className="hero-meta">
          <div className="meta-card">
            <span className="meta-label">Conversation</span>
            <strong>{conversationLabel}</strong>
          </div>
          <div className="meta-card">
            <span className="meta-label">Mode</span>
            <strong>{explanationLevel === "basic" ? "Basic clarity" : "Technical depth"}</strong>
          </div>
        </div>
      </section>

      <section className="workspace">
        <div className="conversation-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Conversation Workspace</p>
              <h2>Ask, refine, follow up</h2>
            </div>
            <span className="status-pill">
              {isLoading ? "Generating answer..." : "Ready"}
            </span>
          </div>

          <div className="messages">
            {messages.length === 0 ? (
              <article className="empty-state">
                <h3>Start with a real financial question</h3>
                <p>
                  Try something like “What is the difference between a tax and a fee?”
                  or “How does a fixed-rate mortgage work?”
                </p>
              </article>
            ) : (
              messages.map((entry) => (
                <article
                  key={entry.id}
                  className={`message-card message-card--${entry.role}`}
                >
                  <header className="message-header">
                    <span className="message-role">
                      {entry.role === "user" ? "You" : "FinanceBuddy"}
                    </span>
                  </header>
                  <p className="message-content">{entry.content}</p>
                </article>
              ))
            )}
          </div>

          <form className="composer" onSubmit={handleSubmit}>
            <div className="composer-controls">
              <div className="segmented-control" role="radiogroup" aria-label="Explanation level">
                <button
                  type="button"
                  className={explanationLevel === "basic" ? "is-active" : ""}
                  onClick={() => setExplanationLevel("basic")}
                >
                  Basic
                </button>
                <button
                  type="button"
                  className={explanationLevel === "technical" ? "is-active" : ""}
                  onClick={() => setExplanationLevel("technical")}
                >
                  Technical
                </button>
              </div>
            </div>

            <label className="composer-label" htmlFor="message">
              Your question
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask about a mortgage, a tax concept, or another financial topic."
              rows={4}
            />

            <div className="composer-actions">
              {error ? <p className="error-text">{error}</p> : <span className="helper-text">Grounded answers only from retrieved evidence.</span>}
              <button type="submit" disabled={!canSubmit}>
                {isLoading ? "Working..." : "Send question"}
              </button>
            </div>
          </form>
        </div>

        <aside className="sources-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Evidence Panel</p>
              <h2>Sources used in the latest answer</h2>
            </div>
          </div>

          <div className="sources-list">
            {latestSources.length === 0 ? (
              <article className="source-empty">
                <p>
                  Supporting sources will appear here after FinanceBuddy retrieves
                  evidence for an answer.
                </p>
              </article>
            ) : (
              latestSources.map((source, index) => (
                <article className="source-card" key={`${source.title}-${index}`}>
                  <span className="source-index">Source {index + 1}</span>
                  <h3>{source.title}</h3>
                  {source.url ? (
                    <a href={source.url} target="_blank" rel="noreferrer">
                      Open source
                    </a>
                  ) : (
                    <p className="source-note">Stored local trusted document</p>
                  )}
                </article>
              ))
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

export default App;
