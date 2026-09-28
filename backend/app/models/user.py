import enum
from sqlalchemy import Column, String, Boolean, Enum
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role", native_enum=False), default=UserRole.USER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
