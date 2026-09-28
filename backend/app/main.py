import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.responses import error_response
from app.api.v1.api import api_router

# Configure structured logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cycloneguard.backend")

# Initialize FastAPI application
app = FastAPI(
    title=f"{settings.APP_NAME} Intelligence Platform API",
    description=(
        "Backend REST API for CycloneGuard — an AI-powered tropical cyclone intelligence platform. "
        "Sprint 1 provides authentication, role-based authorization, database foundations, "
        "and scientific AI integration interfaces."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
origins = settings.cors_origins_list
logger.info(f"Configuring CORS with allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


@app.on_event("startup")
def on_startup():
    """Seeds historical verified benchmark cyclones if not already present."""
    try:
        from app.core.database import SessionLocal
        from app.services.cyclone_seeder import seed_historical_cyclones
        db = SessionLocal()
        seed_historical_cyclones(db)
        db.close()
        logger.info("Historical benchmark cyclones verified in database.")
    except Exception as e:
        logger.warning(f"Could not auto-seed historical cyclones on startup: {e}")



# ----------------------------------------------------
# Exception Handlers (Phase 11 & 12 Security)
# ----------------------------------------------------
@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    """Handle custom application exceptions with consistent error schema."""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details if exc.details else None,
        ),
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors without exposing internal traces."""
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        errors.append({
            "field": field_loc,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            code="VALIDATION_FAILED",
            message="Request payload validation failed",
            details={"validation_errors": errors},
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    """Handle generic Starlette / FastAPI HTTPExceptions."""
    code_map = {
        401: "AUTHENTICATION_FAILED",
        403: "FORBIDDEN_ACCESS",
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=code, message=message),
    )


@app.exception_handler(Exception)
async def handle_unhandled_exception(request: Request, exc: Exception):
    """Global catch-all preventing stack trace or internal credential leaks."""
    logger.exception(f"Unhandled server exception on path {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred. Please contact the system administrator.",
        ),
    )


# ----------------------------------------------------
# Root and API Router Mounts
# ----------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "status": "Operational (Sprint 1)",
    }


# Mount the API v1 endpoints
app.include_router(api_router, prefix="/api/v1")
