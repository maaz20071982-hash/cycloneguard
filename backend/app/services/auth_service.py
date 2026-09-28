from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.repositories.audit_repo import AuditRepository
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.schemas.token import LoginSuccessData
from app.schemas.user import UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register(self, payload: UserRegisterRequest) -> User:
        """Register a new user account with secure password hashing."""
        clean_email = payload.email.lower().strip()

        # Check existing user
        if self.user_repo.email_exists(clean_email):
            raise ConflictError("An account with this email address already exists")

        # Password strength checks
        if len(payload.password) < 8:
            raise ValidationError("Password must contain at least 8 characters")

        hashed_pwd = hash_password(payload.password)
        role = payload.role if payload.role else UserRole.USER

        user = self.user_repo.create_user(
            name=payload.name,
            email=clean_email,
            password_hash=hashed_pwd,
            role=role,
            is_active=True,
        )
        return user

    def login(self, payload: UserLoginRequest) -> LoginSuccessData:
        """Authenticate user and return JWT bearer token with user profile."""
        clean_email = payload.email.lower().strip()
        user = self.user_repo.get_by_email(clean_email)

        # Consistent rejection to prevent email enumeration
        if not user or not user.is_active:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        token = create_access_token(
            subject=user.id,
            role=user.role.value,
            extra_claims={"name": user.name, "email": user.email}
        )

        # Record ADMIN_LOGIN audit trail event if an administrator logs in
        if user.role == UserRole.ADMIN:
            self.audit_repo.log(
                action="ADMIN_LOGIN",
                resource_type="SESSION",
                resource_id=user.id,
                user_id=user.id,
                metadata={
                    "admin_email": user.email,
                    "admin_name": user.name,
                },
            )

        return LoginSuccessData(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def logout(self, current_user: User) -> None:
        """Handle user session termination and record audit log for administrative accounts."""
        if current_user.role == UserRole.ADMIN:
            self.audit_repo.log(
                action="ADMIN_LOGOUT",
                resource_type="SESSION",
                resource_id=current_user.id,
                user_id=current_user.id,
                metadata={
                    "admin_email": current_user.email,
                    "admin_name": current_user.name,
                },
            )
