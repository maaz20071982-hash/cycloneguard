import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "CycloneGuard"
    APP_VERSION: str = "0.1.0-sprint1"
    ENVIRONMENT: str = Field(default="development", description="development, staging, production")
    DEBUG: bool = False

    # Server Binding
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./cycloneguard.db",
        description="SQLAlchemy connection URI (PostgreSQL or SQLite fallback)"
    )
    DB_ECHO: bool = False

    # Security & JWT
    JWT_SECRET: str = Field(
        default="dev-cycloneguard-insecure-secret-key-change-in-production-32bytes",
        description="JWT cryptographic signing secret"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS & Frontend Origins
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated allowed origins or list"
    )
    FRONTEND_URL: str = "http://localhost:3000"

    # Development Seeding (Strictly for dev environment)
    DEV_ADMIN_NAME: str = "Admin Officer"
    DEV_ADMIN_EMAIL: str = "admin@cycloneguard.internal"
    DEV_ADMIN_PASSWORD: str = "CycloneGuard2026!Admin"

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            # Safety check: Prevent unrestricted '*' by default in non-development environments
            if self.ENVIRONMENT.lower() == "production" and "*" in origins:
                raise ValueError("Wildcard '*' CORS origin is strictly forbidden in production.")
            return origins
        return ["http://localhost:3000"]

    @property
    def PROJECT_ROOT(self) -> str:
        """Root directory of the storm workspace."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    @property
    def resolved_database_url(self) -> str:
        """Resolve relative SQLite paths to project root to guarantee consistency regardless of cwd."""
        if self.DATABASE_URL.startswith("sqlite:///"):
            path_part = self.DATABASE_URL.replace("sqlite:///", "")
            # If not an absolute Windows path (e.g. C:/) or unix path (/), resolve relative to project root
            if not (len(path_part) > 2 and path_part[1] == ":") and not path_part.startswith("/"):
                clean_rel = path_part.lstrip("./")
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                canonical_db = os.path.join(root_dir, clean_rel).replace("\\", "/")
                return f"sqlite:///{canonical_db}"
        return self.DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
