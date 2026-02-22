import httpx
from app.config import settings


async def index_document(index_id: str, document_id: str, content: str, metadata: dict = None):
    async with httpx.AsyncClient(
        base_url=settings.NIA_BASE_URL,
        headers={"Authorization": f"Bearer {settings.NIA_API_KEY}"},
        timeout=10.0,
    ) as client:
        resp = await client.post("/index", json={
            "indexId": index_id,
            "documentId": document_id,
            "content": content,
            "metadata": metadata or {},
        })
        resp.raise_for_status()
        return resp.json()


async def search_index(index_id: str, query: str, top_k: int = 5, filters: dict = None) -> list[dict]:
    if not settings.NIA_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(
            base_url=settings.NIA_BASE_URL,
            headers={"Authorization": f"Bearer {settings.NIA_API_KEY}"},
            timeout=10.0,
        ) as client:
            resp = await client.post("/search", json={
                "indexId": index_id,
                "query": query,
                "topK": top_k,
                "filters": filters or {},
            })
            resp.raise_for_status()
            return resp.json().get("results", [])
    except Exception:
        return []
