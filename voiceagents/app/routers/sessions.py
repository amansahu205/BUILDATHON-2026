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
    2. PATCH the ElevenLabs agent with the case-specific system prompt
       (gracefully skipped if the API key lacks convai_write permission)
    3. Get a signed conversation token for the frontend
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

    prompt_patched = False
    try:
        await elevenlabs_service.patch_agent_prompt(
            agent_id=agent_id,
            system_prompt=prompt,
            first_message=FIRST_MESSAGE,
        )
        prompt_patched = True
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            print(
                f"Warning: API key lacks convai_write permission — "
                f"skipping prompt patch. Agent will use its console-configured prompt."
            )
        else:
            raise HTTPException(
                502,
                f"Failed to patch ElevenLabs agent: {exc.response.status_code} — {exc.response.text}",
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
    )
