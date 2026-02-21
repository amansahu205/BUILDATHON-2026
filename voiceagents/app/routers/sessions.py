from fastapi import APIRouter, HTTPException
import httpx

from ..config import settings
from ..models import SessionRequest, SessionResponse
from ..prompt import build_system_prompt
from ..dependencies import get_case_store
from ..services.elevenlabs import elevenlabs_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

FIRST_MESSAGE = (
    "Good morning. Before we begin, confirm you understand "
    "this is a recorded deposition session."
)


@router.post("", response_model=SessionResponse)
async def create_session(body: SessionRequest):
    """Prepare a deposition session:
    1. Look up the case
    2. Get a signed conversation token with a per-session prompt override
       (no shared-agent mutation — safe for concurrent sessions)
    """
    case = get_case_store().get(body.case_id)
    if not case:
        raise HTTPException(404, f"Case '{body.case_id}' not found")

    if not settings.elevenlabs_api_key:
        raise HTTPException(
            500, "ELEVENLABS_API_KEY is not configured on the server"
        )

    agent_id = settings.agent_id
    prompt = build_system_prompt(case)

    override = elevenlabs_service.build_conversation_override(
        system_prompt=prompt,
        first_message=FIRST_MESSAGE,
    )

    try:
        token = await elevenlabs_service.get_conversation_token(agent_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            502,
            f"Failed to get conversation token: {exc.response.status_code} — {exc.response.text}",
        )

    witness = case.witness_name.split(";")[0].strip()

    return SessionResponse(
        conversation_token=token,
        agent_id=agent_id,
        case_id=case.id,
        case_name=case.case_name,
        witness_name=witness,
        conversation_config_override=override,
    )
