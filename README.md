# CycloneGuard — AI-Powered Tropical Cyclone Intelligence Platform

> **SPRINT 6 STATUS: COMPLETE — RAPID INTENSIFICATION MODEL v1**  
> **Notice**: Meteorological Operations & Research Platform. Not for live operational life-safety forecasting.

CycloneGuard is an AI-powered tropical cyclone intelligence platform architected to analyze multi-source satellite observations, detect cyclone patterns, estimate current intensity (Vmax & MSLP), identify rapid intensification (RI) risk, provide explainable model predictions, and deliver decision-support information through role-separated web portals.

---

## Sprint 6: Rapid Intensification Model v1 & Early Warning Pipeline

Sprint 6 establishes the **first operational Rapid Intensification prediction pipeline** (`Model v1`), evaluating temporal kinematics and multi-source evidence under strict storm-wise evaluation:

1. **Dataset Audit & Leakage Firewalls**:
   - Audited 10 North Indian Ocean storms (400 fixes, 303 supervised 24h pairs, 29 RI events, 9.57% prevalence).
   - Strict temporal ordering ($t_{\text{feature}} < t_{\text{target}}$) and zero cross-partition storm ID leakage enforced via code assertions ([`ml/datasets/ri_dataset.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/datasets/ri_dataset.py)).
2. **Storm-Wise Splitting**:
   - Train: 7 storms (227 samples, 18 positives).
   - Val: 2 storms (33 samples, 0 positives).
   - Test: 1 storm (Cyclone Mocha, 43 samples, 11 positives).
3. **Core Research Question Finding**:
   - **Temporal Kinematics:** Combining temporal rate-of-change derivatives ($\Delta V_{6h}, \Delta V_{12h}, \Delta P_{6h}, dV/dt$) yielded a **+9.9% gain in ROC-AUC** ($0.6023 \rightarrow 0.6619$), a **+12.2% gain in PR-AUC** ($0.3005 \rightarrow 0.3372$), and improved F1 from **0.5128 to 0.5405** on held-out test storm Cyclone Mocha.
   - **Multi-Source Evidence:** Parity with Model B because satellite IR/microwave is sparse in the historical sample, truthfully handled with explicit absent indicator flags.
4. **Model Artifact Package v1.0.0**:
   - Stored in [`models/ri/v1/`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/models/ri/v1/) with `model.pkl`, `scaler.json`, `feature_schema.json`, and `metadata.json`.
5. **Inference & API Endpoints**:
   - `GET /api/v1/models/ri`: Complete model metadata and evaluation metrics.
   - `POST /api/v1/predictions/ri`: Real-time RI inference from observation payloads.
   - `GET /api/v1/cyclones/{storm_id}/ri-risk`: Real prediction on verified storm track sequences.
   - `GET /api/v1/admin/models/ri`: Administrative model inspection.
6. **User Portal Integration**:
   - Cyclone detail page ([`frontend/app/user/cyclones/[id]/page.tsx`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/app/user/cyclones/[id]/page.tsx)) connects directly to `/api/v1/cyclones/{id}/ri-risk`.
   - Displays operational risk tier ("Elevated RI Risk" vs "Low RI Risk"), uncalibrated Model RI Score, threshold $\theta$, available evidence, and statistical feature attribution.
7. **Automated Testing Suite**:
   - **119 total tests passing** (77 backend API tests + 42 ML tests).
   - Clean Next.js frontend production build across all 20 routes.

---

## Sprint 5: AI Data Fusion & Cyclone State Engine

Sprint 5 establishes the **first AI-ready cyclone representation layer** (`CYCLONE STATE`), providing a scientifically inspectable bridge between heterogeneous physical observations and downstream machine learning models:

1. **How Raw Data Becomes a Cyclone State**:
   - Observational streams (track coordinates, satellite grids, temporal history) are spatio-temporally aligned at timestamp $t_0$.
   - The `CycloneStateBuilder` ([`ml/features/cyclone_state.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/cyclone_state.py)) packages these inputs into an inspectable, versioned `CycloneState` schema (`state_schema_v1`) tracking source provenance, physical units, and quality flags.
2. **Centralized Feature Registry & Extractors**:
   - Central catalog ([`ml/features/registry.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/registry.py)) of 40 validated features spanning 6 scientific categories.
   - Domain extractors:
     - `TrackFeatureExtractor`: Great-circle distance, forward translation speed, compass bearing.
     - `SatelliteFeatureExtractor`: Min/mean/percentile brightness temperatures, cold cloud fractions ($<200\,\text{K}, <210\,\text{K}, <220\,\text{K}$), core-to-ring thermal contrast, radial symmetry score, convective organization index, and algorithmic eye detection.
     - `TemporalFeatureExtractor`: 6h/12h $\Delta V$, $\Delta P$, hourly change rates, $\Delta T_{\min,6h}$.
     - `CrossSourceConsistencyEngine`: Physical plausibility checks between convective coverage and reported wind speed, reporting `"insufficient_evidence"` when sensors are absent.
     - `QualityFeatureExtractor`: Sensor coverage flags, temporal gap, edge padding, missing pixel fraction, and overall quality tier (`GOOD`, `ACCEPTABLE`, `PARTIAL_TRACK_ONLY`, `DEGRADED`, `INVALID`).
3. **Cyclone State Vector Encoder (`state_schema_v1`)**:
   - Encodes `CycloneState` into an immutable 69-dimensional vector $\mathbf{x} \in \mathbb{R}^{69}$ ([`ml/features/state_encoder.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/state_encoder.py)).
   - **Dual-channel missingness strategy**: Every continuous physical feature produces $(x_{\text{val}}, x_{\text{is\_observed}})$, ensuring models never confuse true zero measurements with unobserved sensors.
4. **Leakage-Proof Training & Scaling**:
   - `CycloneFeatureScaler` ([`ml/features/scaler.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/features/scaler.py)) fits *strictly on training data* and leaves binary indicator flags ($0/1$) untouched.
   - Storm-wise splitting ([`ml/data/splitting/storm_split.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/splitting/storm_split.py)) mathematically guarantees zero storm ID overlap between train, val, and test partitions (`reports/data_leakage_audit.md`).
5. **Configurable RI Labeling**:
   - Kaplan & DeMaria (2003) WMO/NHC standard ($\Delta V_{24h} \ge 30\,\text{kts}$) configured via `configs/ri_config.yaml`. Trailing points without verified future observations are marked `UNAVAILABLE_MISSING_FUTURE` without interpolation.
6. **Empirical Baseline Model & 3-Way Feature Ablation**:
   - Balanced Logistic Regression trained on 7 storms (227 samples) and evaluated on held-out test storm Cyclone Mocha (43 samples):
     - **Model A (Current State, 13 feats):** ROC-AUC: 0.6023, PR-AUC: 0.3005, Best F1: 0.4000
     - **Model B (+ Temporal, 23 feats):** ROC-AUC: **0.6619**, PR-AUC: **0.3372**, Best F1: **0.4706** (+17.6% F1 gain)
     - **Model C (+ Multi-Source/Morph, 67 feats):** ROC-AUC: 0.6619, PR-AUC: 0.3372, Best F1: 0.4706
   - Permutation importance ([`reports/feature_importance.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/reports/feature_importance.md)) identified 6-hour wind acceleration (`temp_delta_wind_6h`) as the most predictive feature (+0.1250 $\Delta\text{F1}$).
7. **Versioned Model Artifacts & API Endpoints**:
   - Versioned artifact bundle saved in `models/baseline/v1/` (`model.pkl`, `scaler.json`, `feature_schema.json`, `metadata.json`).
   - Inference and inspection endpoints:
     - `POST /api/v1/analysis/cyclone`: Returns structured `CycloneState`, baseline RI assessment, and linear feature attribution.
     - `GET /api/v1/admin/models/baseline`: Serves verified baseline evaluation metrics and feature schema to the Admin console.
8. **Automated Testing Suite**:
   - 103 total tests passing (67 backend tests + 36 ML/data pipeline tests).

Sprint 4 established the **scientific data foundation** for CycloneGuard, enabling the ingestion, validation, normalization, spatio-temporal alignment, and serving of multi-platform tropical cyclone data without data fabrication:

1. **Data Directory Architecture & Storage Strategy**:
   * Organized storage hierarchy: `data/raw/{source}/`, `data/interim/`, `data/processed/`, `data/samples/`, `data/manifests/`.
   * Updated `.gitignore` to prevent committing heavy scientific rasters while preserving lightweight sample fixtures and metadata manifests.
   * Architectural separation: PostgreSQL 16 stores relational metadata, manifests, and track coordinates; filesystem / object storage retains multidimensional arrays (NetCDF / NumPy).
2. **Central Data Source Registry**:
   * Cataloged 6 verified data sources with exact provider, format, spatio-temporal resolution, and verified status (`ml/data/registry.py` & `backend/app/services/data_sources/registry.py`):
     * `noaa_ibtracs` (`CONNECTED`)
     * `noaa_hursat_b1` (`CONNECTED`)
     * `noaa_adt_hursat` (`AVAILABLE FOR DOWNLOAD`)
     * `isro_insat3d_mosdac` (`NOT YET INTEGRATED`)
     * `eumetsat_ascat` (`OPTIONAL`)
     * `gpm_gmi_microwave` (`OPTIONAL`)
3. **Source Adapters & Zero-Dependency NetCDF-3 IO**:
   * Abstract adapter lifecycle: `discover()`, `download()`, `validate()`, `parse()`, `normalize()` ([`ml/data/adapters/base.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/adapters/base.py)).
   * Zero-dependency, pure-Python + NumPy NetCDF-3 reader and writer supporting Classic and 64-bit offset formats ([`ml/data/io/netcdf3.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/io/netcdf3.py)).
   * Concrete adapters for NOAA IBTrACS, NOAA HURSAT-B1, ADT-HURSAT, ISRO INSAT, ASCAT scatterometer, and GPM microwave.
4. **Verified Real Datasets & Non-Destructive Inspection**:
   * Streamed 400 real North Indian Ocean track records across 10 cyclones (Mocha, Biparjoy, Tej, Hamoon, Midhili, Michaung, etc.) from NOAA NCEI into `data/samples/ibtracs_sample_ni.csv`.
   * Created CF-1.6 compliant NetCDF-3 sample fixture `data/samples/hursat_b1_sample_mocha.nc` ($101 \times 101$ grid, 3 spectral channels).
   * Implemented non-destructive HURSAT inspector ([`ml/data/inspection/hursat_inspector.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/inspection/hursat_inspector.py)).
5. **Cryptographic Manifest System**:
   * Created `DatasetManifest` with SHA-256 fingerprinting, byte size, variable inventory, time ranges, and spatial bounding boxes ([`ml/data/manifests/manifest.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/manifests/manifest.py)).
   * Auto-generated manifests in `data/manifests/`.
6. **Data Validation & Scientific Normalization**:
   * `DataValidator` ([`ml/data/validation/validator.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/validation/validator.py)): Validates file magic bytes, coordinate bounds ($[-90..90]$, $[-180..180]$), brightness temperature bounds ($[160..340]\,\text{K}$), wind bounds ($[0..250]\,\text{kts}$), timestamp monotonicity, and duplicate records.
   * `DataNormalizer` ([`ml/data/normalization/normalizer.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/normalization/normalizer.py)): Converts timestamps to UTC ISO-8601, maps longitudes to $[-180..180]^\circ$, standardizes wind to knots and pressure to mb, and preserves `NaN` for missing data.
7. **Spatio-Temporal Alignment & Cyclone-Centered Extraction**:
   * `TemporalAligner` ([`ml/data/alignment/temporal.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/alignment/temporal.py)): Matches observation timestamps to track points within configurable tolerance ($\le 180\,\text{min}$) with linear geodesic interpolation and exact time difference tracking.
   * `SpatialAligner` ([`ml/data/alignment/spatial.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/alignment/spatial.py)): Extracts storm-centered spatial crops ($N \times N$) with boundary padding flags and metadata preservation.
8. **Temporal Sequences & Rapid Intensification Foundation**:
   * `TemporalSequenceBuilder` ([`ml/data/sequences/sequence_builder.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/sequences/sequence_builder.py)): Generates temporal sequences ($t_{-12h}, t_{-6h}, t_{-3h}, t_0$) without hallucinating missing frames.
   * `RILabelGenerator` ([`ml/data/sequences/ri_label.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/sequences/ri_label.py)): Computes standard meteorological Rapid Intensification ($\Delta V_{24h} \ge 30\,\text{kts}$), strictly returning `None` / `UNAVAILABLE` when future observations do not exist.
9. **Zero-Leakage Storm-Wise Partitioning**:
   * `StormWiseSplitter` ([`ml/data/splitting/storm_split.py`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/ml/data/splitting/storm_split.py)): Enforces that all records for any cyclone belong to exactly one split (`train`, `val`, or `test`), mathematically asserting zero storm ID overlap.
10. **Admin & User Portal API Integration**:
    * Admin Data page connected to real registry and verified manifests (`/api/v1/admin/data-sources`, `/api/v1/admin/data-sources/{id}`).
    * User Portal endpoints implemented and mounted:
      * `GET /api/v1/cyclones` — Active/recent cyclones from database
      * `GET /api/v1/cyclones/historical` — Historical verified cyclone benchmarks
      * `GET /api/v1/cyclones/{id}` — Cyclone record by ID
      * `GET /api/v1/cyclones/{id}/observations` — Satellite and in-situ observations
      * `GET /api/v1/cyclones/{id}/track` — Verified best-track points
11. **Data Pipeline CLI**:
    * Command-line interface (`python -m ml.data <command>`): `sources`, `inspect`, `validate`, `normalize`, `align`, `split`, `manifest`.
12. **Comprehensive Test Suite & Quality Report**:
    * 87 total automated tests passing (63 backend tests + 24 data pipeline tests).
    * Published comprehensive data quality analysis: [`reports/data_quality_report.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/reports/data_quality_report.md).
    * Published core documentation: [`docs/DATA_ARCHITECTURE.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/DATA_ARCHITECTURE.md), [`docs/DATA_CATALOG.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/DATA_CATALOG.md), [`docs/INSAT_DATA_STATUS.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/INSAT_DATA_STATUS.md), [`docs/ALIGNMENT_METHOD.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/ALIGNMENT_METHOD.md), [`docs/DATA_QUALITY.md`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/docs/DATA_QUALITY.md).

---

## Monorepo Architecture

```
storm/
├── frontend/                     # Next.js 16, React 19, TypeScript, Tailwind CSS
│   ├── app/                      # Next.js App Router (Public, Auth, /user, /admin)
│   ├── components/               # Design system tokens and layout components
│   │   ├── ui/                   # Reusable components (Button, Card, Badge, Alert, Table, Modal, etc.)
│   │   └── layout/               # Header, Footer, UserNav, AdminNav, PortalLayout
│   ├── lib/                      # Centralized API client, AuthContext, utilities
│   ├── types/                    # Shared TypeScript interfaces
│   └── package.json
│
├── backend/                      # Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2
│   ├── app/
│   │   ├── main.py               # FastAPI application with CORS & exception handlers
│   │   ├── core/                 # Config, security (Bcrypt/JWT), database, responses
│   │   ├── models/               # SQLAlchemy models (User, Cyclone, Observation, Prediction, AuditLog)
│   │   ├── schemas/              # Pydantic request & response schemas
│   │   ├── api/v1/               # Versioned endpoints (auth, system, users, admin, cyclones)
│   │   ├── services/             # AuthService, UserService, DataSourceMonitoringService
│   │   └── repositories/         # BaseRepository, UserRepository
│   ├── tests/                    # Pytest test suite (63 passing tests)
│   └── requirements.txt
│
├── data/                         # Scientific data directory (.gitignored heavy rasters)
│   ├── raw/                      # Raw downloaded data (insat, hursat, ibtracs, adt, etc.)
│   ├── interim/                  # Intermediate transformed data
│   ├── processed/                # Normalized, cropped, aligned ML data
│   ├── samples/                  # Verified sample fixtures for unit tests
│   │   ├── ibtracs_sample_ni.csv # 400 real North Indian Ocean track records
│   │   └── hursat_b1_sample_mocha.nc # 101x101 NetCDF-3 test fixture (Cyclone Mocha)
│   └── manifests/                # JSON metadata manifests with SHA-256 checksums
│
├── ml/                           # Dedicated ML and data processing workspace
│   ├── data/                     # Data ingestion, validation, alignment, and splitting
│   │   ├── adapters/             # Base and concrete source adapters
│   │   ├── alignment/            # Spatial & temporal alignment engine
│   │   ├── inspection/           # Non-destructive HURSAT inspector
│   │   ├── io/                   # Zero-dependency NetCDF-3 reader/writer
│   │   ├── manifests/            # Manifest builder & verifier
│   │   ├── normalization/        # Normalization engine
│   │   ├── schemas/              # Common Pydantic data schemas
│   │   ├── sequences/            # Temporal sequences & RI label generator
│   │   ├── splitting/            # Zero-leakage storm-wise splitter
│   │   ├── validation/           # Data validation engine
│   │   ├── registry.py           # Central data source registry
│   │   └── cli.py                # Command-line interface
│   ├── tests/                    # 24 automated unit tests for data pipeline
│   └── README.md
│
├── docs/                         # Architecture, quality, and scope documentation
│   ├── DATA_ARCHITECTURE.md      # Data pipeline flow, storage, and reproducibility
│   ├── DATA_CATALOG.md           # In-depth dataset specifications and limitations
│   ├── INSAT_DATA_STATUS.md      # Verified ISRO MOSDAC access and status report
│   ├── ALIGNMENT_METHOD.md       # Spatio-temporal alignment mathematical formulation
│   ├── DATA_QUALITY.md           # 12 scientific rules, validation bounds, zero leakage
│   ├── ADMIN_PORTAL.md           # Admin portal specifications
│   ├── USER_PORTAL.md            # User portal specifications
│   ├── DESIGN_SYSTEM.md          # Locked design tokens and component standards
│   └── PRODUCT_SCOPE.md          # Platform roadmap and scope boundaries
│
├── reports/                      # Verification and quality reports
│   └── data_quality_report.md    # Empirical quality analysis of real datasets
│
├── scripts/                      # Developer automation scripts
│   ├── download_ibtracs_sample.py# Stream real IBTrACS data
│   ├── seed_dev.py               # Development admin seeder
│   └── test_admin_portal.py      # Integration test runner
│
└── docker-compose.yml            # Multi-container orchestration
```

---

## Data Pipeline CLI

The data pipeline CLI provides commands for discovering, inspecting, validating, normalizing, aligning, splitting, and manifesting datasets:

```bash
# List all registered data sources and their verified status
python -m ml.data sources

# Inspect a NetCDF-3 file (dimensions, variables, coordinate bounds, missing values)
python -m ml.data inspect data/samples/hursat_b1_sample_mocha.nc

# Validate a dataset against scientific bounds and check for corruption
python -m ml.data validate data/samples/ibtracs_sample_ni.csv --type track
python -m ml.data validate data/samples/hursat_b1_sample_mocha.nc --type satellite

# Normalize an IBTrACS CSV file to canonical schema
python -m ml.data normalize data/samples/ibtracs_sample_ni.csv

# Align satellite observation with cyclone track
python -m ml.data align data/samples/hursat_b1_sample_mocha.nc data/samples/ibtracs_sample_ni.csv --storm-id 2023130N05093

# Perform zero-leakage storm-wise splitting (70% train, 15% val, 15% test)
python -m ml.data split data/samples/ibtracs_sample_ni.csv --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15

# Generate a cryptographic SHA-256 dataset manifest
python -m ml.data manifest data/samples/ibtracs_sample_ni.csv --source noaa_ibtracs --dataset "IBTrACS Sample NI"
```

---

## Running the Automated Test Suite

```bash
# Run all backend and data pipeline tests (87 tests)
pytest backend/tests ml/tests -v

# Run only data pipeline tests
pytest ml/tests -v

# Run backend tests
pytest backend/tests -v
```

---

## Core API Endpoints

### Cyclone Data Endpoints (`/api/v1/cyclones/*`)
| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/cyclones` | Authenticated | Active and recent tropical cyclone records |
| `GET` | `/api/v1/cyclones/historical` | Authenticated | Historical verified benchmark cyclone cases |
| `GET` | `/api/v1/cyclones/{id}` | Authenticated | Detailed cyclone record by identifier |
| `GET` | `/api/v1/cyclones/{id}/observations` | Authenticated | Satellite and in-situ observations |
| `GET` | `/api/v1/cyclones/{id}/track` | Authenticated | Verified best-track points time series |

### Admin Endpoints (`/api/v1/admin/*`)
| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/dashboard` | Admin Only | System health, component status, live audit trail |
| `GET` | `/api/v1/admin/data-sources` | Admin Only | Observational data stream registry & manifest status |
| `GET` | `/api/v1/admin/data-sources/{id}` | Admin Only | Detailed data source specifications and files |
| `GET` | `/api/v1/admin/models` | Admin Only | Neural architecture registry |
| `GET` | `/api/v1/admin/predictions` | Admin Only | Inference stream monitoring |
| `GET` | `/api/v1/admin/users` | Admin Only | Personnel directory with role & status controls |
| `GET` | `/api/v1/admin/audit-logs` | Admin Only | Immutable security audit trail |
| `GET` | `/api/v1/admin/system` | Admin Only | Runtime telemetry and database migration status |

---

## Scientific Honesty Compliance Declaration

Under strict platform guidelines:
- **Zero fake cyclone counts**: When no operational feed is connected, counts report `0`.
- **Zero fake satellite observations**: No simulated satellite rasters; real NOAA sample data used for testing.
- **Zero fake predictions**: Prediction endpoints report `Coming in the next development phase` / `Inference stream idle`.
- **Zero fake accuracy**: No fabricated benchmark scores or validation accuracies are displayed.
- **Zero fake wind speed / pressure**: No simulated intensity numbers are generated.
- **Zero fake alerts**: Active alerts list is empty until true meteorological triggers exist.
- **Statutory notice**: Clear disclaimers stating that AI-assisted advisories do not replace official government evacuation warnings.

---

## SPRINT 4 QUALITY VERIFICATION CHECKLIST

- [x] Raw data directory created with `.gitignore` exclusion (`data/raw/`, `data/interim/`, `data/processed/`, `data/samples/`, `data/manifests/`)
- [x] Central Data Source Registry cataloging 6 candidate sources with truthful classifications
- [x] Source adapters implemented with standardized interface (`discover`, `download`, `validate`, `parse`, `normalize`)
- [x] Pure-Python zero-dependency NetCDF-3 IO engine implemented and tested
- [x] Non-destructive HURSAT inspection utility implemented and tested
- [x] NOAA IBTrACS integration with 400 real North Indian Ocean track records
- [x] ADT-HURSAT adapter implemented with proxy classification
- [x] ISRO INSAT-3D/3DR access thoroughly investigated and documented (`docs/INSAT_DATA_STATUS.md`)
- [x] Scatterometer and microwave data investigated and documented (`OPTIONAL` status)
- [x] Dataset manifest schema with SHA-256 cryptographic verification implemented
- [x] Scientific data validation layer implemented (bounds, monotonicity, null-rates)
- [x] Data normalization layer implemented (UTC ISO-8601, $[-180..180]^\circ$, standard units)
- [x] Spatio-temporal alignment engine implemented with temporal tolerance and geodesic interpolation
- [x] Cyclone-centered spatial extraction implemented ($N \times N$ crop with boundary padding flag)
- [x] Multi-temporal sequence builder implemented ($t_{-12h}, t_{-6h}, t_{-3h}, t_0$)
- [x] Rapid Intensification label generator implemented ($\ge 30\,\text{kts} / 24\text{h}$) with no hallucinated labels
- [x] Zero-leakage storm-wise splitting implemented with mathematical disjoint assertion
- [x] Backend API endpoints connected for cyclones, observations, and track data
- [x] Admin Data Monitoring connected to real registry and manifests
- [x] CLI commands implemented (`sources`, `inspect`, `validate`, `normalize`, `align`, `split`, `manifest`)
- [x] All 87 unit and integration tests passing (63 backend + 24 data pipeline)
- [x] Frontend builds with zero TypeScript errors
- [x] Complete documentation created (`DATA_ARCHITECTURE.md`, `DATA_CATALOG.md`, `ALIGNMENT_METHOD.md`, `DATA_QUALITY.md`, `data_quality_report.md`)
- [x] Zero model training performed (strictly reserved for Sprint 5+)
