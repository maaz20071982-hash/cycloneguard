# CycloneGuard Product Scope & Roadmap

## 1. Executive Product Vision
CycloneGuard is an AI-powered tropical cyclone intelligence platform that transforms raw multi-source geostationary satellite feeds and atmospheric environmental reanalysis data into actionable, interpretable meteorological intelligence for disaster managers, meteorological analysts, and institutional decision-makers.

---

## 2. Sprint 1 MVP Scope (Delivered)

### Core Deliverables
- **Monorepo Architecture**: Clean separation between `frontend`, `backend`, `database`, `ml`, and `docs`.
- **Backend API Foundation**: FastAPI REST framework with OpenAPI documentation (`/docs`, `/redoc`), database pooling, structured CORS policies, and standardized JSON error envelopes.
- **Authentication & RBAC**:
  - Secure Bcrypt password hashing (minimum 8 characters).
  - Signed HS256 JWT access tokens with 24-hour expiration.
  - Role-based authorization distinguishing `USER` and `ADMIN` roles.
  - Enforced server-side `require_admin` dependency.
- **Database & Migrations**:
  - SQLAlchemy 2.0 ORM with PostgreSQL and SQLite fallback support.
  - Alembic migrations with fully defined initial schema for `users`, `cyclones`, `observations`, `model_versions`, `predictions`, and `alerts`.
  - Idempotent development seeder (`scripts/seed_dev.py`) using environment variables.
- **Frontend Design System & Portals**:
  - Next.js 16 (React 19) with Tailwind CSS v4.
  - Meteorological, scientific, dark-navy aesthetic with custom radar grid textures.
  - Public Landing Page with status banner, hero section, and capability previews.
  - Protected User Portal (`/user/dashboard`, `/user/cyclones`, `/user/history`, `/user/profile`).
  - Protected Admin Portal (`/admin/dashboard`, `/admin/data`, `/admin/models`, `/admin/predictions`, `/admin/alerts`, `/admin/users`, `/admin/system`).
  - Centralized API client (`frontend/lib/api/`) eliminating scattered fetch requests.
- **Scientific Integrity Principle**:
  - Strict zero-fabrication policy: no synthetic storm counts, fake wind speeds, or simulated AI predictions.
  - All unintegrated modules explicitly state "Awaiting data source" or "Model not deployed".
- **Containerization**:
  - `docker-compose.yml` linking PostgreSQL, FastAPI, and Next.js.
  - Production Dockerfiles for backend and frontend.

---

## 3. User Portal Capabilities

### Sprint 1 Foundation (Current)
- Secure registration and authentication session.
- Operational overview with satellite connection health.
- Cyclone monitor with basin filtering tabs and honest empty states.
- Historical storm archive roadmap placeholders.
- Analyst profile and active session management.

### Future Roadmap (Sprints 2–5)
- Interactive satellite imagery viewer with channel toggling (IR1, WV, VIS).
- Real-time storm center coordinate tracking and wind radii cones.
- Estimated Maximum Sustained Winds (Vmax in knots) and Central Pressure (MSLP in hPa).
- Rapid Intensification (RI) risk probability gauge (0–100%) with 24-hour forecast window.
- Track trajectory cone projections (24h, 48h, 72h).
- Grad-CAM heatmap overlays displaying convolutional attention regions.
- Plain-English meteorological explanation cards for decision-makers.

---

## 4. Admin Portal Capabilities

### Sprint 1 Foundation (Current)
- Comprehensive operational dashboard covering all 7 system domains:
  1. System Health & Database Telemetry
  2. Observational Data Sources Status
  3. AI / ML Model Status
  4. Recent Predictions Telemetry
  5. Active Alerts Registry
  6. User Accounts & Access Control
  7. System Audit Logs
- Live user directory consuming `/api/v1/users` with role indicators.
- System diagnostics page validating runtime configuration, migration state, and security posture.

### Future Roadmap (Sprints 2–5)
- Ingestion pipeline monitoring for ISRO INSAT-3D/3DR and JMA Himawari-9.
- Data ingestion retry queues and raw storage volume metrics.
- Model registry managing PyTorch/ONNX checkpoints and inference latency.
- Automated alert threshold configuration (e.g. notify on RI probability > 65%).
- User role elevation and account suspension controls.

---

## 5. Planned AI/ML Subsystems (Sprint 2+)

| Model | Objective | Planned Architecture | Target Milestone |
| :--- | :--- | :--- | :--- |
| **CycloneNet-Detect** | Center localization & storm presence | ResNet-50 Feature Pyramid Network | Sprint 2 |
| **CycloneNet-Intensity**| Vmax (knots) and MSLP (hPa) estimation | Multi-Modal Vision Transformer (ViT) | Sprint 3 |
| **CycloneNet-RI** | 24-hour Rapid Intensification (≥30kt surge) | ConvLSTM + Gated Environmental Wind Shear | Sprint 3 |
| **CycloneNet-Track** | 24-72h forward trajectory cone | Physics-Informed Temporal Neural Operator | Sprint 4 |
| **CycloneNet-Explain**| Explainable AI & saliency attribution | Grad-CAM + Integrated Gradients | Sprint 4 |

---

## 6. Planned Satellite & Atmospheric Data Sources

1. **INSAT-3D & INSAT-3DR (ISRO)**
   - *Channels*: Thermal Infrared 1 (TIR1 10.8µm), Water Vapor (WV 6.9µm), Visible (VIS 0.65µm).
   - *Basin Coverage*: North Indian Ocean (Arabian Sea and Bay of Bengal).
   - *Ingestion cadence*: 15-minute / 30-minute intervals via MOSDAC API.
2. **Himawari-9 (Japan Meteorological Agency / JMA)**
   - *Channels*: Band 13 (Clean IR), Band 8 (Upper Troposphere WV), Band 3 (Red VIS).
   - *Basin Coverage*: Western North Pacific and East Asian waters.
3. **GOES-16 & GOES-18 (NOAA)**
   - *Channels*: Band 13 (Clean IR), Band 14 (IR Longwave).
   - *Basin Coverage*: North Atlantic and Eastern Pacific.
4. **ECMWF / ERA5 Reanalysis & GFS Forecasts**
   - *Fields*: 850–200 hPa Vertical Wind Shear (VWS), Sea Surface Temperature (SST), 700–500 hPa Relative Humidity.
   - *Role*: Environmental gating inputs for Rapid Intensification prediction models.
