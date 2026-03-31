FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv \
    && uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "finance_buddy_backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
