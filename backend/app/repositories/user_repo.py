from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        normalized_email = email.lower().strip()
        return self.db.query(User).filter(User.email == normalized_email).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
        is_active: bool = True
    ) -> User:
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        return self.create(user)

    def list_all_ordered(self, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            self.db.query(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        query = self.db.query(User)
        if role is not None:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users, total

