# CycloneGuard — User Portal Architecture & Specifications

> **Sprint 2 Documentation**  
> **Status: Locked & Operational**  
> **Scope**: Meteorological Analyst & Decision-Support User Interface

---

## 1. Overview & Information Architecture

The CycloneGuard User Portal is designed for meteorologists, emergency response analysts, disaster management coordinators, and research scientists. In adherence to Sprint 2 requirements, it provides a calm, information-first interface built on the locked CycloneGuard design system tokens.

### Route Map

| Path | Access Level | Primary Responsibility | Key Components |
| :--- | :--- | :--- | :--- |
| `/user/dashboard` | Authenticated (User/Admin) | Operational overview: "What is happening with tropical cyclones?" | `CycloneMap`, `Card`, `Badge`, `Alert` |
| `/user/monitor` | Authenticated (User/Admin) | Full-screen spatial observation, forecast, and risk layer workspace | `CycloneMap`, Map Controls, Layer Telemetry |
| `/user/cyclones` | Authenticated (User/Admin) | Structured searchable cyclone registry and system inventory | Filter Controls, `Table`, Empty States |
| `/user/cyclones/[id]` | Authenticated (User/Admin) | In-depth multi-source cyclone intelligence and intensity diagnostic | `RIRiskPanel`, `EvidencePanel`, `ExplanationPanel`, `ForecastTimeline`, `CycloneMap` |
| `/user/history` | Authenticated (User/Admin) | Retrospective search and benchmark reanalysis exploration | Multi-parameter filters (basin, season, category, RI) |
| `/user/profile` | Authenticated (User/Admin) | Analyst identity, role permissions, and credential management | Profile details, Password change modal |
| `/about` | Public | Scientific rationale, methodology, limitations, and disclaimers | 7 core sections, No marketing hyperbole |

---

## 2. Authentication & Session Flow

The User Portal enforces robust client-side session verification via `PortalLayout` paired with JWT bearer tokens for backend requests.

### Client-Side Session Gating
1. When a user requests any `/user/*` route, `PortalLayout` evaluates the session via `useAuth()`.
2. While verifying local storage and API session health, a clean loading state (`Verifying platform session...`) is displayed.
3. If unauthenticated, the user is redirected cleanly to `/login?redirect={targetPath}`.
4. If authenticated, the portal shell renders with the standard CycloneGuard top navigation.

### Navigation Architecture
In accordance with Sprint 2 instructions:
- **No massive generic sidebar** is used.
- Navigation utilizes the established top bar:
  ```
  CYCLONEGUARD       Monitor   Cyclones   History   About       [User Name / Role]   Sign out
  ```
- **Mobile responsiveness**: Collapses into a compact dropdown menu with accessible touch targets, avoiding horizontal scrollbars across all screen widths down to 375px.

---

## 3. Page Responsibilities & Interfaces

### 3.1 User Dashboard (`/user/dashboard`)
- **Header**: Greets the authenticated analyst with active session role badge (`METEOROLOGICAL ANALYST`).
- **Main Map Area**: Embeds `CycloneMap` displaying live observational layers. Clearly reports `Current operational data: Not connected`.
- **Current Systems Section**: Honest empty state when no storms are active.
- **Recent Activity Section**: Log of recent observational updates.
- **System Status Bar**: Reports live telemetry for Satellite Ingest (`Not connected`), AI Analysis (`Not deployed`), and Database Connection (`Connected`).

### 3.2 Cyclone Monitor (`/user/monitor`)
- Dedicated map-centric interface for synoptic monitoring.
- Provides layer toggles for:
  - Track & Trajectory (`Not connected`)
  - Wind Field (`Not connected`)
  - Precipitation / Rainfall (`Not connected`)
  - RI Risk Contour (`Not connected`)
  - Satellite Imagery (`Not connected`)
- Quick basin filters (North Indian Ocean, Western Pacific, Eastern Pacific, North Atlantic, Southern Hemisphere).

### 3.3 Cyclone Registry (`/user/cyclones`)
- Comprehensive list of active and recent tropical cyclone systems.
- Features search by storm name or international identifier, basin selector, and intensity sort.
- Displays structured empty state when no active operational feed is ingested:
  `"No cyclone records are currently available. Data will appear when a cyclone data source is connected."`
- Pre-wired to render: Name, Date, Region, Current Intensity, Trend, RI Risk, and Status once backend feeds activate.

### 3.4 Cyclone Detail Page (`/user/cyclones/[id]`)
- One of the core future intelligence screens, designed with a complete 10-section layout:
  1. **Header & Context**: Cyclone identifier, basin, observation timestamp, breadcrumbs, demo badge.
  2. **Core Metrics Bar**: Intensity ($V_{max}$ & MSLP), 6h Trend, RI Risk state.
  3. **Spatial Synopsis Map**: Embedded `CycloneMap` showing current center and observation cone.
  4. **Intensity Evolution**: Historical timeline and future trajectory container.
  5. **Rapid Intensification Analysis**: Powered by `RIRiskPanel`.
  6. **Multi-Source Evidence**: Powered by `EvidencePanel`.
  7. **Model Explanation & Attribution**: Powered by `ExplanationPanel`.
  8. **Forecast Timeline**: Powered by `ForecastTimeline`.
  9. **Data Source Audit**: Detailed telemetry of sensors (INSAT-3D, Himawari-9, ERA5).
  10. **Scientific Disclaimer**: Prominent reminder of advisory decision-support scope.

### 3.5 Historical Cyclone Analysis (`/user/history`)
- Retrospective workbench for evaluating past cyclone seasons and benchmark cases.
- Multi-parameter filter panel for:
  - Basin selection
  - Season / Year range
  - Cyclone intensity category (Depression to Category 5)
  - Maximum sustained wind speed range
  - Rapid Intensification (RI) occurrence filter
- Scientific empty state: `"No historical reanalysis database connected."`

### 3.6 User Profile (`/user/profile`)
- Displays user identification: Full Name, Email, Role (`USER` / `ADMIN`), Account Creation Date.
- Security-compliant credential update modal (`POST /api/v1/users/change-password`) with Bcrypt verification and re-hashing.
- Explicitly safeguards against leaking passwords, password hashes, JWT secrets, or internal DB identifiers.

### 3.7 About Platform (`/about`)
- Public informational page written in neutral scientific prose.
- Contains 7 key sections:
  1. What is CycloneGuard?
  2. Why Multi-Source Satellite Data?
  3. Why Rapid Intensification Matters?
  4. How the Platform Architecture Works (5-stage pipeline).
  5. AI-Assisted Decision Support Philosophy.
  6. Platform Limitations.
  7. Scientific Advisory Disclaimer.
- Strictly adheres to the anti-hype policy (no "100% accurate", "first ever", or "predicts disasters").

---

## 4. Reusable Meteorological UI Components

Sprint 2 created modular, scientifically honest UI components that accept structured data types or gracefully present locked empty states:

| Component | Purpose | Current State / Fallback |
| :--- | :--- | :--- |
| `CycloneMap` | Geospatial map container for tracks, wind fields, and risk polygons | Renders `Map data unavailable` with layer telemetry and explicit `(Not connected)` badges. |
| `RIRiskPanel` | Rapid Intensification 24h/48h probability diagnostic | Supports 6 states (`unavailable`, `low`, `moderate`, `elevated`, `high`, `critical`). Defaults to `"Awaiting AI analysis"`. |
| `EvidencePanel` | Multi-source sensor alignment matrix (IR, Microwave, Scatterometer, ERA5) | Defaults to `"Multi-source analysis will appear when satellite data is connected."` |
| `ExplanationPanel` | Explainable AI (Grad-CAM saliency and atmospheric feature attribution) | Defaults to `"Model explanation unavailable until an AI prediction is generated."` |
| `ForecastTimeline` | Step-wise intensity and track horizon projection | Renders vertical tree (NOW $\to$ 12h $\to$ 24h $\to$ 36h $\to$ 48h) with `"Forecast unavailable"`. |
| `DemoModeBanner` | Persistent high-contrast indicator for benchmark validation cases | Injects `"DEMONSTRATION DATA"` banner when `is_demonstration: true`. |

---

## 5. API Dependencies & Service Layer

The frontend interfaces with the FastAPI backend via `frontend/lib/api/cyclones.ts`:

- `getCyclones()` $\to$ `GET /api/v1/cyclones` (Returns `{ cyclones: [], total: 0 }`)
- `getCyclone(id)` $\to$ `GET /api/v1/cyclones/{id}`
- `getHistoricalCyclones(params)` $\to$ `GET /api/v1/cyclones/historical`
- `getCycloneForecast(id)` $\to$ `GET /api/v1/cyclones/{id}/forecast`
- `getCycloneAnalysis(id)` $\to$ `GET /api/v1/cyclones/{id}/analysis`
- `changeUserPassword(payload)` $\to$ `POST /api/v1/users/change-password`

All requests attach the active JWT Bearer token in the `Authorization` header.

---

## 6. Demonstration Data Policy

CycloneGuard strictly separates operational data from demonstration data:
1. **Never conflate benchmark data with live operations**: If demonstration data is loaded for retrospective analysis, the `DemoModeBanner` component must be displayed immediately at the top of the interface.
2. **Zero fabricated statistics**: No simulated wind speeds, fake pressure readings, or pseudo-random risk scores may be generated under the guise of live telemetry.
3. **Traceability**: All demonstration datasets must cite their historical ground truth source (e.g., JTWC Best Track, IMD RSMC New Delhi, IBTrACS v04).

---

## 7. Future AI Integration Points (Sprint 3 & Beyond)

| Component / Layer | Sprint Scheduled | Planned Backend/ML Contract |
| :--- | :--- | :--- |
| **Cyclone Ingestion Pipeline** | Sprint 3 | Satellite netCDF/HDF5 parsing from INSAT-3D/3DR and Himawari-9 feeds. |
| **CycloneNet-Detect** | Sprint 3 | Deep learning center locator generating bounding box coordinates and vortex center points for `CycloneMap`. |
| **CycloneNet-Intensity** | Sprint 3 | ViT multi-spectral intensity estimator outputting sustained wind ($kt$) and central pressure ($hPa$). |
| **CycloneNet-RI** | Sprint 4 | ConvLSTM spatio-temporal classifier feeding probabilities into `RIRiskPanel`. |
| **CycloneNet-Explain** | Sprint 4 | Grad-CAM attribution tensors and saliency heatmaps rendering into `ExplanationPanel`. |
| **Forecast Trajectory Engine** | Sprint 4 | Multi-horizon track & intensity vectors populating `ForecastTimeline`. |
