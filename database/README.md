# CycloneGuard Database & Migrations

This directory contains database schema documentation and Alembic database migration scripts for CycloneGuard.

## Database Engine
- **Primary / Production**: PostgreSQL 16+
- **Driver**: `psycopg2` / `postgresql+psycopg2://`
- **ORM**: SQLAlchemy 2.0+
- **Migration Framework**: Alembic

## Core Models Defined in Sprint 1

### 1. `users` (Active in Sprint 1)
- `id`: UUID (Primary Key, indexed)
- `name`: VARCHAR(255), Not Null
- `email`: VARCHAR(255), Unique, Indexed, Not Null
- `password_hash`: VARCHAR(255), Not Null (Bcrypt-hashed)
- `role`: Enum ('USER', 'ADMIN'), Default 'USER', Indexed
- `is_active`: BOOLEAN, Default True
- `created_at`: TIMESTAMP WITH TIME ZONE (UTC)
- `updated_at`: TIMESTAMP WITH TIME ZONE (UTC)

### 2. Future Cyclone Records Schema (`cyclones`)
- `id`: UUID
- `basin`: VARCHAR (e.g. North Indian Ocean, Western Pacific, North Atlantic)
- `international_id`: VARCHAR, Nullable
- `name`: VARCHAR
- `status`: VARCHAR ('ACTIVE', 'DISSIPATED', 'EXTRATROPICAL')
- `genesis_time`: TIMESTAMP WITH TIME ZONE
- `dissipation_time`: TIMESTAMP WITH TIME ZONE, Nullable
- `created_at`, `updated_at`

### 3. Future Observations Schema (`observations`)
- `id`: UUID
- `cyclone_id`: Foreign Key (`cyclones.id`)
- `source`: VARCHAR (e.g., 'INSAT-3D', 'HIMAWARI-9', 'GOES-16', 'ERA5')
- `channel`: VARCHAR (e.g., 'IR1', 'WV', 'VIS')
- `timestamp`: TIMESTAMP WITH TIME ZONE
- `storage_path`: TEXT
- `metadata`: JSONB / JSON
- `created_at`

### 4. Future Predictions Schema (`predictions`)
- `id`: UUID
- `cyclone_id`: Foreign Key (`cyclones.id`)
- `model_version_id`: Foreign Key (`model_versions.id`)
- `timestamp`: TIMESTAMP WITH TIME ZONE
- `estimated_intensity_vmax_knots`: FLOAT
- `estimated_mslp_hpa`: FLOAT
- `ri_probability_24h`: FLOAT (0.0 - 1.0)
- `ri_risk_level`: VARCHAR ('LOW', 'MODERATE', 'HIGH', 'EXTREME')
- `explanation_summary`: JSONB / JSON
- `created_at`

### 5. Future Alerts Schema (`alerts`)
- `id`: UUID
- `cyclone_id`: Foreign Key (`cyclones.id`)
- `severity`: VARCHAR ('ADVISORY', 'WATCH', 'WARNING', 'CRITICAL')
- `title`: VARCHAR
- `description`: TEXT
- `target_region`: VARCHAR
- `issued_at`: TIMESTAMP WITH TIME ZONE
- `expires_at`: TIMESTAMP WITH TIME ZONE, Nullable
- `created_at`

### 6. Future Model Versions Schema (`model_versions`)
- `id`: UUID
- `model_name`: VARCHAR
- `version`: VARCHAR
- `architecture`: VARCHAR
- `is_active`: BOOLEAN
- `metrics_manifest`: JSONB / JSON
- `created_at`

## Running Migrations
From repository root:
```bash
# Upgrade to latest revision
alembic -c database/alembic.ini upgrade head

# Generate a new migration
alembic -c database/alembic.ini revision --autogenerate -m "description"
```
