from sqlalchemy import String, Boolean, Integer, BigInteger, DateTime, ForeignKey, JSON, Enum as PgEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

_DOCUMENT_TYPE_ENUM = PgEnum(
    'PRIOR_DEPOSITION', 'MEDICAL_RECORDS', 'FINANCIAL_RECORDS',
    'CORRESPONDENCE', 'EXHIBIT', 'OTHER',
    name='DocumentType', create_type=False,
)
_INGESTION_STATUS_ENUM = PgEnum(
    'PENDING', 'UPLOADING', 'INDEXING', 'READY', 'FAILED',
    name='IngestionStatus', create_type=False,
)


class Document(Base):
    __tablename__ = "Document"

    id: Mapped[str] = mapped_column("id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column("caseId", String, ForeignKey("Case.id", ondelete="CASCADE"))
    firm_id: Mapped[str] = mapped_column("firmId", String)
    uploader_id: Mapped[str | None] = mapped_column("uploaderId", String, nullable=True)
    filename: Mapped[str] = mapped_column("filename", String)
    s3_key: Mapped[str] = mapped_column("s3Key", String, unique=True)
    file_size_bytes: Mapped[int] = mapped_column("fileSizeBytes", BigInteger)
    mime_type: Mapped[str] = mapped_column("mimeType", String)
    doc_type: Mapped[str] = mapped_column("docType", _DOCUMENT_TYPE_ENUM)
    page_count: Mapped[int | None] = mapped_column("pageCount", Integer, nullable=True)
    ingestion_status: Mapped[str] = mapped_column("ingestionStatus", _INGESTION_STATUS_ENUM, default="PENDING")
    ingestion_started_at: Mapped[DateTime | None] = mapped_column("ingestionStartedAt", DateTime, nullable=True)
    ingestion_completed_at: Mapped[DateTime | None] = mapped_column("ingestionCompletedAt", DateTime, nullable=True)
    ingestion_error: Mapped[str | None] = mapped_column("ingestionError", String, nullable=True)
    nia_index_id: Mapped[str | None] = mapped_column("niaIndexId", String, nullable=True)
    extracted_facts: Mapped[dict | None] = mapped_column("extractedFacts", JSON, nullable=True)
    facts_confirmed_at: Mapped[DateTime | None] = mapped_column("factsConfirmedAt", DateTime, nullable=True)
    file_hash: Mapped[str | None] = mapped_column("fileHash", String, nullable=True)
    version: Mapped[int] = mapped_column("version", Integer, default=1)
    created_at: Mapped[DateTime] = mapped_column("createdAt", DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    case: Mapped["Case"] = relationship("Case", back_populates="documents")
