import httpx
import json
from app.config import settings


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

    async with httpx.AsyncClient(
        base_url=settings.NEMOTRON_BASE_URL,
        headers={"Authorization": f"Bearer {settings.NEMOTRON_API_KEY}"},
        timeout=settings.NEMOTRON_TIMEOUT_MS / 1000,
    ) as client:
        resp = await client.post("/chat/completions", json={
            "model": settings.NEMOTRON_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.1,
        })
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        return json.loads(text)
