# FinanceBuddy Roadmap

This roadmap reflects the incremental build order currently being followed.

## Active Branch Focus

Current active branch: `agentic_v1`

Branch objective:
- design and implement a LangGraph-based agent workflow in parallel to the existing RAG path
- keep the current production RAG flow stable and unchanged as the baseline
- add internal-first decision-making before any optional public web lookup
- define explicit agent state, nodes, edges, and runtime trace events
- evaluate the agent path against the baseline before considering any merge into `main`

Branch constraints:
- do not replace the existing default chat path during `agentic_v1`
- do not introduce unconstrained autonomous tool use
- do not let public web lookup bypass trusted internal retrieval
- do not use MLflow as the primary runtime tracing system
- keep source provenance explicit when mixing trusted and public sources

## Completed

- [x] Define initial repository structure
- [x] Initialize backend using uv and pyproject.toml
- [x] Clean backend architecture for routes and schemas
- [x] Implement GET /health
- [x] Implement mock POST /chat
- [x] Initialize frontend with React + TypeScript + Vite
- [x] Connect frontend to backend mock /chat
- [x] Setup Docker Compose for frontend, backend, and database
- [x] Design the initial database schema
- [x] Add the initial persistence layer
- [x] Setup Alembic and apply the first migration
- [x] Persist conversations and messages through repository and service layers
- [x] Add GET /chat/{conversation_id} for conversation history
- [x] Build the document ingestion pipeline baseline
- [x] Add a local ingestion script for trusted PDF sources
- [x] Implement retrieval over persisted chunks
- [x] Add retrieval-side repositories and services
- [x] Integrate retrieval into the chat flow with persisted retrieval events
- [x] Implement grounded answer generation from retrieved evidence
- [x] Connect the frontend to the conversation-aware grounded chat API
- [x] Display supporting sources in the frontend chat UI
- [x] Preserve conversation_id across follow-up turns
- [x] Restore persisted conversation history in the frontend after refresh
- [x] Improve retrieval for multilingual tax queries through query normalization
- [x] Create a first retrieval evaluation dataset and manifest grounded in the Agencia Tributaria corpus
- [x] Build a retrieval-only evaluation runner with MLflow experiment tracking
- [x] Log baseline retrieval runs, per-example results, and failure summaries to MLflow
- [x] Add a backend feedback endpoint with persistence-backed create/update behavior for assistant messages
- [x] Return persisted assistant message ids to the frontend chat flow
- [x] Add frontend thumbs up/down feedback controls for assistant answers

## Next

- [ ] Add optional negative-feedback comments in the frontend and backend flow
- [ ] Add a simple review path for low-rated answers
- [ ] Use real user feedback to identify the highest-value retrieval, prompting, and UX fixes before expanding scope
- [ ] Run systematic retrieval comparisons in MLflow, starting with query normalization on vs off
- [ ] Turn baseline retrieval findings into concrete retriever improvements and regression checks
- [ ] Add structured application logging for chat, retrieval, generation, and ingestion flows
- [ ] Define a minimal observability model for request tracing, latency, retrieval quality, and generation failures
- [ ] Expose operational metrics and health signals for backend and ingestion workflows
- [ ] Add error monitoring and a clear debugging workflow for failed chat requests
- [ ] Add generation evaluation with answer artifacts, latency/cost tracking, and LLM-as-a-judge metrics
- [ ] Design the LangGraph agent architecture for `agentic_v1`, including state, nodes, edges, and policy rules
- [ ] Add a parallel agent execution path without changing the default RAG endpoint behavior
- [ ] Implement internal-first evidence assessment before any optional public web lookup
- [ ] Define and persist runtime trace events for agent node execution and branch decisions
- [ ] Add constrained, user-authorized web lookup as a later node in the agent path
- [ ] Compare the agent path against the baseline RAG path with evaluation artifacts before merge

## Later

- [ ] Preload the sentence-transformer model at backend startup and optionally bake it into the backend image to reduce chat cold-start latency
- [ ] Add a local-first retrieval agent with optional user-authorized lookup over approved public web sources
- [ ] Add source tracing
- [ ] Add a bills and invoices (`facturas`) document-analysis module
- [ ] Expand beyond tax education into broader personal-finance and mortgage workflows

## Guiding Principles

- Keep steps small and testable
- Explain decisions before coding
- Prefer guided implementation so new milestones are learned and built incrementally
- Prefer clear boundaries over premature complexity
- Treat retrieved evidence as the source of truth
- Add observability before expanding scope so new modules are easier to debug and evaluate
- Evaluate retrieval and generation separately before trusting end-to-end RAG metrics
- Evolve from deterministic RAG to agentic behavior only through explicit, reviewable workflow control
- Keep the baseline path intact long enough to compare agent behavior against a stable reference
