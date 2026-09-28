from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.exceptions import ModelUnavailableError


class CycloneAIServiceInterface(ABC):
    """Abstract contract for future Cyclone AI/ML inference integrations (Phase 21).
    
    Future PyTorch/TorchScript models in subsequent sprints will implement this interface.
    The web API and UI interact solely with this contract, preventing frontend rewrites.
    """

    @abstractmethod
    def predict_cyclone(self, observation_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Detect cyclone presence, center location, and basic bounding geometry."""
        pass

    @abstractmethod
    def estimate_intensity(self, observation_id: str, satellite_channels: List[str]) -> Dict[str, Any]:
        """Estimate current maximum sustained winds (knots) and minimum sea level pressure (hPa)."""
        pass

    @abstractmethod
    def predict_ri_risk(self, cyclone_id: str, history_window_hours: int = 24) -> Dict[str, Any]:
        """Compute the probability and risk classification of Rapid Intensification (RI >= 30kt in 24h)."""
        pass

    @abstractmethod
    def predict_trend(self, cyclone_id: str, horizon_hours: int = 48) -> Dict[str, Any]:
        """Predict forward track trajectory and intensity evolution."""
        pass

    @abstractmethod
    def generate_explanation(self, prediction_id: str) -> Dict[str, Any]:
        """Produce Grad-CAM saliency maps, feature attribution weights, and meteorologist rationale."""
        pass


class PlaceholderAIService(CycloneAIServiceInterface):
    """Sprint 1 Placeholder AI implementation adhering to scientific honesty rules.
    
    Explicitly refuses to invent fake predictions or fake meteorological statistics.
    """

    def predict_cyclone(self, observation_metadata: Dict[str, Any]) -> Dict[str, Any]:
        raise ModelUnavailableError(
            "Cyclone detection model (CycloneNet-Detect) is not deployed in Sprint 1. "
            "Planned for Sprint 2 with INSAT-3D and Himawari-9 observation pipelines."
        )

    def estimate_intensity(self, observation_id: str, satellite_channels: List[str]) -> Dict[str, Any]:
        raise ModelUnavailableError(
            "Intensity estimation model (IntensityCNN) is awaiting trained weights and calibration data. "
            "No fake wind speed or pressure statistics will be generated."
        )

    def predict_ri_risk(self, cyclone_id: str, history_window_hours: int = 24) -> Dict[str, Any]:
        raise ModelUnavailableError(
            "Rapid Intensification (RI) analysis model is awaiting training datasets. "
            "Status: Coming in the next development phase."
        )

    def predict_trend(self, cyclone_id: str, horizon_hours: int = 48) -> Dict[str, Any]:
        raise ModelUnavailableError(
            "Track and intensity trend extrapolation is not deployed in Sprint 1."
        )

    def generate_explanation(self, prediction_id: str) -> Dict[str, Any]:
        raise ModelUnavailableError(
            "Explainable AI (Grad-CAM feature attribution) pipeline is scheduled for model training sprints."
        )


# Singleton instance of the current phase service
ai_service = PlaceholderAIService()
