"""
Databricks Vector Search service.

Replaces the former Nia HTTP API.  Uses two Direct Access indexes pre-created
by scripts/setup_databricks.py:

  verdict.sessions.fre_rules_index
    — Full FRE corpus (Rules 101–1103).  Queried by Objection Copilot.
    — Filter: is_deposition_relevant = true

  verdict.sessions.prior_statements_index
    — Prior sworn statements extracted from uploaded case documents.
    — Filter: case_id = <case_id>  (firm-level isolation guaranteed by ingestion)

Both indexes use Databricks Foundation Model API (databricks-gte-large-en, 1024d)
for embedding, so only query_text is needed — no separate embedding call.

All VectorSearchClient calls are synchronous; we wrap them with
asyncio.to_thread so they don't block the FastAPI event loop.
"""

import asyncio
import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_client():
    """Return a cached VectorSearchClient.  Lazily imported so the app starts
    even when DATABRICKS_HOST / DATABRICKS_TOKEN are not yet configured."""
    from databricks.vector_search.client import VectorSearchClient  # noqa: PLC0415

    return VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
        disable_notice=True,
    )


def _parse_vs_response(resp: dict) -> list[dict]:
    """Convert the Databricks similarity_search response dict into a flat list
    of row dicts keyed by column name."""
    cols = [c["name"] for c in resp.get("manifest", {}).get("columns", [])]
    rows = resp.get("result", {}).get("data_array", [])
    return [dict(zip(cols, row)) for row in rows]


def _databricks_configured() -> bool:
    return bool(settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN)


# ── FRE Rules Index (Objection Copilot) ────────────────────────────────────

def _search_fre_sync(query: str, top_k: int) -> list[dict]:
    index = _get_client().get_index(
        endpoint_name=settings.DATABRICKS_VECTOR_ENDPOINT,
        index_name=settings.DATABRICKS_FRE_INDEX,
    )
    resp = index.similarity_search(
        query_text=query,
        columns=["content", "rule_number", "article", "is_deposition_relevant"],
        filters={"is_deposition_relevant": "true"},
        num_results=top_k,
    )
    return _parse_vs_response(resp)


async def search_fre_rules(query: str, top_k: int = 3, deposition_only: bool = True) -> list[dict]:
    """Async wrapper — search the FRE corpus index.

    Returns a list of dicts with at least a 'content' key.
    Returns [] gracefully when Databricks is not configured or unavailable.
    """
    if not _databricks_configured():
        logger.warning("Databricks not configured — FRE search returning empty")
        return []
    try:
        return await asyncio.to_thread(_search_fre_sync, query, top_k)
    except Exception as exc:
        logger.error("Databricks FRE search failed: %s", exc)
        return []


# ── Prior Statements Index (Inconsistency Detector + Interrogator) ──────────

def _search_prior_sync(case_id: str, query: str, top_k: int) -> list[dict]:
    index = _get_client().get_index(
        endpoint_name=settings.DATABRICKS_VECTOR_ENDPOINT,
        index_name=settings.DATABRICKS_VECTOR_INDEX,
    )
    resp = index.similarity_search(
        query_text=query,
        columns=["content", "page", "line", "doc_type", "witness_name"],
        filters={"case_id": case_id},
        num_results=top_k,
    )
    return _parse_vs_response(resp)


async def search_prior_statements(
    case_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Async wrapper — search prior sworn statements for a specific case.

    Returns a list of dicts with at least 'content', 'page', 'line' keys.
    Returns [] gracefully when Databricks is not configured or unavailable.
    """
    if not _databricks_configured():
        logger.warning("Databricks not configured — prior statement search returning empty")
        return []
    try:
        return await asyncio.to_thread(_search_prior_sync, case_id, query, top_k)
    except Exception as exc:
        logger.error("Databricks prior-statement search failed: %s", exc)
        return []


# ── Upsert (Document Ingestion Pipeline) ────────────────────────────────────

def _upsert_sync(record: dict) -> None:
    index = _get_client().get_index(
        endpoint_name=settings.DATABRICKS_VECTOR_ENDPOINT,
        index_name=settings.DATABRICKS_VECTOR_INDEX,
    )
    index.upsert([record])


async def upsert_prior_statement(
    case_id: str,
    document_id: str,
    content: str,
    page: int | None = None,
    line: int | None = None,
    doc_type: str = "PRIOR_DEPOSITION",
    witness_name: str | None = None,
) -> bool:
    """Upsert a single prior statement chunk into the prior statements index.

    Called by the document ingestion pipeline after text extraction.
    Returns True on success, False on any failure.
    """
    if not _databricks_configured():
        logger.warning("Databricks not configured — upsert skipped")
        return False
    record = {
        "id": f"{document_id}_{page}_{line}",
        "content": content,
        "case_id": case_id,
        "document_id": document_id,
        "page": page,
        "line": line,
        "doc_type": doc_type,
        "witness_name": witness_name,
    }
    try:
        await asyncio.to_thread(_upsert_sync, record)
        return True
    except Exception as exc:
        logger.error("Databricks upsert failed for doc %s: %s", document_id, exc)
        return False
