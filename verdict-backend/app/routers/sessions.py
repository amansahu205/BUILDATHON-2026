import json
import time
import base64
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.session import Session
from app.models.witness import Witness
from app.models.case import Case
from app.models.session_event import SessionEvent
from app.models.alert import Alert
from app.agents.interrogator import generate_question
from app.agents.objection import analyze_for_objections
from app.agents.detector import detect_inconsistency
from app.agents.models import VerdictCase
from app.services.elevenlabs import text_to_speech, speech_to_text, _voice_available
from app.services.s3 import upload_bytes
from app.schemas.sessions import CreateSessionRequest, QuestionRequest, ObjectionRequest, InconsistencyRequest
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


def _append_transcript_line(session: Session, speaker: str, content: str) -> None:
    line = f"[{speaker}]: {content}".strip()
    if session.transcript_raw:
        session.transcript_raw = f"{session.transcript_raw.rstrip()}\n{line}"
    else:
        session.transcript_raw = line


def _event_to_live_entry(event: SessionEvent, idx: int, started_at: datetime | None) -> dict:
    ts = 0
    if started_at and event.created_at:
        ts = max(0, int((event.created_at - started_at).total_seconds()))
    speaker = "system"
    if event.speaker_role == "INTERROGATOR":
        speaker = "interrogator"
    elif event.speaker_role == "WITNESS":
        speaker = "witness"
    return {
        "id": event.id or f"evt-{idx}",
        "speaker": speaker,
        "text": event.content or "",
        "timestamp": ts,
        "flagged": False,
    }


def _alert_to_live_alert(alert: Alert) -> dict:
    type_map = {
        "OBJECTION": "objection",
        "INCONSISTENCY": "inconsistency",
        "COMPOSURE": "behavioral",
    }
    severity = "info"
    if (alert.impeachment_risk or "").upper() == "HIGH":
        severity = "critical"
    elif (alert.impeachment_risk or "").upper() == "MEDIUM":
        severity = "warning"

    return {
        "id": alert.id,
        "type": type_map.get(alert.alert_type, "behavioral"),
        "severity": severity,
        "timestamp": int(alert.question_number or 0),
        "title": alert.alert_type.title(),
        "description": alert.annotation or alert.fre_classification or "Live alert",
        "freRule": alert.fre_rule,
        "confidenceScore": alert.confidence,
        "priorQuote": alert.prior_quote,
        "priorSource": "Prior statement" if alert.prior_quote else None,
        "priorPageLine": (
            f"p.{alert.prior_source_page} l.{alert.prior_source_line}"
            if alert.prior_source_page is not None and alert.prior_source_line is not None
            else None
        ),
        "status": (alert.status or "PENDING").lower(),
    }


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
            "caseId": session.case_id,
            "witnessId": session.witness_id,
            "status": session.status,
            "sessionNumber": session.session_number,
            "durationMinutes": session.duration_minutes,
            "focusAreas": session.focus_areas or [],
            "aggression": session.aggression,
            "objectionCopilotEnabled": session.objection_copilot_enabled,
            "sentinelEnabled": session.sentinel_enabled,
            "createdAt": session.created_at,
            "startedAt": session.started_at,
            "endedAt": session.ended_at,
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


@router.post("/")
async def create_session(
    body: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Create a new deposition practice session for a witness."""
    result = await db.execute(
        select(Case).where(Case.id == body.caseId, Case.firm_id == user.firm_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(404, detail={"code": "CASE_NOT_FOUND"})

    result = await db.execute(
        select(Witness).where(Witness.id == body.witnessId, Witness.case_id == body.caseId)
    )
    witness = result.scalar_one_or_none()
    if not witness:
        raise HTTPException(404, detail={"code": "WITNESS_NOT_FOUND"})

    existing = await db.execute(
        select(Session).where(
            Session.witness_id == body.witnessId,
            Session.case_id == body.caseId,
        )
    )
    existing_sessions = existing.scalars().all()
    session_number = len(existing_sessions) + 1

    from nanoid import generate
    witness_token = generate(size=24)

    session = Session(
        case_id=body.caseId,
        witness_id=body.witnessId,
        firm_id=user.firm_id,
        attorney_id=user.id,
        session_number=session_number,
        status="LOBBY",
        duration_minutes=body.durationMinutes,
        aggression=body.aggression,
        focus_areas=body.focusAreas,
        objection_copilot_enabled=body.objectionCopilotEnabled,
        sentinel_enabled=body.sentinelEnabled,
        witness_token=witness_token,
    )
    db.add(session)

    witness.session_count = session_number
    await db.commit()
    await db.refresh(session)

    return {
        "success": True,
        "data": {
            "id": session.id,
            "sessionNumber": session_number,
            "status": "LOBBY",
            "witnessToken": witness_token,
            "durationMinutes": session.duration_minutes,
        },
    }


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """End an active session and mark it as COMPLETE."""
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    if session.status not in ("ACTIVE", "PAUSED"):
        raise HTTPException(400, detail={
            "code": "INVALID_STATUS",
            "message": f"Cannot end session in {session.status} state.",
        })

    session.status = "COMPLETE"
    session.ended_at = datetime.utcnow()
    await db.commit()

    return {
        "success": True,
        "data": {
            "sessionId": session_id,
            "status": "COMPLETE",
            "endedAt": session.ended_at.isoformat(),
        },
    }


@router.post("/{session_id}/pause")
async def pause_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Pause an active session."""
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    if session.status != "ACTIVE":
        raise HTTPException(400, detail={"code": "NOT_ACTIVE"})

    session.status = "PAUSED"
    session.paused_at = datetime.utcnow()
    await db.commit()

    return {"success": True, "data": {"sessionId": session_id, "status": "PAUSED"}}


@router.post("/{session_id}/resume")
async def resume_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Resume a paused session."""
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    if session.status != "PAUSED":
        raise HTTPException(400, detail={"code": "NOT_PAUSED"})

    if session.paused_at:
        pause_duration = int((datetime.utcnow() - session.paused_at).total_seconds() * 1000)
        session.total_pause_ms = (session.total_pause_ms or 0) + pause_duration

    session.status = "ACTIVE"
    session.paused_at = None
    await db.commit()

    return {"success": True, "data": {"sessionId": session_id, "status": "ACTIVE"}}


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

        event = SessionEvent(
            session_id=session.id,
            firm_id=session.firm_id,
            event_type="QUESTION",
            speaker_role="INTERROGATOR",
            content=full_text,
            question_number=body.questionNumber,
            metadata_={"topic": body.currentTopic},
        )
        db.add(event)
        session.question_count = max(session.question_count or 0, body.questionNumber)
        _append_transcript_line(session, "INTERROGATOR", full_text)
        await db.commit()

        try:
            audio = await text_to_speech(full_text, settings.ELEVENLABS_INTERROGATOR_VOICE_ID)
            yield f"data: {json.dumps({'type': 'QUESTION_AUDIO', 'audioBase64': base64.b64encode(audio).decode()})}\n\n"
        except Exception:
            pass  # TTS failure is non-fatal; frontend falls back to text

        yield f"data: {json.dumps({'type': 'QUESTION_END', 'fullText': full_text})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{session_id}/answers/audio")
async def upload_answer_audio(
    session_id: str,
    file: UploadFile = File(...),
    questionNumber: int = Form(0),
    durationMs: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.firm_id == user.firm_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    if session.status not in ("ACTIVE", "PAUSED"):
        raise HTTPException(400, detail={"code": "INVALID_STATUS"})

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(400, detail={"code": "EMPTY_AUDIO"})

    audio_key = None
    try:
        ext = (file.filename or "chunk.webm").split(".")[-1]
        audio_key = (
            f"sessions/{session.firm_id}/{session_id}/answers/"
            f"{int(time.time() * 1000)}_q{questionNumber or 0}.{ext}"
        )
        upload_bytes(audio_key, audio_bytes, file.content_type or "application/octet-stream")
    except Exception:
        audio_key = None

    try:
        transcript_text = (await speech_to_text(audio_bytes)).strip()
    except Exception:
        transcript_text = ""
    if not transcript_text:
        transcript_text = "(inaudible)"

    event = SessionEvent(
        session_id=session.id,
        firm_id=session.firm_id,
        event_type="ANSWER",
        speaker_role="WITNESS",
        content=transcript_text,
        question_number=questionNumber or None,
        audio_s3_key=audio_key,
        duration_ms=durationMs,
        metadata_={"filename": file.filename, "contentType": file.content_type},
    )
    db.add(event)
    _append_transcript_line(session, "WITNESS", transcript_text)
    await db.commit()
    await db.refresh(event)

    return {
        "success": True,
        "data": {
            "eventId": event.id,
            "sessionId": session_id,
            "questionNumber": questionNumber,
            "transcriptText": transcript_text,
            "audioS3Key": audio_key,
            "durationMs": durationMs,
        },
    }


@router.get("/{session_id}/live-state")
async def get_live_state(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.firm_id == user.firm_id)
        .options(
            selectinload(Session.events),
            selectinload(Session.alerts),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    events = sorted(session.events or [], key=lambda e: e.created_at or datetime.utcnow())
    alerts = sorted(session.alerts or [], key=lambda a: a.created_at or datetime.utcnow())
    last_topic = "PRIOR_STATEMENTS"
    for e in reversed(events):
        if e.event_type == "QUESTION" and e.metadata_ and e.metadata_.get("topic"):
            last_topic = e.metadata_.get("topic")
            break

    elapsed = 0
    if session.started_at:
        end = session.ended_at or datetime.utcnow()
        elapsed = max(0, int((end - session.started_at).total_seconds()))

    return {
        "success": True,
        "data": {
            "status": (session.status or "LOBBY").lower(),
            "elapsedSeconds": elapsed,
            "totalSeconds": int((session.duration_minutes or 0) * 60),
            "currentTopic": last_topic,
            "questionCount": session.question_count or 0,
            "transcript": [
                _event_to_live_entry(event, idx, session.started_at)
                for idx, event in enumerate(events)
                if event.content
            ],
            "alerts": [_alert_to_live_alert(alert) for alert in alerts],
            "witnessConnected": bool(session.witness_joined),
            "serviceStatus": {
                "elevenlabs": _voice_available(),
                "nemotron": bool(settings.NEMOTRON_API_KEY),
                "nia": True,
            },
        },
    }


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
    if analysis.get("isObjectionable"):
        alert = Alert(
            session_id=session_id,
            firm_id=user.firm_id,
            alert_type="OBJECTION",
            status="PENDING",
            confidence=analysis.get("confidence"),
            current_quote=body.questionText,
            fre_rule=analysis.get("freRule"),
            fre_classification=analysis.get("category"),
            question_number=body.questionNumber,
        )
        db.add(alert)
        await db.commit()
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
    if detection.get("flagFound"):
        alert = Alert(
            session_id=session_id,
            firm_id=user.firm_id,
            alert_type="INCONSISTENCY",
            status="PENDING",
            confidence=detection.get("contradictionConfidence"),
            prior_quote=detection.get("priorQuote"),
            prior_source_page=detection.get("priorDocumentPage"),
            prior_source_line=detection.get("priorDocumentLine"),
            current_quote=body.answerText,
            impeachment_risk=detection.get("impeachmentRisk", "LOW"),
            question_number=body.questionNumber,
        )
        db.add(alert)
        await db.commit()
    return {"success": True, "data": detection}
