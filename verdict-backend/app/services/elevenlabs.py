import httpx
from elevenlabs.client import AsyncElevenLabs
from app.config import settings

# Only create client when API key is set so missing key doesn't cause 401s on first use
def _client():
    if not (settings.ELEVENLABS_API_KEY or "").strip():
        return None
    return AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

eleven = _client()

VOICES = {
    "INTERROGATOR": (settings.ELEVENLABS_INTERROGATOR_VOICE_ID or "").strip(),
    "COACH": (settings.ELEVENLABS_COACH_VOICE_ID or "").strip(),
}


def _voice_available() -> bool:
    return eleven is not None and bool(VOICES.get("INTERROGATOR") or VOICES.get("COACH"))


async def text_to_speech(text: str, voice_id: str = "") -> bytes:
    if not _voice_available():
        return b""
    vid = (voice_id or VOICES["INTERROGATOR"] or "").strip()
    if not vid:
        return b""
    try:
        audio = await eleven.text_to_speech.convert(
            voice_id=vid,
            text=text,
            model_id="eleven_turbo_v2_5",
        )
        chunks = []
        async for chunk in audio:
            chunks.append(chunk)
        return b"".join(chunks)
    except Exception:
        return b""


async def speech_to_text(audio_bytes: bytes) -> str:
    if not eleven:
        return ""
    from io import BytesIO
    try:
        result = await eleven.speech_to_text.convert(
            file=BytesIO(audio_bytes),
            model_id="scribe_v1",
        )
        return (result.text or "").strip()
    except Exception:
        return ""


async def get_conversation_token(agent_id: str) -> str:
    """Get a signed WebSocket URL for an ElevenLabs Conversational AI session.
    Each URL is single-use and expires after 30 minutes.
    """
    if not (settings.ELEVENLABS_API_KEY or "").strip():
        return ""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url",
            headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
            params={"agent_id": agent_id},
        )
        resp.raise_for_status()
        return resp.json().get("signed_url", "")


def build_conversation_override(system_prompt: str, first_message: str) -> dict:
    """Build a per-session ElevenLabs conversation config override.

    Injected at session start so each witness gets a unique interrogator
    configured with their case facts — prevents race conditions from mutating
    the shared agent configuration in ElevenLabs dashboard.
    """
    return {
        "agent": {
            "prompt": {"prompt": system_prompt},
            "first_message": first_message,
        }
    }
