from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, JSON, Enum as PgEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

_SESSION_STATUS_ENUM = PgEnum(
    'LOBBY', 'ACTIVE', 'PAUSED', 'COMPLETE', 'ABANDONED',
    name='SessionStatus', create_type=False,
)

_AGGRESSION_ENUM = PgEnum(
    'STANDARD', 'ELEVATED', 'HIGH_STAKES',
    name='Aggression', create_type=False,
)


class Session(Base):
    __tablename__ = "Session"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column("caseId", String, ForeignKey("Case.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    witness_id: Mapped[str] = mapped_column("witnessId", String, ForeignKey("Witness.id", ondelete="CASCADE"))
    attorney_id: Mapped[str | None] = mapped_column("attorneyId", String, nullable=True)
    session_number: Mapped[int] = mapped_column("sessionNumber", Integer, default=1)
    status: Mapped[str] = mapped_column("status", _SESSION_STATUS_ENUM, default="LOBBY")
    duration_minutes: Mapped[int] = mapped_column("durationMinutes", Integer)
    aggression: Mapped[str] = mapped_column("aggression", _AGGRESSION_ENUM, default="STANDARD")
    focus_areas: Mapped[list] = mapped_column("focusAreas", ARRAY(String), default=list)
    objection_copilot_enabled: Mapped[bool] = mapped_column("objectionCopilotEnabled", Boolean, default=True)
    sentinel_enabled: Mapped[bool] = mapped_column("sentinelEnabled", Boolean, default=False)
    witness_token: Mapped[str | None] = mapped_column("witnessToken", String, nullable=True, unique=True)
    witness_joined: Mapped[bool] = mapped_column("witnessJoined", Boolean, default=False)
    witness_joined_at: Mapped[DateTime | None] = mapped_column("witnessJoinedAt", DateTime, nullable=True)
    started_at: Mapped[DateTime | None] = mapped_column("startedAt", DateTime, nullable=True)
    ended_at: Mapped[DateTime | None] = mapped_column("endedAt", DateTime, nullable=True)
    paused_at: Mapped[DateTime | None] = mapped_column("pausedAt", DateTime, nullable=True)
    total_pause_ms: Mapped[int] = mapped_column("totalPauseMs", Integer, default=0)
    question_count: Mapped[int] = mapped_column("questionCount", Integer, default=0)
    session_score: Mapped[int | None] = mapped_column("sessionScore", Integer, nullable=True)
    consistency_rate: Mapped[float | None] = mapped_column("consistencyRate", Float, nullable=True)
    transcript_raw: Mapped[str | None] = mapped_column("transcriptRaw", String, nullable=True)
    nia_session_context_id: Mapped[str | None] = mapped_column("niaSessionContextId", String, nullable=True)
    prior_weak_areas: Mapped[dict | None] = mapped_column("priorWeakAreas", JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="sessions")
    witness: Mapped["Witness"] = relationship("Witness", back_populates="sessions")
    events: Mapped[list["SessionEvent"]] = relationship("SessionEvent", back_populates="session", cascade="all, delete")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="session", cascade="all, delete")
    brief: Mapped["Brief | None"] = relationship("Brief", back_populates="session", uselist=False)
    annotations: Mapped[list["AttorneyAnnotation"]] = relationship("AttorneyAnnotation", back_populates="session", cascade="all, delete")
