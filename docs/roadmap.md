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

## Next

- [ ] Connect the frontend to the new conversation-aware chat API
- [ ] Implement grounded answer generation from retrieved evidence
- [ ] Decide the first MVP generation strategy and prompt structure

## Later

- [ ] Add source tracing
- [ ] Add evaluation and feedback flows

## Guiding Principles

- Keep steps small and testable
- Explain decisions before coding
- Prefer clear boundaries over premature complexity
- Treat retrieved evidence as the source of truth
