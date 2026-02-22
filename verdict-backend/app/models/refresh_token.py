from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class RefreshToken(Base):
    __tablename__ = "RefreshToken"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column("userId", String, ForeignKey("User.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column("tokenHash", String, unique=True)
    device_info: Mapped[str | None] = mapped_column("deviceInfo", String, nullable=True)
    expires_at: Mapped[DateTime] = mapped_column("expiresAt", DateTime)
    revoked_at: Mapped[DateTime | None] = mapped_column("revokedAt", DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
