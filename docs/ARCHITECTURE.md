# CycloneGuard System Architecture — Sprint 1

```
                    INTERNET (Public Users & Meteorological Analysts)
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │      FRONTEND APPLICATION     │
                      │     Next.js 16 + React 19     │
                      │   TypeScript + Tailwind CSS   │
                      └───────────────┬───────────────┘
                                      │
                     HTTPS / REST     │ (JWT Bearer Authorization)
                                      ▼
                      ┌───────────────────────────────┐
                      │       BACKEND REST API        │
                      │      FastAPI + Pydantic       │
                      │         Uvicorn ASGI          │
                      └───────┬───────────────┬───────┘
                              │               │
                              ▼               ▼
                      ┌───────────────┐ ┌───────────────────────────┐
                      │  POSTGRESQL   │ │  AI INFERENCE ABSTRACTION │
                      │   DATABASE    │ │ (Future PyTorch / ONNX)   │
                      │  SQLAlchemy   │ │    CycloneAIService       │
                      │  Alembic Migr │ └─────────────┬─────────────┘
                      └───────────────┘               │
                                                      ▼
                                        ┌───────────────────────────┐
                                        │  SATELLITE DATA LAYER     │
                                        │ (Future INSAT / Himawari) │
                                        └───────────────────────────┘
```

---

## 1. High-Level Architecture Overview

CycloneGuard is an AI-powered tropical cyclone intelligence platform designed to ingest multi-source satellite observations, localize storm centers, estimate current intensity (Vmax and MSLP), detect rapid intensification (RI) risk, provide explainable model predictions, and deliver decision support information through dedicated web portals.

In **Sprint 1**, the architectural foundation has been established:
- **Clean Monorepo Separation**: Independent frontend, backend, database migrations, and future ML directories.
- **Stateless RESTful Backend**: FastAPI application with structured Pydantic v2 schemas and centralized exception handling.
- **Dual Portal Routing**: Role-restricted user and administrative portals with distinct layout containers.
- **Strict Scientific Honesty**: Zero fabricated meteorological statistics or fake AI predictions.

---

## 2. Frontend Architecture (Next.js App Router)

- **Framework**: Next.js 16.3+ (React 19, TypeScript)
- **Styling**: Tailwind CSS v4 design system adhering to a meteorology-focused, dark-navy scientific palette (`#090e17`, `#0f1826`, `#1e314b`, with radar grid accents and cyan telemetry highlights).
- **Component Hierarchy**:
  - `components/ui/`: Atomic design tokens (`Button`, `Card`, `Badge`, `Alert`, `Table`, `Modal`, `Loading`, `EmptyState`, `ErrorState`, `Input`).
  - `components/layout/`: `Header`, `Footer`, `UserNav`, `AdminNav`, and `PortalLayout`.
- **State Management & Authentication**:
  - `lib/auth-context.tsx`: React Context providing authenticated user state, JWT token lifecycle management, and role differentiation.
  - `lib/api/client.ts`: Centralized, environment-aware API client that handles bearer headers, network timeouts, and typed API errors without hard-coded localhost assumptions.
- **Route Matrix**:
  - `/`: Public landing page with status banner, hero, planned capabilities, and zero-fake-stats guarantee.
  - `/login` & `/register`: Clean validation forms with user-friendly error banners and automatic role routing.
  - `/user/*`: Protected User Portal (`dashboard`, `cyclones`, `cyclones/[id]`, `history`, `profile`).
  - `/admin/*`: Protected Admin Portal (`dashboard`, `data`, `models`, `predictions`, `alerts`, `users`, `system`).

---

## 3. Backend Architecture (FastAPI)

- **Framework**: FastAPI (Python 3.11) with Uvicorn ASGI server.
- **Directory Layout**:
  - `app/core/`: Configuration via `pydantic-settings`, security primitives (`bcrypt`, `pyjwt`), database engine, custom exceptions, and standardized responses.
  - `app/models/`: SQLAlchemy 2.0 declarative models (`User`, `Cyclone`, `Observation`, `ModelVersion`, `Prediction`, `Alert`).
  - `app/schemas/`: Pydantic models for strict input validation, response serialization, and Swagger doc generation.
  - `app/repositories/`: Data access layer separating raw database queries from business services (`BaseRepository`, `UserRepository`).
  - `app/services/`: Domain business logic (`AuthService`, `UserService`, and future AI service interfaces).
  - `app/api/v1/`: Versioned routing with dependency injection for authentication (`get_current_user`) and role authorization (`require_admin`).
- **Security & Error Handling**:
  - Centralized exception handlers catch all `AppException` and `RequestValidationError` instances, returning uniform JSON payloads:
    ```json
    {
      "success": false,
      "data": null,
      "error": {
        "code": "AUTHENTICATION_FAILED",
        "message": "Invalid email or password"
      }
    }
    ```
  - Global catch-all prevents internal tracebacks, paths, or secrets from leaking to clients.

---

## 4. Database Architecture & Migrations

- **RDBMS**: PostgreSQL 16+ (with local SQLite fallback for isolated zero-dependency dev/test execution).
- **Driver**: `psycopg2-binary` for PostgreSQL, built-in `sqlite3` for local fallback.
- **Migration Framework**: Alembic 1.20+ configured via `database/alembic.ini` and `database/migrations/env.py`.
- **Sprint 1 Schema State**:
  - `users`: Active table managing user identities, Bcrypt password hashes, and `USER` / `ADMIN` roles.
  - Future tables (`cyclones`, `observations`, `model_versions`, `predictions`, `alerts`) are fully defined in SQLAlchemy models and generated into the initial migration script (`database/migrations/versions/`).

---

## 5. Authentication & Role-Based Authorization Flow

1. **Registration**: User submits name, email, and password (minimum 8 chars). Passwords are hashed with Bcrypt (salt rounds: 12) before database insertion.
2. **Login**: User submits credentials. Backend verifies hash, issues a signed JWT containing subject ID, role, issue time, and expiration (24h default).
3. **Session Persistence**: Frontend stores JWT in secure client-side storage, transmitting it via the `Authorization: Bearer <token>` header.
4. **Backend Role Enforcement**:
   - `get_current_user`: Validates JWT cryptographic signature, expiry, and retrieves the active user from the database.
   - `require_admin`: Verifies `user.role == UserRole.ADMIN`. If unauthorized, rejects the request with HTTP 403 `FORBIDDEN_ACCESS`.
5. **Frontend Role Guarding**:
   - `PortalLayout` checks role before rendering admin views; unauthorized normal users are shown an explicit access denial screen and redirected to the User Portal.

---

## 6. Future AI Integration Architecture (Phase 21)

To ensure that upcoming PyTorch and ONNX deep learning models can be introduced without disrupting business logic or rewriting frontend components, the platform introduces a decoupled interface in `backend/app/services/ai/interfaces.py`:

```python
class CycloneAIServiceInterface(ABC):
    @abstractmethod
    def predict_cyclone(self, observation_metadata: Dict[str, Any]) -> Dict[str, Any]: ...
    
    @abstractmethod
    def estimate_intensity(self, observation_id: str, satellite_channels: List[str]) -> Dict[str, Any]: ...
    
    @abstractmethod
    def predict_ri_risk(self, cyclone_id: str, history_window_hours: int = 24) -> Dict[str, Any]: ...
    
    @abstractmethod
    def predict_trend(self, cyclone_id: str, horizon_hours: int = 48) -> Dict[str, Any]: ...
    
    @abstractmethod
    def generate_explanation(self, prediction_id: str) -> Dict[str, Any]: ...
```

In Sprint 1, `PlaceholderAIService` implements this interface, strictly refusing to invent synthetic predictions and returning explicit "Model not deployed" statuses.

---

## 7. Deployment Architecture (Phase 22)

- **Containerization**:
  - `backend/Dockerfile`: Multi-stage Python 3.11 slim container with non-root security.
  - `frontend/Dockerfile`: Multi-stage Node.js 20 Alpine container with standalone build optimization.
  - `docker-compose.yml`: Local multi-container development orchestration linking PostgreSQL, FastAPI, and Next.js on an isolated bridge network (`cycloneguard-net`).
- **Configuration Decoupling**:
  - No localhost URLs are hard-coded in source files.
  - Frontend dynamically reads `NEXT_PUBLIC_API_URL`.
  - Backend dynamically reads `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, and `ENVIRONMENT`.
  - Production CORS disallows wildcard `*` by default.
