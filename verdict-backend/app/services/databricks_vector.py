"""
Databricks Vector Search service.

Calls a FastAPI retrieval proxy (e.g. http://127.0.0.1:8000/api/retrieve)
that wraps Databricks Vector Search indexes:

  verdict.sessions.fre_rules_index
    — Full FRE corpus (Rules 101–1103).  Queried by Objection Copilot.

  verdict.sessions.prior_statements_index
    — Prior sworn statements extracted from uploaded case documents.
    — Filtered by case_id for firm-level isolation.

The proxy accepts POST requests with a JSON body and returns matching documents.
Authentication is via Bearer token in the Authorization header.
"""

import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _databricks_configured() -> bool:
    return bool(settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN)


def _build_url() -> str:
    host = settings.DATABRICKS_HOST.rstrip("/")
    path = settings.DATABRICKS_RETRIEVE_PATH
    return f"{host}{path}"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }


def _normalize_results(resp_data: dict | list) -> list[dict]:
    """Normalize various response formats into a flat list of dicts."""
    if isinstance(resp_data, list):
        return resp_data

    if isinstance(resp_data, dict):
        if "results" in resp_data:
            return resp_data["results"] if isinstance(resp_data["results"], list) else []
        if "data" in resp_data:
            return resp_data["data"] if isinstance(resp_data["data"], list) else []
        if "manifest" in resp_data and "result" in resp_data:
            cols = [c["name"] for c in resp_data.get("manifest", {}).get("columns", [])]
            rows = resp_data.get("result", {}).get("data_array", [])
            return [dict(zip(cols, row)) for row in rows]
        return [resp_data]

    return []


# ── FRE Rules Index (Objection Copilot) ────────────────────────────────────

async def search_fre_rules(query: str, top_k: int = 3, deposition_only: bool = True) -> list[dict]:
    """Search the FRE corpus index via the retrieval proxy.

    Returns a list of dicts with at least a 'content' key.
    Returns [] gracefully when Databricks is not configured or unavailable.
    """
    if not _databricks_configured():
        logger.warning("Databricks not configured — FRE search returning empty")
        return []

    payload = {
        "query": query,
        "index_name": settings.DATABRICKS_FRE_INDEX,
        "endpoint_name": settings.DATABRICKS_VECTOR_ENDPOINT,
        "num_results": top_k,
        "columns": ["content", "rule_number", "article", "is_deposition_relevant"],
    }
    if deposition_only:
        payload["filters"] = {"is_deposition_relevant": "true"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(_build_url(), json=payload, headers=_headers())
            resp.raise_for_status()
            return _normalize_results(resp.json())
    except Exception as exc:
        logger.error("Databricks FRE search failed: %s", exc)
        return []


# ── Prior Statements Index (Inconsistency Detector + Interrogator) ──────────

async def search_prior_statements(
    case_id: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Search prior sworn statements for a specific case via the retrieval proxy.

    Returns a list of dicts with at least 'content', 'page', 'line' keys.
    Returns [] gracefully when Databricks is not configured or unavailable.
    """
    if not _databricks_configured():
        logger.warning("Databricks not configured — prior statement search returning empty")
        return []

    payload = {
        "query": query,
        "index_name": settings.DATABRICKS_VECTOR_INDEX,
        "endpoint_name": settings.DATABRICKS_VECTOR_ENDPOINT,
        "num_results": top_k,
        "columns": ["content", "page", "line", "doc_type", "witness_name"],
        "filters": {"case_id": case_id},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(_build_url(), json=payload, headers=_headers())
            resp.raise_for_status()
            return _normalize_results(resp.json())
    except Exception as exc:
        logger.error("Databricks prior-statement search failed: %s", exc)
        return []


# ── Upsert (Document Ingestion Pipeline) ────────────────────────────────────

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
    Sends to the retrieval proxy's upsert endpoint (same base, /api/upsert or
    falls back to including an 'action' field in the retrieve payload).
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

    host = settings.DATABRICKS_HOST.rstrip("/")
    upsert_url = f"{host}/api/upsert"

    payload = {
        "index_name": settings.DATABRICKS_VECTOR_INDEX,
        "endpoint_name": settings.DATABRICKS_VECTOR_ENDPOINT,
        "data": record,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(upsert_url, json=payload, headers=_headers())
            if resp.status_code == 404:
                payload_alt = {
                    "action": "upsert",
                    "index_name": settings.DATABRICKS_VECTOR_INDEX,
                    "record": record,
                }
                resp = await client.post(_build_url(), json=payload_alt, headers=_headers())
            resp.raise_for_status()
            return True
    except Exception as exc:
        logger.error("Databricks upsert failed for doc %s: %s", document_id, exc)
        return False
