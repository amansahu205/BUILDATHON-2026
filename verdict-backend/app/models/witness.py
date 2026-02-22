from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

_WITNESS_ROLE_ENUM = PgEnum(
    'DEFENDANT', 'PLAINTIFF', 'EXPERT', 'CORPORATE_REPRESENTATIVE', 'OTHER',
    name='WitnessRole', create_type=False,
)


class Witness(Base):
    __tablename__ = "Witness"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column("caseId", String, ForeignKey("Case.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    name: Mapped[str] = mapped_column("name", String)
    email: Mapped[str] = mapped_column("email", String)
    role: Mapped[str] = mapped_column("role", _WITNESS_ROLE_ENUM)
    notes: Mapped[str | None] = mapped_column("notes", String, nullable=True)
    linked_document_ids: Mapped[list] = mapped_column("linkedDocumentIds", ARRAY(String), default=list)
    session_count: Mapped[int] = mapped_column("sessionCount", Integer, default=0)
    latest_score: Mapped[int | None] = mapped_column("latestScore", Integer, nullable=True)
    baseline_score: Mapped[int | None] = mapped_column("baselineScore", Integer, nullable=True)
    plateau_detected: Mapped[bool] = mapped_column("plateauDetected", Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="witnesses")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="witness")
