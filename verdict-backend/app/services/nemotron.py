import httpx
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


async def score_contradiction(
    witness_answer: str,
    prior_statements: list[dict],
    case_context: str,
) -> dict:
    prompt = f"""You are analyzing a witness deposition for contradictions.

Case context: {case_context}

Witness answer just given:
\"{witness_answer}\"

Prior sworn statements on record:
{chr(10).join(f'[{i}] "{s.get("content", "")}"' for i, s in enumerate(prior_statements))}

Respond ONLY with JSON:
{{
  "contradiction_confidence": <float 0.0-1.0>,
  "best_match_index": <integer index of most contradicted statement, or -1>,
  "reasoning": "<one sentence>"
}}"""

    headers = {
        "Authorization": f"Bearer {settings.NEMOTRON_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.NEMOTRON_HTTP_REFERER:
        headers["HTTP-Referer"] = settings.NEMOTRON_HTTP_REFERER
    if settings.NEMOTRON_X_TITLE:
        headers["X-Title"] = settings.NEMOTRON_X_TITLE

    async with httpx.AsyncClient(
        base_url=settings.NEMOTRON_BASE_URL,
        headers=headers,
        timeout=settings.NEMOTRON_TIMEOUT_MS / 1000,
    ) as client:
        resp = await client.post("/chat/completions", json={
            "model": settings.NEMOTRON_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.1,
        })
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        clean = content.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
        return json.loads(clean.strip())
