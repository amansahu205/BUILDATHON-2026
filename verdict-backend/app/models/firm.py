from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Firm(Base):
    __tablename__ = "Firm"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column("name", String)
    slug: Mapped[str] = mapped_column("slug", String, unique=True)
    sso_metadata_url: Mapped[str | None] = mapped_column("ssoMetadataUrl", String, nullable=True)
    sso_metadata_xml: Mapped[str | None] = mapped_column("ssoMetadataXml", String, nullable=True)
    sso_enabled: Mapped[bool] = mapped_column("ssoEnabled", Boolean, default=False)
    password_login_enabled: Mapped[bool] = mapped_column("passwordLoginEnabled", Boolean, default=True)
    retention_days: Mapped[int] = mapped_column("retentionDays", Integer, default=90)
    sentinel_enabled: Mapped[bool] = mapped_column("sentinelEnabled", Boolean, default=False)
    seats: Mapped[int] = mapped_column("seats", Integer)
    plan: Mapped[str] = mapped_column("plan", String, default="trial")
    plan_expires_at: Mapped[DateTime | None] = mapped_column("planExpiresAt", DateTime, nullable=True)
    setup_complete: Mapped[bool] = mapped_column("setupComplete", Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    users: Mapped[list["User"]] = relationship("User", back_populates="firm", cascade="all, delete")
    cases: Mapped[list["Case"]] = relationship("Case", back_populates="firm", cascade="all, delete")
