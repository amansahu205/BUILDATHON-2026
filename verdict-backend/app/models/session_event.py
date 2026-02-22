from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class SessionEvent(Base):
    __tablename__ = "SessionEvent"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column("sessionId", String, ForeignKey("Session.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    event_type: Mapped[str] = mapped_column("eventType", String)
    speaker_role: Mapped[str | None] = mapped_column("speakerRole", String, nullable=True)
    content: Mapped[str | None] = mapped_column("content", String, nullable=True)
    question_number: Mapped[int | None] = mapped_column("questionNumber", Integer, nullable=True)
    audio_s3_key: Mapped[str | None] = mapped_column("audioS3Key", String, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column("durationMs", Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())

    session: Mapped["Session"] = relationship("Session", back_populates="events")
