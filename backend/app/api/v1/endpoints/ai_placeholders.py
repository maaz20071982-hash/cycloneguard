from fastapi import APIRouter, Depends
from app.core.responses import success_response
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Meteorological & Model Endpoints (Placeholders)"])


@router.get("/cyclones/{cyclone_id}/forecast", summary="Get cyclone forecast timeline by ID")
def get_cyclone_forecast(cyclone_id: str, current_user: User = Depends(get_current_user)):
    return success_response(data={
        "cyclone_id": cyclone_id,
        "status": "unavailable",
        "horizons": [],
        "message": "AI trajectory and intensity forecast models will be deployed in Sprint 4."
    })


@router.get("/cyclones/{cyclone_id}/analysis", summary="Get multi-source evidence and model explanation by ID")
def get_cyclone_analysis(cyclone_id: str, current_user: User = Depends(get_current_user)):
    return success_response(data={
        "cyclone_id": cyclone_id,
        "status": "unavailable",
        "ri_risk": {
            "cyclone_id": cyclone_id,
            "state": "unavailable",
            "probability_24h": None,
            "probability_48h": None,
            "status_message": "Awaiting AI analysis"
        },
        "evidence": {
            "cyclone_id": cyclone_id,
            "sources": [],
            "summary": "Multi-source analysis will appear when satellite data is connected."
        },
        "explanation": {
            "cyclone_id": cyclone_id,
            "method": "Awaiting Model",
            "summary": "Model explanation unavailable until an AI prediction is generated.",
            "is_available": False,
            "features": []
        }
    })


@router.get("/data-sources", summary="Status of satellite and atmospheric data feeds")
def get_data_sources(current_user: User = Depends(get_current_user)):
    """Status of observational satellite feeds."""
    sources = [
        {
            "name": "INSAT-3D / 3DR Imager",
            "type": "Geostationary Meteorological Satellite",
            "basin": "North Indian Ocean (Arabian Sea & Bay of Bengal)",
            "channels": ["Thermal Infrared (TIR1)", "Water Vapor (WV)", "Visible (VIS)"],
            "status": "Not connected",
            "note": "API ingestion pipeline scheduled for Sprint 2",
        },
        {
            "name": "Himawari-9 AHI",
            "type": "Advanced Himawari Imager",
            "basin": "Western Pacific & East Asia",
            "channels": ["Band 13 Clean IR", "Band 8 Upper WV", "Band 3 Red VIS"],
            "status": "Not connected",
            "note": "Scheduled for Sprint 2",
        },
        {
            "name": "GOES-16 / GOES-18 ABI",
            "type": "Advanced Baseline Imager",
            "basin": "Atlantic & Eastern Pacific",
            "channels": ["Band 13 Clean IR", "Band 14 IR Longwave"],
            "status": "Not connected",
            "note": "Scheduled for multi-basin expansion",
        },
        {
            "name": "ECMWF / ERA5 Reanalysis",
            "type": "Atmospheric Reanalysis & Environmental Fields",
            "basin": "Global",
            "channels": ["Vertical Wind Shear (VWS)", "Sea Surface Temperature (SST)", "Relative Humidity"],
            "status": "Awaiting data source",
            "note": "Environmental field integration",
        },
    ]
    return success_response(data={"data_sources": sources, "connected_count": 0})


@router.get("/models", summary="AI/ML model inventory and deployment status")
def get_models_status(current_user: User = Depends(get_current_user)):
    """Status of AI inference models adhering to the no-fake-prediction principle."""
    models = [
        {
            "name": "CycloneNet-Detect",
            "target": "Cyclone Detection & Center Localization",
            "architecture": "ResNet-50 Feature Pyramid Network",
            "status": "Model not deployed",
            "deployed": False,
            "version": "v0.1.0-uninitialized",
            "note": "Sprint 1 foundation phase. Training pipeline begins in Sprint 2.",
        },
        {
            "name": "CycloneNet-Intensity",
            "target": "Current Intensity (Vmax & MSLP) Estimation",
            "architecture": "Multi-Modal Convolutional Vision Transformer (ViT)",
            "status": "Model not deployed",
            "deployed": False,
            "version": "v0.1.0-uninitialized",
            "note": "Awaiting satellite data training set.",
        },
        {
            "name": "CycloneNet-RI",
            "target": "Rapid Intensification (RI) 24h Risk Classification",
            "architecture": "Spatio-Temporal ConvLSTM + Environmental Gated Network",
            "status": "Model not deployed",
            "deployed": False,
            "version": "v0.1.0-uninitialized",
            "note": "RI definition: >= 30 knot increase in 24 hours.",
        },
        {
            "name": "CycloneNet-Explain",
            "target": "Explainable AI (Grad-CAM & Atmospheric Attribution)",
            "architecture": "Gradient-weighted Class Activation Mapping",
            "status": "Model not deployed",
            "deployed": False,
            "version": "v0.1.0-uninitialized",
            "note": "Provides meteorologist-interpretable saliency maps.",
        },
    ]
    return success_response(data={"models": models, "active_deployments": 0})


@router.get("/predictions", summary="Recent AI model predictions")
def list_predictions(current_user: User = Depends(get_current_user)):
    return success_response(data={
        "predictions": [],
        "total": 0,
        "status": "Coming in the next development phase",
        "message": "AI prediction engine is not deployed in Sprint 1."
    })


@router.get("/alerts", summary="Operational meteorological alerts")
def list_alerts(current_user: User = Depends(get_current_user)):
    return success_response(data={
        "alerts": [],
        "total": 0,
        "status": "Awaiting data source and detection pipeline",
        "message": "No active alerts issued."
    })
