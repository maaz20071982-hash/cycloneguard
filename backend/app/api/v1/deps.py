from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency that extracts, validates JWT token, and retrieves the active user."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authorization header is missing or malformed")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise AuthenticationError(str(e))

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload missing subject identifier")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError("User account associated with token no longer exists")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that enforces ADMIN role authorization on protected endpoints."""
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError("Access denied: Administrative privileges required")
    return current_user
