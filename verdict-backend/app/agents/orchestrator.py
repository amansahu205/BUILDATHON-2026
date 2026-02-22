import json
from app.services.claude import claude_chat
from app.services.elevenlabs import text_to_speech
from app.config import settings

ORCHESTRATOR_SYSTEM = """You are an elite litigation coach reviewing a completed deposition practice session.
Analyze the session transcript, alerts, and performance data to generate a comprehensive coaching brief.
Respond ONLY with valid JSON matching the exact format specified. No preamble, no markdown."""


async def generate_brief(
    session_id: str,
    transcript: list[dict],
    alerts: list[dict],
    case_type: str,
    witness_role: str,
    aggression_level: str,
    duration_minutes: int,
    question_count: int,
) -> dict:
    transcript_text = "\n".join(
        f"[{e.get('speaker', 'UNKNOWN')}] {e.get('content', '')}" for e in transcript
    )
    alerts_text = "\n".join(
        f"- {a.get('alertType', '')}: {a.get('priorQuote', '')} (confidence: {a.get('confidence', 0):.2f})"
        for a in alerts
    ) or "None"

    prompt = f"""Session Summary:
- Case type: {case_type}
- Witness role: {witness_role}
- Aggression level: {aggression_level}
- Duration: {duration_minutes} minutes
- Questions asked: {question_count}

Full Transcript:
{transcript_text}

Alerts Fired:
{alerts_text}

Generate a coaching brief as JSON:
{{
  "sessionScore": <integer 0-100>,
  "consistencyRate": <float 0.0-1.0>,
  "topRecommendations": ["<rec 1>", "<rec 2>", "<rec 3>"],
  "narrativeText": "<2-3 paragraph coaching narrative>",
  "weaknessMapScores": {{
    "timeline": <0-100>, "financials": <0-100>, "communications": <0-100>,
    "relationships": <0-100>, "composure": <0-100>
  }},
  "confirmedFlags": <integer>,
  "objectionCount": <integer>,
  "composureAlerts": <integer>
}}"""

    raw = await claude_chat(ORCHESTRATOR_SYSTEM, prompt, max_tokens=1500)
    brief_data = json.loads(raw)

    narration = f"Session complete. Your overall score is {brief_data['sessionScore']} out of 100. {brief_data['narrativeText']}"
    try:
        audio_bytes = await text_to_speech(narration, settings.ELEVENLABS_COACH_VOICE_ID)
        brief_data["coachAudioBytes"] = audio_bytes
    except Exception:
        brief_data["coachAudioBytes"] = None

    return brief_data
