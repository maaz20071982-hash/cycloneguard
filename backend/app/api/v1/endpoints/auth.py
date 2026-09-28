from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse
from app.schemas.token import LoginSuccessData
from app.services.auth_service import AuthService
from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user account")
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user account with validated credentials."""
    auth_service = AuthService(db)
    user = auth_service.register(payload)
    user_response = UserResponse.model_validate(user)
    return success_response(data=user_response.model_dump())


@router.post("/login", status_code=status.HTTP_200_OK, summary="Authenticate and acquire JWT access token")
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate with email and password to receive a signed JWT access token."""
    auth_service = AuthService(db)
    login_data: LoginSuccessData = auth_service.login(payload)
    return success_response(data=login_data.model_dump())


@router.get("/me", status_code=status.HTTP_200_OK, summary="Retrieve authenticated user profile")
def get_me(
    current_user: User = Depends(get_current_user)
):
    """Fetch the currently authenticated user's account details and role."""
    user_response = UserResponse.model_validate(current_user)
    return success_response(data=user_response.model_dump())


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Sign out user session")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sign out currently authenticated session. Records audit event for administrators."""
    auth_service = AuthService(db)
    auth_service.logout(current_user)
    return success_response(data={"message": "Session terminated successfully"})

