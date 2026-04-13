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

type AgentTraceEvent = {
  node_name: string;
  status: string;
  summary?: string | null;
  retrieval_status?: string | null;
  retrieval_query?: string | null;
  scores?: number[];
  decision?: string | null;
  chunk_count?: number | null;
  source_count?: number | null;
  answer_status?: string | null;
  request_type?: string | null;
  internal_evidence_status?: string | null;
};

type AgentRetrievedChunk = {
  source_id?: number | null;
  source_title?: string | null;
  source_url?: string | null;
  source_publisher?: string | null;
  score?: number | null;
  text?: string | null;
};

type AgentWebResult = {
  title?: string | null;
  url?: string | null;
  publisher?: string | null;
  snippet?: string | null;
};

type AgentChatResponse = ChatResponse & {
  trace_events?: AgentTraceEvent[];
  retrieved_chunks?: AgentRetrievedChunk[];
  web_results?: AgentWebResult[];
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

type ChatMode = "baseline" | "agent";

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
  const [chatMode, setChatMode] = useState<ChatMode>("baseline");
  const [allowWebSearch, setAllowWebSearch] = useState(false);
  const [showDeveloperDebug, setShowDeveloperDebug] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [latestSources, setLatestSources] = useState<ChatSource[]>([]);
  const [latestTraceEvents, setLatestTraceEvents] = useState<AgentTraceEvent[]>([]);
  const [latestRetrievedChunks, setLatestRetrievedChunks] = useState<AgentRetrievedChunk[]>([]);
  const [latestWebResults, setLatestWebResults] = useState<AgentWebResult[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoringConversation, setIsRestoringConversation] = useState(true);

  const canSubmit = message.trim().length > 0 && !isLoading;
  const chatEndpoint = chatMode === "agent" ? "/agent/chat" : "/chat";

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
        setLatestTraceEvents([]);
        setLatestRetrievedChunks([]);
        setLatestWebResults([]);
      } catch {
        window.localStorage.removeItem(conversationStorageKey);
        setConversationId(null);
        setMessages([]);
        setLatestSources([]);
        setLatestTraceEvents([]);
        setLatestRetrievedChunks([]);
        setLatestWebResults([]);
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
    setLatestTraceEvents([]);
    setLatestRetrievedChunks([]);
    setLatestWebResults([]);
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
      const backendResponse = await fetch(`${apiBaseUrl}${chatEndpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
          explanation_level: explanationLevel,
          conversation_id: conversationId,
          allow_web_search: chatMode === "agent" ? allowWebSearch : false,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error("Request failed");
      }

      const data: AgentChatResponse = await backendResponse.json();
      const assistantMessage: Message = {
        id: `assistant-${data.message_id}`,
        backendMessageId: data.message_id,
        role: "assistant",
        content: data.answer,
        sources: data.sources,
      };

      setConversationId(data.conversation_id);
      setLatestSources(data.sources);
      setLatestTraceEvents(chatMode === "agent" ? (data.trace_events ?? []) : []);
      setLatestRetrievedChunks(chatMode === "agent" ? (data.retrieved_chunks ?? []) : []);
      setLatestWebResults(chatMode === "agent" ? (data.web_results ?? []) : []);
      setMessages((current) => [...current, assistantMessage]);
    } catch {
      setError("Could not connect to the backend or generate a response.");
      setMessages((current) => current.slice(0, -1));
      setLatestTraceEvents([]);
      setLatestRetrievedChunks([]);
      setLatestWebResults([]);
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
            <span className="meta-subtext">
              {chatMode === "agent" ? "Agent V1 path" : "Baseline RAG path"}
            </span>
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
              <div className="segmented-control" role="radiogroup" aria-label="Chat backend path">
                <button
                  type="button"
                  className={chatMode === "baseline" ? "is-active" : ""}
                  onClick={() => setChatMode("baseline")}
                  disabled={isLoading || isRestoringConversation}
                >
                  Baseline RAG
                </button>
                <button
                  type="button"
                  className={chatMode === "agent" ? "is-active" : ""}
                  onClick={() => setChatMode("agent")}
                  disabled={isLoading || isRestoringConversation}
                >
                  Agent V1
                </button>
              </div>
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

            {chatMode === "agent" ? (
              <div className="agent-toggle-group">
                <label className="web-search-toggle">
                  <input
                    type="checkbox"
                    checked={allowWebSearch}
                    onChange={(event) => setAllowWebSearch(event.target.checked)}
                    disabled={isLoading || isRestoringConversation}
                  />
                  <span>
                    Allow approved public web search when internal evidence is insufficient
                  </span>
                </label>

                <label className="web-search-toggle">
                  <input
                    type="checkbox"
                    checked={showDeveloperDebug}
                    onChange={(event) => setShowDeveloperDebug(event.target.checked)}
                    disabled={isLoading || isRestoringConversation}
                  />
                  <span>Developer debug view for scores and LangSearch results</span>
                </label>
              </div>
            ) : null}

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

          {chatMode === "agent" && showDeveloperDebug && latestTraceEvents.length > 0 ? (
            <div className="trace-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Agent Trace</p>
                  <h2>Latest agent execution</h2>
                </div>
              </div>

              <div className="trace-list">
                {latestTraceEvents.map((event, index) => (
                  <article className="trace-card" key={`${event.node_name}-${index}`}>
                    <div className="trace-card-header">
                      <strong>{event.node_name}</strong>
                      <span className="trace-status">{event.status}</span>
                    </div>
                    {event.summary ? <p className="trace-summary">{event.summary}</p> : null}
                    <div className="trace-meta">
                      {event.decision ? <span>Decision: {event.decision}</span> : null}
                      {event.retrieval_status ? (
                        <span>Retrieval: {event.retrieval_status}</span>
                      ) : null}
                      {event.answer_status ? <span>Answer: {event.answer_status}</span> : null}
                      {typeof event.chunk_count === "number" ? (
                        <span>Chunks: {event.chunk_count}</span>
                      ) : null}
                      {event.scores && event.scores.length > 0 ? (
                        <span>Scores: {event.scores.map((score) => score.toFixed(3)).join(", ")}</span>
                      ) : null}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          ) : null}

          {chatMode === "agent" && showDeveloperDebug && latestRetrievedChunks.length > 0 ? (
            <div className="trace-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">Retrieved Chunks</p>
                  <h2>Chunk scores</h2>
                </div>
              </div>

              <div className="trace-list">
                {latestRetrievedChunks.map((chunk, index) => (
                  <article className="trace-card" key={`${chunk.source_id ?? "chunk"}-${index}`}>
                    <div className="trace-card-header">
                      <strong>{chunk.source_title ?? `Chunk ${index + 1}`}</strong>
                      {typeof chunk.score === "number" ? (
                        <span className="trace-status">{chunk.score.toFixed(3)}</span>
                      ) : null}
                    </div>
                    <div className="trace-meta">
                      {chunk.source_publisher ? <span>{chunk.source_publisher}</span> : null}
                      {typeof chunk.source_id === "number" ? <span>Source ID: {chunk.source_id}</span> : null}
                    </div>
                    {chunk.text ? (
                      <p className="trace-summary">{chunk.text.slice(0, 220)}...</p>
                    ) : null}
                  </article>
                ))}
              </div>
            </div>
          ) : null}

          {chatMode === "agent" && showDeveloperDebug && latestWebResults.length > 0 ? (
            <div className="trace-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-kicker">LangSearch Results</p>
                  <h2>Raw web retrieval payload</h2>
                </div>
              </div>

              <div className="trace-list">
                {latestWebResults.map((result, index) => (
                  <article className="trace-card" key={`${result.url ?? "web"}-${index}`}>
                    <div className="trace-card-header">
                      <strong>{result.title ?? `Web result ${index + 1}`}</strong>
                      <span className="trace-status">Web</span>
                    </div>
                    <div className="trace-meta">
                      {result.publisher ? <span>{result.publisher}</span> : null}
                      {result.url ? (
                        <span className="trace-url">{result.url}</span>
                      ) : null}
                    </div>
                    {result.snippet ? (
                      <p className="trace-summary">{result.snippet}</p>
                    ) : null}
                  </article>
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </section>
    </main>
  );
}

export default App;
