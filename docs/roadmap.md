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

### Primary track: complete `agentic_v1`

- [x] Design the LangGraph agent architecture for `agentic_v1`, including state, nodes, edges, and policy rules
- [x] Add a parallel agent execution path without changing the default RAG endpoint behavior
- [x] Implement internal-first evidence assessment before any optional public web lookup
- [x] Add constrained, user-authorized web lookup as a later node in the agent path
- [x] Implement the remaining V1 graph nodes: `check_web_search_policy`, `web_search`, `generate_mixed_response`, and `validate_answer_policy`
- [x] Define and persist runtime trace events for agent node execution and branch decisions
- [ ] Formalize the FinanceBuddy agent capability model so internal retrieval, web search, and document workflows remain explicit graph-controlled tools rather than unconstrained LLM-selected tools
- [ ] Decide which agent capabilities are deterministic, which are policy-gated, and which later decisions may be model-assisted
- [ ] Compare the agent path against the baseline RAG path with evaluation artifacts before merge

### Secondary track: improve the baseline product loop

- [ ] Add optional negative-feedback comments in the frontend and backend flow
- [ ] Add a simple review path for low-rated answers
- [ ] Use real user feedback to identify the highest-value retrieval, prompting, and UX fixes before expanding scope
- [ ] Run systematic retrieval comparisons in MLflow, starting with query normalization on vs off
- [ ] Turn baseline retrieval findings into concrete retriever improvements and regression checks
- [ ] Add generation evaluation with answer artifacts, latency/cost tracking, and LLM-as-a-judge metrics

### Supporting track: operational readiness

- [ ] Add structured application logging for chat, retrieval, generation, and ingestion flows
- [ ] Define a minimal observability model for request tracing, latency, retrieval quality, and generation failures
- [ ] Expose operational metrics and health signals for backend and ingestion workflows
- [ ] Add error monitoring and a clear debugging workflow for failed chat requests

## Later

- [ ] Preload the sentence-transformer model at backend startup and optionally bake it into the backend image to reduce chat cold-start latency
- [ ] Add a local-first retrieval agent with optional user-authorized lookup over approved public web sources
- [ ] Add source tracing
- [ ] Add a bills and invoices (`facturas`) document-analysis module
- [ ] Expand beyond tax education into broader personal-finance and mortgage workflows

## Agentic V1 Progress Snapshot

Current implemented `agentic_v1` slice:

- `/agent/chat` runs a separate LangGraph-backed path while `/chat` remains the baseline RAG path
- `AgentState` is defined and initialized explicitly
- implemented nodes: `load_request`, `classify_request`, `internal_retrieve`, `assess_internal_evidence`, `check_web_search_policy`, `web_search`, `generate_internal_only_response`, `generate_mixed_response`, `validate_answer_policy`
- internal evidence assessment now uses retrieval similarity thresholds instead of the old "any chunk means sufficient" rule
- approved-domain LangSearch fallback is available when the request authorizes public web lookup
- the frontend can switch between baseline RAG and Agent V1 without changing history or feedback persistence
- runtime `trace_events` are persisted in the database and still returned to the frontend for debugging
- the frontend exposes a developer debug view for trace events, internal chunk scores, and raw web-search results

Still missing before V1 is complete:

- evaluation of agent behavior against the baseline path

## Agentic V1 Status

`agentic_v1` is now functionally successful.

That means the branch demonstrates the intended product behavior:

- a separate graph-controlled agent path
- internal-first retrieval
- policy-gated public web fallback
- mixed-source answer generation with explicit provenance
- persisted runtime traces for later inspection

The remaining work is closure work, not core capability creation:

- baseline-vs-agent evaluation
- capability/policy cleanup and documentation tightening
- production hardening around observability and debugging workflows

## Recommended Next Step

The next highest-value step is to evaluate `agentic_v1` against the baseline path and turn the result into merge criteria.

Recommended implementation order inside that step:

1. Define a small comparison dataset that mixes internal-answerable questions with questions expected to trigger approved web fallback.
2. Capture baseline RAG outputs and Agent V1 outputs as comparable artifacts.
3. Review failure modes across retrieval quality, policy gating, and mixed-source answer quality.
4. Turn the comparison into explicit merge criteria for the branch.

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
