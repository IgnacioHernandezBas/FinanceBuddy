# FinanceBuddy

FinanceBuddy is a production-oriented full-stack financial education assistant built incrementally to learn backend architecture, frontend integration, and later a grounded RAG pipeline.

## Current Status

Current backend progress includes:

- FastAPI backend with `GET /health`
- Persistence-backed `POST /chat`
- `GET /chat/{conversation_id}` for conversation history
- PostgreSQL schema managed with Alembic
- SQLAlchemy models, repositories, and chat service layer
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

### 3. Run the backend

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

### 4. Run the frontend

From [frontend](/d:/FinanceBuddy/frontend):

```powershell
cd D:\FinanceBuddy\frontend
npm install
npm run dev
```

The frontend will usually be available at `http://localhost:5173`.

### 5. Ingest trusted source documents

The ingestion script requires the PostgreSQL container to be running. The backend API does not need to be running for this script.

From [backend](/d:/FinanceBuddy/backend):

```powershell
cd D:\FinanceBuddy\backend
uv run python scripts/ingest_sources.py
```

This loads trusted PDF files from the configured data directory, normalizes and chunks them, and stores sources plus document chunks in the database.

## Current Development Flow

1. Start Docker Desktop and bring up the containers.
2. Run the backend from [backend](/d:/FinanceBuddy/backend).
3. Run the frontend from [frontend](/d:/FinanceBuddy/frontend).
4. Use `POST /chat` to create or continue a conversation.
5. Use `GET /chat/{conversation_id}` to inspect persisted message history.
6. Run the ingestion script when you want to load trusted PDF sources into PostgreSQL.

## Notes

- The assistant response content is still mock text, but conversations and messages are persisted.
- The current frontend still needs to be updated to fully use `conversation_id` and conversation history.
- Alembic is the official schema management workflow.
- The next major backend milestone is the ingestion pipeline for trusted sources and chunks.

## Roadmap

See [docs/roadmap.md](/d:/FinanceBuddy/docs/roadmap.md).

Useful commands reference: [docs/dev-commands.md](/d:/FinanceBuddy/docs/dev-commands.md).
