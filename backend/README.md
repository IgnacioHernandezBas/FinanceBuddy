# Backend

Run the API from the `backend` directory:

```powershell
cd D:\FinanceBuddy\backend
uv run uvicorn finance_buddy_backend.main:app --reload
```

Why this matters:

- The backend uses a `src` layout, so the package must be installed from the `backend` project directory.
- With the packaging metadata in `pyproject.toml`, `uv run` can resolve `finance_buddy_backend.main:app` correctly.

If your local environment is already created and you want a direct fallback in PowerShell, this also works:

```powershell
cd D:\FinanceBuddy\backend
$env:PYTHONPATH = "src"
.\.venv\Scripts\uvicorn.exe finance_buddy_backend.main:app --reload
```

## Docker Notes

The backend container bind-mounts [src](src) into `/app/src`, so normal backend code changes reload automatically inside the container.

After changing backend dependencies in [pyproject.toml](pyproject.toml) or [uv.lock](uv.lock), rebuild the backend container:

```powershell
docker compose up -d --build backend
docker compose logs backend
```

The backend Docker environment must use the psycopg v3 URL form:

```text
postgresql+psycopg://finance_buddy:finance_buddy@db:5432/finance_buddy
```

Available endpoints:

- `GET /health`
- `POST /chat`
- `GET /chat/{conversation_id}`
- `GET /docs`

