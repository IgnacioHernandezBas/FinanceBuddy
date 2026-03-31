import { useState, type SubmitEvent } from "react";
import "./App.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ChatSource = {
  title: string;
  url: string;
};

type ChatResponse = {
  answer: string;
  sources: ChatSource[];
};

function App() {
  const [message, setMessage] = useState("");
  const [explanationLevel, setExplanationLevel] = useState("basic");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResponse(null);
    setIsLoading(true);

    try {
      const backendResponse = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          explanation_level: explanationLevel,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error("Request failed");
      }

      const data: ChatResponse = await backendResponse.json();
      setResponse(data);
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Finance Buddy</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="message">Question</label>
        <input
          id="message"
          type="text"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="What is a mortgage?"
          required
        />

        <label htmlFor="explanation-level">Explanation Level</label>
        <select
          id="explanation-level"
          value={explanationLevel}
          onChange={(event) => setExplanationLevel(event.target.value)}
        >
          <option value="basic">Basic</option>
          <option value="technical">Technical</option>
        </select>

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Ask"}
        </button>
      </form>

      {error && <p>{error}</p>}

      {response && (
        <section>
          <h2>Answer</h2>
          <p>{response.answer}</p>

          <h3>Sources</h3>
          <ul>
            {response.sources.map((source) => (
              <li key={source.url}>
                <a href={source.url} target="_blank" rel="noreferrer">
                  {source.title}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}

export default App;
