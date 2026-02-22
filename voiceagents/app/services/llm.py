"""
LLM client for transcript analysis.

Calls the Anthropic Messages API to produce a structured deposition
report. Falls back to None if no API key is configured, letting the
caller use the rule-based engine instead.
"""

import json
import httpx

from ..config import settings


async def analyze_transcript(
    system_prompt: str,
    transcript_text: str,
) -> dict | None:
    """Send the transcript to Claude for analysis.

    Returns the parsed JSON report dict, or None if no Anthropic key
    is configured or the call fails.
    """
    if not settings.anthropic_api_key:
        return None

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.anthropic_model,
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Analyze the following deposition transcript and "
                            "return your JSON report.\n\n"
                            "--- TRANSCRIPT START ---\n"
                            f"{transcript_text}\n"
                            "--- TRANSCRIPT END ---"
                        ),
                    }
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()

    raw_text = data["content"][0]["text"].strip()

    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw_text = "\n".join(lines)

    return json.loads(raw_text)
