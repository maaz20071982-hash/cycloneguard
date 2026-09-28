from typing import Any, Optional, Dict
from pydantic import BaseModel, Field


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class StandardResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[ErrorPayload] = None


def success_response(data: Any = None) -> Dict[str, Any]:
    """Helper to construct standard success response dictionary."""
    return {
        "success": True,
        "data": data,
        "error": None,
    }


def error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper to construct standard error response dictionary."""
    payload: Dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if details:
        payload["details"] = details

    return {
        "success": False,
        "data": None,
        "error": payload,
    }
