from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class AttorneyAnnotation(Base):
    __tablename__ = "AttorneyAnnotation"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column("sessionId", String, ForeignKey("Session.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    user_id: Mapped[str | None] = mapped_column("userId", String, ForeignKey("User.id"), nullable=True)
    brief_id: Mapped[str | None] = mapped_column("briefId", String, ForeignKey("Brief.id"), nullable=True)
    content: Mapped[str] = mapped_column("content", String)
    timestamp_ms: Mapped[int | None] = mapped_column("timestampMs", Integer, nullable=True)
    question_number: Mapped[int | None] = mapped_column("questionNumber", Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    session: Mapped["Session"] = relationship("Session", back_populates="annotations")
    user: Mapped["User | None"] = relationship("User", back_populates="annotations")
    brief: Mapped["Brief | None"] = relationship("Brief", back_populates="annotations")
