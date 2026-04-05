# FinanceBuddy Roadmap

This roadmap reflects the incremental build order currently being followed.

## Completed

- [x] Define initial repository structure
- [x] Initialize backend using `uv` and `pyproject.toml`
- [x] Clean backend architecture for routes and schemas
- [x] Implement `GET /health`
- [x] Implement mock `POST /chat`
- [x] Initialize frontend with React + TypeScript + Vite
- [x] Connect frontend to backend mock `/chat`
- [x] Setup Docker Compose for frontend, backend, and database
- [x] Design the initial database schema
- [x] Add the initial persistence layer
- [x] Setup Alembic and apply the first migration
- [x] Persist conversations and messages through repository and service layers
- [x] Add `GET /chat/{conversation_id}` for conversation history
- [x] Build the document ingestion pipeline baseline
- [x] Add a local ingestion script for trusted PDF sources
- [x] Implement retrieval over persisted chunks
- [x] Add retrieval-side repositories and services
- [x] Integrate retrieval into the chat flow with persisted retrieval events
- [x] Implement grounded answer generation from retrieved evidence
- [x] Connect the frontend to the conversation-aware grounded chat API
- [x] Display supporting sources in the frontend chat UI
- [x] Preserve `conversation_id` across follow-up turns
- [x] Restore persisted conversation history in the frontend after refresh
- [x] Improve retrieval for multilingual tax queries through query normalization

## Next

- [ ] Add structured application logging for chat, retrieval, generation, and ingestion flows
- [ ] Define a minimal observability model for request tracing, latency, retrieval quality, and generation failures
- [ ] Expose operational metrics and health signals for backend and ingestion workflows
- [ ] Add error monitoring and a clear debugging workflow for failed chat requests

## Later

- [ ] Preload the sentence-transformer model at backend startup and optionally bake it into the backend image to reduce chat cold-start latency
- [ ] Add a local-first retrieval agent with optional user-authorized lookup over approved public web sources
- [ ] Add source tracing
- [ ] Add evaluation and feedback flows
- [ ] Add a bills and invoices (`facturas`) document-analysis module
- [ ] Expand beyond tax education into broader personal-finance and mortgage workflows

## Guiding Principles

- Keep steps small and testable
- Explain decisions before coding
- Prefer clear boundaries over premature complexity
- Treat retrieved evidence as the source of truth
- Add observability before expanding scope so new modules are easier to debug and evaluate
