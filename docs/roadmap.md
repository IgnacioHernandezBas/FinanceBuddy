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

## Next

- [ ] Setup Docker Compose for frontend, backend, and database
- [ ] Design the initial database schema
- [ ] Add the persistence layer

## Later

- [ ] Build the document ingestion pipeline
- [ ] Implement retrieval
- [ ] Implement grounded generation
- [ ] Add source tracing
- [ ] Add evaluation and feedback flows

## Guiding Principles

- Keep steps small and testable
- Explain decisions before coding
- Prefer clear boundaries over premature complexity
- Treat retrieved evidence as the source of truth
