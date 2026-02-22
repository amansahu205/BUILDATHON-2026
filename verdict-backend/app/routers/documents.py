"""
Document management endpoints — upload, ingestion, and fact review.

Implements P0.4 (Case File Ingestion Pipeline) from the PRD.
"""

import asyncio
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, AsyncSessionLocal
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.case import Case
from app.models.document import Document
from app.services.s3 import build_s3_key, generate_presigned_upload, generate_presigned_download
from app.services.ingestion import run_ingestion

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


class UploadRequest(BaseModel):
    filename: str
    mimeType: str
    fileSizeBytes: int
    docType: str = "OTHER"


class ConfirmUploadRequest(BaseModel):
    documentId: str


class ConfirmFactsRequest(BaseModel):
    sections: list[str]


# ── Upload Flow ──────────────────────────────────────────────────────

@router.post("/cases/{case_id}/documents/upload")
async def request_upload(
    case_id: str,
    body: UploadRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Step 1: Request a presigned S3 upload URL.

    Creates a Document record in PENDING status and returns a presigned PUT URL
    for the client to upload directly to S3.
    """
    case = await _get_case(case_id, user, db)

    if body.mimeType not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, detail={
            "code": "UNSUPPORTED_FORMAT",
            "message": f"File type {body.mimeType} not supported. Use PDF, DOCX, or TXT.",
        })

    if body.fileSizeBytes > MAX_FILE_SIZE:
        raise HTTPException(400, detail={
            "code": "FILE_TOO_LARGE",
            "message": f"File is {body.fileSizeBytes // (1024*1024)}MB — max is 200MB.",
        })

    s3_key = build_s3_key(user.firm_id, case_id, body.filename)
    presigned_url = generate_presigned_upload(s3_key, body.mimeType)

    doc = Document(
        case_id=case_id,
        firm_id=user.firm_id,
        uploader_id=user.id,
        filename=body.filename,
        s3_key=s3_key,
        file_size_bytes=body.fileSizeBytes,
        mime_type=body.mimeType,
        doc_type=body.docType,
        ingestion_status="PENDING",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {
        "success": True,
        "data": {
            "documentId": doc.id,
            "uploadUrl": presigned_url,
            "s3Key": s3_key,
        },
    }


@router.post("/cases/{case_id}/documents/{document_id}/confirm")
async def confirm_upload(
    case_id: str,
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Step 2: Confirm upload is complete and trigger ingestion pipeline.

    After the client finishes uploading to S3 via the presigned URL,
    this endpoint kicks off the async ingestion pipeline.
    """
    await _get_case(case_id, user, db)
    doc = await _get_document(document_id, case_id, user.firm_id, db)

    if doc.ingestion_status not in ("PENDING", "FAILED"):
        raise HTTPException(400, detail={
            "code": "ALREADY_PROCESSING",
            "message": "Document is already being processed.",
        })

    background_tasks.add_task(_run_ingestion_background, document_id)

    return {
        "success": True,
        "data": {
            "documentId": doc.id,
            "status": "UPLOADING",
            "message": "Ingestion pipeline started.",
        },
    }


async def _run_ingestion_background(document_id: str):
    """Run ingestion in a background task with its own DB session."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if doc:
            await run_ingestion(doc, db)


@router.post("/cases/{case_id}/documents/{document_id}/retry")
async def retry_ingestion(
    case_id: str,
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Retry a failed ingestion."""
    await _get_case(case_id, user, db)
    doc = await _get_document(document_id, case_id, user.firm_id, db)

    if doc.ingestion_status != "FAILED":
        raise HTTPException(400, detail={
            "code": "NOT_FAILED",
            "message": "Only failed documents can be retried.",
        })

    doc.ingestion_status = "PENDING"
    doc.ingestion_error = None
    await db.commit()

    background_tasks.add_task(_run_ingestion_background, document_id)

    return {"success": True, "data": {"documentId": doc.id, "status": "PENDING"}}


# ── Document Listing & Status ────────────────────────────────────────

@router.get("/cases/{case_id}/documents")
async def list_documents(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """List all documents for a case with ingestion status."""
    await _get_case(case_id, user, db)

    result = await db.execute(
        select(Document)
        .where(Document.case_id == case_id, Document.firm_id == user.firm_id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    return {
        "success": True,
        "data": {
            "documents": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "mimeType": d.mime_type,
                    "docType": d.doc_type,
                    "fileSizeBytes": d.file_size_bytes,
                    "pageCount": d.page_count,
                    "ingestionStatus": d.ingestion_status,
                    "ingestionError": d.ingestion_error,
                    "createdAt": d.created_at.isoformat() if d.created_at else None,
                }
                for d in docs
            ],
            "total": len(docs),
            "readyCount": sum(1 for d in docs if d.ingestion_status == "READY"),
        },
    }


@router.get("/cases/{case_id}/documents/{document_id}")
async def get_document(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Get details for a single document including extracted facts."""
    await _get_case(case_id, user, db)
    doc = await _get_document(document_id, case_id, user.firm_id, db)

    download_url = None
    if doc.s3_key:
        try:
            download_url = generate_presigned_download(doc.s3_key)
        except Exception:
            pass

    return {
        "success": True,
        "data": {
            "id": doc.id,
            "filename": doc.filename,
            "mimeType": doc.mime_type,
            "docType": doc.doc_type,
            "fileSizeBytes": doc.file_size_bytes,
            "pageCount": doc.page_count,
            "ingestionStatus": doc.ingestion_status,
            "ingestionError": doc.ingestion_error,
            "extractedFacts": doc.extracted_facts,
            "factsConfirmedAt": doc.facts_confirmed_at.isoformat() if doc.facts_confirmed_at else None,
            "downloadUrl": download_url,
            "createdAt": doc.created_at.isoformat() if doc.created_at else None,
        },
    }


# ── Fact Review ──────────────────────────────────────────────────────

@router.get("/cases/{case_id}/facts")
async def get_case_facts(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Get aggregated extracted facts across all READY documents for a case."""
    await _get_case(case_id, user, db)

    result = await db.execute(
        select(Document).where(
            Document.case_id == case_id,
            Document.firm_id == user.firm_id,
            Document.ingestion_status == "READY",
        )
    )
    docs = result.scalars().all()

    parties = []
    key_dates = []
    disputed_facts = []
    prior_statements = []

    for doc in docs:
        facts = doc.extracted_facts or {}
        for p in facts.get("parties", []):
            p["sourceDocument"] = doc.filename
            parties.append(p)
        for d in facts.get("keyDates", []):
            d["sourceDocument"] = doc.filename
            key_dates.append(d)
        for f in facts.get("disputedFacts", []):
            f["sourceDocument"] = doc.filename
            disputed_facts.append(f)
        for s in facts.get("priorStatements", []):
            s["sourceDocument"] = doc.filename
            prior_statements.append(s)

    all_confirmed = all(d.facts_confirmed_at is not None for d in docs) if docs else False

    return {
        "success": True,
        "data": {
            "parties": parties,
            "keyDates": key_dates,
            "disputedFacts": disputed_facts,
            "priorStatements": prior_statements,
            "documentCount": len(docs),
            "allConfirmed": all_confirmed,
        },
    }


@router.post("/cases/{case_id}/facts/confirm")
async def confirm_facts(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Mark all extracted facts for a case as confirmed by the attorney."""
    case = await _get_case(case_id, user, db)

    result = await db.execute(
        select(Document).where(
            Document.case_id == case_id,
            Document.firm_id == user.firm_id,
            Document.ingestion_status == "READY",
        )
    )
    docs = result.scalars().all()

    if not docs:
        raise HTTPException(400, detail={
            "code": "NO_READY_DOCUMENTS",
            "message": "No documents are ready for fact confirmation.",
        })

    now = datetime.utcnow()
    for doc in docs:
        doc.facts_confirmed_at = now

    all_facts = []
    all_prior = []
    for doc in docs:
        facts = doc.extracted_facts or {}
        all_facts.extend(facts.get("disputedFacts", []))
        all_prior.extend(
            s.get("content", "") for s in facts.get("priorStatements", [])
        )

    case.extracted_facts = "\n".join(
        f.get("fact", "") for f in all_facts
    ) if all_facts else case.extracted_facts

    case.prior_statements = "\n---\n".join(all_prior) if all_prior else case.prior_statements

    await db.commit()

    return {
        "success": True,
        "data": {
            "confirmedDocuments": len(docs),
            "confirmedAt": now.isoformat(),
        },
    }


@router.delete("/cases/{case_id}/documents/{document_id}")
async def delete_document(
    case_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Delete a document and its S3 file."""
    await _get_case(case_id, user, db)
    doc = await _get_document(document_id, case_id, user.firm_id, db)

    from app.services.s3 import delete_object
    if doc.s3_key:
        try:
            delete_object(doc.s3_key)
        except Exception:
            pass

    await db.delete(doc)
    await db.commit()

    return {"success": True, "message": "Document deleted."}


# ── Helpers ──────────────────────────────────────────────────────────

async def _get_case(case_id: str, user: User, db: AsyncSession) -> Case:
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(404, detail={"code": "CASE_NOT_FOUND"})
    return case


async def _get_document(doc_id: str, case_id: str, firm_id: str, db: AsyncSession) -> Document:
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.case_id == case_id,
            Document.firm_id == firm_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, detail={"code": "DOCUMENT_NOT_FOUND"})
    return doc
