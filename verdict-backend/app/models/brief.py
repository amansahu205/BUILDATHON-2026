from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Brief(Base):
    __tablename__ = "Brief"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column("sessionId", String, ForeignKey("Session.id", ondelete="CASCADE"), unique=True)
    firm_id: Mapped[str] = mapped_column("firmId", String)
    witness_id: Mapped[str] = mapped_column("witnessId", String)
    session_score: Mapped[int] = mapped_column("sessionScore", Integer)
    consistency_rate: Mapped[float] = mapped_column("consistencyRate", Float)
    delta_vs_baseline: Mapped[int | None] = mapped_column("deltaVsBaseline", Integer, nullable=True)
    confirmed_flags: Mapped[int] = mapped_column("confirmedFlags", Integer, default=0)
    objection_count: Mapped[int] = mapped_column("objectionCount", Integer, default=0)
    composure_alerts: Mapped[int] = mapped_column("composureAlerts", Integer, default=0)
    top_recommendations: Mapped[list] = mapped_column("topRecommendations", ARRAY(String), default=list)
    narrative_text: Mapped[str] = mapped_column("narrativeText", String)
    pdf_s3_key: Mapped[str | None] = mapped_column("pdfS3Key", String, nullable=True)
    share_token: Mapped[str | None] = mapped_column("shareToken", String, nullable=True, unique=True)
    share_token_expires_at: Mapped[DateTime | None] = mapped_column("shareTokenExpiresAt", DateTime, nullable=True)
    weakness_map_scores: Mapped[dict | None] = mapped_column("weaknessMapScores", JSON, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    session: Mapped["Session"] = relationship("Session", back_populates="brief")
    annotations: Mapped[list["AttorneyAnnotation"]] = relationship("AttorneyAnnotation", back_populates="brief")
