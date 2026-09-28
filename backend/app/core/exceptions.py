from typing import Optional, Dict, Any
from fastapi import status


class AppException(Exception):
    """Base application exception with standardized code and status code."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(AppException):
    def __init__(self, message: str = "Invalid credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN_ACCESS",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class BadRequestError(AppException):
    def __init__(self, message: str = "Invalid request", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ModelUnavailableError(AppException):
    def __init__(self, message: str = "AI Model is not deployed or connected in current phase"):
        super().__init__(
            message=message,
            code="MODEL_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class FeatureContractInvalidError(AppException):
    def __init__(self, message: str = "Input observation violates 61-feature contract", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FEATURE_CONTRACT_INVALID",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class SatelliteDataUnavailableError(AppException):
    def __init__(self, message: str = "Satellite structural evidence unavailable for this observation", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SATELLITE_DATA_UNAVAILABLE",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class TemporalDataUnavailableError(AppException):
    def __init__(self, message: str = "Temporal kinematic evidence unavailable for this observation", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="TEMPORAL_DATA_UNAVAILABLE",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ObservationNotFoundError(AppException):
    def __init__(self, message: str = "Cyclone observation not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="OBSERVATION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class PredictionFailedError(AppException):
    def __init__(self, message: str = "Prediction computation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="PREDICTION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class NoPredictionAvailableError(AppException):
    def __init__(self, message: str = "No prediction records available", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NO_PREDICTION_AVAILABLE",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )

