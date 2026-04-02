# FinanceBuddy

FinanceBuddy is a production-oriented full-stack financial education assistant built incrementally to learn backend architecture, frontend integration, and later a grounded RAG pipeline.

## Current Status

Current backend progress includes:

- FastAPI backend with `GET /health`
- Persistence-backed `POST /chat`
- `GET /chat/{conversation_id}` for conversation history
- Retrieval-backed `POST /chat` with semantic chunk search and real source references
- PostgreSQL schema managed with Alembic
- SQLAlchemy models, repositories, and service-layer orchestration
- React + TypeScript + Vite frontend scaffold
- Docker Compose setup for frontend, backend, and PostgreSQL with pgvector

## Repository Structure

```text
FinanceBuddy/
|- backend/
|- frontend/
|- infra/
|- docs/
|- .env.example
|- .gitignore
|- docker-compose.yml
`- Project_codex_prompt.txt
```

## Local Startup

### 1. Prerequisites

Make sure you have installed:

- Docker Desktop
- Python 3.12
- `uv`
- Node.js

### 2. Start infrastructure

Docker Desktop must be running before starting the project containers.

From the repository root:

```powershell
docker compose up -d
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000`
- PostgreSQL + pgvector: `localhost:5432`

### 3. Docker development notes

The backend container bind-mounts [backend/src](/d:/FinanceBuddy/backend/src) into `/app/src`, so ordinary backend code changes reload automatically inside the container.

After changing backend dependencies in [backend/pyproject.toml](/d:/FinanceBuddy/backend/pyproject.toml) or [backend/uv.lock](/d:/FinanceBuddy/backend/uv.lock), rebuild the backend image:

```powershell
docker compose up -d --build backend
docker compose logs backend
```

The backend container must use a psycopg v3 connection URL:

```text
postgresql+psycopg://finance_buddy:finance_buddy@db:5432/finance_buddy
```

### 4. Run the backend locally

From [backend](/d:/FinanceBuddy/backend):

```powershell
cd D:\FinanceBuddy\backend
uv run uvicorn finance_buddy_backend.main:app --reload
```

The backend will be available at `http://127.0.0.1:8000`.

Useful endpoints:

- `GET /health`
- `POST /chat`
- `GET /chat/{conversation_id}`
- `GET /docs`

Running the backend locally is optional if the backend container is already healthy. It is still useful for faster debugging and script-heavy development.

### 5. Run the frontend

From [frontend](/d:/FinanceBuddy/frontend):

```powershell
cd D:\FinanceBuddy\frontend
npm install
npm run dev
```

The frontend will usually be available at `http://localhost:5173`.

### 6. Ingest trusted source documents

The ingestion script requires the PostgreSQL container to be running. The backend API does not need to be running for this script.

From [backend](/d:/FinanceBuddy/backend):

```powershell
cd D:\FinanceBuddy\backend
uv run python scripts/ingest_sources.py
```

This loads trusted PDF files from the configured data directory, normalizes and chunks them, and stores sources plus document chunks in the database.

## Current Development Flow

1. Start Docker Desktop and bring up the containers.
2. Rebuild the backend container after dependency changes.
3. Run the backend locally only when you want a faster local debug loop.
4. Run the frontend from [frontend](/d:/FinanceBuddy/frontend).
5. Use `POST /chat` to create or continue a conversation.
6. Use `GET /chat/{conversation_id}` to inspect persisted message history.
7. Run the ingestion script when you want to load trusted PDF sources into PostgreSQL.

## Notes

- The assistant answer is still mock text, but retrieval is now real and source-backed.
- The current frontend still needs to be updated to fully use `conversation_id` and conversation history.
- Alembic is the official schema management workflow.
- The next major backend milestone is grounded answer generation over retrieved evidence.

## Roadmap

See [docs/roadmap.md](/d:/FinanceBuddy/docs/roadmap.md).

Useful commands reference: [docs/dev-commands.md](/d:/FinanceBuddy/docs/dev-commands.md).
