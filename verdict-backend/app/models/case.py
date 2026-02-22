from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

_CASE_TYPE_ENUM = PgEnum(
    'MEDICAL_MALPRACTICE', 'EMPLOYMENT_DISCRIMINATION', 'COMMERCIAL_DISPUTE',
    'CONTRACT_BREACH', 'OTHER',
    name='CaseType', create_type=False,
)


class Case(Base):
    __tablename__ = "Case"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_id: Mapped[str] = mapped_column("firmId", String, ForeignKey("Firm.id", ondelete="CASCADE"))
    owner_id: Mapped[str] = mapped_column("ownerId", String, ForeignKey("User.id"))
    case_name: Mapped[str] = mapped_column("caseName", String)
    case_type: Mapped[str] = mapped_column("caseType", _CASE_TYPE_ENUM)
    case_type_custom: Mapped[str | None] = mapped_column("caseTypeCustom", String, nullable=True)
    opposing_party: Mapped[str | None] = mapped_column("opposingParty", String, nullable=True)
    deposition_date: Mapped[DateTime | None] = mapped_column("depositionDate", DateTime, nullable=True)
    witness_name: Mapped[str | None] = mapped_column("witnessName", String, nullable=True)
    witness_role: Mapped[str | None] = mapped_column("witnessRole", String, nullable=True)
    aggression_level: Mapped[str | None] = mapped_column("aggressionLevel", String, nullable=True)
    extracted_facts: Mapped[str | None] = mapped_column("extractedFacts", Text, nullable=True)
    prior_statements: Mapped[str | None] = mapped_column("priorStatements", Text, nullable=True)
    exhibit_list: Mapped[str | None] = mapped_column("exhibitList", Text, nullable=True)
    focus_areas: Mapped[str | None] = mapped_column("focusAreas", Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column("isArchived", Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    firm: Mapped["Firm"] = relationship("Firm", back_populates="cases")
    owner: Mapped["User"] = relationship("User", back_populates="owned_cases", foreign_keys=[owner_id])
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="case", cascade="all, delete")
    witnesses: Mapped[list["Witness"]] = relationship("Witness", back_populates="case", cascade="all, delete")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="case", cascade="all, delete")
