# FinanceBuddy

FinanceBuddy is a production-oriented full-stack financial education assistant built incrementally to learn backend architecture, frontend integration, and later a grounded RAG pipeline.

## Project Intent And Data Usage

- This project uses data from public sources.
- The current tax education materials are taken from publicly accessible Agencia Tributaria, CNMV, Banco de España resources.
- FinanceBuddy is a non-profit project built for educational and learning purposes.
- It is intended as an engineering-learning project, not as a commercial product.

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

- The assistant answer is now generated from retrieved evidence and returned with supporting source references.
- The current frontend still needs to be updated to fully use `conversation_id` and conversation history.
- Alembic is the official schema management workflow.
- A reasonable backend optimization for a later step is to preload the sentence-transformer model at application startup and optionally download it during image build, which would trade higher steady backend container memory for lower request latency.
- Another future capability is a local-first retrieval agent with optional user-authorized public web lookup, where FinanceBuddy answers from internal trusted sources first and only searches approved public sources when the user explicitly allows it.

## Roadmap

See [docs/roadmap.md](/d:/FinanceBuddy/docs/roadmap.md).

Useful commands reference: [docs/dev-commands.md](/d:/FinanceBuddy/docs/dev-commands.md).

