from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Alert(Base):
    __tablename__ = "Alert"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column("sessionId", String, ForeignKey("Session.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    alert_type: Mapped[str] = mapped_column("alertType", String)
    impeachment_risk: Mapped[str | None] = mapped_column("impeachmentRisk", String, nullable=True)
    status: Mapped[str] = mapped_column("status", String, default="PENDING")
    confidence: Mapped[float | None] = mapped_column("confidence", Float, nullable=True)
    prior_quote: Mapped[str | None] = mapped_column("priorQuote", String, nullable=True)
    prior_source_page: Mapped[int | None] = mapped_column("priorSourcePage", Integer, nullable=True)
    prior_source_line: Mapped[int | None] = mapped_column("priorSourceLine", Integer, nullable=True)
    current_quote: Mapped[str | None] = mapped_column("currentQuote", String, nullable=True)
    fre_rule: Mapped[str | None] = mapped_column("freRule", String, nullable=True)
    fre_classification: Mapped[str | None] = mapped_column("freClassification", String, nullable=True)
    composure_data: Mapped[dict | None] = mapped_column("composureData", JSON, nullable=True)
    question_number: Mapped[int | None] = mapped_column("questionNumber", Integer, nullable=True)
    confirmed_at: Mapped[DateTime | None] = mapped_column("confirmedAt", DateTime, nullable=True)
    rejected_at: Mapped[DateTime | None] = mapped_column("rejectedAt", DateTime, nullable=True)
    annotated_at: Mapped[DateTime | None] = mapped_column("annotatedAt", DateTime, nullable=True)
    annotation: Mapped[str | None] = mapped_column("annotation", String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    session: Mapped["Session"] = relationship("Session", back_populates="alerts")
