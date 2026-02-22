import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import io

from app.config import settings
from app.services.elevenlabs2 import elevenlabs_service

router = APIRouter(tags=["tts"])


class CoachingBriefRequest(BaseModel):
    """Request body for coaching brief narration."""
    report_id: str | None = None
    text: str | None = None
    voice: str = "coach"


class TTSRequest(BaseModel):
    """Generic TTS request."""
    text: str
    voice_id: str | None = None
    stability: float = 0.5
    similarity_boost: float = 0.75


@router.post("/coaching-brief")
async def narrate_coaching_brief(body: CoachingBriefRequest):
    """Generate TTS audio of the coaching brief using the Coach voice (Rachel).

    Provide EITHER:
      - report_id: auto-extracts coaching text from a saved report
      - text: arbitrary coaching text to narrate
    """
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(500, "ELEVENLABS_API_KEY is not configured")

    narration_text = body.text

    if body.report_id and not narration_text:
        report_path = Path("reports") / f"{body.report_id}.json"
        if not report_path.exists():
            raise HTTPException(404, f"Report '{body.report_id}' not found")

        report = json.loads(report_path.read_text())
        brief = report.get("lawyer_brief", {})
        coaching = report.get("coaching_suggestions", [])
        vulnerability = report.get("critical_vulnerability", {})

        sections = []
        sections.append(
            f"Deposition Analysis for {report.get('witness_name', 'the witness')} "
            f"in {report.get('case_name', 'this case')}."
        )

        rating = brief.get("overall_rating", "")
        score = brief.get("overall_score", 0)
        if rating:
            sections.append(
                f"Overall performance rating: {rating}, with a score of {score} out of 100."
            )

        readiness = brief.get("trial_readiness", "")
        if readiness:
            sections.append(readiness)

        if vulnerability:
            sections.append(
                f"Critical vulnerability identified. "
                f"The interrogator used {vulnerability.get('interrogator_tactic_used', 'a tactical approach')}. "
                f"{vulnerability.get('witness_reaction', '')}. "
                f"Trial risk: {vulnerability.get('trial_risk', '')}."
            )

        if coaching:
            sections.append("Coaching recommendations:")
            for i, item in enumerate(coaching, 1):
                sections.append(f"Number {i}: {item}")

        next_steps = brief.get("recommended_next_steps", [])
        if next_steps:
            sections.append("Recommended next steps:")
            for i, step in enumerate(next_steps, 1):
                sections.append(f"{i}. {step}")

        narration_text = "\n\n".join(sections)

    if not narration_text:
        raise HTTPException(422, "Provide either 'report_id' or 'text'")

    voice_id = (
        settings.ELEVENLABS_INTERROGATOR_VOICE_ID if body.voice == "interrogator"
        else settings.ELEVENLABS_COACH_VOICE_ID
    )

    try:
        audio_bytes = await elevenlabs_service.text_to_speech(
            text=narration_text,
            voice_id=voice_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            502, f"ElevenLabs TTS error: {exc.response.status_code} — {exc.response.text}"
        )

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="coaching_brief.mp3"',
        },
    )


@router.post("/speak")
async def text_to_speech(body: TTSRequest):
    """Generic TTS endpoint — send any text and get audio back."""
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(500, "ELEVENLABS_API_KEY is not configured")

    voice_id = body.voice_id or settings.ELEVENLABS_COACH_VOICE_ID

    try:
        audio_bytes = await elevenlabs_service.text_to_speech(
            text=body.text,
            voice_id=voice_id,
            stability=body.stability,
            similarity_boost=body.similarity_boost,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            502, f"ElevenLabs TTS error: {exc.response.status_code} — {exc.response.text}"
        )

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="speech.mp3"'},
    )
