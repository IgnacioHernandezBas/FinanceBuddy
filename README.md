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

### Backend

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

### Docker Compose

From the repository root:

```powershell
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000`
- PostgreSQL + pgvector: `localhost:5432`

### Frontend

From [frontend](/d:/FinanceBuddy/frontend):

```bash
npm run dev
```

The frontend will usually be available at `http://localhost:5173`.

## Current Development Flow

1. Start the backend.
2. Start PostgreSQL, either with Docker Compose or the standalone DB container.
3. Use `POST /chat` to create or continue a conversation.
4. Use `GET /chat/{conversation_id}` to inspect persisted message history.
5. Start the frontend separately while the frontend integration catches up with the new conversation-aware API.

## Notes

- The assistant response content is still mock text, but conversations and messages are persisted.
- The current frontend still needs to be updated to fully use `conversation_id` and conversation history.
- Alembic is the official schema management workflow.
- The next major backend milestone is the ingestion pipeline for trusted sources and chunks.

## Roadmap

See [docs/roadmap.md](/d:/FinanceBuddy/docs/roadmap.md).
