from elevenlabs.client import AsyncElevenLabs
from app.config import settings

eleven = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

VOICES = {
    "INTERROGATOR": settings.ELEVENLABS_INTERROGATOR_VOICE_ID,
    "COACH": settings.ELEVENLABS_COACH_VOICE_ID,
}


async def text_to_speech(text: str, voice_id: str = "") -> bytes:
    vid = voice_id or VOICES["INTERROGATOR"]
    audio = await eleven.text_to_speech.convert(
        voice_id=vid,
        text=text,
        model_id="eleven_turbo_v2_5",
    )
    chunks = []
    async for chunk in audio:
        chunks.append(chunk)
    return b"".join(chunks)


async def speech_to_text(audio_bytes: bytes) -> str:
    from io import BytesIO
    result = await eleven.speech_to_text.convert(
        file=BytesIO(audio_bytes),
        model_id="scribe_v1",
    )
    return result.text or ""
