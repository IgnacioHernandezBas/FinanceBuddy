# Repository Layer

This package should contain data access logic only.

Use repositories to keep query logic out of:

- API routes
- Pydantic schemas
- service orchestration

## Recommended Modules

- `source_repository.py`
- `conversation_repository.py`
- `retrieval_repository.py`
- `feedback_repository.py`

## Rule of Thumb

If the code is primarily about:

- selecting rows
- inserting rows
- updating rows
- joining related models

it belongs in a repository, not in a route.

## Why This Matters

Repositories make the application easier to:

- test
- refactor
- explain in interviews
- evolve from mock logic to real persistence

The service layer should call repositories to perform persistence work, while routes should call services.
