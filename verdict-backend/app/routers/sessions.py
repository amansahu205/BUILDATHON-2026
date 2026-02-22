import json
import time
import base64
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.session import Session
from app.agents.interrogator import generate_question
from app.agents.objection import analyze_for_objections
from app.agents.detector import detect_inconsistency
from app.agents.models import VerdictCase
from app.services.elevenlabs import text_to_speech
from app.schemas.sessions import QuestionRequest, ObjectionRequest, InconsistencyRequest
from app.config import settings

router = APIRouter()


def _build_verdict_case(session: Session) -> VerdictCase:
    """Assemble a VerdictCase from the ORM objects attached to a Session.

    Requires session.case and session.witness to be eager-loaded before calling.
    """
    case = session.case
    witness = session.witness
    return VerdictCase(
        id=case.id,
        case_name=case.name,
        case_type=case.case_type,
        opposing_party=case.opposing_firm or "opposing party",
        deposition_date=case.deposition_date.isoformat() if case.deposition_date else "TBD",
        witness_name=witness.name if witness else "Unknown",
        witness_role=witness.role if witness else "OTHER",
        extracted_facts=case.extracted_facts or "",
        prior_statements=case.prior_statements or "",
        exhibit_list=case.exhibit_list or "",
        focus_areas=", ".join(session.focus_areas) if session.focus_areas else "",
        aggression_level=session.aggression or "STANDARD",
    )


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {
        "success": True,
        "data": {
            "id": session.id,
            "status": session.status,
            "sessionNumber": session.session_number,
            "durationMinutes": session.duration_minutes,
            "startedAt": session.started_at,
            "questionCount": session.question_count,
        },
    }


@router.post("/{session_id}/start")
async def start_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    session.status = "ACTIVE"
    session.started_at = datetime.utcnow()
    await db.commit()
    return {
        "success": True,
        "data": {
            "sessionId": session_id,
            "status": "ACTIVE",
            "startedAt": session.started_at.isoformat(),
        },
    }


@router.post("/{session_id}/agents/question")
async def stream_question(
    session_id: str,
    body: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.firm_id == user.firm_id)
        .options(
            selectinload(Session.case),
            selectinload(Session.witness),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    verdict_case = _build_verdict_case(session)

    async def event_stream():
        full_text = ""
        yield f"data: {json.dumps({'type': 'QUESTION_START', 'questionNumber': body.questionNumber})}\n\n"

        async for chunk in generate_question(
            case=verdict_case,
            current_topic=body.currentTopic,
            question_number=body.questionNumber,
            prior_answer=body.priorAnswer,
            hesitation_detected=body.hesitationDetected,
            recent_inconsistency_flag=body.recentInconsistencyFlag,
            prior_weak_areas=session.prior_weak_areas or [],
        ):
            full_text += chunk
            yield f"data: {json.dumps({'type': 'QUESTION_CHUNK', 'text': chunk})}\n\n"

        try:
            audio = await text_to_speech(full_text, settings.ELEVENLABS_INTERROGATOR_VOICE_ID)
            yield f"data: {json.dumps({'type': 'QUESTION_AUDIO', 'audioBase64': base64.b64encode(audio).decode()})}\n\n"
        except Exception:
            pass  # TTS failure is non-fatal; frontend falls back to text

        yield f"data: {json.dumps({'type': 'QUESTION_END', 'fullText': full_text})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{session_id}/agents/objection")
async def check_objection(
    session_id: str,
    body: ObjectionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    start = time.time()
    analysis = await analyze_for_objections(
        question_text=body.questionText,
        session_id=session_id,
    )
    return {
        "success": True,
        "data": {**analysis, "processingMs": int((time.time() - start) * 1000)},
    }


@router.post("/{session_id}/agents/inconsistency")
async def check_inconsistency(
    session_id: str,
    body: InconsistencyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.firm_id == user.firm_id)
        .options(selectinload(Session.case))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    detection = await detect_inconsistency(
        question_text=body.questionText,
        answer_text=body.answerText,
        session_id=session_id,
        case_id=session.case_id,          # Databricks filters prior_statements by case_id
        case_type=session.case.case_type if session.case else "OTHER",
    )
    return {"success": True, "data": detection}
