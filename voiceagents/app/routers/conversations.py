from fastapi import APIRouter, HTTPException, Query
import httpx

from ..config import settings
from ..services.elevenlabs import elevenlabs_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
async def list_conversations(
    cursor: str | None = Query(None),
    page_size: int = Query(20, ge=1, le=100),
):
    """List past conversation sessions from ElevenLabs."""
    if not settings.elevenlabs_api_key:
        raise HTTPException(500, "ELEVENLABS_API_KEY is not configured")

    try:
        return await elevenlabs_service.list_conversations(
            agent_id=settings.agent_id,
            cursor=cursor,
            page_size=page_size,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"ElevenLabs API error: {exc.response.status_code}")


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get full transcript and analysis for a single conversation."""
    if not settings.elevenlabs_api_key:
        raise HTTPException(500, "ELEVENLABS_API_KEY is not configured")

    try:
        return await elevenlabs_service.get_conversation(conversation_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(404, "Conversation not found")
        raise HTTPException(502, f"ElevenLabs API error: {exc.response.status_code}")
