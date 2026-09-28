from fastapi import APIRouter
from app.api.v1.endpoints import auth, system, users, ai_placeholders, admin, cyclones, analysis, ri_models

api_router = APIRouter()

# Authentication endpoints: /api/v1/auth/*
api_router.include_router(auth.router)

# System and health endpoints: /api/v1/health, /api/v1/system/info
api_router.include_router(system.router)

# Administrative user endpoints: /api/v1/users/* (user profile, password change)
api_router.include_router(users.router)

# Dedicated Admin Portal endpoints: /api/v1/admin/*
api_router.include_router(admin.router)

# Operational Cyclone & Observation endpoints: /api/v1/cyclones/*
api_router.include_router(cyclones.router)

# AI Cyclone Analysis & Inference: /api/v1/analysis/*
api_router.include_router(analysis.router)

# Rapid Intensification Models & Inference (Sprint 6): /api/v1/models/ri, /api/v1/predictions/ri, etc.
api_router.include_router(ri_models.router)

# Meteorological & Model Placeholders: /api/v1/models, /api/v1/predictions, etc.
api_router.include_router(ai_placeholders.router)

