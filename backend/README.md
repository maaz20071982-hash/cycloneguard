# CycloneGuard Backend (FastAPI)

FastAPI REST application providing authentication, role authorization, database ORM, and scientific placeholder interfaces for the CycloneGuard platform.

## Features
- **FastAPI** with async architecture and strict Pydantic v2 schemas.
- **SQLAlchemy 2.0 ORM** with Alembic migrations.
- **PostgreSQL / SQLite support** (zero-config local SQLite fallback for dev/testing, PostgreSQL for production).
- **JWT Authentication** (Bcrypt password hashing, access token issuance, bearer token authentication).
- **Role-Based Authorization** (`USER` and `ADMIN` role enforcement with `require_admin` dependency).
- **Standardized Error Responses** consistent across 4xx and 5xx exceptions without leaking stack traces or internal secrets.
- **Scientific AI Integration Points** (`app/services/ai/interfaces.py`) decoupling ML models from business logic.
- **No Fake Data Guarantee**: Explicit empty/unconnected states throughout all endpoints.

## Local Execution
From project root:
```bash
# Run backend with uvicorn
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests
```bash
pytest backend/tests -v
```

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
