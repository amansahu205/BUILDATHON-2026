import json
import re
from app.services.claude import claude_chat
from app.services.elevenlabs import text_to_speech
from app.config import settings

ORCHESTRATOR_SYSTEM = """You are an elite litigation coach reviewing a completed deposition practice session.
Analyze the session transcript, alerts, and performance data to generate a comprehensive coaching brief.
Respond ONLY with valid JSON matching the exact format specified.
STRICT RULES:
- No preamble, no markdown, no code fences around the JSON
- All string values must be on a single line; use \\n for paragraph breaks, never literal newlines inside string values
- No trailing commas
- No comments"""


def _extract_json(text: str) -> dict:
    """Robustly extract JSON from Claude response, handling fences and literal newlines."""
    cleaned = text.strip()

    # 1. Strip markdown code fences with regex
    fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
    if fence:
        cleaned = fence.group(1).strip()

    # 2. Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Find the outermost { ... } block
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # 4. Replace literal newlines inside string values and retry
            sanitized = re.sub(r'(?<!\\)\n', r'\\n', candidate)
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"Could not extract valid JSON from orchestrator response. "
        f"First 300 chars: {text[:300]}"
    )


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

Generate a coaching brief as JSON (ALL strings must be single-line, use \\n for paragraph breaks):
{{
  "sessionScore": <integer 0-100>,
  "consistencyRate": <float 0.0-1.0>,
  "topRecommendations": ["<rec 1>", "<rec 2>", "<rec 3>"],
  "narrativeText": "<coaching narrative using \\n for paragraph breaks, no literal newlines>",
  "weaknessMapScores": {{
    "composure": <0-100>, "tactical_discipline": <0-100>, "professionalism": <0-100>,
    "directness": <0-100>, "consistency": <0-100>
  }},
  "confirmedFlags": <integer>,
  "objectionCount": <integer>,
  "composureAlerts": <integer>
}}"""

    raw = await claude_chat(ORCHESTRATOR_SYSTEM, prompt, max_tokens=1500)
    brief_data = _extract_json(raw)

    narration = (
        f"Session complete. Your overall score is {brief_data['sessionScore']} out of 100. "
        f"{brief_data.get('narrativeText', '')}"
    )
    try:
        audio_bytes = await text_to_speech(narration, settings.ELEVENLABS_COACH_VOICE_ID)
        brief_data["coachAudioBytes"] = audio_bytes
    except Exception:
        brief_data["coachAudioBytes"] = None

    return brief_data
