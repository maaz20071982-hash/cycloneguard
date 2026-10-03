# CycloneGuard Admin Portal Specification & Architecture

> **Document Version**: 3.0.0  
> **Status**: Approved Operational Baseline (Sprint 3)  
> **Classification**: Operations & Engineering Console  
> **Design Philosophy**: Meteorological Operations Console — Operational, Precise, Scientific, Information-Dense, Trustworthy.

---

## 1. Overview & Operational Principles

The **CycloneGuard Admin Portal** serves as the central operations console for systems monitoring, data feed health, neural model registry management, prediction audit trails, risk advisory triggers, and user identity governance.

### Core Architecture Standards:
1. **Scientific Honesty & Verification**: No fabricated operational data. When satellite downlinks or neural inference models are not yet deployed, the console displays truthful states (`Not connected`, `Not deployed`, `No data`, `—`). Zero synthetic model accuracy, synthetic cyclone counts, or fake uptime percentages are permitted.
2. **Design System Integrity**: Reuses the locked CycloneGuard Design System (Sprint 1.5). Light-first off-white background (`#f8f9fa`), deep ocean teal (`#0f5b6c`), controlled status accents, crisp borders (`#e2e6e9`), and tabular telemetry numerals. Zero neon glows, generic purple SaaS gradients, or excessive card rounding.
3. **Defense-in-Depth Authorization**: Route gating is enforced at both frontend layout layer (`AdminLayout`) and backend API dependency layer (`require_admin()`). Standard analysts (`USER`) are strictly barred from administrative endpoints.

---

## 2. Admin Routes Architecture

| Route | View Component | Purpose | Access Control |
| :--- | :--- | :--- | :--- |
| `/admin` | `AdminIndexRedirect` | Clean programmatic redirect to `/admin/dashboard` | `ADMIN` Role Required |
| `/admin/dashboard` | `AdminDashboardPage` | Operational system overview, component health, live audit trail | `ADMIN` Role Required |
| `/admin/data` | `AdminDataSourcesPage` | Observational data stream registry (IMD, INSAT, HURSAT, etc.) | `ADMIN` Role Required |
| `/admin/models` | `AdminModelsPage` | Neural architecture registry (PyTorch detection, intensity, RI) | `ADMIN` Role Required |
| `/admin/predictions` | `AdminPredictionsPage` | Inference stream monitoring with prepared tabular schema | `ADMIN` Role Required |
| `/admin/alerts` | `AdminAlertsPage` | AI-assisted monitoring advisories with statutory disclaimer | `ADMIN` Role Required |
| `/admin/users` | `AdminUsersPage` | Personnel directory, role modification, account activation | `ADMIN` Role Required |
| `/admin/system` | `AdminSystemPage` | Runtime telemetry, database migration status, audit trail | `ADMIN` Role Required |

---

## 3. Role-Based Access Control (RBAC) & Authorization Model

CycloneGuard maintains strict role segregation between operational analysts and platform administrators:

```
[Incoming Request]
        │
        ▼
   Bearer JWT Token Present?
  ┌─────┴─────┐
  │ YES       │ NO ──> HTTP 401 (AUTHENTICATION_FAILED)
  ▼           ▼
User Exists & Active?
  ┌─────┴─────┐
  │ YES       │ NO ──> HTTP 401 (Disabled / Non-existent)
  ▼           ▼
User Role == ADMIN?
  ┌─────┴─────┐
  │ YES       │ NO ──> HTTP 403 (FORBIDDEN_ACCESS)
  ▼           ▼
Endpoint Execution
```

### Safety Rules Enforced by Backend (`UserService`):
- **Self-Lockout Prevention**: An authenticated administrator cannot revoke their own `ADMIN` role (`HTTP 400 Bad Request`).
- **Self-Deactivation Prevention**: An authenticated administrator cannot deactivate or suspend their own account (`HTTP 400 Bad Request`).
- **Privilege Segregation**: Standard `USER` accounts cannot access or mutate roles, statuses, or telemetry (`HTTP 403 Forbidden`).

---

## 4. Admin API Specification (`/api/v1/admin/*`)

All administrative endpoints are grouped under `/api/v1/admin/` and require the `require_admin()` dependency:

| Method | Endpoint | Description | Response Structure |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/dashboard` | Aggregated system overview, health probes, and recent activity | `AdminDashboardResponse` |
| `GET` | `/api/v1/admin/data-sources` | Registry of satellite downlinks and synoptic data streams | `AdminDataSourcesResponse` |
| `GET` | `/api/v1/admin/models` | Deep learning model checkpoint registry and specs | `AdminModelsResponse` |
| `GET` | `/api/v1/admin/predictions` | Inference stream queue and batch prediction monitor | `AdminPredictionsResponse` |
| `GET` | `/api/v1/admin/alerts` | AI-assisted advisory threshold triggers and rules | `AdminAlertsResponse` |
| `GET` | `/api/v1/admin/users` | Paginated personnel directory with role & status filters | `AdminUsersResponse` |
| `GET` | `/api/v1/admin/users/{id}` | Inspect individual user account details | `UserResponse` |
| `PATCH`| `/api/v1/admin/users/{id}` | Modify user name or promote/demote role | `UserResponse` |
| `PATCH`| `/api/v1/admin/users/{id}/status` | Activate or deactivate user platform access | `UserResponse` |
| `GET` | `/api/v1/admin/audit-logs` | Immutable audit trail queryable by action/resource | `AdminAuditLogsResponse` |
| `GET` | `/api/v1/admin/system` | Detailed runtime configuration and telemetry | `AdminSystemTelemetry` |

---

## 5. Audit Logging Architecture

Administrative and security events are logged to the database table `audit_logs` using the `AuditService`:

### Schema (`audit_logs`):
- `id` (VARCHAR(36), PK): UUID identifier
- `user_id` (VARCHAR(36), FK): Initiating user ID (nullable for system actions)
- `action` (VARCHAR(100)): Action code (e.g. `ADMIN_LOGIN`, `ADMIN_LOGOUT`, `USER_ROLE_CHANGED`, `USER_ACTIVATED`, `USER_DEACTIVATED`, `USER_UPDATED`)
- `resource_type` (VARCHAR(50)): Target resource (`USER`, `SESSION`, `SYSTEM`, `MODEL`, `ALERT`)
- `resource_id` (VARCHAR(100)): Target resource identifier
- `timestamp` (DATETIME): UTC timestamp
- `metadata_json` (JSON): Structured event metadata with automatic password and secret sanitization

---

## 6. System Health & Probes

Health checks probe each operational component truthfully:

```json
{
  "status": "ok",
  "timestamp": "2026-09-26T07:41:40.123456+00:00",
  "application": "ok",
  "database": "connected",
  "ai_engine": "not_deployed",
  "data_pipeline": "not_connected",
  "version": "0.1.0-sprint1",
  "environment": "development"
}
```

Components not yet operational return truthful states (`not_deployed`, `not_connected`) rather than false positives.

---

## 7. Future AI Model Registry & Integration Roadmap

In Sprint 4 and subsequent sprints, the following architectures will transition from `Not deployed` to operational inference:

1. **CycloneNet-Detect**: ResNet-50 Feature Pyramid Network for center localization.
2. **CycloneNet-Classify**: Convolutional Vision Transformer for IMD category classification.
3. **CycloneNet-Intensity**: Multi-modal ViT for Vmax (knots) and MSLP (hPa) estimation.
4. **CycloneNet-RI**: ConvLSTM with environmental shear gating for Rapid Intensification risk.
5. **CycloneNet-Forecast**: Spatiotemporal autoregressive model for 12h–48h trajectory tracks.
6. **CycloneNet-Explain**: Grad-CAM attribution engine delivering meteorologist saliency heatmaps.
