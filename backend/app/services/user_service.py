from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError, AuthenticationError, BadRequestError, AuthorizationError
from app.core.security import verify_password, hash_password
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.services.audit_service import AuditService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    def get_by_id(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} was not found")
        return user

    def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        return self.user_repo.list_filtered(skip=skip, limit=limit, role=role, is_active=is_active)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = self.get_by_id(user_id)
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("The current password provided is incorrect")
        user.password_hash = hash_password(new_password)
        self.db.add(user)
        self.db.commit()

    def update_user(
        self,
        user_id: str,
        current_admin: User,
        name: Optional[str] = None,
        role: Optional[UserRole] = None,
    ) -> User:
        """Update user properties (name, role) with administrative safety rules."""
        target_user = self.get_by_id(user_id)

        # Safety rule: Admin cannot remove their own ADMIN role (prevent lockout)
        if target_user.id == current_admin.id and role is not None and role != UserRole.ADMIN:
            raise BadRequestError(
                "Administrators cannot revoke their own administrative privileges to prevent system lockout."
            )

        old_role = target_user.role
        role_changed = False

        if name is not None and name.strip():
            target_user.name = name.strip()

        if role is not None and role != old_role:
            target_user.role = role
            role_changed = True

        self.db.add(target_user)
        self.db.commit()
        self.db.refresh(target_user)

        # Audit log creation
        if role_changed:
            self.audit_service.record_event(
                action="USER_ROLE_CHANGED",
                resource_type="USER",
                resource_id=target_user.id,
                user_id=current_admin.id,
                metadata={
                    "target_email": target_user.email,
                    "target_name": target_user.name,
                    "previous_role": str(old_role.value if hasattr(old_role, "value") else old_role),
                    "new_role": str(target_user.role.value if hasattr(target_user.role, "value") else target_user.role),
                },
            )
        else:
            self.audit_service.record_event(
                action="USER_UPDATED",
                resource_type="USER",
                resource_id=target_user.id,
                user_id=current_admin.id,
                metadata={
                    "target_email": target_user.email,
                    "updated_name": target_user.name,
                },
            )

        return target_user

    def update_user_status(
        self,
        user_id: str,
        current_admin: User,
        is_active: bool,
    ) -> User:
        """Activate or deactivate user account with safety rules."""
        target_user = self.get_by_id(user_id)

        # Safety rule: Admin cannot deactivate their own account
        if target_user.id == current_admin.id and not is_active:
            raise BadRequestError(
                "Administrators cannot deactivate their own account to prevent system lockout."
            )

        previous_status = target_user.is_active
        if previous_status == is_active:
            return target_user

        target_user.is_active = is_active
        self.db.add(target_user)
        self.db.commit()
        self.db.refresh(target_user)

        action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
        self.audit_service.record_event(
            action=action,
            resource_type="USER",
            resource_id=target_user.id,
            user_id=current_admin.id,
            metadata={
                "target_email": target_user.email,
                "target_name": target_user.name,
                "is_active": is_active,
                "previous_status": previous_status,
            },
        )

        return target_user
