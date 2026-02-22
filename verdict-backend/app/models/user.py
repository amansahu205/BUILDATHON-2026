from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

_USER_ROLE_ENUM = PgEnum(
    'PARTNER', 'ASSOCIATE', 'PARALEGAL', 'ADMIN',
    name='Role', create_type=False,
)


class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_id: Mapped[str] = mapped_column("firmId", String, ForeignKey("Firm.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column("email", String, unique=True)
    name: Mapped[str] = mapped_column("name", String)
    role: Mapped[str] = mapped_column("role", _USER_ROLE_ENUM)
    password_hash: Mapped[str | None] = mapped_column("passwordHash", String, nullable=True)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column("emailVerified", Boolean, default=False)
    last_login_at: Mapped[DateTime | None] = mapped_column("lastLoginAt", DateTime, nullable=True)
    login_attempts: Mapped[int] = mapped_column("loginAttempts", Integer, default=0)
    locked_until: Mapped[DateTime | None] = mapped_column("lockedUntil", DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    firm: Mapped["Firm"] = relationship("Firm", back_populates="users")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete")
    owned_cases: Mapped[list["Case"]] = relationship("Case", back_populates="owner", foreign_keys="Case.owner_id")
    annotations: Mapped[list["AttorneyAnnotation"]] = relationship("AttorneyAnnotation", back_populates="user")
