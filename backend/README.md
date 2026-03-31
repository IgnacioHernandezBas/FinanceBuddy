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

Available endpoints:

- `GET /health`
- `POST /chat`
- `GET /docs`
