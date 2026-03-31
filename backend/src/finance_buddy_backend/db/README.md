# FinanceBuddy Database Structure

This package contains the persistence foundation for the backend.

The goal is to keep the database layer separate from:

- API routes
- Pydantic request/response schemas
- application services

That separation matters because the database is a core part of the RAG system. It stores trusted sources, chunk-level retrieval data, conversation history, and traceability records that later let us explain where an answer came from.

## Current Step

Step 9: design the database schema.

This README documents the structure we want before implementing the persistence layer in Step 10.

## Recommended Package Layout

```text
finance_buddy_backend/
├── api/
│   └── routes/
├── core/
├── db/
│   ├── README.md
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── source.py
│       ├── conversation.py
│       ├── retrieval.py
│       └── feedback.py
├── repositories/
│   ├── source_repository.py
│   ├── conversation_repository.py
│   ├── retrieval_repository.py
│   └── feedback_repository.py
├── schemas/
└── services/
```

## Responsibility of Each Part

### `db/base.py`

This file should define the shared ORM base class.

Why it exists:

- gives all ORM models one common base
- keeps model definitions consistent
- provides a single import point for metadata later

Typical responsibility:

- create the SQLAlchemy declarative base

### `db/session.py`

This file should manage the database engine and sessions.

Why it exists:

- centralizes database connection setup
- prevents connection logic from being repeated in routes or repositories
- becomes the place to configure PostgreSQL and later pgvector support

Typical responsibility:

- create the engine
- create the session factory
- expose a dependency/helper for getting a session

### `db/models/`

This folder should contain ORM models only.

Do not put route logic, validation logic, or business workflows here.

Recommended split:

- `source.py`
  - `Source`
  - `DocumentChunk`
- `conversation.py`
  - `Conversation`
  - `Message`
- `retrieval.py`
  - `RetrievalEvent`
- `feedback.py`
  - `MessageFeedback`

Why split by domain instead of one large file:

- easier to read and teach
- clearer ownership of related entities
- avoids a giant `models.py` as the project grows

## Why These Tables Belong Together

### `Source` and `DocumentChunk`

These tables support ingestion and retrieval.

- `Source` stores the parent trusted document
- `DocumentChunk` stores chunked fragments used during retrieval

This design preserves traceability:

- chunks can always be linked back to the original source
- retrieval can operate on small chunks without losing document context

### `Conversation` and `Message`

These tables support the chat product itself.

- `Conversation` groups a chat session
- `Message` stores the ordered transcript

This separation matters because one conversation contains many messages, and later the assistant will need that history to generate better grounded answers.

### `RetrievalEvent`

This table supports observability and answer auditing.

It should record which chunks were retrieved for a user message, including ranking and similarity score.

Without this table, you can answer a user question, but you cannot reliably inspect why the system answered the way it did.

### `MessageFeedback`

This table supports evaluation and product learning.

It should attach user feedback to assistant messages, not to the whole conversation.

That gives you much better signal when you later want to analyze:

- weak answers
- poor retrieval quality
- gaps in your source data

## Separation of Concerns

Use these rules consistently:

- `api/routes/` handles HTTP
- `schemas/` handles request and response validation
- `db/models/` defines tables and relationships
- `repositories/` handles database queries
- `services/` orchestrates application behavior

Routes should not know how SQL queries work.

Repositories should not know how HTTP works.

Services should coordinate workflows using repositories rather than embedding SQL directly.

## Recommended Flow Later

When the chat endpoint becomes real, the flow should look like this:

1. The route receives the request.
2. A service coordinates the chat workflow.
3. A repository stores the user message.
4. Retrieval logic finds relevant chunks.
5. Retrieval results are stored as `RetrievalEvent` records.
6. The grounded assistant answer is stored as a new `Message`.
7. Feedback can later be stored on that assistant message.

This keeps the architecture modular and interview-ready.

## What We Are Intentionally Not Adding Yet

To keep the MVP realistic but not over-engineered, we are not adding:

- a `users` table
- prompt versioning tables
- retrieval run parent tables
- multiple embedding-version tables
- advanced evaluation experiment tables

Those can be introduced later when there is a concrete need.

## Practical Notes for Step 10

When implementing the persistence layer, build in this order:

1. `db/base.py`
2. `db/session.py`
3. ORM models in `db/models/`
4. repository modules
5. service integration

That order keeps dependencies clean and reduces rework.

## Short Interview Explanation

The database structure is organized so that the persistence layer supports grounded generation rather than acting as generic storage. Source and chunk models support retrieval, conversation and message models support the chat product, and retrieval plus feedback records support traceability, debugging, and future evaluation workflows.
