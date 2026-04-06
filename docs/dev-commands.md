# Development Commands

This file collects the most useful local development and inspection commands for FinanceBuddy.

## Infrastructure

Start the Docker services from the project root:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker compose ps
```

Stop the containers:

```powershell
docker compose down
```

## Backend

Run the FastAPI backend from [backend](../backend):

```powershell
cd D:\FinanceBuddy\backend
uv run uvicorn finance_buddy_backend.main:app --reload
```

## Frontend

Run the Vite frontend from [frontend](../frontend):

```powershell
cd D:\FinanceBuddy\frontend
npm install
npm run dev
```

## Ingestion

Run the ingestion script from [backend](../backend):

```powershell
cd D:\FinanceBuddy\backend
uv run python scripts/ingest_sources.py
```

The PostgreSQL container must be running before ingestion.

## Database Inspection

Open a shell in the PostgreSQL container:

```powershell
docker compose exec db bash
```

Connect to PostgreSQL with `psql`:

```bash
psql -U finance_buddy -d finance_buddy
```

List tables:

```sql
\dt
```

Show the schema for `sources`:

```sql
\d sources
```

Inspect stored sources:

```sql
SELECT id, title, ingestion_status FROM sources;
```

Inspect stored chunks:

```sql
SELECT id, source_id, chunk_index FROM document_chunks LIMIT 20;
```

Exit `psql`:

```sql
\q
```

Run a one-off table listing without entering the container shell:

```powershell
docker compose exec db psql -U finance_buddy -d finance_buddy -c "\dt"
```

