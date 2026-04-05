# Service Layer

This package contains application orchestration logic.

Services sit between:

- API routes
- repositories
- external model providers
- ingestion processors

## Responsibility

A service should coordinate a workflow such as:

- ingesting a document
- retrieving relevant chunks
- generating a grounded answer
- restoring conversation history with source context

Services should not contain raw SQL or direct request/response routing concerns.

## Current Services

- `chat_service.py`
  Orchestrates the chat flow. It creates or continues conversations, stores user and assistant messages, triggers retrieval, stores retrieval events, calls grounded generation, and returns source-aware chat responses and conversation history.

- `embedding_service.py`
  Wraps the sentence-transformer model used to generate embeddings for both document chunks and user queries.

- `retrieval_service.py`
  Prepares the user query for retrieval, generates the query embedding, and delegates similarity search to the retrieval repository.

- `query_normalization_service.py`
  Expands multilingual and tax-domain queries into retrieval-friendly Spanish phrasing. This is the current fix for mixed-language queries such as `What is IRPF tax` against a Spanish corpus.

- `generation_service.py`
  Builds the grounded generation prompt and calls Gemini to produce an answer based only on retrieved evidence.

- `ingestion_service.py`
  Coordinates PDF ingestion: load file text, normalize it, chunk it, embed the chunks, persist the source and chunks, and track ingestion status.

## How They Compose

The current chat path is:

1. Route calls `ChatService`.
2. `ChatService` stores the user message.
3. `RetrievalService` normalizes the query and retrieves relevant chunks.
4. `ChatService` stores retrieval events for traceability.
5. `GenerationService` produces a grounded answer from the retrieved chunks.
6. `ChatService` stores the assistant answer and returns source metadata to the frontend.

The current ingestion path is:

1. `IngestionService` loads a PDF.
2. Text is normalized and chunked.
3. `EmbeddingService` generates chunk embeddings.
4. Source and chunks are stored through the source repository.

## Rule Of Thumb

If the code is primarily about:

- coordinating several components
- enforcing application flow
- calling repositories and model providers in sequence
- translating business logic into a response shape

it belongs in a service.

If the code is primarily about selecting, inserting, updating, or joining database rows, it belongs in a repository.
