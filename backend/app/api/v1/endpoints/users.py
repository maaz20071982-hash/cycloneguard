from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.responses import success_response
from app.core.exceptions import AuthorizationError
from app.schemas.user import UserResponse, UsersListResponse, UserSummary, UserPasswordChangeRequest
from app.services.user_service import UserService
from app.api.v1.deps import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.post("/change-password", status_code=status.HTTP_200_OK, summary="Change current user password")
def change_password(
    payload: UserPasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update password for the currently authenticated user."""
    user_service = UserService(db)
    user_service.change_password(
        user_id=current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return success_response(data={"message": "Password successfully updated"})


@router.get("", status_code=status.HTTP_200_OK, summary="List all registered platform users (Admin only)")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve paginated user accounts. Strictly requires ADMIN role."""
    user_service = UserService(db)
    users, total = user_service.list_users(skip=skip, limit=limit)
    response_data = {
        "users": [UserSummary.model_validate(u).model_dump() for u in users],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
    return success_response(data=response_data)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, summary="Get user details by ID")
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve profile for a specific user ID. Restricted to user self or admin."""
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise AuthorizationError("Access denied: You can only view your own user profile")

    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    return success_response(data=UserResponse.model_validate(user).model_dump())
