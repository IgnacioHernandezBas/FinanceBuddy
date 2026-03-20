# FinanceBuddy

FinanceBuddy is a production-oriented full-stack financial education assistant built incrementally to learn backend architecture, frontend integration, and later a grounded RAG pipeline.

## Current Status

`v0` includes:

- FastAPI backend with `GET /health`
- Mock `POST /chat` endpoint
- React + TypeScript + Vite frontend
- Frontend connected to the backend mock chat endpoint
- CORS enabled for local development

## Repository Structure

```text
FinanceBuddy/
├── backend/
├── frontend/
├── infra/
├── docs/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── Project_codex_prompt.txt
```

## Local Startup

### Backend

From [backend](/d:/FinanceBuddy/backend):

```bash
uv run uvicorn finance_buddy_backend.main:app --reload
```

The backend will be available at `http://127.0.0.1:8000`.

Useful endpoints:

- `GET /health`
- `POST /chat`
- `GET /docs`

### Frontend

From [frontend](/d:/FinanceBuddy/frontend):

```bash
npm run dev
```

The frontend will usually be available at `http://localhost:5173`.

## Current Development Flow

1. Start the backend.
2. Start the frontend.
3. Open the frontend in the browser.
4. Submit a question through the UI.
5. Verify the frontend receives the mock response from the backend.

## Notes

- The current `/chat` endpoint is mocked on purpose.
- The current frontend is an integration-first UI, not the final product design.
- Docker Compose and database setup are planned next, but not part of `v0`.

## Roadmap

See [docs/roadmap.md](/d:/FinanceBuddy/docs/roadmap.md).
