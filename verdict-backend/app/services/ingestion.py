"""
Document ingestion pipeline.

Orchestrates the full flow:
  1. Download file from S3
  2. Extract text (PDF/DOCX/TXT)
  3. Claude fact extraction (parties, dates, disputed facts, prior statements)
  4. Upsert prior statement chunks into Databricks Vector Search
  5. Update document record with status progression
"""

import hashlib
import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.services.s3 import download_bytes
from app.services.text_extraction import extract_text, ExtractedChunk
from app.services.claude import claude_chat
from app.services.databricks_vector import upsert_prior_statement

logger = logging.getLogger(__name__)

FACT_EXTRACTION_SYSTEM = """You are a legal document analyst. Extract structured facts from the provided document text.
Respond ONLY with valid JSON matching the exact format specified. No preamble, no markdown."""

FACT_EXTRACTION_PROMPT = """Analyze this document text and extract:

Document Text:
{text}

Return JSON:
{{
  "parties": [
    {{"name": "<full name>", "role": "<plaintiff/defendant/expert/witness/other>"}}
  ],
  "keyDates": [
    {{"date": "<date string>", "event": "<what happened>", "source": "<where in doc>"}}
  ],
  "disputedFacts": [
    {{"fact": "<the disputed fact>", "context": "<surrounding context>"}}
  ],
  "priorStatements": [
    {{"content": "<exact statement>", "speaker": "<who said it>", "context": "<context>"}}
  ]
}}

If a section has no relevant data, return an empty array for it."""


def compute_file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


async def extract_facts_with_claude(text: str) -> dict:
    """Use Claude to extract structured facts from document text."""
    truncated = text[:15000]
    prompt = FACT_EXTRACTION_PROMPT.format(text=truncated)

    try:
        raw = await claude_chat(FACT_EXTRACTION_SYSTEM, prompt, max_tokens=2000)
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
        return json.loads(clean)
    except Exception as exc:
        logger.error("Claude fact extraction failed: %s", exc)
        return {
            "parties": [],
            "keyDates": [],
            "disputedFacts": [],
            "priorStatements": [],
        }


async def run_ingestion(document: Document, db: AsyncSession) -> None:
    """Run the full ingestion pipeline for a document.

    Updates the document record in-place with status transitions.
    Caller is responsible for committing the session.
    """
    try:
        document.ingestion_status = "UPLOADING"
        document.ingestion_started_at = datetime.utcnow()
        await db.commit()

        file_data = download_bytes(document.s3_key)

        file_hash = compute_file_hash(file_data)
        document.file_hash = file_hash

        document.ingestion_status = "INDEXING"
        await db.commit()

        chunks = extract_text(file_data, document.mime_type)
        document.page_count = max(
            (c.page for c in chunks if c.page is not None), default=len(chunks)
        )

        full_text = "\n\n".join(c.content for c in chunks)

        extracted_facts = await extract_facts_with_claude(full_text)
        document.extracted_facts = extracted_facts

        upsert_count = 0
        for chunk in chunks:
            success = await upsert_prior_statement(
                case_id=document.case_id,
                document_id=document.id,
                content=chunk.content,
                page=chunk.page,
                line=chunk.line,
                doc_type=document.doc_type,
                witness_name=None,
            )
            if success:
                upsert_count += 1

        if extracted_facts.get("priorStatements"):
            for stmt in extracted_facts["priorStatements"]:
                await upsert_prior_statement(
                    case_id=document.case_id,
                    document_id=document.id,
                    content=stmt.get("content", ""),
                    page=None,
                    line=None,
                    doc_type=document.doc_type,
                    witness_name=stmt.get("speaker"),
                )

        document.ingestion_status = "READY"
        document.ingestion_completed_at = datetime.utcnow()
        document.ingestion_error = None
        await db.commit()

        logger.info(
            "Ingestion complete for %s: %d chunks, %d upserted to Databricks",
            document.id, len(chunks), upsert_count,
        )

    except ValueError as exc:
        document.ingestion_status = "FAILED"
        document.ingestion_error = str(exc)
        document.ingestion_completed_at = datetime.utcnow()
        await db.commit()
        logger.error("Ingestion failed for %s: %s", document.id, exc)

    except Exception as exc:
        document.ingestion_status = "FAILED"
        document.ingestion_error = f"Unexpected error: {exc}"
        document.ingestion_completed_at = datetime.utcnow()
        await db.commit()
        logger.error("Ingestion failed for %s: %s", document.id, exc)
