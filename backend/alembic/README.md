# Alembic Migration Strategy

This project uses Alembic as the official database schema management tool.

## Why Alembic Instead of `Base.metadata.create_all()`

`Base.metadata.create_all()` is useful for quick local validation, but it is not a complete schema evolution strategy.

Alembic is the better choice for this project because it provides:

- versioned database changes
- reviewable migration files
- reproducible schema updates across environments
- safer long-term schema evolution as the application grows

FinanceBuddy is intended to be production-oriented. The database schema will evolve as we add ingestion, retrieval, vector search, tracing, and feedback workflows. That makes migration history an important part of the architecture.

## Role of SQLAlchemy Models

The SQLAlchemy ORM models define the desired schema in Python.

Alembic uses those models and their metadata to:

- detect schema changes
- generate migration scripts
- apply upgrades and downgrades in a controlled way

## Practical Rule

For this project:

- Alembic is the source of truth for schema changes
- `create_all()` may be used only as a temporary local validation tool
- real schema evolution should happen through migrations

## Why This Matters

As the schema changes over time, unmanaged updates increase the risk of:

- schema drift between environments
- missing tables or columns
- unsafe manual changes
- accidental data loss during ad hoc modifications

Alembic does not magically eliminate all migration risk, but it gives us an explicit and reviewable process, which is much safer than unmanaged schema changes.
