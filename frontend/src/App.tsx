import { useEffect, useMemo, useState, type FormEvent } from "react";
import "./App.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const conversationStorageKey = "financebuddy-conversation-id";

type ChatSource = {
  title: string;
  url: string | null;
  publisher: string | null;
};

type ChatResponse = {
  answer: string;
  sources: ChatSource[];
  conversation_id: number;
  message_id: number;
};

type ConversationHistoryMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  explanation_level: string | null;
  answer_status: string | null;
  created_at: string;
  sources: ChatSource[];
};

type ConversationHistoryResponse = {
  conversation_id: number;
  messages: ConversationHistoryMessage[];
};

type FeedbackRating = "positive" | "negative";

type FeedbackResponse = {
  message_id: number;
  rating: FeedbackRating;
  comment: string | null;
};

type Message = {
  id: string;
  backendMessageId?: number;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  feedbackRating?: FeedbackRating;
  feedbackComment?: string | null;
  isSubmittingFeedback?: boolean;
};

function App() {
  // Main chat and request state.
  const [message, setMessage] = useState("");
  const [explanationLevel, setExplanationLevel] = useState<"basic" | "technical">(
    "basic",
  );
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [latestSources, setLatestSources] = useState<ChatSource[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoringConversation, setIsRestoringConversation] = useState(true);

  const canSubmit = message.trim().length > 0 && !isLoading;

  const conversationLabel = useMemo(() => {
    if (conversationId === null) {
      return "New conversation";
    }

    return `Conversation #${conversationId}`;
  }, [conversationId]);

  // Restore the last conversation persisted in local storage.
  useEffect(() => {
    const storedConversationId = window.localStorage.getItem(conversationStorageKey);
    if (!storedConversationId) {
      setIsRestoringConversation(false);
      return;
    }

    const parsedConversationId = Number(storedConversationId);
    if (Number.isNaN(parsedConversationId)) {
      window.localStorage.removeItem(conversationStorageKey);
      setIsRestoringConversation(false);
      return;
    }

    async function restoreConversation() {
      try {
        const response = await fetch(`${apiBaseUrl}/chat/${parsedConversationId}`);
        if (!response.ok) {
          throw new Error("Could not restore conversation");
        }

        const data: ConversationHistoryResponse = await response.json();
        const restoredMessages: Message[] = data.messages.map((entry) => ({
          id: `history-${entry.id}`,
          backendMessageId: entry.id,
          role: entry.role,
          content: entry.content,
          sources: entry.role === "assistant" ? entry.sources : undefined,
        }));

        setConversationId(data.conversation_id);
        setMessages(restoredMessages);
        setLatestSources([]);
      } catch {
        window.localStorage.removeItem(conversationStorageKey);
        setConversationId(null);
        setMessages([]);
        setLatestSources([]);
        setError(
          "Could not restore the previous conversation. A new one will start with your next message.",
        );
      } finally {
        setIsRestoringConversation(false);
      }
    }

    void restoreConversation();
  }, []);

  // Keep the active conversation id available across refreshes.
  useEffect(() => {
    if (conversationId === null) {
      window.localStorage.removeItem(conversationStorageKey);
      return;
    }

    window.localStorage.setItem(conversationStorageKey, String(conversationId));
  }, [conversationId]);

  function resetConversation() {
    setConversationId(null);
    setMessages([]);
    setLatestSources([]);
    setError("");
    window.localStorage.removeItem(conversationStorageKey);
  }

  async function submitFeedback(messageId: string, rating: FeedbackRating) {
    const targetMessage = messages.find((entry) => entry.id === messageId);

    if (!targetMessage?.backendMessageId) {
      setError("Could not submit feedback for this message.");
      return;
    }

    setError("");
    setMessages((current) =>
      current.map((entry) =>
        entry.id === messageId
          ? { ...entry, isSubmittingFeedback: true }
          : entry,
      ),
    );

    try {
      const response = await fetch(
        `${apiBaseUrl}/chat/${targetMessage.backendMessageId}/feedback`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            rating,
            comment: null,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Feedback request failed");
      }
      const data: FeedbackResponse = await response.json();

      setMessages((current) =>
        current.map((entry) =>
          entry.id === messageId
            ? {
                ...entry,
                feedbackRating: data.rating,
                feedbackComment: data.comment,
                isSubmittingFeedback: false,
              }
            : entry,
        ),
      );
    } catch {
      setError("Could not submit feedback right now.");
      setMessages((current) =>
        current.map((entry) =>
          entry.id === messageId
            ? { ...entry, isSubmittingFeedback: false }
            : entry,
        ),
      );
    }
  }

  // Send a new user question and append the grounded assistant answer.
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
        id: `assistant-${data.message_id}`,
        backendMessageId: data.message_id,
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
      {/* Product intro and current session metadata. */}
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

      {/* Main chat area plus the latest-answer evidence panel. */}
      <section className="workspace">
        <div className="conversation-panel">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Conversation Workspace</p>
              <h2>Ask, refine, follow up</h2>
            </div>
            <div className="panel-actions">
              <span className="status-pill">
                {isRestoringConversation
                  ? "Restoring conversation..."
                  : isLoading
                  ? "Generating answer..."
                  : "Ready"}
              </span>
              <button
                type="button"
                className="secondary-button"
                onClick={resetConversation}
                disabled={isLoading || isRestoringConversation}
              >
                New conversation
              </button>
            </div>
          </div>

          <div className="messages">
            {isRestoringConversation ? (
              <article className="empty-state">
                <h3>Restoring your previous conversation</h3>
                <p>FinanceBuddy is loading the saved thread from the backend.</p>
              </article>
            ) : messages.length === 0 ? (
              <article className="empty-state">
                <h3>Start with a real financial question</h3>
                <p>
                  Try something like "What is the difference between a tax and a fee?"
                  or "How does a fixed-rate mortgage work?"
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
                  {entry.role === "assistant" && entry.backendMessageId ? (
                    <div className="message-feedback">
                      <span className="message-feedback-label">Was this helpful?</span>
                      <div className="message-feedback-actions">
                        <button
                          type="button"
                          className={
                            entry.feedbackRating === "positive"
                              ? "feedback-button feedback-button--positive is-selected"
                              : "feedback-button feedback-button--positive"
                          }
                          onClick={() => void submitFeedback(entry.id, "positive")}
                          disabled={entry.isSubmittingFeedback}
                        >
                          Helpful
                        </button>
                        <button
                          type="button"
                          className={
                            entry.feedbackRating === "negative"
                              ? "feedback-button feedback-button--negative is-selected"
                              : "feedback-button feedback-button--negative"
                          }
                          onClick={() => void submitFeedback(entry.id, "negative")}
                          disabled={entry.isSubmittingFeedback}
                        >
                          Not helpful
                        </button>
                      </div>
                      {entry.feedbackRating ? (
                        <p
                          className={
                            entry.feedbackRating === "positive"
                              ? "feedback-status feedback-status--positive"
                              : "feedback-status feedback-status--negative"
                          }
                        >
                          {entry.feedbackRating === "positive"
                            ? "You marked this answer as helpful."
                            : "You marked this answer as not helpful."}
                        </p>
                      ) : null}
                    </div>
                  ) : null}

                  {entry.role === "assistant" && entry.sources && entry.sources.length > 0 ? (
                    <div className="message-sources">
                      <span className="message-sources-label">Sources</span>
                      <div className="message-source-list">
                        {entry.sources.map((source, index) => (
                          <article className="message-source-card" key={`${source.title}-${index}`}>
                            <div className="message-source-copy">
                              <strong>{source.title}</strong>
                              {source.publisher ? (
                                <span className="source-publisher">{source.publisher}</span>
                              ) : null}
                            </div>
                            {source.url ? (
                              <a href={source.url} target="_blank" rel="noreferrer">
                                Open source
                              </a>
                            ) : (
                              <span className="source-note">Stored local trusted document</span>
                            )}
                          </article>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </article>
              ))
            )}
          </div>

          {/* Question composer and explanation-level controls. */}
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
              disabled={isRestoringConversation}
            />

            <div className="composer-actions">
              {error ? (
                <p className="error-text">{error}</p>
              ) : (
                <span className="helper-text">
                  Grounded answers only from retrieved evidence.
                </span>
              )}
              <button type="submit" disabled={!canSubmit || isRestoringConversation}>
                {isLoading ? "Working..." : "Send question"}
              </button>
            </div>
          </form>
        </div>

        {/* Dedicated panel for the sources used in the latest answer. */}
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
                  {source.publisher ? (
                    <p className="source-publisher">{source.publisher}</p>
                  ) : null}
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
